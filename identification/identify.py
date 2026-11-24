from dataclasses import dataclass
from pathlib import Path
import itertools
import math
import sys
import numpy as np

FOLDER = Path(__file__).parent
sys.path.append(str(FOLDER.parent / "catalog"))
sys.path.append(str(FOLDER.parent / "mapping"))
sys.path.append(str(FOLDER.parent / "dataset"))
sys.path.append(str(FOLDER.parent / "detection"))
from star_catalog import CatalogStar
from constellations import FIGURES
from generate_dataset import direction, read_catalog
from star_detection import StarDetector
from star_map import SIZE

PHOTOS = FOLDER.parent / "detection" / "input"
BOX_MARGIN = 0.15 # the YOLO box is widened by 15 % on each side
DRAWING_TOLERANCE = 0.05 # a star falls on a point within 5 % of the size of the drawing
NAMING_TOLERANCE_PX = 5 # max distance between a placed star and a detected point
FOCAL_RANGE = 0.3 # the focal length is searched up to 30 % away from its first guess
FOCAL_TRIES = 31
CANDIDATES_PER_POINT = 2 # catalogue stars tried for each detected point
REFINEMENTS = 3
MAX_ERROR_DEG = 0.35 # beyond this, the stars do not fall well enough and we say we do not know
MIN_NAMED = 4

type Box = tuple[float, float, float, float] # left, top, right, bottom

# the box YOLO draws around the Big Dipper on the map of our two photos
EXAMPLES: dict[str, Box] = {
    "5EDC6EFC-96D4-4133-B3E6-95080B4A5F90.jpg": (229.1, 194.2, 525.5, 343.2),
    "4E7389EB-1824-4346-B29D-B48E8E28571A.jpg": (153.0, 193.2, 434.7, 363.8),
}

@dataclass
class Orientation:
    focal: float # in pixels
    rotation: np.ndarray # turns a direction of the sky into a direction of the camera
    error_deg: float

@dataclass
class Identification:
    constellation: str
    orientation: Orientation
    names: list[CatalogStar | None] # the star of each detected point, None if unknown

# names every star of a photo once YOLO has found a constellation, without the time or the place
class Identifier:
    # keeps the catalogue and the direction of each star
    def __init__(self, stars: list[CatalogStar]):
        self.stars: list[CatalogStar] = stars
        self.by_hip: dict[int, CatalogStar] = {star.hip: star for star in stars}
        self.directions: np.ndarray = np.array([direction(star.ra, star.dec) for star in stars])

    # puts the stars of the drawing flat, around its center (real part to the east, imaginary part to the north)
    def flat_drawing(self, hips: list[int]) -> np.ndarray:
        directions = [direction(self.by_hip[hip].ra, self.by_hip[hip].dec) for hip in hips]
        center = sum(directions)
        center = center / np.linalg.norm(center)
        east = np.cross([0.0, 0.0, 1.0], center)
        east = east / np.linalg.norm(east)
        north = np.cross(center, east)
        return np.array([complex(d @ east / (d @ center), d @ north / (d @ center)) for d in directions])

    # finds which detected point is each star of the drawing (Hipparcos number to index of the point)
    def fit_drawing(self, points: np.ndarray, box: Box, constellation: str) -> dict[int, int]:
        hips = sorted({hip for line in FIGURES[constellation] for hip in line})
        drawing = self.flat_drawing(hips)
        drawing_size = max(abs(a - b) for a, b in itertools.combinations(drawing, 2))

        left, top, right, bottom = box
        margin_x = BOX_MARGIN * (right - left)
        margin_y = BOX_MARGIN * (bottom - top)
        wide: Box = (left - margin_x, top - margin_y, right + margin_x, bottom + margin_y)
        photo = np.array([complex(x, y) for x, y in points])
        candidates = [i for i, z in enumerate(photo) if inside(z, wide)]

        # two stars are enough to place the drawing, so we try every pair of stars on every pair of points
        best: dict[int, int] = {}
        best_error = math.inf
        for a, b in itertools.permutations(range(len(hips)), 2):
            for p, q in itertools.permutations(candidates, 2):
                scale = (photo[q] - photo[p]) / (drawing[b] - drawing[a]) # size and angle of the drawing
                placed = scale * (drawing - drawing[a]) + photo[p]
                if not all(inside(z, wide) for z in placed):
                    continue
                tolerance = DRAWING_TOLERANCE * abs(scale) * drawing_size
                found: dict[int, int] = {}
                error = 0.0
                for k, z in enumerate(placed):
                    distances = np.abs(photo[candidates] - z)
                    closest = int(np.argmin(distances))
                    if distances[closest] < tolerance:
                        found[hips[k]] = candidates[closest]
                        error += distances[closest]
                if len(found) > len(best) or (len(found) == len(best) and error < best_error):
                    best = found
                    best_error = error
        # the two stars of the pair always fit, so we want a third one and more than half of the drawing
        if len(best) < 3 or 2 * len(best) <= len(hips):
            return {}
        return best

    # finds the focal length and the rotation that best explain the stars already named
    def orient(self, points: np.ndarray, width: int, height: int,
               pairs: list[tuple[int, CatalogStar]], focal_guess: float) -> Orientation:
        sky = [direction(star.ra, star.dec) for _, star in pairs]
        best: Orientation | None = None
        for focal in np.linspace(focal_guess * (1 - FOCAL_RANGE), focal_guess * (1 + FOCAL_RANGE), FOCAL_TRIES):
            measured = [pixel_direction(points[i], width, height, focal) for i, _ in pairs]
            rotation = kabsch(measured, sky)
            error = angular_error(measured, sky, rotation)
            if best is None or error < best.error_deg:
                best = Orientation(focal, rotation, error)
        return best

    # places the whole catalogue on the photo and gives each detected point the star that falls on it
    def name_all(self, points: np.ndarray, width: int, height: int,
                 orientation: Orientation) -> list[CatalogStar | None]:
        camera = self.directions @ orientation.rotation.T
        x = width / 2 + orientation.focal * camera[:, 0] / camera[:, 2]
        y = height / 2 + orientation.focal * camera[:, 1] / camera[:, 2]
        visible = (camera[:, 2] > 0) & (x >= 0) & (x < width) & (y >= 0) & (y < height)
        names: list[CatalogStar | None] = [None] * len(points)
        # the catalogue goes from the brightest star, so at one place the brightest star gets the name
        for i in np.nonzero(visible)[0][:CANDIDATES_PER_POINT * len(points)]:
            distances = np.hypot(points[:, 0] - x[i], points[:, 1] - y[i])
            closest = int(np.argmin(distances))
            if distances[closest] < NAMING_TOLERANCE_PX and names[closest] is None:
                names[closest] = self.stars[i]
        return names

    # the whole chain, or None if we do not know
    def identify(self, points: np.ndarray, width: int, height: int, box: Box,
                 constellation: str) -> Identification | None:
        fitted = self.fit_drawing(points, box, constellation)
        if not fitted:
            return None
        # we orient with the stars of the drawing, name everything, then start again with all the named stars
        pairs = [(i, self.by_hip[hip]) for hip, i in fitted.items()]
        focal = first_focal(points, pairs)
        for _ in range(REFINEMENTS):
            orientation = self.orient(points, width, height, pairs, focal)
            focal = orientation.focal
            names = self.name_all(points, width, height, orientation)
            pairs = [(i, star) for i, star in enumerate(names) if star is not None]
            if len(pairs) < MIN_NAMED:
                return None
        if orientation.error_deg > MAX_ERROR_DEG:
            return None
        return Identification(constellation, orientation, names)

# checks that a point is in the box
def inside(z: complex, box: Box) -> bool:
    left, top, right, bottom = box
    return left <= z.real <= right and top <= z.imag <= bottom

# turns a pixel into a direction for the camera (x to the right, y down, z in front)
def pixel_direction(point: np.ndarray, width: int, height: int, focal: float) -> np.ndarray:
    v = np.array([point[0] - width / 2, point[1] - height / 2, focal])
    return v / np.linalg.norm(v)

# the rotation that best brings the directions of the sky onto the measured ones (Kabsch algorithm, with an SVD)
def kabsch(measured: list[np.ndarray], sky: list[np.ndarray]) -> np.ndarray:
    u, _, vt = np.linalg.svd(np.array(measured).T @ np.array(sky))
    sign = np.sign(np.linalg.det(u @ vt))
    return u @ np.diag([1, 1, sign]) @ vt

# the mean gap in degrees between the measured stars and the turned catalogue
def angular_error(measured: list[np.ndarray], sky: list[np.ndarray], rotation: np.ndarray) -> float:
    gaps = [math.degrees(math.acos(min(1.0, float(m @ (rotation @ s))))) for m, s in zip(measured, sky)]
    return math.sqrt(np.mean(np.square(gaps)))

# a first guess of the focal length, from the pixels per radian between two stars
def first_focal(points: np.ndarray, pairs: list[tuple[int, CatalogStar]]) -> float:
    (i, a), (j, b) = pairs[:2]
    angle = math.acos(min(1.0, float(direction(a.ra, a.dec) @ direction(b.ra, b.dec))))
    return float(np.hypot(*(points[i] - points[j]))) / angle

# turns a box on the map into a box on the photo
def box_on_photo(box: Box, width: int, height: int) -> Box:
    scale = SIZE / max(width, height)
    offset_x = (SIZE - width * scale) / 2
    offset_y = (SIZE - height * scale) / 2
    left, top, right, bottom = box
    return ((left - offset_x) / scale, (top - offset_y) / scale, (right - offset_x) / scale, (bottom - offset_y) / scale)

# names the stars of our two photos of the Big Dipper, from the box YOLO found on their map
def main():
    identifier = Identifier(read_catalog())
    for name, box in EXAMPLES.items():
        detection = StarDetector(PHOTOS / name).detect()
        points = np.array([[star.x, star.y] for star in detection.stars], dtype=float)
        box = box_on_photo(box, detection.width, detection.height)
        result = identifier.identify(points, detection.width, detection.height, box, "Ursa Major")
        if result is None:
            print(name+": we do not know")
            continue
        field = math.degrees(2 * math.atan(detection.width / 2 / result.orientation.focal))
        named = [star for star in result.names if star is not None]
        print(name+": "+str(len(named))+" stars named, field of view "+str(round(field, 1))+" deg, error "
              +str(round(result.orientation.error_deg, 3))+" deg")
        for star in named:
            print("  HIP "+str(star.hip)+", magnitude "+str(star.magnitude))

if __name__ == "__main__":
    main()

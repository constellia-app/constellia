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

type Box = tuple[float, float, float, float] # left, top, right, bottom

# the box YOLO draws around the Big Dipper on the map of our two photos
EXAMPLES: dict[str, Box] = {
    "5EDC6EFC-96D4-4133-B3E6-95080B4A5F90.jpg": (229.1, 194.2, 525.5, 343.2),
    "4E7389EB-1824-4346-B29D-B48E8E28571A.jpg": (153.0, 193.2, 434.7, 363.8),
}

# names the stars of a photo once YOLO has found a constellation
class Identifier:
    # keeps the catalogue, with each star by its Hipparcos number
    def __init__(self, stars: list[CatalogStar]):
        self.stars: list[CatalogStar] = stars
        self.by_hip: dict[int, CatalogStar] = {star.hip: star for star in stars}

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

# checks that a point is in the box
def inside(z: complex, box: Box) -> bool:
    left, top, right, bottom = box
    return left <= z.real <= right and top <= z.imag <= bottom

# turns a box on the map into a box on the photo
def box_on_photo(box: Box, width: int, height: int) -> Box:
    scale = SIZE / max(width, height)
    offset_x = (SIZE - width * scale) / 2
    offset_y = (SIZE - height * scale) / 2
    left, top, right, bottom = box
    return ((left - offset_x) / scale, (top - offset_y) / scale, (right - offset_x) / scale, (bottom - offset_y) / scale)

# finds the stars of the Big Dipper on our two photos, from the box YOLO found on their map
def main():
    identifier = Identifier(read_catalog())
    for name, box in EXAMPLES.items():
        detection = StarDetector(PHOTOS / name).detect()
        points = np.array([[star.x, star.y] for star in detection.stars], dtype=float)
        box = box_on_photo(box, detection.width, detection.height)
        fitted = identifier.fit_drawing(points, box, "Ursa Major")
        print(name+": "+str(len(fitted))+" stars of the drawing found")
        for hip, i in fitted.items():
            print("  HIP "+str(hip)+" at x="+str(int(points[i][0]))+", y="+str(int(points[i][1])))

if __name__ == "__main__":
    main()

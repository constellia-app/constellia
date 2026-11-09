from pathlib import Path
import csv
import math
import random
import sys
import cv2
import numpy as np

FOLDER = Path(__file__).parent
sys.path.append(str(FOLDER.parent / "catalog"))
sys.path.append(str(FOLDER.parent / "mapping"))
from star_catalog import CatalogStar
from constellations import FIGURES
from star_map import SIZE, StarMap

CATALOG = FOLDER.parent / "catalog" / "star_catalog.csv"
OUTPUT = FOLDER / "output"
IMAGE_COUNT = 20000
VALIDATION_SHARE = 0.15 # the maps kept aside to check the training
SOUTH_OF_FRANCE_LATITUDE = 41.4
MIN_DECLINATION = SOUTH_OF_FRANCE_LATITUDE - 90 + 10 # further south, a star never rises 10 degrees
MIN_FIELD_DEG = 40 # the field of view of a phone
MAX_FIELD_DEG = 80
MIN_STARS = 10 # a photo shows between 10 and 80 stars
MAX_STARS = 80
MAX_FALSE_POINTS = 10 # noise, edges of clouds, street lights
BOX_MARGIN_PX = 15
CONSTELLATIONS = list(FIGURES) # the YOLO classes, in this order

# all the stars of the catalogue, from the brightest to the faintest
def read_catalog() -> list[CatalogStar]:
    with open(CATALOG, encoding="utf-8") as file:
        stars = [CatalogStar(int(line["hip"]), float(line["ra_deg"]), float(line["dec_deg"]),
                             float(line["magnitude"])) for line in csv.DictReader(file)]
    return sorted(stars, key=lambda star: star.magnitude)

# the direction of a star seen from the Earth
def direction(ra: float, dec: float) -> np.ndarray:
    ra = math.radians(ra)
    dec = math.radians(dec)
    return np.array([math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec)])

# fake photos of the sky made from the catalogue, so the box around each constellation is exact
class SkyGenerator:
    # keeps the stars seen from France, and the ones that draw a constellation
    def __init__(self, stars: list[CatalogStar]):
        self.stars: list[CatalogStar] = stars
        self.directions: np.ndarray = np.array([direction(star.ra, star.dec) for star in stars])
        in_a_figure = {hip for lines in FIGURES.values() for line in lines for hip in line}
        self.visible: list[CatalogStar] = [star for star in stars if star.dec >= MIN_DECLINATION]
        self.in_figures: list[CatalogStar] = [star for star in self.visible if star.hip in in_a_figure]

    # the three axes of the camera (right, up, and the direction it points to)
    def aim(self, center: CatalogStar, roll: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        axis = direction(center.ra, center.dec)
        # facing the sky, east is on the left, so the right of the image points west
        west = np.cross(axis, [0.0, 0.0, 1.0])
        west = west / np.linalg.norm(west)
        north = np.cross(west, axis)
        right = math.cos(roll) * west + math.sin(roll) * north
        up = -math.sin(roll) * west + math.cos(roll) * north
        return right, up, axis

    # the position of every star on the map, and whether it falls inside
    def project(self, right: np.ndarray, up: np.ndarray, axis: np.ndarray,
                focal: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        depth = self.directions @ axis
        x = SIZE / 2 + focal * (self.directions @ right) / depth
        y = SIZE / 2 - focal * (self.directions @ up) / depth
        inside = (depth > 0) & (x >= 0) & (x < SIZE) & (y >= 0) & (y < SIZE)
        return x, y, inside

    # points the camera half the time at a constellation, otherwise anywhere
    def random_view(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        center = random.choice(self.in_figures if random.random() < 0.5 else self.visible)
        right, up, axis = self.aim(center, random.uniform(0, 2 * math.pi))
        field = math.radians(random.uniform(MIN_FIELD_DEG, MAX_FIELD_DEG))
        return self.project(right, up, axis, SIZE / 2 / math.tan(field / 2))

    # one map and its YOLO labels, with only the brightest stars as on a photo
    def generate(self) -> tuple[np.ndarray, list[str]]:
        x, y, inside = self.random_view()
        drawn = list(np.nonzero(inside)[0][:random.randint(MIN_STARS, MAX_STARS)])
        xs = list(x[drawn])
        ys = list(y[drawn])
        for _ in range(random.randint(0, MAX_FALSE_POINTS)):
            xs.append(random.uniform(0, SIZE))
            ys.append(random.uniform(0, SIZE))
        positions = {self.stars[i].hip: (x[i], y[i]) for i in drawn}
        return StarMap.draw(xs, ys), self.annotate(positions)

    # a box around each constellation with at least 3 stars and more than half of its drawing
    def annotate(self, positions: dict[int, tuple[float, float]]) -> list[str]:
        labels: list[str] = []
        for number, constellation in enumerate(CONSTELLATIONS):
            drawing = {hip for line in FIGURES[constellation] for hip in line}
            seen = [positions[hip] for hip in drawing if hip in positions]
            if len(seen) < 3 or len(seen) * 2 <= len(drawing):
                continue
            left = max(0, min(p[0] for p in seen) - BOX_MARGIN_PX)
            right = min(SIZE, max(p[0] for p in seen) + BOX_MARGIN_PX)
            top = max(0, min(p[1] for p in seen) - BOX_MARGIN_PX)
            bottom = min(SIZE, max(p[1] for p in seen) + BOX_MARGIN_PX)
            # class, center x, center y, width and height, between 0 and 1 (the YOLO format)
            labels.append(f"{number} {(left + right) / 2 / SIZE:.5f} {(top + bottom) / 2 / SIZE:.5f} "
                          f"{(right - left) / SIZE:.5f} {(bottom - top) / SIZE:.5f}")
        return labels

# the file that tells YOLO where the images are and the name of each class
def write_config(folder: Path):
    lines = ["path: "+str(folder.resolve()), "train: images/train", "val: images/val", "names:"]
    lines += ["  "+str(number)+": "+name for number, name in enumerate(CONSTELLATIONS)]
    (folder / "constellations.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")

# python generate_dataset.py [number of images]
def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else IMAGE_COUNT
    for part in ("train", "val"):
        (OUTPUT / "images" / part).mkdir(parents=True, exist_ok=True)
        (OUTPUT / "labels" / part).mkdir(parents=True, exist_ok=True)
    generator = SkyGenerator(read_catalog())
    for number in range(count):
        image, labels = generator.generate()
        part = "val" if random.random() < VALIDATION_SHARE else "train"
        name = f"sky_{number:06d}"
        cv2.imwrite(str(OUTPUT / "images" / part / (name + ".png")), image)
        (OUTPUT / "labels" / part / (name + ".txt")).write_text("\n".join(labels), encoding="utf-8")
    write_config(OUTPUT)
    print(str(count)+" maps written in "+str(OUTPUT))

if __name__ == "__main__":
    main()

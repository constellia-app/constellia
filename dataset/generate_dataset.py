from pathlib import Path
import csv
import math
import random
import sys
import cv2
import numpy as np

FOLDER = Path(__file__).parent
sys.path.append(str(FOLDER.parent / "catalog"))
from star_catalog import CatalogStar
from star_map import SIZE, StarMap

CATALOG = FOLDER.parent / "catalog" / "star_catalog.csv"
OUTPUT = FOLDER / "output" / "sky"
MAP_COUNT = 10
SOUTH_OF_FRANCE_LATITUDE = 41.4
MIN_DECLINATION = SOUTH_OF_FRANCE_LATITUDE - 90 + 10 # further south, a star never rises 10 degrees
MIN_FIELD_DEG = 40 # the field of view of a phone
MAX_FIELD_DEG = 80
MIN_STARS = 10 # a photo shows between 10 and 80 stars
MAX_STARS = 80

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

# fake photos of the sky made from the catalogue, drawn like the map of a real photo
class SkyGenerator:
    # keeps the stars seen from France
    def __init__(self, stars: list[CatalogStar]):
        self.stars: list[CatalogStar] = stars
        self.directions: np.ndarray = np.array([direction(star.ra, star.dec) for star in stars])
        self.visible: list[CatalogStar] = [star for star in stars if star.dec >= MIN_DECLINATION]

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

    # points the camera at a random star, with a random tilt and field of view
    def random_view(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        center = random.choice(self.visible)
        right, up, axis = self.aim(center, random.uniform(0, 2 * math.pi))
        field = math.radians(random.uniform(MIN_FIELD_DEG, MAX_FIELD_DEG))
        return self.project(right, up, axis, SIZE / 2 / math.tan(field / 2))

    # one map, with only the brightest stars as on a photo
    def generate(self) -> np.ndarray:
        x, y, inside = self.random_view()
        drawn = list(np.nonzero(inside)[0][:random.randint(MIN_STARS, MAX_STARS)])
        return StarMap.draw(list(x[drawn]), list(y[drawn]))

# python generate_dataset.py [number of maps]
def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else MAP_COUNT
    OUTPUT.mkdir(parents=True, exist_ok=True)
    generator = SkyGenerator(read_catalog())
    for number in range(count):
        cv2.imwrite(str(OUTPUT / f"sky_{number:03d}.png"), generator.generate())
    print(str(count)+" maps written in "+str(OUTPUT))

if __name__ == "__main__":
    main()

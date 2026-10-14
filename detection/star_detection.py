from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np

@dataclass(frozen=True)
class Star:
    x: int
    y: int

@dataclass
class Detection:
    stars: list[Star]
    width: int
    height: int

class StarDetector:
    # loads the photo
    def __init__(self, path: Path):
        self.image: np.ndarray = self.read_image(path).astype(np.float32)
        self.height: int = self.image.shape[0]
        self.width: int = self.image.shape[1]

    # reads the photo in black and white and shrinks it to 1024 px at most
    def read_image(self, path: Path) -> np.ndarray:
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(path)
        reduction: float = 1024 / max(image.shape)
        if reduction < 1:
            image = cv2.resize(image, None, fx=reduction, fy=reduction, interpolation=cv2.INTER_AREA)
        return image

    # finds every pixel brighter than all its neighbours  (star candidates)
    def find_peaks(self) -> tuple[np.ndarray, np.ndarray]:
        local_max = cv2.dilate(self.image, np.ones((9, 9), np.uint8))
        local_min = cv2.erode(self.image, np.ones((9, 9), np.uint8))
        is_peak = (self.image == local_max) & (self.image > local_min + 1) # brightest pixel of its 9x9 square, and not in a flat area
        ys, xs = np.nonzero(is_peak) # rows and columns of the True pixels
        return xs, ys

    # gives each candidate a contrast
    def get_contrasts(self, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
        surrounding = cv2.blur(self.image, (36, 36))
        excess = self.image[ys, xs] - surrounding[ys, xs]
        ordinary: float = np.median(excess)
        spread: float = np.median(np.abs(excess - ordinary))
        return (excess - ordinary) / spread

    # checks that the candidate is a small point surrounded by black
    def is_isolated(self, darkest: float, x: int, y: int) -> bool:
        half_height: float = darkest + (self.image[y, x] - darkest) / 2
        top: int = max(0, y - 6)
        left: int = max(0, x - 6)
        square = self.image[top:y + 7, left:x + 7]
        border = np.concatenate([square[0], square[-1], square[:, 0], square[:, -1]])
        return border.max() <= half_height

    # checks that the candidate is not right next to a star already kept
    def is_already_found(self, stars: list[Star], x: int, y: int) -> bool:
        # two touching pixels with the same brightness are the same star
        for star in stars:
            if abs(star.x - x) <= 4 and abs(star.y - y) <= 4:
                return True
        return False

    # chains all the steps and returns the stars found
    def detect(self) -> Detection:
        xs, ys = self.find_peaks()
        contrasts = self.get_contrasts(xs, ys)
        darkest_around = cv2.erode(self.image, np.ones((36, 36), np.uint8))

        stars: list[Star] = []
        # best contrast first
        for i in np.argsort(-contrasts):
            # contrasts are sorted, so all the next ones are too low
            if contrasts[i] < 15 or len(stars) == 80:
                break
            x = int(xs[i])
            y = int(ys[i])
            if self.is_already_found(stars, x, y):
                continue
            if self.is_isolated(darkest_around[y, x], x, y):
                stars.append(Star(x, y))

        return Detection(stars, self.width, self.height)

def main():
    detection = StarDetector(Path("detection/input/5EDC6EFC-96D4-4133-B3E6-95080B4A5F90.jpg")).detect()
    print("Image: "+str(detection.width)+" x "+str(detection.height))
    print("Stars found: "+str(len(detection.stars)))
    for star in detection.stars:
        print(star.x, star.y)

if __name__ == "__main__":
    main()

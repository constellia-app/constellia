from pathlib import Path
import sys
import cv2
import numpy as np

FOLDER = Path(__file__).parent
sys.path.append(str(FOLDER.parent / "detection"))
from star_detection import Detection, StarDetector

PHOTOS = FOLDER.parent / "detection" / "input"
OUTPUT = FOLDER / "output" / "maps"
SIZE = 640 # the size of the images YOLO works on
POINT_RADIUS = 3

# a photo and a piece of the catalogue are drawn the same way, so YOLO always sees the same kind of image
class StarMap:
    # draws one white point per star on a black square
    @staticmethod
    def draw(xs: list[float], ys: list[float]) -> np.ndarray:
        image = np.zeros((SIZE, SIZE), np.uint8)
        for x, y in zip(xs, ys):
            cv2.circle(image, (round(x), round(y)), POINT_RADIUS, 255, -1, cv2.LINE_AA)
        return image

    # fits the whole photo in the square without stretching it
    @staticmethod
    def from_detection(detection: Detection) -> np.ndarray:
        scale: float = SIZE / max(detection.width, detection.height)
        offset_x: float = (SIZE - detection.width * scale) / 2
        offset_y: float = (SIZE - detection.height * scale) / 2
        xs = [star.x * scale + offset_x for star in detection.stars]
        ys = [star.y * scale + offset_y for star in detection.stars]
        return StarMap.draw(xs, ys)

# draws the map of every photo of detection/input
def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for photo in sorted(PHOTOS.iterdir()):
        detection = StarDetector(photo).detect()
        cv2.imwrite(str(OUTPUT / (photo.stem + ".png")), StarMap.from_detection(detection))
        print(photo.name+": "+str(len(detection.stars))+" stars")

if __name__ == "__main__":
    main()

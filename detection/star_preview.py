from pathlib import Path
import cv2
import numpy as np
from star_detection import Detection, StarDetector

FOLDER = Path(__file__).parent
PHOTO = FOLDER / "input" / "5EDC6EFC-96D4-4133-B3E6-95080B4A5F90.jpg"
OUTPUT = FOLDER / "output" / "star_preview.png"

# reads the photo in color, at the same size as the one used by the detector
def read_photo(path: Path, detection: Detection) -> np.ndarray:
    photo = cv2.imread(str(path))
    if photo is None:
        raise FileNotFoundError(path)
    return cv2.resize(photo, (detection.width, detection.height), interpolation=cv2.INTER_AREA)

# draws each star found on a black image
def draw_stars(detection: Detection) -> np.ndarray:
    black = np.zeros((detection.height, detection.width, 3), np.uint8)
    for star in detection.stars:
        cv2.circle(black, (star.x, star.y), 4, (255, 255, 255), -1)
    return black

# writes on top
def draw_title(width: int, path: Path) -> np.ndarray:
    title = np.zeros((42, width, 3), np.uint8)
    text = "detection/star_detection.py -> StarDetector("+path.name+").detect()"
    cv2.putText(title, text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    return title

# puts the photo and the stars side by side, with the title above
def main():
    detection = StarDetector(PHOTO).detect()
    separator = np.full((detection.height, 4, 3), 128, np.uint8)
    body = np.hstack([read_photo(PHOTO, detection), separator, draw_stars(detection)])
    image = np.vstack([draw_title(body.shape[1], PHOTO), body])
    cv2.imwrite(str(OUTPUT), image)
    print("Image saved: "+str(OUTPUT))

if __name__ == "__main__":
    main()

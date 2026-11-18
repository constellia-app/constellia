from pathlib import Path
import sys
import cv2
from ultralytics import YOLO

FOLDER = Path(__file__).parent
sys.path.append(str(FOLDER.parent / "detection"))
sys.path.append(str(FOLDER.parent / "dataset"))
from star_detection import StarDetector
from star_map import StarMap

MODEL = FOLDER / "runs" / "constellations" / "weights" / "best.pt"
PHOTOS = FOLDER.parent / "detection" / "input"
OUTPUT = FOLDER / "output"
MIN_CONFIDENCE = 0.25 # below this, YOLO announces nothing
COLOR = (0, 180, 255)

# puts the map of each real photo through YOLO and draws the boxes it finds
def main():
    model = YOLO(str(MODEL))
    OUTPUT.mkdir(exist_ok=True)
    for photo in sorted(PHOTOS.iterdir()):
        image = cv2.cvtColor(StarMap.from_detection(StarDetector(photo).detect()), cv2.COLOR_GRAY2BGR)
        result = model.predict(image, conf=MIN_CONFIDENCE, verbose=False)[0]
        found: list[str] = []
        for box in result.boxes:
            label = model.names[int(box.cls)]+" "+str(round(float(box.conf) * 100))+" %"
            x1, y1, x2, y2 = (int(value) for value in box.xyxy[0])
            cv2.rectangle(image, (x1, y1), (x2, y2), COLOR, 2)
            cv2.putText(image, label, (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR, 1)
            found.append(label)
        cv2.imwrite(str(OUTPUT / (photo.stem + ".png")), image)
        print(photo.name+": "+(", ".join(found) or "nothing"))

if __name__ == "__main__":
    main()

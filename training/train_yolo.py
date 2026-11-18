from pathlib import Path
from ultralytics import YOLO

FOLDER = Path(__file__).parent
DATASET = FOLDER.parent / "dataset" / "output" / "constellations.yaml"
PRETRAINED = "yolo11n.pt" # the smallest YOLO, already trained on everyday photos
SIZE = 640

# our training settings, run on Google Colab with a GPU
SETTINGS = {
    "imgsz": SIZE,
    "epochs": 50,
    "batch": 32,
    "fliplr": 0.0, # never mirror a map, a mirrored constellation does not exist in the sky
    "mosaic": 0.0, # never glue four maps together, it would make impossible skies
    "scale": 0.0, # the generator already changes the field of view
}

# trains YOLO on our maps, then exports it for the phone (the file is saved as models/best.tflite)
def main():
    model = YOLO(PRETRAINED)
    model.train(data=str(DATASET), project=str(FOLDER / "runs"), name="constellations", **SETTINGS)
    metrics = model.val()
    print("mAP50: "+str(round(metrics.box.map50, 3)))
    model.export(format="tflite", imgsz=SIZE)

if __name__ == "__main__":
    main()

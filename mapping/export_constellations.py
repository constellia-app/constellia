from pathlib import Path
import json
from constellations import FIGURES

FOLDER = Path(__file__).parent
OUTPUT = FOLDER.parent / "app" / "assets" / "constellations.json"

# writes the drawing of each constellation in a JSON file for the app, in the order of the YOLO classes
def main():
    constellations = []
    for number, (name, lines) in enumerate(FIGURES.items()):
        constellations.append({"name": name, "yolo_class": number, "lines": [list(line) for line in lines]})
    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump({"constellations": constellations}, file, indent=2)
        file.write("\n")
    print(str(len(constellations))+" constellations saved in "+str(OUTPUT))

if __name__ == "__main__":
    main()

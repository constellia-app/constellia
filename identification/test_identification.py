from pathlib import Path
import random
import sys
import numpy as np

FOLDER = Path(__file__).parent
sys.path.append(str(FOLDER.parent / "dataset"))
from generate_dataset import CONSTELLATIONS, MAX_FALSE_POINTS, MAX_STARS, MIN_STARS, SIZE, SkyGenerator, read_catalog
from identify import Box, Identifier
from star_catalog import CatalogStar

SKIES = 200
SEED = 1

# makes a sky where we know every star, and gives its points, the true star of each point and the boxes
def one_sky(generator: SkyGenerator) -> tuple[np.ndarray, list[CatalogStar | None], list[tuple[str, Box]]]:
    x, y, inside = generator.random_view()
    drawn = list(np.nonzero(inside)[0][:random.randint(MIN_STARS, MAX_STARS)])
    points = [(round(x[i]), round(y[i])) for i in drawn]
    truth: list[CatalogStar | None] = [generator.stars[i] for i in drawn]
    for _ in range(random.randint(0, MAX_FALSE_POINTS)):
        points.append((random.randrange(SIZE), random.randrange(SIZE)))
        truth.append(None) # a false point has no star
    boxes: list[tuple[str, Box]] = []
    for label in generator.annotate({generator.stars[i].hip: (x[i], y[i]) for i in drawn}):
        number, cx, cy, w, h = label.split()
        cx, cy, w, h = (float(value) * SIZE for value in (cx, cy, w, h))
        boxes.append((CONSTELLATIONS[int(number)], (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)))
    return np.array(points, dtype=float), truth, boxes

# gives the identification the points and the box of one constellation, like YOLO would, then counts the right and wrong names
def main():
    random.seed(SEED)
    stars = read_catalog()
    generator = SkyGenerator(stars)
    identifier = Identifier(stars)
    tries = answered = right = wrong = false_named = stars_in_skies = stars_in_answered = 0
    while tries < SKIES:
        points, truth, boxes = one_sky(generator)
        if not boxes:
            continue
        constellation, box = random.choice(boxes)
        tries += 1
        result = identifier.identify(points, SIZE, SIZE, box, constellation)
        real_stars = sum(1 for star in truth if star is not None)
        stars_in_skies += real_stars
        if result is None:
            continue
        answered += 1
        stars_in_answered += real_stars
        for found, true in zip(result.names, truth):
            if found is None:
                continue
            if true is None:
                false_named += 1
            elif found.hip == true.hip:
                right += 1
            else:
                wrong += 1
    print(str(tries)+" skies, drawing fitted in "+str(answered))
    print("stars named right "+str(right)+" of "+str(stars_in_skies)+" ("+str(round(100 * right / stars_in_skies))+" %)")
    print("  in the skies where it answers "+str(round(100 * right / stars_in_answered))+" %")
    print("stars named wrong "+str(wrong))
    print("false points named "+str(false_named))

if __name__ == "__main__":
    main()

from dataclasses import dataclass
from pathlib import Path
import csv
import urllib.request

HIPPARCOS_URL = "https://cdsarc.cds.unistra.fr/ftp/cats/I/239/hip_main.dat"
FOLDER = Path(__file__).parent
OUTPUT = FOLDER / "star_catalog.csv"
MAX_MAGNITUDE = 6.5 # the faintest stars the naked eye can see

@dataclass(frozen=True)
class CatalogStar:
    hip: int # number of the star in the Hipparcos catalogue
    ra: float # position in the sky, in degrees (right ascension)
    dec: float # position in the sky, in degrees (declination)
    magnitude: float # brightness (the smaller, the brighter)

class CatalogBuilder:
    # keeps the address of the Hipparcos catalogue (European Space Agency, 1997)
    def __init__(self, url: str):
        self.url: str = url

    # reads one line of the catalogue, where the columns are separated by "|"
    def read_line(self, line: str) -> CatalogStar | None:
        fields: list[str] = line.split("|")
        magnitude: str = fields[5].strip()
        ra: str = fields[8].strip()
        dec: str = fields[9].strip()
        # a few stars have no position, they are left out
        if magnitude == "" or ra == "" or dec == "":
            return None
        return CatalogStar(int(fields[1]), float(ra), float(dec), float(magnitude))

    # downloads the catalogue and keeps the stars visible to the naked eye, the brightest first
    def download(self) -> list[CatalogStar]:
        stars: list[CatalogStar] = []
        with urllib.request.urlopen(self.url, timeout=60) as response:
            for raw_line in response:
                star = self.read_line(raw_line.decode("ascii"))
                if star is not None and star.magnitude <= MAX_MAGNITUDE:
                    stars.append(star)
        return sorted(stars, key=lambda star: star.magnitude)

    # writes one line per star in a CSV file
    def save(self, stars: list[CatalogStar], path: Path):
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["hip", "ra_deg", "dec_deg", "magnitude"])
            for star in stars:
                writer.writerow([star.hip, star.ra, star.dec, star.magnitude])

# downloads the catalogue and saves the visible stars in catalog/star_catalog.csv
def main():
    builder = CatalogBuilder(HIPPARCOS_URL)
    stars = builder.download()
    builder.save(stars, OUTPUT)
    print("Stars saved: "+str(len(stars))+" in "+str(OUTPUT))

if __name__ == "__main__":
    main()

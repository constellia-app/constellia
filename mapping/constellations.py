type Line = tuple[int, int]

# lines drawing each constellation, between two Hipparcos numbers
FIGURES: dict[str, list[Line]] = {
    "Ursa Major": [
        (54061, 53910),   # Dubhe - Merak
        (53910, 58001),   # Merak - Phecda
        (58001, 59774),   # Phecda - Megrez
        (59774, 54061),   # Megrez - Dubhe
        (59774, 62956),   # Megrez - Alioth
        (62956, 65378),   # Alioth - Mizar
        (65378, 67301),   # Mizar - Alkaid
    ],
    "Ursa Minor": [
        (11767, 85822),   # Polaris - DelUMi
        (85822, 82080),   # DelUMi - EpsUMi
        (82080, 77055),   # EpsUMi - ZetUMi
        (77055, 72607),   # ZetUMi - Kochab
        (72607, 75097),   # Kochab - Pherkad
        (75097, 79822),   # Pherkad - EtaUMi
        (79822, 77055),   # EtaUMi - ZetUMi
    ],
    "Cassiopeia": [
        (746, 3179),      # Caph - Schedar
        (3179, 4427),     # Schedar - GammaCas
        (4427, 6686),     # GammaCas - Ruchbah
        (6686, 8886),     # Ruchbah - Segin
    ],
    "Orion": [
        (27989, 25336),   # Betelgeuse - Bellatrix
        (27989, 26727),   # Betelgeuse - Alnitak
        (25336, 25930),   # Bellatrix - Mintaka
        (25930, 26311),   # Mintaka - Alnilam
        (26311, 26727),   # Alnilam - Alnitak
        (26727, 27366),   # Alnitak - Saiph
        (25930, 24436),   # Mintaka - Rigel
        (27989, 26207),   # Betelgeuse - Meissa
        (25336, 26207),   # Bellatrix - Meissa
    ],
    "Cygnus": [
        (102098, 100453), # Deneb - Sadr
        (100453, 95947),  # Sadr - Albireo
        (102488, 100453), # GienahCyg - Sadr
        (100453, 97165),  # Sadr - DeltaCyg
    ],
    "Lyra": [
        (91262, 92420),   # Vega - Sheliak
        (92420, 93194),   # Sheliak - Sulafat
        (93194, 91262),   # Sulafat - Vega
    ],
    "Aquila": [
        (97278, 97649),   # Tarazed - Altair
        (97649, 98036),   # Altair - Alshain
    ],
    "Pegasus": [
        (113963, 113881), # Markab - Scheat
        (113881, 677),    # Scheat - Alpheratz
        (677, 1067),      # Alpheratz - Algenib
        (1067, 113963),   # Algenib - Markab
        (113963, 107315), # Markab - Enif
    ],
    "Andromeda": [
        (677, 3092),      # Alpheratz - DeltaAnd
        (3092, 5447),     # DeltaAnd - Mirach
        (5447, 9640),     # Mirach - Almach
    ],
    "Perseus": [
        (15863, 14576),   # Mirfak - Algol
        (15863, 18532),   # Mirfak - EpsPer
        (14576, 18246),   # Algol - ZetaPer
    ],
    "Taurus": [
        (21421, 25428),   # Aldebaran - Elnath
        (21421, 20205),   # Aldebaran - GammaTau
    ],
    "Leo": [
        (49669, 50583),   # Regulus - Algieba
        (50583, 54872),   # Algieba - Zosma
        (54872, 57632),   # Zosma - Denebola
    ],
}

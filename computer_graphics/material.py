import pyrr

class Material:
    def __init__(self, ambient: pyrr.Vector3, diffuse: pyrr.Vector3,
                 specular: pyrr.Vector3, shininess: float, transparency: float):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.transparency = transparency

BLACK_RUBBER = Material(
    pyrr.Vector3((0.02, 0.02, 0.02), dtype='f4'),
    pyrr.Vector3((0.01, 0.01, 0.01), dtype='f4'),
    pyrr.Vector3((0.4, 0.4, 0.4), dtype='f4'),
    0.078125,
    1.0,
)

RED_PLASTIC = Material(
    pyrr.Vector3((0.0, 0.0, 0.0), dtype='f4'),
    pyrr.Vector3((0.5, 0.0, 0.0), dtype='f4'),
    pyrr.Vector3((0.7, 0.6, 0.6), dtype='f4'),
    0.25,
    1.0,
)

GOLD = Material(
    pyrr.Vector3((0.24725, 0.1995, 0.0745), dtype='f4'),
    pyrr.Vector3((0.75164, 0.60648, 0.22648), dtype='f4'),
    pyrr.Vector3((0.628281, 0.555802, 0.366065), dtype='f4'),
    0.4,
    1.0,
)

SHINY_GOLD = Material(
    pyrr.Vector3((0.24725, 0.1995, 0.0745), dtype='f4'),
    pyrr.Vector3((0.75164, 0.60648, 0.22648), dtype='f4'),
    pyrr.Vector3((0.628281, 0.555802, 0.366065), dtype='f4'),
    1.0,
    1.0,
)

OBSIDIAN = Material(
    pyrr.Vector3((0.05375, 0.05, 0.06625), dtype='f4'),
    pyrr.Vector3((0.18275, 0.17, 0.22525), dtype='f4'),
    pyrr.Vector3((0.332741, 0.328634, 0.346435), dtype='f4'),
    0.3,
    1.0,
)

OBSIDIAN_GLASS = Material(
    pyrr.Vector3((0.05375, 0.05, 0.06625), dtype='f4'),
    pyrr.Vector3((0.18275, 0.17, 0.22525), dtype='f4'),
    pyrr.Vector3((0.332741, 0.328634, 0.346435), dtype='f4'),
    0.7,
    0.3,
)

PEARL = Material(
    pyrr.Vector3((0.25, 0.20725, 0.20725), dtype='f4'),
    pyrr.Vector3((1, 0.829, 0.829), dtype='f4'),
    pyrr.Vector3((0.296648, 0.296648, 0.296648), dtype='f4'),
    0.088,
    1.0,
)

PEARL_GLASS = Material(
    pyrr.Vector3((0.25, 0.20725, 0.20725), dtype='f4'),
    pyrr.Vector3((1, 0.829, 0.829), dtype='f4'),
    pyrr.Vector3((0.296648, 0.296648, 0.296648), dtype='f4'),
    0.088,
    0.3,
)
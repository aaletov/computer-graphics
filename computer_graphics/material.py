import pyrr

class Material:
    def __init__(self, ambient: pyrr.Vector3, diffuse: pyrr.Vector3,
                 specular: pyrr.Vector3, shininess: float):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess

BLACK_RUBBER = Material(
    pyrr.Vector3((0.02, 0.02, 0.02), dtype='f4'),
    pyrr.Vector3((0.01, 0.01, 0.01), dtype='f4'),
    pyrr.Vector3((0.4, 0.4, 0.4), dtype='f4'),
    0.078125
)

RED_PLASTIC = Material(
    pyrr.Vector3((0.0, 0.0, 0.0), dtype='f4'),
    pyrr.Vector3((0.5, 0.0, 0.0), dtype='f4'),
    pyrr.Vector3((0.7, 0.6, 0.6), dtype='f4'),
    0.25,
)

GOLD = Material(
    pyrr.Vector3((0.24725, 0.1995, 0.0745), dtype='f4'),
    pyrr.Vector3((0.75164, 0.60648, 0.22648), dtype='f4'),
    pyrr.Vector3((0.628281, 0.555802, 0.366065), dtype='f4'),
    0.4,
)
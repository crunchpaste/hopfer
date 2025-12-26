import numpy as np


def hex_to_numpy(hex):
    hex = hex.lstrip("#")

    rgb = [int(hex[i : i + 2], 16) for i in (0, 2, 4)]

    return np.array(rgb, dtype=np.uint8)

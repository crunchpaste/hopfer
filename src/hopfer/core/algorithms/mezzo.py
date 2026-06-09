import numpy as np

from hopfer.core.algorithms.cython_ops import compare


def mezzo(img, settings, mode="uniform"):
    seed = settings["seed"]
    h, w = img.shape
    rng = np.random.default_rng(seed)

    if mode == "uniform":
        # the GUI still works in floats, while i've switched to ints internally
        r_min_f, r_max_f = settings["range"]
        r_min, r_max = int(r_min_f * 255), int(r_max_f * 255)
        noise = rng.integers(r_min, r_max + 1, (h, w), dtype=np.uint8)

    elif mode == "gauss":
        loc = settings["location"]
        std = settings["std"]
        # TODO: look for a more elegant solution. currently this would do.
        noise = (np.clip(rng.normal(loc, std, (h, w)), 0, 1) * 255).astype(
            np.uint8
        )

    elif mode == "beta":
        alpha = settings["alpha"] / 10
        beta = settings["beta"] / 10
        noise = rng.beta(alpha, beta, (h, w))

    img = compare(img, noise)
    return img

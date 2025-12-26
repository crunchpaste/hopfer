from .static import niblack, phansalkar, sauvola, thresh


def threshold(img, settings):
    value = settings["threshold"]
    return thresh(img, value)


def niblack_threshold(img, settings):
    block_size = int(settings["block_size"])
    k = settings["k_factor"]
    return niblack(img, block_size, k)


def sauvola_threshold(img, settings):
    block_size = int(settings["block_size"])
    dynamic_range = settings["dynamic_range"]
    k = settings["k_factor"]
    return sauvola(img, block_size, dynamic_range, k)


def phansalkar_threshold(img, settings):
    block_size = int(settings["block_size"])
    dynamic_range = settings["dynamic_range"]
    k = settings["k_factor"]
    p = settings["p_factor"]
    q = settings["q_factor"]
    return phansalkar(img, block_size, dynamic_range, k, p, q)

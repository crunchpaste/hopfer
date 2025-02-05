from .static import thresh, sauvola, phansalkar, niblack

def threshold(img, settings):
    value = settings["threshold_value"] / 100
    return thresh(img, value)

def niblack_threshold(img, settings):
    block_size = int(settings["block_size"])
    k = settings["k_factor"] / 100
    return niblack(img, block_size, k)

def sauvola_threshold(img, settings):
    block_size = int(settings["block_size"])
    dynamic_range = settings["dynamic_range"] / 100
    k = settings["k_factor"] / 100
    return sauvola(img, block_size, dynamic_range, k)

def phansalkar_threshold(img, settings):
    block_size = int(settings["block_size"])
    dynamic_range = settings["dynamic_range"] / 100
    k = settings["k_factor"] / 100
    p = settings["p_factor"] / 100
    q = settings["q_factor"] / 10
    return phansalkar(img, block_size, dynamic_range, k, p, q)

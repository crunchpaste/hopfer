from .static import thresh, sauvola

def threshold(img, settings):
    value = settings["threshold_value"] / 100
    return thresh(img, value)

def sauvola_threshold(img, settings):
    block_size = int(settings["block_size"])
    dynamic_range = settings["dynamic_range"] / 100
    k = settings["k_factor"] / 100
    return sauvola(img, block_size, dynamic_range, k)

from .static import thresh

def threshold(img, settings):
    value = settings["threshold_value"] / 100
    return thresh(img, value)

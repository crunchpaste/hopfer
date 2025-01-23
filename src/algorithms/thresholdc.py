from .static import threshold

def threshold(img, settings):
    value = settings["threshold_value"] / 100
    return thresh(img, value)

from .static import ed, eds
import numpy as np

def error_diffusion(img, kernel, settings):
    str = settings['diffusion_factor'] / 100
    serpentine = settings['serpentine']
    print(str, serpentine)
    if serpentine:
        output_img = static.eds(img, kernel, str)
    else:
        output_img = static.ed(img, kernel, str)

    return output_img

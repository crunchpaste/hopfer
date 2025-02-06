from .static import ed, eds


def error_diffusion(img, kernel, settings):
    str = settings["diffusion_factor"] / 100
    serpentine = settings["serpentine"]
    print(str, serpentine)
    if serpentine:
        output_img = eds(img, kernel, str)
    else:
        output_img = ed(img, kernel, str)

    return output_img

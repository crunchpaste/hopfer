import numpy as np


def get_kernel(algorithm):
    if algorithm == "Floyd-Steinberg":
        # fmt: off
        kernel = (
            np.array([[0, 0, 0],
                      [0, 0, 7],
                      [3, 5, 1]], dtype=np.float64) / 16.0)
        # fmt: on
    elif algorithm == "False Floyd-Steinberg":
        # fmt: off
        kernel = (
            np.array([[0, 0, 0],
                      [0, 0, 3],
                      [0, 3, 2]], dtype=np.float64) / 8.0
        )
        # fmt: on
    elif algorithm == "Jarvis":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 7, 5],
                    [3, 5, 7, 5, 3],
                    [1, 3, 5, 3, 1],
                ],
                dtype=np.float64,
            )
            / 48.0
        )

    elif algorithm == "Stucki":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 8, 4],
                    [2, 4, 8, 4, 2],
                    [1, 2, 4, 2, 1],
                ],
                dtype=np.float64,
            )
            / 42.0
        )

    elif algorithm == "Stucki small":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 8, 2],
                    [0, 2, 8, 2, 0],
                    [0, 0, 2, 0, 0],
                ],
                dtype=np.float64,
            )
            / 24.0
        )

    elif algorithm == "Stucki large":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 8, 4, 2],
                    [2, 4, 8, 8, 8, 4, 2],
                    [2, 4, 4, 4, 4, 4, 2],
                    [2, 2, 2, 2, 2, 2, 2],
                ],
                dtype=np.float64,
            )
            / 88.0
        )

    elif algorithm == "Atkinson":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 1],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                ],
                dtype=np.float64,
            )
            / 8
        )

    elif algorithm == "Burkes":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 8, 4],
                    [2, 4, 8, 4, 2],
                    [0, 0, 0, 0, 0],
                ],
                dtype=np.float64,
            )
            / 32.0
        )

    elif algorithm == "Sierra":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 5, 3],
                    [2, 4, 5, 4, 2],
                    [0, 2, 3, 2, 0],
                ],
                dtype=np.float64,
            )
            / 32.0
        )

    elif algorithm == "Sierra2":
        kernel = (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 4, 3],
                    [1, 2, 3, 2, 1],
                    [0, 0, 0, 0, 0],
                ],
                dtype=np.float64,
            )
            / 16.0
        )

    elif algorithm == "Sierra2 4A":
        # fmt: off
        kernel = (
            np.array([[0, 0, 0],
                      [0, 0, 2],
                      [1, 1, 0]], dtype=np.float64) / 4.0)
        # fmt: on
    elif algorithm == "Nakano":
        kernel = np.array(
            [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 6, 4],
                [0, 1, 6, 0, 0, 5, 3],
                [0, 0, 4, 7, 3, 5, 3],
                [0, 0, 3, 5, 3, 4, 2],
            ],
            dtype=np.float64,
        )
        # Normalize the kernel as im too lazy to count the values
        kernel /= float(np.sum(kernel))
    else:
        # in case something goes wrong return the Sierra2 4A
        # fmt: off
        kernel = (
            np.array([[0, 0, 0],
                      [0, 0, 2],
                      [1, 1, 0]], dtype=np.float64) / 4.0)
        # fmt: on

    return kernel

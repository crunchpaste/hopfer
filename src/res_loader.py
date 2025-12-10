import os
import sys

from PySide6.QtCore import QByteArray


def get_path(relative_path):
    """
    Returns the correct path to a resource, taking into account whether the program is running from a nuitka binary or directly from source code. Mostly used to load the icons for the UI.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    if getattr(sys, "frozen", False):
        # Running from a bundled executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Running from source code
        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )  # Directory of this script

        # If inside the `src` folder, move up one level to the project root
        if "src" in base_path:
            base_path = os.path.dirname(base_path)

    # Some hacky way of actually getting a proper path in windows.
    if os.name == "nt":
        base_path = base_path.replace("\\", "/") + "/"

    # Return the final path by joining the base path with the relative resource path
    return os.path.join(base_path, relative_path)


def load_svg(file_path, colors=None):
    if not os.path.exists(file_path):
        return QByteArray()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            svg_string = f.read()
    except Exception:
        return QByteArray()

    if colors is not None:
        svg_string = svg_string.replace("@primary", colors.primary)
    else:
        svg_string = svg_string.replace("@primary", "#f0f6f0")

    svg_byte_string = svg_string.encode("utf-8")

    svg_qbytearray = QByteArray(svg_byte_string)

    return svg_qbytearray

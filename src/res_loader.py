import sys
import os
import subprocess

def get_path(relative_path):
    """
    Returns the correct path to a resource, taking into account whether the program is running from a nuitka binary or directly from source code. Mostly used to load the icons for the UI.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    if getattr(sys, 'frozen', False):
        # Running from a bundled executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Running from source code
        base_path = os.path.dirname(os.path.abspath(__file__))  # Directory of this script

        # If inside the `src` folder, move up one level to the project root
        if 'src' in base_path:
            base_path = os.path.dirname(base_path)

    # Return the final path by joining the base path with the relative resource path
    return os.path.join(base_path, relative_path)

def create_desktop_file(bin_path, icon_path):
    """
    Creates a temporary .desktop file so that an icon is displayed in the docks, taskbars and panels on Linux systems. This is a very hacky aproach, but it will have to do until I have some time to package it properly for Linux.

    Args:
        bin_path (str): The path to the binary executable.
        icon_path (str): The path to the application icon.

    Returns:
        str: The path to the created .desktop file.
    """
    app_name = "hopfer"
    desktop_dir = os.path.expanduser("~/.local/share/applications/")
    os.makedirs(desktop_dir, exist_ok=True)

    desktop_file_path = os.path.join(desktop_dir, f"{app_name}.desktop")

    desktop_content = f"""[Desktop Entry]
Name={app_name}
Exec={bin_path}/hopfer.bin
Icon={icon_path}
Type=Application
Terminal=false
Category=Graphics
StartupNotify=true
"""

    # Write the content to the desktop file
    with open(desktop_file_path, "w") as desktop_file:
        desktop_file.write(desktop_content)

    # Set the appropriate permissions for the desktop file
    os.chmod(desktop_file_path, 0o644)

    # Update the desktop database (ensure taskbar visibility)
    subprocess.run(["update-desktop-database", desktop_dir], check=False)

    return desktop_file_path

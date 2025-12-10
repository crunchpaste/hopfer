from res_loader import get_path


def load_qss(app, qss_file_path, colors=None):
    """
    Load and apply the QSS file with custom variables and paths to the application.

    Args:
        app (QApplication): The application instance.
        qss_file_path (str): Path to the QSS file.
    """

    _ext = "svg"

    try:
        with open(qss_file_path, "r") as file:
            qss_content = file.read()

        if colors is not None:
            if colors.theme == "dark":
                theme = ""
            else:
                theme = "_" + colors.theme
            primary_color = colors.primary
            secondary_color = colors.secondary
            accent_color = colors.accent
            disabled_color = colors.disabled

            titlebar_bg = colors.titlebar_bg
            titlebar_sh = colors.titlebar_sh

        else:
            # Default dark theme
            theme = ""
            primary_color = "#f0f6f0"
            secondary_color = "#222323"
            accent_color = "#fa8072"
            disabled_color = "#6a6d6b"

            titlebar_bg = "#202121"
            titlebar_sh = "#192020"

        # # Define colors
        # # primary_color = "#f0f6f0"  # Primary color in hex
        # # secondary_color = "#222323"  # Secondary color in hex
        # secondary_color = "#f0f6f0"  # Primary color in hex
        # primary_color = "#222323"  # Secondary color in hex
        # # accent_color = "#fa8072"  # Accent color in hex #e9967a
        # accent_color = "#d4004c"
        # disabled_color = "#6a6d6b"  # Color for disabled elements
        #
        # # titlebar_bg = "#202121" # eaf0ea
        # titlebar_bg = "#eaf0ea" # eaf0ea
        # # titlebar_sh = "#192020" # e5ebe5
        # titlebar_sh = "#e5ebe5" # e5ebe5

        # Get the resource path
        menu_down_path = get_path("res")

        # Replace placeholders in the QSS file
        qss_content = qss_content.replace("@res", menu_down_path)
        qss_content = qss_content.replace("@primary", primary_color)
        qss_content = qss_content.replace("@secondary", secondary_color)
        qss_content = qss_content.replace("@accent", accent_color)
        qss_content = qss_content.replace("@disabled", disabled_color)
        qss_content = qss_content.replace("@titlebarBg", titlebar_bg)
        qss_content = qss_content.replace("@titlebarSh", titlebar_sh)
        qss_content = qss_content.replace("@theme", theme)
        qss_content = qss_content.replace("@ext", _ext)

        # Apply the QSS content to the application
        app.setStyleSheet(qss_content)

    except FileNotFoundError:
        print(f"Error: The QSS file at {qss_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while loading the QSS: {e}")

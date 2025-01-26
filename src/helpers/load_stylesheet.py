from res_loader import get_path
import os

def load_qss(app, qss_file_path):
    """
    Load and apply the QSS file with custom variables and paths to the application.

    Args:
        app (QApplication): The application instance.
        qss_file_path (str): Path to the QSS file.
    """

    _ext = "svg"

    try:
        with open(qss_file_path, 'r') as file:
            qss_content = file.read()

        # Define colors
        primary_color = '#f0f6f0'  # Primary color in hex
        secondary_color = '#222323'  # Secondary color in hex
        accent_color = '#fa8072'  # Accent color in hex
        disabled_color = '#6a6d6b' # Color for disabled elements

        # Get the resource path
        menu_down_path = get_path('res')

        # Replace placeholders in the QSS file
        qss_content = qss_content.replace('@res', menu_down_path)
        qss_content = qss_content.replace('@primary', primary_color)
        qss_content = qss_content.replace('@secondary', secondary_color)
        qss_content = qss_content.replace('@accent', accent_color)
        qss_content = qss_content.replace('@disabled', disabled_color)
        qss_content = qss_content.replace('@ext', _ext)

        # Apply the QSS content to the application
        app.setStyleSheet(qss_content)

    except FileNotFoundError:
        print(f"Error: The QSS file at {qss_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while loading the QSS: {e}")

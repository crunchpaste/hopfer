class ColorManager:
    """A very simple class that holds the colors. It is used mainly for live color theme switching"""

    def __init__(self, theme="dark"):
        self.theme = theme
        self.primary = None  # Color of text
        self.secondary = None  # Color of backgrounds
        self.accent = None  # Color of focused elements
        self.disabled = None  # Color of disabled elements
        self.titlebar_bg = None  # Color of the titlebar background
        self.titlebar_sh = None  # Color of the titlebar shadow
        self.titlebar_btn = None  # Background of the titlebar buttons
        self.separator = None  # Color of the separator in halftone combo
        self.muted = None  # 2b2d2c

        self.set_theme(self.theme)

    def set_theme(self, theme):
        self.theme = theme.lower()
        if self.theme == "dark":
            self.primary = "#f0f6f0"
            self.secondary = "#222323"
            self.accent = "#fa8072"
            self.disabled = "#6a6d6b"
            self.titlebar_bg = "#202121"
            self.titlebar_sh = "#192020"
            self.titlebar_btn = "#1c1d1d"
            self.separator = "#282929"
            self.muted = "#2b2d2c"

        elif self.theme == "light":
            self.primary = "#222323"
            self.secondary = "#f0f6f0"
            self.accent = "#d4004c"
            self.disabled = "#6a6d6b"
            self.titlebar_bg = "#eaf0ea"
            self.titlebar_sh = "#e5ebe5"
            self.titlebar_btn = "#d8dfd8"
            self.separator = "#d3d4d4"
            self.muted = "#d3d4d4"

import platformdirs
from PySide6.QtCore import Property, QObject, Signal


class Config(QObject):
    # this is the main config object. it is used for two-way sync of the state between the bridge and the ui. plenty of boilerplate, but should make working on the frontend easier.
    versionChanged = Signal()

    def __init__(self, data, version_str="1.0.0"):
        super().__init__()
        self._version = data.get("version", version_str)

        self._window = WindowConfig(data.get("window", {}))
        self._style = StyleConfig(data.get("style", {}))
        self._options = OptionsConfig(data.get("options", {}))
        self._paths = PathsConfig(data.get("paths", {}))

    @Property(str, constant=True)
    def version(self):
        return self._version

    @Property(QObject, constant=True)
    def window(self):
        return self._window

    @Property(QObject, constant=True)
    def style(self):
        return self._style

    @Property(QObject, constant=True)
    def options(self):
        return self._options

    @Property(QObject, constant=True)
    def paths(self):
        return self._paths

    def to_dict(self):
        """Returns the entire configuration including version as a nested dictionary."""
        return {
            "version": self._version,
            "window": self._window.to_dict(),
            "style": self._style.to_dict(),
            "options": self._options.to_dict(),
            "paths": self._paths.to_dict(),
        }


class WindowConfig(QObject):
    xChanged = Signal()
    yChanged = Signal()
    widthChanged = Signal()
    heightChanged = Signal()
    maximizedChanged = Signal()
    nativeFrameChanged = Signal()
    sidebarWidthChanged = Signal()

    def __init__(self, data):
        super().__init__()
        self._x = data.get("x", 100)
        self._y = data.get("y", 100)
        self._width = data.get("width", 800)
        self._height = data.get("height", 600)
        self._maximized = data.get("maximized", False)
        self._native_frame = data.get("native_frame", True)
        self._sidebar_width = data.get("sidebar_width", 250)

    def getX(self):
        return self._x

    def setX(self, v):
        if self._x != v:
            self._x = v
            self.xChanged.emit()

    x = Property(int, getX, setX, notify=xChanged)

    def getY(self):
        return self._y

    def setY(self, v):
        if self._y != v:
            self._y = v
            self.yChanged.emit()

    y = Property(int, getY, setY, notify=yChanged)

    def getWidth(self):
        return self._width

    def setWidth(self, v):
        if self._width != v:
            self._width = v
            self.widthChanged.emit()

    width = Property(int, getWidth, setWidth, notify=widthChanged)

    def getHeight(self):
        return self._height

    def setHeight(self, v):
        if self._height != v:
            self._height = v
            self.heightChanged.emit()

    height = Property(int, getHeight, setHeight, notify=heightChanged)

    def getMaximized(self):
        return self._maximized

    def setMaximized(self, v):
        if self._maximized != v:
            self._maximized = v
            self.maximizedChanged.emit()

    maximized = Property(
        bool, getMaximized, setMaximized, notify=maximizedChanged
    )

    def getNativeFrame(self):
        return self._native_frame

    def setNativeFrame(self, v):
        if self._native_frame != v:
            self._native_frame = v
            self.nativeFrameChanged.emit()

    native_frame = Property(
        bool, getNativeFrame, setNativeFrame, notify=nativeFrameChanged
    )

    def getSidebarWidth(self):
        return self._sidebar_width

    def setSidebarWidth(self, v):
        if self._sidebar_width != v:
            self._sidebar_width = v
            self.sidebarWidthChanged.emit()

    sidebar_width = Property(
        int, getSidebarWidth, setSidebarWidth, notify=sidebarWidthChanged
    )

    def to_dict(self):
        return {
            "x": self._x,
            "y": self._y,
            "width": self._width,
            "height": self._height,
            "maximized": self._maximized,
            "native_frame": self._native_frame,
            "sidebar_width": self._sidebar_width,
        }


class StyleConfig(QObject):
    themeChanged = Signal()
    accentChanged = Signal()
    fontSizeChanged = Signal()

    def __init__(self, data):
        super().__init__()
        self._theme = data.get("theme", 0)
        self._accent = data.get("accent", 0)
        self._font_size = data.get("font_size", 11)

    def getTheme(self):
        return self._theme

    def setTheme(self, v):
        if self._theme != v:
            self._theme = v
            self.themeChanged.emit()

    theme = Property(int, getTheme, setTheme, notify=themeChanged)

    def getAccent(self):
        return self._accent

    def setAccent(self, v):
        if self._accent != v:
            self._accent = v
            self.accentChanged.emit()

    accent = Property(int, getAccent, setAccent, notify=accentChanged)

    def getFontSize(self):
        return self._font_size

    def setFontSize(self, v):
        if self._font_size != v:
            self._font_size = v
            self.fontSizeChanged.emit()

    font_size = Property(int, getFontSize, setFontSize, notify=fontSizeChanged)

    def to_dict(self):
        return {
            "theme": self._theme,
            "accent": self._accent,
            "font_size": self._font_size,
        }


class OptionsConfig(QObject):
    memoryWarningThresholdChanged = Signal()
    shortShortcutsChanged = Signal()
    lowMemoryChanged = Signal()

    def __init__(self, data):
        super().__init__()
        self._memory_warning_threshold = data.get(
            "memory_warning_threshold", 1024
        )
        self._short_shortcuts = data.get("short_shortcuts", False)
        self._low_memory = data.get("low_memory", False)

    def getMemoryWarningThreshold(self):
        return self._memory_warning_threshold

    def setMemoryWarningThreshold(self, v):
        if self._memory_warning_threshold != v:
            self._memory_warning_threshold = v
            self.memoryWarningThresholdChanged.emit()

    memory_warning_threshold = Property(
        int,
        getMemoryWarningThreshold,
        setMemoryWarningThreshold,
        notify=memoryWarningThresholdChanged,
    )

    def getShortShortcuts(self):
        return self._short_shortcuts

    def setShortShortcuts(self, v):
        if self._short_shortcuts != v:
            self._short_shortcuts = v
            self.shortShortcutsChanged.emit()

    short_shortcuts = Property(
        bool, getShortShortcuts, setShortShortcuts, notify=shortShortcutsChanged
    )

    def getLowMemory(self):
        return self._low_memory

    def setLowMemory(self, v):
        if self._low_memory != v:
            self._low_memory = v
            self.lowMemoryChanged.emit()

    low_memory = Property(
        bool, getLowMemory, setLowMemory, notify=lowMemoryChanged
    )

    def to_dict(self):
        return {
            "memory_warning_threshold": self._memory_warning_threshold,
            "short_shortcuts": self._short_shortcuts,
            "low_memory": self._low_memory,
        }


class PathsConfig(QObject):
    openPathChanged = Signal()
    savePathChanged = Signal()
    rememberOpenChanged = Signal()
    rememberSaveChanged = Signal()

    def __init__(self, data):
        super().__init__()
        self._open_path = data.get(
            "open_path", platformdirs.user_pictures_dir()
        )
        self._save_path = data.get(
            "save_path", platformdirs.user_pictures_dir()
        )
        self._remember_open = data.get("remember_open", True)
        self._remember_save = data.get("remember_save", False)

    def getOpenPath(self):
        return self._open_path

    def setOpenPath(self, v):
        if self._open_path != v:
            self._open_path = v
            self.openPathChanged.emit()

    open_path = Property(str, getOpenPath, setOpenPath, notify=openPathChanged)

    def getSavePath(self):
        return self._save_path

    def setSavePath(self, v):
        if self._save_path != v:
            self._save_path = v
            self.savePathChanged.emit()

    save_path = Property(str, getSavePath, setSavePath, notify=savePathChanged)

    def getRememberOpen(self):
        return self._remember_open

    def setRememberOpen(self, v):
        if self._remember_open != v:
            self._remember_open = v
            self.rememberOpenChanged.emit()

    remember_open = Property(
        bool, getRememberOpen, setRememberOpen, notify=rememberOpenChanged
    )

    def getRememberSave(self):
        return self._remember_save

    def setRememberSave(self, v):
        if self._remember_save != v:
            self._remember_save = v
            self.rememberSaveChanged.emit()

    remember_save = Property(
        bool, getRememberSave, setRememberSave, notify=rememberSaveChanged
    )

    def to_dict(self):
        return {
            "open_path": self._open_path,
            "save_path": self._save_path,
            "remember_open": self._remember_open,
            "remember_save": self._remember_save,
        }

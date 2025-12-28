import QtQuick
import QtQuick.Controls.Material

QtObject {
    id: root

    property int selectedIndex: 0
    property int themeMode: 2
    property bool dark: true

    readonly property bool isDark: themeMode === 2
    readonly property bool isMedium: themeMode === 1
    readonly property bool isLight: themeMode === 0

    readonly property color windowBg: {
        if (dark) return "#1c1b1f";   // Your default Dark
        if (!dark) return "#5a5a5a"; // Placeholder for your Medium
        return "#fffbfe"               // Your default Light
    }

    readonly property color monochrome: dark ? "#f8f8ff" : "#393d47"
    readonly property color salmon: dark ?  "salmon" : "#e95044"
    readonly property color pink: dark ? "#f48fb1" : "#e91e63"
    readonly property color green: dark ? "#a5d6a7" : "#4caf50"
    readonly property color teal: dark ? "#80cbc4" : "#009688"

    readonly property color currentAccent: {
        if (selectedIndex === 0) return monochrome;
        if (selectedIndex === 1) return salmon;
        if (selectedIndex === 2) return pink;
        if (selectedIndex === 3) return green;
        if (selectedIndex === 4) return teal;
        return monochrome;
    }
}

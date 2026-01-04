import Components
import Icons
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material


ColumnLayout {
    Layout.fillWidth: true
    Layout.fillHeight: true
    Label {
        Layout.fillWidth: true
        Layout.fillHeight: true
        textFormat: Text.RichText
        wrapMode: Text.WordWrap
        onLinkActivated: (link) => Qt.openUrlExternally(link)
        text: `<html>
                  <head>
                    <style>
                      a { color: ${Material.accent}; text-decoration: underline; font-weight: bold; }
                      a:hover { text-decoration: underline; }
                      p { margin-bottom: 10px; }
                    </style>
                  </head>
                  <body>
                    <p>
                      Hopfer is a simple <a href="https://www.qt.io/">Qt6</a> app meant as a companion
                      to my PhD thesis on halftoning algorithms for print, written almost exclusively
                      in Python and using <a href="https://numpy.org/">NumPy</a> and
                      <a href="https://numba.pydata.org/">Numba</a> for acceleration.
                    </p>

                    <p>
                      The app is named after <a href="https://en.wikipedia.org/wiki/Daniel_Hopfer">Daniel Hopfer</a>
                      &mdash; an early German blacksmith-turned-printmaker, mostly known for his
                      technical achievements, especially the invention of etching. That's the reason
                      I probably went a bit overboard with the logo.
                    </p>

                    <p>
                      Keep in mind <b>hopfer</b> is still in its very early development,
                      so expect bugs and crashes.
                    </p>
                  </body>
                  </html>`
              HoverHandler {
                  enabled: parent.hoveredLink
                  cursorShape: Qt.PointingHandCursor
              }
    }
    Label {
      Layout.fillWidth: true
      text: "Pavel Lefterov"
      horizontalAlignment: Text.AlignHCenter
    }
    Label {
        Layout.fillWidth: true
        text: `<style>
          a { color: ${Material.accent}; text-decoration: underline; font-weight: bold; } </style> <p> Licensed under <a href='https://www.gnu.org/licenses/gpl-3.0.en.html'>GPLv3</a></p>`
        textFormat: Text.RichText
        horizontalAlignment: Text.AlignHCenter
        linkColor: Material.accent
        onLinkActivated: (link) => Qt.openUrlExternally(link)
        HoverHandler {
          enabled: parent.hoveredLink
          cursorShape: Qt.PointingHandCursor
        }
    }
    Item {
      height: 5
    }
    RoundButton {
        Layout.alignment: Qt.AlignHCenter
        radius: 5
        // topInset: 0
        // bottomInset: 0
        // leftInset: 0
        // rightInset: 0
        // highlighted: true
        icon.source: "../Icons/github.svg"
        // icon.color: Material.accent
        padding: 15
        text: "Source code"
        onClicked: {
        Qt.openUrlExternally("https://github.com/crunchpaste/hopfer")
        }
    }
}

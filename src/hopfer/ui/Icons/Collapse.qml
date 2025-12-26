// Generated from SVG file collapse.svg
import QtQuick
import QtQuick.Shapes

Item {
    property alias fill: _qt_shapePath_0.fillColor
    implicitWidth: 30
    implicitHeight: 30
    transform: [
        Scale { xScale: width / 7.938; yScale: height / 7.938 }
    ]
    id: _qt_node0
    Item {
        id: _qt_node1
        transform: Matrix4x4 { matrix: PlanarTransform.fromAffineMatrix(1, 0, 0, 1, -1.984, -1.984)}
        Shape {
            id: _qt_node2
            preferredRendererType: Shape.CurveRenderer
            transform: Matrix4x4 { matrix: PlanarTransform.fromAffineMatrix(0.004725, 0, 0, 0.004725, 3.685, 8.221)}
            ShapePath {
                id: _qt_shapePath_0
                strokeColor: "transparent"
                fillColor: "#fffa8072"
                fillRule: ShapePath.WindingFill
                PathSvg { path: "M 440 -440 L 440 -200 L 360 -200 L 360 -360 L 200 -360 L 200 -440 L 440 -440 M 600 -760 L 600 -600 L 760 -600 L 760 -520 L 520 -520 L 520 -760 L 600 -760 " }
            }
        }
    }
}

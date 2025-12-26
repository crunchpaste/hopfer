// Generated from SVG file expand.svg
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
            preferredRendererType: Shape.CurveRenderer
            id: _qt_node2
            transform: Matrix4x4 { matrix: PlanarTransform.fromAffineMatrix(0.004725, 0, 0, 0.004725, 3.685, 8.221)}
            ShapePath {
                id: _qt_shapePath_0
                strokeColor: "transparent"
                fillColor: "#fff8f8ff"
                fillRule: ShapePath.WindingFill
                PathSvg { path: "M 200 -200 L 200 -440 L 280 -440 L 280 -280 L 440 -280 L 440 -200 L 200 -200 M 680 -520 L 680 -680 L 520 -680 L 520 -760 L 760 -760 L 760 -520 L 680 -520 " }
            }
        }
    }
}

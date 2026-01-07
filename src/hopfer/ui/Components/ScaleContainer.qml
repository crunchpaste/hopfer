import QtQuick

Item {
    id: scaler
    default property alias content: container.data
    property real zoom: 1.0

    Item {
        id: container
        width: scaler.width / scaler.zoom
        height: scaler.height / scaler.zoom

        transform: Scale {
            xScale: scaler.zoom
            yScale: scaler.zoom
            origin.x: 0; origin.y: 0
        }
    }
}

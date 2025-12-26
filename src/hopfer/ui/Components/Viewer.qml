import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: viewport

    property alias source: image.source
    property alias status: image.status
    property bool hasImage: image.status === Image.Ready

    function fit() {
        mouseArea.fit();
    }

    function busy(state) {
        busy.visible = state;
    }

    function actual() {
        let cx = Math.floor(mouseArea.width / 2)
        let cy = Math.floor(mouseArea.height / 2)
        mouseArea.zoom_to_point(cx, cy, 1, 1)
    }

    clip: true

    Image {
        id: image

        smooth: false
        mipmap: (imageScale.xScale % 1 !== 0) && (imageScale.xScale < 2)
        anchors.centerIn: parent
        transform: [
            Scale {
                id: imageScale

                xScale: 1
                yScale: 1
                origin.x: image.width / 2
                origin.y: image.height / 2
            },
            Translate {
                id: imageTranslate

                x: 0
                y: 0
            }
        ]
    }

    PinchHandler {
        id: pinch

        // anchors.fill: parent
        target: null
        // onScaleChanged: (console.log(imageScale.xScale))
        rotationAxis.enabled: false
        onScaleChanged: function(scale_f) {
            mouseArea.zoom_to_point(pinch.centroid.position.x, pinch.centroid.position.y, scale_f);
        }
        onTranslationChanged: function(delta) {
            // may or may not work on a touchscreen and some touchpads. dont really know as i dont own any.
            var delta_x = delta.x;
            var delta_y = delta.y;
            mouseArea.pan(delta_x, delta_y);
        }
    }

    MouseArea {
        // console.log(center_x, center_y)

        id: mouseArea

        property real lx: 0
        property real ly: 0
        property real zoom_index: 0
        property real zoom_base: 1.2

        function snap_to_int(current_scale, proposed_scale) {
            // in case a boundary was crossed

            // get the integers needed for the snapping
            const curr_floor = Math.floor(current_scale);
            const prop_floor = Math.floor(proposed_scale);
            // this handles the exception in the case of 0 as we dont want to snap to zero.
            if (prop_floor <= 0)
                return proposed_scale;

            // if no int boundary was crossed just rescale
            if (prop_floor == curr_floor)
                return proposed_scale;

            // in case we we already at an integer return the proposed scale
            if (current_scale == curr_floor)
                return proposed_scale;

            // when going up rescale to the floored proposal
            if (prop_floor > curr_floor)
                return prop_floor;

            // if crossing down and the current scale is not an int already, return the current floor
            if (current_scale !== curr_floor)
                return curr_floor;

            return proposed_scale;
        }

        function pan(delta_x, delta_y) {
            // in case it is bigger clamp the values

            const w = image.width;
            const h = image.height;
            const scale = imageScale.xScale;
            const vw = mouseArea.width;
            const vh = mouseArea.height;
            // get the corners of the image in viewport coords
            var nw = image.mapToItem(mouseArea, 0, 0);
            var ne = image.mapToItem(mouseArea, w, 0);
            var sw = image.mapToItem(mouseArea, 0, h);
            var se = image.mapToItem(mouseArea, w, h);
            var dx = delta_x;
            var dy = delta_y;
            // if the image is smaller than the viewport on x
            // ignore translations on x and center it in the
            // viewport
            if (Math.round(se.x - nw.x) <= vw) {
                imageTranslate.x = 0;
                dx = 0;
            } else {
                // Right clamp

                // Left clamp
                if (nw.x + dx > 0) {
                    let overshoot = nw.x + dx;
                    dx -= overshoot;
                } else if (se.x + dx < vw) {
                    let undershoot = vw - (se.x + dx);
                    dx += undershoot;
                }
            }
            // do the same for the y axis
            if (Math.round(se.y - nw.y) <= vh) {
                imageTranslate.y = 0;
                dy = 0;
            } else {
                // Bottom clamp

                // Top clamp
                if (nw.y + dy > 0) {
                    let overshoot = nw.y + dy;
                    dy -= overshoot;
                } else if (se.y + dy < vh) {
                    let undershoot = vh - (se.y + dy);
                    dy += undershoot;
                }
            }
            imageTranslate.x += dx;
            imageTranslate.y += dy;
        }

        function zoom_to_point(center_x, center_y, scale_f, target_scale) {
            // scale factor
            // TODO: make it configurable
            // var scale_f = wheel.angleDelta.y > 0 ? 1.10 : 1 / 1.1;
            // const step = wheel.angleDelta.y > 0 ? 1.0 : -1.0;
            // zoom_index += step;
            // var new_scale = Math.pow(zoom_base, zoom_index);

            const zoom_out_f = 1;
            var current_scale = imageScale.xScale;
            var new_scale = current_scale * scale_f;
            // if ((current_scale < 1) && (new_scale > 1)) {
            //     new_scale = 1
            // }
            if (target_scale == undefined) {
              new_scale = snap_to_int(current_scale, new_scale);
            }
            else { new_scale = target_scale }

            const w = image.width;
            const h = image.height;
            const vw = mouseArea.width;
            const vh = mouseArea.height;
            const w_ratio = vw / w;
            const h_ratio = vh / h;
            var min_scale = Math.min(w_ratio, h_ratio) * zoom_out_f;
            // in case the new scale would result in an image smaller
            // than the viewport apply the minimum required to fit
            // the viewport
            if (new_scale.toFixed(3) <= min_scale.toFixed(3)) {
                imageTranslate.x = 0;
                imageTranslate.y = 0;
                imageScale.xScale = min_scale;
                imageScale.yScale = min_scale;
                return ;
            }
            var local_point = mouseArea.mapToItem(image, center_x, center_y);
            var x = local_point.x;
            var y = local_point.y;
            var image_cx = image.width / 2;
            var image_cy = image.height / 2;
            var dx = x - image_cx;
            var dy = y - image_cy;
            var scale_diff = new_scale - current_scale;
            var transl_x = dx * scale_diff;
            var transl_y = dy * scale_diff;
            var nw = image.mapToItem(mouseArea, 0, 0);
            var se = image.mapToItem(mouseArea, w, h);
            imageScale.xScale = new_scale;
            imageScale.yScale = new_scale;
            if (Math.round(se.x - nw.x) <= vw * zoom_out_f) {
                imageTranslate.x = 0;
            } else {
                const proposed_tx = imageTranslate.x - transl_x;
                const new_scaled_w = w * new_scale;
                const max_left_pos = (vw / 2) * zoom_out_f - (new_scaled_w / 2);
                const max_right_pos = (new_scaled_w / 2) - (vw / 2) * zoom_out_f;
                // console.log(max_left_pos, max_right_pos)
                let final_tx = Math.max(proposed_tx, max_left_pos);
                final_tx = Math.min(final_tx, max_right_pos);
                imageTranslate.x = final_tx;
            }
            if (Math.round(se.y - nw.y) <= vh * zoom_out_f) {
                imageTranslate.y = 0;
            } else {
                const proposed_ty = imageTranslate.y - transl_y;
                const new_scaled_h = h * new_scale;
                const max_top_pos = (vh / 2) * zoom_out_f - (new_scaled_h / 2);
                const max_bottom_pos = (new_scaled_h / 2) - (vh / 2) * zoom_out_f;
                let final_ty = Math.max(proposed_ty, max_top_pos);
                final_ty = Math.min(final_ty, max_bottom_pos);
                imageTranslate.y = final_ty;
            }
        }

        function fit() {
            const w = image.width;
            const h = image.height;
            const vw = mouseArea.width;
            const vh = mouseArea.height;
            // center the image
            imageTranslate.x = 0;
            imageTranslate.y = 0;
            // calculate ratios
            const w_ratio = vw / w;
            const h_ratio = vh / h;
            // choose a ratio
            var min_scale = Math.min(w_ratio, h_ratio);
            // apply scale
            imageScale.xScale = min_scale;
            imageScale.yScale = min_scale;
        }

        function fill() {
            const w = image.width;
            const h = image.height;
            const vw = mouseArea.width;
            const vh = mouseArea.height;
            const scale = imageScale.xScale;
            // Get the north west corner of the image in MouseArea
            // coordinate system
            var nw = image.mapToItem(mouseArea, 0, 0);
            // Same for the south east
            var se = image.mapToItem(mouseArea, w, h);
            if (Math.round(se.x - nw.x) <= vw)
                imageTranslate.x = 0;

            if (Math.round(se.y - nw.y) <= vh)
                imageTranslate.y = 0;

            const w_ratio = vw / w;
            const h_ratio = vh / h;
            var min_scale = Math.min(w_ratio, h_ratio);
            if (scale < min_scale) {
                imageScale.xScale = min_scale;
                imageScale.yScale = min_scale;
            }
        }

        anchors.fill: viewport
        onPressed: function(mouse) {
            lx = mouse.x;
            ly = mouse.y;
        }
        onWidthChanged: fill()
        onHeightChanged: fill()
        onPositionChanged: function(mouse) {
            if (mouseArea.pressed) {
                var delta_x = mouse.x - lx;
                var delta_y = mouse.y - ly;
                pan(delta_x, delta_y);
                lx = mouse.x;
                ly = mouse.y;
            }
        }
        onWheel: function(wheel) {
            var scale_f = wheel.angleDelta.y > 0 ? 1.1 : 1 / 1.1;
            zoom_to_point(wheel.x, wheel.y, scale_f);
        }
    }

    Item {
        id: busy

        anchors.centerIn: parent
        width: 150
        height: 150
        visible: false
        opacity: visible ? 1 : 0

        Rectangle {
            anchors.fill: parent
            color: "black"
            opacity: 0.5
            radius: 10
        }

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 20

            BusyIndicator {
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                Layout.alignment: Qt.AlignHCenter
                text: "Processing"
            }

        }

    }

    SnackBar {
    }

}

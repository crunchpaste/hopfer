import QtQuick
import QtQuick.Controls

SpinBox {
    id: control
    editable: true

    // Default values if not provided by the parent
    property int decimals: 0
    property real factor: Math.pow(10, decimals)

    validator: RegularExpressionValidator {
        regularExpression: new RegExp("[0-9+\\-*/(). " + Qt.locale().decimalPoint + "]+")
    }

    textFromValue: function(v, locale) {
        return (v / factor).toLocaleString(locale, 'f', decimals)
    }

    valueFromText: function(text, locale) {
        try {
            let sep = locale.decimalPoint;
            let cleanRegex = new RegExp("[^0-9+\\-*/(). " + sep + "]", "g");
            let cleanText = text.replace(cleanRegex, '');
            let firstChar = cleanText.trim().charAt(0);
            let mathReadyText = cleanText;

            if (["+", "-", "*", "/"].indexOf(firstChar) !== -1) {
                mathReadyText = (value / factor).toString() + cleanText;
            }
            
            mathReadyText = mathReadyText.split(sep).join('.');
            let result = new Function('return ' + mathReadyText)();

            return Math.round(result * factor);
        } catch (e) {
            return value;
        }
    }
}

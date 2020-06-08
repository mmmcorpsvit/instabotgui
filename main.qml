//import QtQuick 2.10
//import QtQuick.Controls 2.3
//
//ApplicationWindow {
//
//    visible: true
//    width: 500
//    height: 400
//    title: "InstagramBot v0.1"
//
//    Grid {
//        anchors.fill: parent
//    }
//
//}
//

import QtQuick 2.10
import QtQuick.Controls 2.3

ApplicationWindow {
    visible: true
    width: 500
    height: 400
    title: "InstagramBot v0.1"


    header: ToolBar {
        Layout.fillWidth: true

       RowLayout {
            anchors.fill: parent

            ToolButton {
                width: parent.height
                anchors.margins: 4
//                iconSource: "ico/abacus.png"
            }

        }
    }

    Grid {
        anchors.fill: parent
    }
}




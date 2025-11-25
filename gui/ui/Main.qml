import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Effects 1.15
import QtQuick.Window 6.5

ApplicationWindow {
    id: root
    width: 1180
    height: 760
    visible: true
    title: qsTr("LLM Council – Desktop")
    color: "#0f1115"

    property color accent: "#1dc6ff"
    property color panel: "#171a20"
    property color muted: "#9ca3af"

    Rectangle {
        anchors.fill: parent
        color: root.color

        RowLayout {
            anchors.fill: parent
            spacing: 0

            // Side rail
            Rectangle {
                id: rail
                Layout.preferredWidth: 280
                Layout.fillHeight: true
                color: Qt.rgba(0.12, 0.13, 0.16, 0.8)
                border.color: "#1f2933"
                radius: 0
                layer.enabled: true
                layer.effect: DropShadow {
                    horizontalOffset: 2
                    verticalOffset: 0
                    radius: 16
                    samples: 25
                    color: Qt.rgba(0, 0, 0, 0.35)
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Label {
                            text: "LLM Council"
                            font.pixelSize: 20
                            font.bold: true
                            color: "white"
                        }
                        Rectangle {
                            width: 10
                            height: 10
                            radius: 5
                            color: accent
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Label {
                        text: "Desktop preview — wired for backend streaming next."
                        wrapMode: Label.Wrap
                        color: muted
                        font.pixelSize: 12
                    }

                    Button {
                        text: "New Conversation"
                        Layout.fillWidth: true
                        font.pixelSize: 14
                        background: Rectangle {
                            radius: 10
                            color: control.down ? Qt.darker(root.accent, 1.2) : root.accent
                        }
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: "#1f2933" }

                    Label {
                        text: "Recent"
                        color: muted
                        font.pixelSize: 12
                        Layout.leftMargin: 4
                    }

                    ListView {
                        id: convoList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: ListModel {
                            ListElement { title: "Prompt comparison"; status: "Complete" }
                            ListElement { title: "Research outline"; status: "Streaming" }
                            ListElement { title: "Data viz ideas"; status: "Draft" }
                        }
                        delegate: Item {
                            width: convoList.width
                            height: 52
                            Rectangle {
                                anchors.fill: parent
                                anchors.margins: 6
                                radius: 10
                                color: ListView.isCurrentItem ? Qt.rgba(0.12,0.6,0.9,0.18) : "#12151b"
                                border.color: Qt.rgba(0.12,0.6,0.9,0.35)
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 10
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2
                                        Label {
                                            text: title
                                            color: "white"
                                            font.pixelSize: 14
                                            elide: Label.ElideRight
                                        }
                                        Label {
                                            text: status
                                            color: muted
                                            font.pixelSize: 11
                                        }
                                    }
                                    Rectangle {
                                        width: 10
                                        height: 10
                                        radius: 5
                                        color: status === "Streaming" ? accent : "#22c55e"
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Main content
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: root.panel
                radius: 0
                anchors.margins: 0

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 14

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        Label {
                            text: "Conversation"
                            color: "white"
                            font.pixelSize: 24
                            font.bold: true
                        }
                        Rectangle {
                            radius: 8
                            color: Qt.rgba(0.12,0.6,0.9,0.18)
                            border.color: Qt.rgba(0.12,0.6,0.9,0.45)
                            height: 30
                            width: 120
                            anchors.verticalCenter: parent.verticalCenter
                            Row {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle {
                                    width: 10; height: 10; radius: 5; color: accent
                                    SequentialAnimation on opacity {
                                        loops: Animation.Infinite
                                        NumberAnimation { from: 0.35; to: 1.0; duration: 900; easing.type: Easing.InOutSine }
                                        NumberAnimation { from: 1.0; to: 0.35; duration: 900; easing.type: Easing.InOutSine }
                                    }
                                }
                                Label { text: "Idle"; color: accent; font.pixelSize: 12 }
                            }
                        }
                        Item { Layout.fillWidth: true }
                        Button {
                            text: "Settings"
                            flat: true
                            icon.name: "settings"
                            contentItem: Label { text: control.text; color: "white" }
                        }
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: "#1f2933" }

                    // Stage tabs placeholder
                    RowLayout {
                        spacing: 10
                        Label { text: "Stage 1 · Models"; color: muted; font.pixelSize: 13 }
                        Rectangle { width: 6; height: 6; radius: 3; color: "#374151"; anchors.verticalCenter: parent.verticalCenter }
                        Label { text: "Stage 2 · Rankings"; color: muted; font.pixelSize: 13 }
                        Rectangle { width: 6; height: 6; radius: 3; color: "#374151"; anchors.verticalCenter: parent.verticalCenter }
                        Label { text: "Stage 3 · Final"; color: muted; font.pixelSize: 13 }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 12
                        color: "#0f1218"
                        border.color: "#1f2933"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 12

                            Label {
                                text: "Streaming view is coming next. Backend events will paint model tabs, rankings, and the synthesized reply."
                                wrapMode: Label.Wrap
                                color: muted
                                font.pixelSize: 14
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 140
                                radius: 12
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: Qt.rgba(0.11, 0.22, 0.35, 0.65) }
                                    GradientStop { position: 1.0; color: Qt.rgba(0.08, 0.11, 0.18, 0.85) }
                                }
                                border.color: Qt.rgba(0.12,0.6,0.9,0.35)

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 8
                                    Label { text: "Stage timeline"; color: "white"; font.pixelSize: 16; font.bold: true }
                                    Label { text: "• Stage 1: per-model responses\n• Stage 2: anonymous peer rankings\n• Stage 3: chairman synthesis"; color: muted; font.pixelSize: 13 }
                                }
                            }

                            Item { Layout.fillHeight: true }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 64
                                radius: 12
                                color: "#12151b"
                                border.color: "#1f2933"
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 10

                                    TextArea {
                                        id: inputBox
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        placeholderText: "Ask the council anything..."
                                        color: "white"
                                        placeholderTextColor: "#6b7280"
                                        wrapMode: TextEdit.Wrap
                                        background: Rectangle {
                                            radius: 10
                                            color: "#0f1115"
                                            border.color: "#1f2933"
                                        }
                                    }

                                    Button {
                                        text: "Send"
                                        icon.name: "arrow-up"
                                        width: 96
                                        Layout.alignment: Qt.AlignVCenter
                                        background: Rectangle {
                                            radius: 12
                                            color: control.down ? Qt.darker(root.accent, 1.2) : root.accent
                                        }
                                        contentItem: Label { text: control.text; color: "#0b1020"; font.bold: true }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

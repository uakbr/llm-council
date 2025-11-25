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
    property bool settingsOpen: false

    Component.onCompleted: bridge.loadConversations()

    function stageComplete(key) {
        if (key === "stage1") return bridge.stageData.stage1 && bridge.stageData.stage1.length > 0;
        if (key === "stage2") return bridge.stageData.stage2 && bridge.stageData.stage2.length > 0;
        if (key === "stage3") return bridge.stageData.stage3 !== null;
        return false;
    }

    function stageActive(key) {
        return bridge.streamStatus.inFlight && bridge.streamStatus.currentStage && bridge.streamStatus.currentStage.indexOf(key) === 0;
    }

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
                        text: "Backend: " + bridge.backendUrl
                        wrapMode: Label.Wrap
                        color: muted
                        font.pixelSize: 12
                    }

                    Button {
                        text: "New Conversation"
                        Layout.fillWidth: true
                        font.pixelSize: 14
                        onClicked: bridge.newConversation()
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
                        model: bridge.conversations
                        delegate: Item {
                            width: convoList.width
                            height: 64
                            property var convo: modelData
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
                                            text: convo.title || "Untitled"
                                            color: "white"
                                            font.pixelSize: 14
                                            elide: Label.ElideRight
                                        }
                                        Label {
                                            text: convo.streaming ? "Streaming" : (convo.message_count + " message(s)")
                                            color: muted
                                            font.pixelSize: 11
                                        }
                                    }
                                    Rectangle {
                                        width: 10
                                        height: 10
                                        radius: 5
                                        color: convo.streaming ? accent : "#22c55e"
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    convoList.currentIndex = index
                                    bridge.selectConversation(convo.id)
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
                    // Error banner
                    Rectangle {
                        visible: bridge.streamStatus.lastEvent === "error" && bridge.streamStatus.error !== undefined && bridge.streamStatus.error !== null && bridge.streamStatus.error !== ""
                        Layout.fillWidth: true
                        height: visible ? 40 : 0
                        radius: 8
                        color: "#2d1b1b"
                        border.color: "#b91c1c"
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8
                            Label { text: "Error"; color: "#f87171"; font.bold: true; font.pixelSize: 13 }
                            Label { text: bridge.streamStatus.error || ""; color: "#fecdd3"; font.pixelSize: 12; wrapMode: Label.Wrap; Layout.fillWidth: true }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        Label {
                            text: bridge.currentConversation ? bridge.currentConversation.title : "Conversation"
                            color: "white"
                            font.pixelSize: 24
                            font.bold: true
                        }
                        Rectangle {
                            radius: 8
                            color: bridge.streamStatus.inFlight ? Qt.rgba(0.12,0.6,0.9,0.18) : Qt.rgba(0.16,0.6,0.35,0.18)
                            border.color: bridge.streamStatus.inFlight ? Qt.rgba(0.12,0.6,0.9,0.45) : Qt.rgba(0.22,0.8,0.6,0.45)
                            height: 30
                            width: 160
                            anchors.verticalCenter: parent.verticalCenter
                            Row {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle {
                                    width: 10; height: 10; radius: 5; color: bridge.streamStatus.inFlight ? accent : "#22c55e"
                                    SequentialAnimation on opacity {
                                        loops: bridge.streamStatus.inFlight ? Animation.Infinite : 1
                                        NumberAnimation { from: 0.35; to: 1.0; duration: 900; easing.type: Easing.InOutSine }
                                        NumberAnimation { from: 1.0; to: 0.35; duration: 900; easing.type: Easing.InOutSine }
                                    }
                                }
                                Label {
                                    text: bridge.streamStatus.inFlight ? (bridge.streamStatus.currentStage || "Streaming") : "Idle"
                                    color: bridge.streamStatus.inFlight ? accent : "#22c55e"
                                    font.pixelSize: 12
                                }
                            }
                        }
                        Item { Layout.fillWidth: true }
                        Button {
                            text: bridge.streamStatus.inFlight ? "Stop" : "Settings"
                            flat: true
                            icon.name: bridge.streamStatus.inFlight ? "media-playback-stop" : "settings"
                            contentItem: Label { text: control.text; color: "white" }
                            onClicked: {
                                if (bridge.streamStatus.inFlight) {
                                    bridge.cancelStream()
                                } else {
                                    settingsOpen = true
                                }
                            }
                        }
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: "#1f2933" }

                    // Stage tabs
                    RowLayout {
                        spacing: 10
                        Repeater {
                            model: [
                                { key: "stage1", label: "Stage 1 · Models" },
                                { key: "stage2", label: "Stage 2 · Rankings" },
                                { key: "stage3", label: "Stage 3 · Final" }
                            ]
                            delegate: RowLayout {
                                spacing: 6
                                Rectangle {
                                    width: 8; height: 8; radius: 4;
                                    color: stageComplete(modelData.key) ? "#22c55e" : stageActive(modelData.key) ? accent : "#374151"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                Label { text: modelData.label; color: stageComplete(modelData.key) ? "white" : muted; font.pixelSize: 13 }
                            }
                        }
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
                            spacing: 16

                            // Stage 1 responses
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                RowLayout {
                                    spacing: 8
                                    Label { text: "Stage 1 · Model Responses"; color: "white"; font.pixelSize: 16; font.bold: true }
                                    Label { text: bridge.stageData.stage1.length ? "(" + bridge.stageData.stage1.length + ")" : ""; color: muted; font.pixelSize: 12 }
                                }
                                Repeater {
                                    model: bridge.stageData.stage1
                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        height: implicitHeight
                                        radius: 10
                                        color: "#111620"
                                        border.color: "#1f2933"
                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 12
                                            spacing: 6
                                            Label { text: modelData.model; color: accent; font.pixelSize: 13; font.bold: true }
                                            Text {
                                                text: modelData.response
                                                wrapMode: Text.Wrap
                                                color: "white"
                                                font.pixelSize: 13
                                            }
                                        }
                                    }
                                }
                                Label {
                                    visible: bridge.stageData.stage1.length === 0
                                    text: bridge.streamStatus.inFlight ? "Waiting for models…" : "No responses yet. Ask a question to start."
                                    color: muted
                                    font.pixelSize: 13
                                }
                            }

                            Rectangle { Layout.fillWidth: true; height: 1; color: "#1f2933" }

                            // Stage 2 rankings
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                RowLayout {
                                    spacing: 8
                                    Label { text: "Stage 2 · Peer Rankings"; color: "white"; font.pixelSize: 16; font.bold: true }
                                    Label { text: bridge.stageData.stage2.length ? "(" + bridge.stageData.stage2.length + ")" : ""; color: muted; font.pixelSize: 12 }
                                }
                                Repeater {
                                    model: bridge.stageData.stage2
                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        radius: 10
                                        color: "#111620"
                                        border.color: "#1f2933"
                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 12
                                            spacing: 6
                                            Label { text: modelData.model; color: accent; font.pixelSize: 13; font.bold: true }
                                            Text {
                                                text: modelData.ranking
                                                wrapMode: Text.Wrap
                                                color: "white"
                                                font.pixelSize: 13
                                            }
                                            Label {
                                                visible: modelData.parsed_ranking && modelData.parsed_ranking.length > 0
                                                text: modelData.parsed_ranking ? modelData.parsed_ranking.join(" → ") : ""
                                                color: muted
                                                font.pixelSize: 12
                                            }
                                        }
                                    }
                                }
                                Label {
                                    visible: bridge.stageData.stage2.length === 0
                                    text: bridge.streamStatus.inFlight ? "Waiting for peer rankings…" : "No rankings yet."
                                    color: muted
                                    font.pixelSize: 13
                                }
                                // Aggregate rankings
                                Repeater {
                                    model: bridge.stageData.aggregateRankings || []
                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        height: 36
                                        radius: 8
                                        color: "#0f1118"
                                        border.color: "#1f2933"
                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 8
                                            Label { text: "" + modelData.model; color: "white"; font.pixelSize: 12; Layout.preferredWidth: 120 }
                                            Rectangle {
                                                Layout.fillWidth: true
                                                height: 8
                                                radius: 4
                                                color: Qt.rgba(0.12, 0.6, 0.9, 0.35)
                                                Rectangle {
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    anchors.left: parent.left
                                                    height: parent.height
                                                    width: Math.max(12, (parent.width * (1.0 / (modelData.average_rank || 1))))
                                                    radius: 4
                                                    color: accent
                                                }
                                            }
                                            Label { text: "avg " + (modelData.average_rank && modelData.average_rank.toFixed ? modelData.average_rank.toFixed(2) : modelData.average_rank); color: muted; font.pixelSize: 12 }
                                        }
                                    }
                                }
                            }

                            Rectangle { Layout.fillWidth: true; height: 1; color: "#1f2933" }

                            // Stage 3 final
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                RowLayout {
                                    spacing: 8
                                    Label { text: "Stage 3 · Final Answer"; color: "white"; font.pixelSize: 16; font.bold: true }
                                    Label { text: bridge.stageData.stage3 ? "ready" : ""; color: muted; font.pixelSize: 12 }
                                }
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: 10
                                    color: "#111620"
                                    border.color: "#1f2933"
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 8
                                        Label { text: bridge.stageData.stage3 ? bridge.stageData.stage3.model : ""; color: accent; font.pixelSize: 13; font.bold: true }
                                        Text {
                                            text: bridge.stageData.stage3 ? bridge.stageData.stage3.response : (bridge.streamStatus.inFlight ? "Synthesizing…" : "Stage 3 not ready")
                                            wrapMode: Text.Wrap
                                            color: "white"
                                            font.pixelSize: 14
                                        }
                                        Label {
                                            visible: bridge.stageData.title
                                            text: bridge.stageData.title ? "Title: " + bridge.stageData.title : ""
                                            color: muted
                                            font.pixelSize: 12
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Input area
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
                                text: bridge.streamStatus.inFlight ? "Stop" : "Send"
                                icon.name: bridge.streamStatus.inFlight ? "media-playback-stop" : "arrow-up"
                                width: 96
                                Layout.alignment: Qt.AlignVCenter
                                enabled: bridge.streamStatus.inFlight ? true : inputBox.text.length > 0
                                onClicked: {
                                    if (bridge.streamStatus.inFlight) {
                                        bridge.cancelStream()
                                    } else {
                                        bridge.sendMessage(inputBox.text)
                                        inputBox.text = ""
                                    }
                                }
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

        // Settings modal
        Popup {
            id: settingsModal
            x: (root.width - width) / 2
            y: (root.height - height) / 3
            width: 420
            height: 280
            modal: true
            dim: true
            visible: settingsOpen
            onVisibleChanged: if (!visible) settingsOpen = false
            background: Rectangle { color: "#0f1218"; radius: 12; border.color: "#1f2933" }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12
                RowLayout {
                    Layout.fillWidth: true
                    Label { text: "Settings"; color: "white"; font.pixelSize: 18; font.bold: true }
                    Item { Layout.fillWidth: true }
                    Button {
                        text: "Close"
                        flat: true
                        onClicked: settingsOpen = false
                        contentItem: Label { text: control.text; color: muted }
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6
                    Label { text: "Backend URL"; color: muted; font.pixelSize: 12 }
                    TextField {
                        id: backendField
                        text: bridge.backendUrl
                        color: "white"
                        placeholderText: "http://localhost:8001"
                        background: Rectangle { radius: 8; color: "#111620"; border.color: "#1f2933" }
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6
                    Label { text: "API Key (optional)"; color: muted; font.pixelSize: 12 }
                    TextField {
                        id: apiKeyField
                        text: bridge.apiKey
                        echoMode: TextInput.Password
                        color: "white"
                        placeholderText: "sk-or-..."
                        background: Rectangle { radius: 8; color: "#111620"; border.color: "#1f2933" }
                    }
                }
                Item { Layout.fillHeight: true }
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Label {
                        id: settingsError
                        color: "#fca5a5"
                        text: ""
                        font.pixelSize: 12
                        visible: text.length > 0
                        Layout.fillWidth: true
                    }
                    Button {
                        text: "Save"
                        onClicked: {
                            bridge.saveSettings(backendField.text, apiKeyField.text).then(function(ok) {
                                if (!ok) {
                                    settingsError.text = "Backend URL required"
                                } else {
                                    settingsError.text = ""
                                    settingsOpen = false
                                }
                            })
                        }
                        background: Rectangle { radius: 10; color: control.down ? Qt.darker(root.accent, 1.2) : root.accent }
                        contentItem: Label { text: control.text; color: "#0b1020"; font.bold: true }
                    }
                }
            }
        }
    }
}

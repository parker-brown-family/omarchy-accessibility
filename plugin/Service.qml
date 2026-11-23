// Keeps loop/oad.py running while the shell runs, and restarts it 5 s after it stops.
// It turns the accessibility bus on, which is what makes apps publish their controls.
import QtQuick
import Quickshell
import Quickshell.Io

Item {
  id: root
  property var shell: null
  readonly property string loop: Quickshell.env("OMARCHY_ACCESSIBILITY_HOME") || (Quickshell.env("HOME") + "/Work/omarchy-accessibility")

  Process {
    id: bus
    running: true
    command: ["gdbus", "call", "--session", "--dest", "org.a11y.Bus", "--object-path", "/org/a11y/bus", "--method", "org.freedesktop.DBus.Properties.Set", "org.a11y.Status", "IsEnabled", "<true>"]
    onExited: daemon.running = true
  }

  Process {
    id: daemon
    command: ["python3", root.loop + "/loop/oad.py"]
    stderr: SplitParser { onRead: line => console.warn("accessibility-voice: " + line) }
    onExited: again.start()
  }

  Timer { id: again; interval: 5000; onTriggered: daemon.running = true }
}

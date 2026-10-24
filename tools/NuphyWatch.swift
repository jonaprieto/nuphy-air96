// NuPhy Air96 menu bar app: shows what tools/watch.py reports and sends it the menu clicks.
//
//     nuphy-watch REPO      (make watch builds it and starts it at login)
//
// watch.py prints one JSON object per line, {"title": ..., "menu": [...]}, where a menu
// entry is {"title", "cmd"?, "checked"?, "items"?} or {"sep": true}; a click writes its
// cmd back as one line on watch.py's stdin.
import Cocoa

final class Watch: NSObject, NSApplicationDelegate {
    let repo: String
    let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    var helper: Process?
    var toHelper: FileHandle?
    var buffer = Data()

    init(repo: String) {
        self.repo = repo
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        item.button?.image = NSImage(systemSymbolName: "keyboard", accessibilityDescription: "NuPhy Air96")
        item.button?.imagePosition = .imageLeading
        show(["title": "\u{2013}", "menu": [["title": "Starting..."]]])
        start()
    }

    // Restarts watch.py if it ever exits, so the menu bar item lives as long as the app.
    func start() {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: repo + "/.venv/bin/python")
        p.arguments = [repo + "/tools/watch.py"]
        let out = Pipe(), inp = Pipe()
        p.standardOutput = out
        p.standardInput = inp
        out.fileHandleForReading.readabilityHandler = { [weak self] h in
            let data = h.availableData
            DispatchQueue.main.async { self?.received(data) }
        }
        p.terminationHandler = { [weak self] _ in
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) { self?.start() }
        }
        do {
            try p.run()
            helper = p
            toHelper = inp.fileHandleForWriting
        } catch {
            show(["title": "!", "menu": [["title": "Cannot start \(repo)/tools/watch.py: \(error)"]]])
        }
    }

    func received(_ data: Data) {
        buffer.append(data)
        while let nl = buffer.firstIndex(of: 0x0A) {
            let line = buffer[buffer.startIndex..<nl]
            buffer.removeSubrange(buffer.startIndex...nl)
            if let state = try? JSONSerialization.jsonObject(with: line) as? [String: Any] {
                show(state)
            }
        }
    }

    func show(_ state: [String: Any]) {
        item.button?.title = " " + (state["title"] as? String ?? "")
        let menu = build(state["menu"] as? [[String: Any]] ?? [])
        menu.addItem(.separator())
        menu.addItem(withTitle: "Quit NuPhy Watch", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "")
        item.menu = menu
    }

    func build(_ entries: [[String: Any]]) -> NSMenu {
        let menu = NSMenu()
        menu.autoenablesItems = false
        for e in entries {
            if e["sep"] as? Bool == true {
                menu.addItem(.separator())
                continue
            }
            let mi = NSMenuItem(title: e["title"] as? String ?? "", action: nil, keyEquivalent: "")
            if let cmd = e["cmd"] as? String {
                mi.action = #selector(clicked(_:))
                mi.target = self
                mi.representedObject = cmd
            }
            mi.state = e["checked"] as? Bool == true ? .on : .off
            if let sub = e["items"] as? [[String: Any]] {
                mi.submenu = build(sub)
            }
            menu.addItem(mi)
        }
        return menu
    }

    @objc func clicked(_ sender: NSMenuItem) {
        guard let cmd = sender.representedObject as? String else { return }
        toHelper?.write((cmd + "\n").data(using: .utf8)!)
    }

    func applicationWillTerminate(_ notification: Notification) {
        helper?.terminationHandler = nil
        helper?.terminate()
    }
}

let repo = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : FileManager.default.currentDirectoryPath
let app = NSApplication.shared
app.setActivationPolicy(.accessory)  // menu bar only, no Dock icon
let watch = Watch(repo: repo)
app.delegate = watch
app.run()

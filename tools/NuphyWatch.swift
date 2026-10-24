// NuPhy Air96 menu bar app: shows what tools/watch.py reports and sends it the menu clicks.
//
//     nuphy-watch REPO      (make watch builds it and starts it at login)
//
// watch.py prints one JSON object per line, {"title": ..., "menu": [...]}, where a menu
// entry is {"title", "cmd"?, "checked"?, "items"?} or {"sep": true}; a click writes its
// cmd back as one line on watch.py's stdin.
//
// It also types the math layer's symbols: the board sends math key i as F13 + i % 8 with
// modifier set i / 8 (plus Shift for the second symbol, see keymap.c), and the symbol
// comes from tools/math_keys.json. Typing needs Accessibility access, asked for once.
import Carbon
import Cocoa

// macOS key codes of F13-F20, and keymap.c's math_mods in Carbon terms.
let fKeys: [UInt32] = [105, 107, 113, 106, 64, 79, 80, 90]
let modSets: [Int] = [controlKey, optionKey, cmdKey, controlKey | optionKey, controlKey | cmdKey, optionKey | cmdKey]
var symbols: [[String]] = []

func type(_ text: String) {
    var units = Array(text.utf16)
    for down in [true, false] {
        guard let e = CGEvent(keyboardEventSource: nil, virtualKey: 0, keyDown: down) else { return }
        e.flags = []  // the board may still hold the shortcut's modifiers
        e.keyboardSetUnicodeString(stringLength: units.count, unicodeString: &units)
        e.post(tap: .cgSessionEventTap)
    }
}

func registerMathShortcuts(repo: String) {
    guard let data = FileManager.default.contents(atPath: repo + "/tools/math_keys.json"),
          let table = try? JSONSerialization.jsonObject(with: data) as? [[String]] else { return }
    symbols = table
    var spec = EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyPressed))
    InstallEventHandler(GetApplicationEventTarget(), { _, event, _ in
        var id = EventHotKeyID()
        GetEventParameter(event, EventParamName(kEventParamDirectObject), EventParamType(typeEventHotKeyID),
                          nil, MemoryLayout<EventHotKeyID>.size, nil, &id)
        let i = Int(id.id) / 2, second = Int(id.id) % 2
        if i < symbols.count { type(symbols[i][second]) }
        return noErr
    }, 1, &spec, nil, nil)
    for i in 0..<min(symbols.count, fKeys.count * modSets.count) {
        for second in 0...1 {
            var ref: EventHotKeyRef?
            let mods = UInt32(modSets[i / fKeys.count] | (second == 1 ? shiftKey : 0))
            RegisterEventHotKey(fKeys[i % fKeys.count], mods, EventHotKeyID(signature: OSType(0x4E555048), id: UInt32(i * 2 + second)),
                                GetApplicationEventTarget(), 0, &ref)
        }
    }
}

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
        registerMathShortcuts(repo: repo)
        // asks once; until granted, math symbols do nothing (LaTeX and everything else work)
        AXIsProcessTrustedWithOptions([kAXTrustedCheckOptionPrompt.takeUnretainedValue(): true] as CFDictionary)
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
        if !AXIsProcessTrusted() {
            menu.insertItem(.separator(), at: 0)
            menu.insertItem(withTitle: "Math symbols need Accessibility access: System Settings > Privacy & Security > Accessibility",
                            action: nil, keyEquivalent: "", at: 0)
        }
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

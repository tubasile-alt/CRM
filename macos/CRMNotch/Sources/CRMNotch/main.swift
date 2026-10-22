import AppKit
import WebKit

private enum NotchSize {
    static let compact = NSSize(width: 360, height: 38)
    static let expandedWidth: CGFloat = 410
    static let login = NSSize(width: 460, height: 650)

    static func expanded(patientCount: Int) -> NSSize {
        let rows = CGFloat(max(patientCount, 1)) * 62
        return NSSize(width: expandedWidth, height: min(520, 118 + rows))
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate, WKScriptMessageHandler, WKNavigationDelegate {
    private let defaultsKey = "crmBaseURL"
    private var window: NSWindow!
    private var webView: WKWebView!
    private var statusItem: NSStatusItem!
    private var baseURL: URL!

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        baseURL = configuredBaseURL()
        buildWebView()
        buildWindow()
        buildMenuBarItem()
        loadNotch()
        window.orderFrontRegardless()

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(screenConfigurationChanged),
            name: NSApplication.didChangeScreenParametersNotification,
            object: nil
        )
    }

    private func configuredBaseURL() -> URL {
        let arguments = CommandLine.arguments
        if let index = arguments.firstIndex(of: "--url"), arguments.indices.contains(index + 1),
           let url = normalizedURL(arguments[index + 1]) {
            UserDefaults.standard.set(url.absoluteString, forKey: defaultsKey)
            return url
        }

        if let environmentURL = ProcessInfo.processInfo.environment["CRM_BASE_URL"],
           let url = normalizedURL(environmentURL) {
            return url
        }

        if let stored = UserDefaults.standard.string(forKey: defaultsKey),
           let url = normalizedURL(stored) {
            return url
        }

        return URL(string: "http://127.0.0.1:5000")!
    }

    private func normalizedURL(_ value: String) -> URL? {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        let candidate = trimmed.contains("://") ? trimmed : "https://\(trimmed)"
        guard var components = URLComponents(string: candidate), components.host != nil else { return nil }
        components.path = components.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        return components.url
    }

    private func buildWebView() {
        let controller = WKUserContentController()
        controller.add(self, name: "notch")
        let configuration = WKWebViewConfiguration()
        configuration.userContentController = controller
        configuration.websiteDataStore = .default()

        webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = self
        webView.setValue(false, forKey: "drawsBackground")
    }

    private func buildWindow() {
        window = NSWindow(
            contentRect: NSRect(origin: .zero, size: NotchSize.compact),
            styleMask: [.borderless, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        window.contentView = webView
        window.isOpaque = false
        window.backgroundColor = .clear
        window.hasShadow = false
        window.level = NSWindow.Level(rawValue: NSWindow.Level.statusBar.rawValue + 1)
        window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary]
        window.isMovable = false
        window.isReleasedWhenClosed = false
        positionWindow(size: NotchSize.compact, animated: false)
    }

    private func buildMenuBarItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        statusItem.button?.image = NSImage(systemSymbolName: "person.2.fill", accessibilityDescription: "Sala de espera")

        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Mostrar sala de espera", action: #selector(showWindow), keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: "Atualizar", action: #selector(reload), keyEquivalent: "r"))
        menu.addItem(.separator())
        menu.addItem(NSMenuItem(title: "Configurar endereço do CRM…", action: #selector(configureCRM), keyEquivalent: ","))
        menu.addItem(.separator())
        menu.addItem(NSMenuItem(title: "Encerrar CRM Notch", action: #selector(quit), keyEquivalent: "q"))
        menu.items.forEach { $0.target = self }
        statusItem.menu = menu
    }

    private func loadNotch() {
        let url = baseURL.appendingPathComponent("espera/notch")
        webView.load(URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData))
    }

    private func positionWindow(size: NSSize, animated: Bool) {
        let screen = window?.screen ?? NSScreen.main ?? NSScreen.screens.first!
        let frame = screen.frame
        let origin = NSPoint(x: frame.midX - size.width / 2, y: frame.maxY - size.height)
        let target = NSRect(origin: origin, size: size)
        window.setFrame(target, display: true, animate: animated)
    }

    @objc private func showWindow() {
        window.orderFrontRegardless()
        webView.evaluateJavaScript("document.body.classList.contains('is-expanded') || document.getElementById('toggle')?.click()")
    }

    @objc private func reload() { loadNotch() }
    @objc private func quit() { NSApp.terminate(nil) }
    @objc private func screenConfigurationChanged() { positionWindow(size: window.frame.size, animated: false) }

    @objc private func configureCRM() {
        NSApp.activate(ignoringOtherApps: true)
        let alert = NSAlert()
        alert.messageText = "Endereço do CRM"
        alert.informativeText = "Informe o endereço usado para abrir o CRM no navegador."
        alert.addButton(withTitle: "Salvar")
        alert.addButton(withTitle: "Cancelar")
        let field = NSTextField(string: baseURL.absoluteString)
        field.placeholderString = "https://crm.exemplo.com"
        field.frame = NSRect(x: 0, y: 0, width: 360, height: 24)
        alert.accessoryView = field

        guard alert.runModal() == .alertFirstButtonReturn, let url = normalizedURL(field.stringValue) else { return }
        baseURL = url
        UserDefaults.standard.set(url.absoluteString, forKey: defaultsKey)
        webView.configuration.websiteDataStore.httpCookieStore.getAllCookies { cookies in
            cookies.forEach { self.webView.configuration.websiteDataStore.httpCookieStore.delete($0) }
        }
        loadNotch()
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "notch", let payload = message.body as? [String: Any],
              let type = payload["type"] as? String else { return }

        switch type {
        case "resize":
            let expanded = payload["expanded"] as? Bool ?? false
            let count = payload["count"] as? Int ?? 0
            positionWindow(size: expanded ? NotchSize.expanded(patientCount: count) : NotchSize.compact, animated: true)
        case "open":
            guard let path = payload["path"] as? String,
                  let url = URL(string: path, relativeTo: baseURL)?.absoluteURL else { return }
            NSWorkspace.shared.open(url)
        default:
            break
        }
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        guard let url = webView.url else { return }
        if url.path == "/login" {
            NSApp.activate(ignoringOtherApps: true)
            window.makeKeyAndOrderFront(nil)
            positionWindow(size: NotchSize.login, animated: true)
        } else if url.path == "/espera/notch" {
            positionWindow(size: NotchSize.compact, animated: true)
            window.orderFrontRegardless()
        }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        showConnectionError(error)
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        showConnectionError(error)
    }

    private func showConnectionError(_ error: Error) {
        let escaped = error.localizedDescription
            .replacingOccurrences(of: "&", with: "&amp;")
            .replacingOccurrences(of: "<", with: "&lt;")
            .replacingOccurrences(of: ">", with: "&gt;")
        let html = """
        <style>body{margin:0;background:#0a0a0b;color:white;font:12px -apple-system;text-align:center}main{padding:12px 18px 18px}b{display:block;margin-bottom:5px}span{color:#999}</style>
        <main><b>CRM indisponível</b><span>\(escaped)</span></main>
        """
        webView.loadHTMLString(html, baseURL: nil)
        positionWindow(size: NSSize(width: 360, height: 82), animated: true)
    }
}

let application = NSApplication.shared
let delegate = AppDelegate()
application.delegate = delegate
application.run()

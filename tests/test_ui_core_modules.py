"""
Core ES modules of the web UI (web/js/core/, WP-E2 Track 1).

Each test runs a small ES module script in Node that imports the real files
under web/js/core/ and prints a JSON result. DOM-dependent behaviour runs
against a minimal fake DOM (FAKE_DOM below); test_overlay_and_html_in_real_browser
repeats the keyboard and XSS checks in headless Chromium when Playwright's
browser is installed.

Covers: html`` auto-escaping (SEC-08 / UI-07), OverlayStack (UI-07),
ToastManager de-duplication, MatrixWebSocket backoff and reconnects (UI-09),
MatrixApi / MatrixState, and that `npm run lint:js` passes.

Needs Node >= 20 on PATH (skipped otherwise); the lint and browser tests also
need `npm ci` to have been run.
"""

import json
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "web" / "js" / "core"
NODE = shutil.which("node")
NPM = shutil.which("npm")

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is not installed")

# A just-enough DOM: elements with attributes, a parent/child tree, focus and
# class lookups, on top of Node's own EventTarget/Event.
FAKE_DOM = r"""
class FakeElement extends EventTarget {
    constructor(doc, tag = 'div', { focusable = false, className = '' } = {}) {
        super();
        this.ownerDocument = doc;
        this.tagName = tag.toUpperCase();
        this.focusable = focusable;
        this.className = className;
        this.attrs = new Map();
        this.children = [];
        this.parentNode = null;
        this.hidden = false;
        this.innerHTML = '';
        this.textContent = '';
        const self = this;
        this.classList = {
            contains: (c) => self.className.split(/\s+/).includes(c),
            add: (c) => { if (!self.classList.contains(c)) self.className = `${self.className} ${c}`.trim(); },
        };
    }
    get isConnected() {
        for (let n = this; n; n = n.parentNode) if (n === this.ownerDocument.body) return true;
        return false;
    }
    setAttribute(n, v) { this.attrs.set(n, String(v)); }
    getAttribute(n) { return this.attrs.has(n) ? this.attrs.get(n) : null; }
    hasAttribute(n) { return this.attrs.has(n); }
    removeAttribute(n) { this.attrs.delete(n); }
    appendChild(c) { c.parentNode = this; this.children.push(c); return c; }
    remove() {
        if (!this.parentNode) return;
        this.parentNode.children = this.parentNode.children.filter((c) => c !== this);
        this.parentNode = null;
    }
    after(node) {
        const p = this.parentNode;
        node.parentNode = p;
        p.children.splice(p.children.indexOf(this) + 1, 0, node);
    }
    contains(el) {
        for (let n = el; n; n = n.parentNode) if (n === this) return true;
        return false;
    }
    closest() { return null; }
    focus() { this.ownerDocument.activeElement = this; }
    descendants() { return this.children.flatMap((c) => [c, ...c.descendants()]); }
    querySelectorAll() { return this.descendants().filter((e) => e.focusable); }
    querySelector(sel) {
        if (sel.startsWith('.')) return this.descendants().find((e) => e.classList.contains(sel.slice(1))) || null;
        return this.querySelectorAll()[0] || null;
    }
}
class FakeDocument extends EventTarget {
    constructor() {
        super();
        this.body = new FakeElement(this, 'body');
        this.activeElement = this.body;
        this.visibilityState = 'visible';
    }
    createElement(tag) { return new FakeElement(this, tag); }
    getElementById(id) { return this.body.descendants().find((e) => e.getAttribute('id') === id) || null; }
    el(opts, parent = this.body) { return parent.appendChild(new FakeElement(this, 'div', opts)); }
}
function key(name, extra = {}) {
    return Object.assign(new Event('keydown', { cancelable: true }), { key: name, shiftKey: false }, extra);
}
/** Manual timers: run them with fire(); records every delay. */
function fakeTimers() {
    let next = 1;
    const pending = new Map();
    const t = {
        delays: [], cleared: [], pending,
        setTimeout(fn, ms) { const id = next++; pending.set(id, fn); t.delays.push(ms); return id; },
        clearTimeout(id) { if (pending.delete(id)) t.cleared.push(id); },
        setInterval() { return next++; },
        clearInterval() {},
        fire() { const [[id, fn]] = pending; pending.delete(id); fn(); },
    };
    return t;
}
"""


def run_node(tmp_path: Path, body: str, *, dom: bool = False, timeout: float = 60) -> dict:
    """Run an ES module snippet; it must end with `out(<json-able result>)`."""
    script = tmp_path / "check.mjs"
    prelude = f"const CORE = {json.dumps(CORE.as_uri())};\nconst out = (v) => console.log(JSON.stringify(v));\n"
    script.write_text(prelude + (FAKE_DOM if dom else "") + textwrap.dedent(body), encoding="utf-8")
    proc = subprocess.run(
        [NODE, str(script)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=timeout
    )
    assert proc.returncode == 0, f"node failed:\n{proc.stdout}\n{proc.stderr}"
    return json.loads(proc.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------- html.js


def test_html_escapes_script_tags(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { html } = await import(CORE + '/html.js');
        out(String(html`<p>${'<script>alert(1)</script>'}</p>`));
        """,
    )
    assert r == "<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>"


def test_html_escapes_quotes_in_attributes(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { html } = await import(CORE + '/html.js');
        out([
            String(html`<a title="${'x" onmouseover="alert(1)'}">`),
            String(html`<a title='${"x' onmouseover='alert(1)"}'>`),
            String(html`${'Tom & Jerry'}`),
        ]);
        """,
    )
    assert r[0] == '<a title="x&quot; onmouseover=&quot;alert(1)">'
    assert r[1] == "<a title='x&#39; onmouseover=&#39;alert(1)'>"
    assert r[2] == "Tom &amp; Jerry"


def test_html_escapes_arrays_and_nests_templates(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { html } = await import(CORE + '/html.js');
        const names = ['<b>A</b>', 'B & C'];
        out([
            String(html`<ul>${names}</ul>`),
            String(html`<ul>${names.map((n) => html`<li>${n}</li>`)}</ul>`),
            String(html`${[['<i>', ['"']], 1]}`),
        ]);
        """,
    )
    assert r[0] == "<ul>&lt;b&gt;A&lt;/b&gt;B &amp; C</ul>"
    assert r[1] == "<ul><li>&lt;b&gt;A&lt;/b&gt;</li><li>B &amp; C</li></ul>"
    assert r[2] == "&lt;i&gt;&quot;1"


def test_html_raw_is_trusted_but_lookalikes_are_not(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { html, raw, isRaw } = await import(CORE + '/html.js');
        const forged = JSON.parse('{"__rawHtml": "<img src=x onerror=alert(1)>"}');
        out({
            raw: String(html`<div>${raw('<svg class="icon"></svg>')}</div>`),
            rawNull: raw(null).__rawHtml,
            forged: String(html`<div>${forged}</div>`),
            forgedIsRaw: isRaw(forged),
            rawIsRaw: isRaw(raw('x')),
            templateIsRaw: isRaw(html`x`),
        });
        """,
    )
    assert r["raw"] == '<div><svg class="icon"></svg></div>'
    assert r["rawNull"] == ""
    assert "<img" not in r["forged"]
    assert r["forged"] == "<div>[object Object]</div>"
    assert r["forgedIsRaw"] is False
    assert r["rawIsRaw"] is True
    assert r["templateIsRaw"] is True


def test_html_empty_values_and_escape_helper(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { html, escapeHtml } = await import(CORE + '/html.js');
        out({
            empty: String(html`[${null}${undefined}${false}]`),
            zero: String(html`${0}${true}`),
            escape: escapeHtml(`&<>"'`),
            escapeNull: escapeHtml(null),
            noDouble: escapeHtml('&amp;'),
        });
        """,
    )
    assert r["empty"] == "[]"
    assert r["zero"] == "0true"
    assert r["escape"] == "&amp;&lt;&gt;&quot;&#39;"
    assert r["escapeNull"] == ""
    assert r["noDouble"] == "&amp;amp;"


def test_html_exposed_to_classic_scripts(tmp_path):
    r = run_node(
        tmp_path,
        """
        globalThis.window = {};
        const m = await import(CORE + '/html.js');
        const o = window.OrcaHtml;
        out({
            same: o.html === m.html && o.raw === m.raw && o.escapeHtml === m.escapeHtml,
            frozen: Object.isFrozen(o),
            works: String(o.html`${'<x>'}`),
        });
        """,
    )
    assert r == {"same": True, "frozen": True, "works": "&lt;x&gt;"}


# ------------------------------------------------------------- overlay.js


def test_overlay_push_pop_peek_size(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { OverlayStack } = await import(CORE + '/overlay.js');
        const doc = new FakeDocument();
        const s = new OverlayStack({ document: doc });
        const log = [];
        s.push({ id: 'drawer', onClose: (r) => log.push(['drawer', r]) });
        s.push({ id: 'modal', onClose: (r) => log.push(['modal', r]) });
        s.push({ id: 'picker', onClose: (r) => log.push(['picker', r]) });
        const sizes = [s.size, s.peek().id];
        s.push({ id: 'modal', onClose: (r) => log.push(['modal', r]) }); // re-push moves to top
        const reordered = [s.size, s.peek().id];
        const popped = s.pop('picker').id; // pop by id never calls onClose
        const missing = s.pop('nope');
        const top = s.closeTop();
        const rest = s.closeAll('route');
        out({ sizes, reordered, popped, missing, top: top.id, rest: rest.map((e) => e.id), log, size: s.size,
              peek: s.peek(), emptyPop: s.pop() });
        """,
        dom=True,
    )
    assert r["sizes"] == [3, "picker"]
    assert r["reordered"] == [3, "modal"]
    assert r["popped"] == "picker"
    assert r["missing"] is None
    assert r["top"] == "modal"
    assert r["rest"] == ["drawer"]
    assert r["log"] == [["modal", "programmatic"], ["drawer", "route"]]
    assert r["size"] == 0 and r["peek"] is None and r["emptyPop"] is None


def test_overlay_escape_closes_only_the_top(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { OverlayStack } = await import(CORE + '/overlay.js');
        const doc = new FakeDocument();
        const s = new OverlayStack({ document: doc });
        const closed = [];
        const drawerEl = doc.el();
        const modalEl = doc.el();
        s.push({ id: 'drawer', element: drawerEl, onClose: (r) => closed.push(['drawer', r]) });
        s.push({ id: 'modal', element: modalEl, onClose: (r) => closed.push(['modal', r]) });
        // A classic drawer's own Escape handler, registered after the stack's.
        let drawerHandlerRan = 0;
        doc.addEventListener('keydown', (e) => { if (e.key === 'Escape') drawerHandlerRan++; });

        const e1 = key('Escape');
        doc.dispatchEvent(e1);
        const afterFirst = { closed: [...closed], size: s.size, top: s.peek()?.id,
                             prevented: e1.defaultPrevented, drawerHandlerRan };
        const e2 = key('Escape');
        doc.dispatchEvent(e2);
        const afterSecond = { closed: [...closed], size: s.size, drawerHandlerRan };
        doc.dispatchEvent(key('Escape')); // stack empty: the page's own handlers run
        out({ afterFirst, afterSecond, finalDrawerHandlerRan: drawerHandlerRan });
        """,
        dom=True,
    )
    assert r["afterFirst"] == {
        "closed": [["modal", "escape"]],
        "size": 1,
        "top": "drawer",
        "prevented": True,
        "drawerHandlerRan": 0,
    }
    assert r["afterSecond"] == {"closed": [["modal", "escape"], ["drawer", "escape"]], "size": 0, "drawerHandlerRan": 0}
    assert r["finalDrawerHandlerRan"] == 1


def test_overlay_escape_respects_close_on_escape_false(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { OverlayStack } = await import(CORE + '/overlay.js');
        const doc = new FakeDocument();
        const s = new OverlayStack({ document: doc });
        s.push({ id: 'drawer' });
        s.push({ id: 'busy', closeOnEscape: false });
        const e = key('Escape');
        doc.dispatchEvent(e);
        out({ size: s.size, top: s.peek().id, prevented: e.defaultPrevented });
        """,
        dom=True,
    )
    assert r == {"size": 2, "top": "busy", "prevented": False}


def test_overlay_sets_and_restores_dialog_aria(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { OverlayStack } = await import(CORE + '/overlay.js');
        const doc = new FakeDocument();
        const s = new OverlayStack({ document: doc });
        const plain = doc.el();
        const alert = doc.el();
        alert.setAttribute('role', 'alertdialog');
        alert.setAttribute('aria-modal', 'false');
        s.push({ id: 'a', element: plain });
        s.push({ id: 'b', element: alert });
        const open = [plain.getAttribute('role'), plain.getAttribute('aria-modal'),
                      alert.getAttribute('role'), alert.getAttribute('aria-modal')];
        s.closeAll();
        const closed = [plain.getAttribute('role'), plain.getAttribute('aria-modal'),
                        alert.getAttribute('role'), alert.getAttribute('aria-modal')];
        out({ open, closed });
        """,
        dom=True,
    )
    assert r["open"] == ["dialog", "true", "alertdialog", "true"]
    assert r["closed"] == [None, None, "alertdialog", "false"]


def test_overlay_restores_focus_to_trigger(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { OverlayStack } = await import(CORE + '/overlay.js');
        const doc = new FakeDocument();
        const s = new OverlayStack({ document: doc });
        const trigger = doc.el({ focusable: true });
        const drawer = doc.el();
        const drawerBtn = doc.el({ focusable: true }, drawer);
        const modal = doc.el();
        const modalInput = doc.el({ focusable: true }, modal);
        const id = (el) => [trigger, drawerBtn, modalInput, modal, drawer].indexOf(el);

        trigger.focus();
        s.push({ id: 'drawer', element: drawer });
        const inDrawer = id(doc.activeElement);
        s.push({ id: 'modal', element: modal });
        const inModal = id(doc.activeElement);
        doc.dispatchEvent(key('Escape'));
        const backInDrawer = id(doc.activeElement);
        doc.dispatchEvent(key('Escape'));
        const backOnTrigger = id(doc.activeElement);

        // Explicit triggerElement wins over document.activeElement.
        drawerBtn.focus();
        s.push({ id: 'x', element: modal, triggerElement: trigger });
        s.pop('x');
        const explicit = id(doc.activeElement);

        // Focus the user moved elsewhere is not stolen back.
        s.push({ id: 'y', element: modal, triggerElement: trigger });
        drawerBtn.focus();
        s.pop('y');
        const notStolen = id(doc.activeElement);

        // A trigger that left the DOM is not focused.
        const gone = doc.el({ focusable: true });
        gone.focus();
        s.push({ id: 'z', element: modal });
        gone.remove();
        s.pop('z');
        out({ inDrawer, inModal, backInDrawer, backOnTrigger, explicit, notStolen, goneFocused: doc.activeElement === gone });
        """,
        dom=True,
    )
    assert r == {
        "inDrawer": 1,
        "inModal": 2,
        "backInDrawer": 1,
        "backOnTrigger": 0,
        "explicit": 0,
        "notStolen": 1,
        "goneFocused": False,
    }


def test_overlay_traps_tab_in_top_overlay(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { OverlayStack } = await import(CORE + '/overlay.js');
        const doc = new FakeDocument();
        const s = new OverlayStack({ document: doc });
        const drawer = doc.el();
        doc.el({ focusable: true }, drawer);
        const modal = doc.el();
        const first = doc.el({ focusable: true }, modal);
        const middle = doc.el({ focusable: true }, modal);
        const last = doc.el({ focusable: true }, modal);
        const id = (el) => [first, middle, last].indexOf(el);
        s.push({ id: 'drawer', element: drawer });
        s.push({ id: 'modal', element: modal });

        const results = [];
        last.focus();
        let e = key('Tab'); doc.dispatchEvent(e); results.push([id(doc.activeElement), e.defaultPrevented]);
        e = key('Tab', { shiftKey: true }); doc.dispatchEvent(e); results.push([id(doc.activeElement), e.defaultPrevented]);
        middle.focus();
        e = key('Tab'); doc.dispatchEvent(e); results.push([id(doc.activeElement), e.defaultPrevented]); // browser moves it
        doc.body.focus(); // focus escaped the overlay
        e = key('Tab'); doc.dispatchEvent(e); results.push([id(doc.activeElement), e.defaultPrevented]);

        const empty = doc.el();
        s.push({ id: 'empty', element: empty });
        e = key('Tab'); doc.dispatchEvent(e);
        out({ results, emptyHoldsFocus: doc.activeElement === empty && e.defaultPrevented,
              emptyTabindex: empty.getAttribute('tabindex') });
        """,
        dom=True,
    )
    assert r["results"] == [[0, True], [2, True], [1, False], [0, True]]
    assert r["emptyHoldsFocus"] is True
    assert r["emptyTabindex"] == "-1"


def test_overlay_listens_only_while_open_and_is_global(tmp_path):
    r = run_node(
        tmp_path,
        """
        const doc = new FakeDocument();
        globalThis.document = doc;
        globalThis.window = {};
        const added = [], removed = [];
        const add = doc.addEventListener.bind(doc), rem = doc.removeEventListener.bind(doc);
        doc.addEventListener = (...a) => { added.push(a[0]); add(...a); };
        doc.removeEventListener = (...a) => { removed.push(a[0]); rem(...a); };
        const { overlayStack, OverlayStack } = await import(CORE + '/overlay.js');
        const before = added.length;
        overlayStack.push({ id: 'a' });
        overlayStack.push({ id: 'b' });
        overlayStack.closeAll();
        out({ global: window.overlayStack === overlayStack, isClass: overlayStack instanceof OverlayStack,
              before, added, removed });
        """,
        dom=True,
    )
    assert r["global"] is True and r["isClass"] is True
    assert r["before"] == 0
    assert r["added"] == ["keydown"]
    assert r["removed"] == ["keydown"]


# --------------------------------------------------------------- toast.js


def test_toast_coalesces_duplicates_with_counter(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { ToastManager } = await import(CORE + '/toast.js');
        const doc = new FakeDocument();
        const container = doc.el();
        container.setAttribute('id', 'toast-container');
        const timers = fakeTimers();
        const t = new ToastManager({ document: doc, timers });
        const a = t.show('Route failed', 'error');
        const b = t.show('Route failed', 'error');
        const c = t.error('Route failed');
        const other = t.show('Route failed', 'warning');
        const badge = a.querySelector('.toast-count');
        out({
            same: a === b && b === c,
            toasts: container.children.length,
            count: t.count('Route failed', 'error'),
            badge: badge && badge.textContent,
            badgeLabel: badge && badge.getAttribute('aria-label'),
            otherIsNew: other !== a,
            otherCount: t.count('Route failed', 'warning'),
            markup: a.innerHTML.includes('Route failed'),
        });
        """,
        dom=True,
    )
    assert r == {
        "same": True,
        "toasts": 2,
        "count": 3,
        "badge": "×3",
        "badgeLabel": "shown 3 times",
        "otherIsNew": True,
        "otherCount": 1,
        "markup": True,
    }


def test_toast_duplicate_restarts_timer_and_dismissal_resets(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { ToastManager } = await import(CORE + '/toast.js');
        const doc = new FakeDocument();
        const container = doc.el();
        const timers = fakeTimers();
        const t = new ToastManager({ document: doc, container, timers });
        const a = t.show('Saved', 'success', 3000);
        t.show('Saved', 'success', 3000);
        const pendingAfterRepeat = timers.pending.size;
        const clearedOnRepeat = timers.cleared.length;
        timers.fire(); // the restarted timer dismisses the toast
        const afterTimeout = { connected: a.isConnected, count: t.count('Saved', 'success') };
        const b = t.show('Saved', 'success');
        b.remove(); // dismissed by something else (e.g. a click on the classic Toast)
        const c = t.show('Saved', 'success');
        out({ pendingAfterRepeat, clearedOnRepeat, afterTimeout, newAfterTimeout: b !== a,
              newAfterRemoval: c !== b, countAfterRemoval: t.count('Saved', 'success') });
        """,
        dom=True,
    )
    assert r == {
        "pendingAfterRepeat": 1,
        "clearedOnRepeat": 1,
        "afterTimeout": {"connected": False, "count": 0},
        "newAfterTimeout": True,
        "newAfterRemoval": True,
        "countAfterRemoval": 1,
    }


def test_toast_escapes_message_and_bridges_to_window_toast(tmp_path):
    r = run_node(
        tmp_path,
        """
        const doc = new FakeDocument();
        globalThis.document = doc;
        const shown = [], dismissed = [];
        globalThis.window = {
            toast: {
                show(message, type, duration) {
                    shown.push([message, type, duration]);
                    const el = doc.el({ className: `toast ${type}` });
                    doc.el({ className: 'toast-message' }, el);
                    return el;
                },
                dismiss(el) { dismissed.push(el); el.remove(); },
            },
        };
        const { toast, ToastManager } = await import(CORE + '/toast.js');
        const el = toast.show('<img src=x onerror=alert(1)>', 'info');
        toast.show('<img src=x onerror=alert(1)>', 'info');
        const badgeAfterMessage = el.children[1]?.className;
        toast.dismissAll();

        const container = doc.el();
        const standalone = new ToastManager({ document: doc, container });
        const s = standalone.show('<b>hi</b>', 'info', 0);
        out({ shown, dismissed: dismissed.length, badgeAfterMessage, standaloneHtml: s.innerHTML });
        """,
        dom=True,
    )
    assert r["shown"] == [["<img src=x onerror=alert(1)>", "info", 0]]  # rendered once, delegate never auto-dismisses
    assert r["dismissed"] == 1
    assert r["badgeAfterMessage"] == "toast-count"
    assert "&lt;b&gt;hi&lt;/b&gt;" in r["standaloneHtml"]
    assert "<b>" not in r["standaloneHtml"]


# ------------------------------------------------------------------ ws.js

FAKE_SOCKET = r"""
const sockets = [];
class FakeSocket {
    constructor(url) { this.url = url; this.readyState = 0; this.sent = []; sockets.push(this); }
    send(d) { this.sent.push(JSON.parse(d)); }
    close() { this.readyState = 3; this.onclose?.({ code: 1000 }); }
    open() { this.readyState = 1; this.onopen?.(); }
    fail() { this.readyState = 3; this.onclose?.({ code: 1006 }); }
}
"""


def test_ws_backoff_is_capped_at_30_seconds(tmp_path):
    r = run_node(
        tmp_path,
        FAKE_SOCKET
        + """
        const { MatrixWebSocket, MAX_RECONNECT_DELAY_MS } = await import(CORE + '/ws.js');
        const timers = fakeTimers();
        const reconnecting = [];
        const w = new MatrixWebSocket({ url: 'ws://hub/ws', WebSocketImpl: FakeSocket, timers,
                                        maxDelay: 120000, onReconnecting: (i) => reconnecting.push(i) });
        w.connect();
        for (let i = 0; i < 9; i++) { sockets.at(-1).fail(); timers.fire(); }
        out({
            cap: MAX_RECONNECT_DELAY_MS,
            maxDelay: w.maxDelay,
            delays: timers.delays,
            attempts: reconnecting.map((i) => i.attempt),
            static: [1, 2, 6, 7, 50].map((n) => MatrixWebSocket.backoffDelay(n, 1000, 999999)),
        });
        """,
        dom=True,
    )
    assert r["cap"] == 30000
    assert r["maxDelay"] == 30000
    assert r["delays"] == [1000, 2000, 4000, 8000, 16000, 30000, 30000, 30000, 30000]
    assert r["attempts"] == list(range(1, 10))
    assert r["static"] == [1000, 2000, 30000, 30000, 30000]


def test_ws_keeps_a_single_pending_reconnect_timer(tmp_path):
    r = run_node(
        tmp_path,
        FAKE_SOCKET
        + """
        const { MatrixWebSocket } = await import(CORE + '/ws.js');
        const timers = fakeTimers();
        const w = new MatrixWebSocket({ url: 'ws://hub/ws', WebSocketImpl: FakeSocket, timers });
        w.connect();
        sockets[0].fail();
        w.scheduleReconnect();
        w.scheduleReconnect();
        const pending = timers.pending.size;
        const cleared = timers.cleared.length;
        w.disconnect();
        out({ pending, cleared, afterDisconnect: timers.pending.size, timer: w.reconnectTimer,
              scheduleWhenStopped: (w.scheduleReconnect(), timers.pending.size) });
        """,
        dom=True,
    )
    assert r == {"pending": 1, "cleared": 2, "afterDisconnect": 0, "timer": None, "scheduleWhenStopped": 0}


def test_ws_reconnects_immediately_on_visible_and_online(tmp_path):
    r = run_node(
        tmp_path,
        FAKE_SOCKET
        + """
        const doc = new FakeDocument();
        globalThis.document = doc;
        globalThis.window = new EventTarget();
        const { MatrixWebSocket } = await import(CORE + '/ws.js');
        const timers = fakeTimers();
        const w = new MatrixWebSocket({ url: 'ws://hub/ws', WebSocketImpl: FakeSocket, timers });
        w.connect();
        for (let i = 0; i < 4; i++) { sockets.at(-1).fail(); timers.fire(); }
        sockets.at(-1).fail(); // now waiting 16 s
        const waiting = { pending: timers.pending.size, sockets: sockets.length };

        doc.visibilityState = 'hidden';
        doc.dispatchEvent(new Event('visibilitychange'));
        const whileHidden = { pending: timers.pending.size, sockets: sockets.length };

        doc.visibilityState = 'visible';
        doc.dispatchEvent(new Event('visibilitychange'));
        const onVisible = { pending: timers.pending.size, sockets: sockets.length, delay: w.reconnectDelay };

        sockets.at(-1).fail();
        const nextDelay = timers.delays.at(-1);
        window.dispatchEvent(new Event('online'));
        const onOnline = { pending: timers.pending.size, sockets: sockets.length };

        sockets.at(-1).open();
        window.dispatchEvent(new Event('online')); // connected: nothing to do
        const whenConnected = sockets.length;
        w.disconnect();
        window.dispatchEvent(new Event('online')); // listeners are removed on disconnect
        out({ waiting, whileHidden, onVisible, nextDelay, onOnline, whenConnected, afterDisconnect: sockets.length });
        """,
        dom=True,
    )
    assert r["waiting"] == {"pending": 1, "sockets": 5}
    assert r["whileHidden"] == {"pending": 1, "sockets": 5}
    assert r["onVisible"] == {"pending": 0, "sockets": 6, "delay": 1000}
    assert r["nextDelay"] == 1000  # backoff restarted
    assert r["onOnline"] == {"pending": 0, "sockets": 7}
    assert r["whenConnected"] == 7
    assert r["afterDisconnect"] == 7


def test_ws_resyncs_on_reconnect_and_passes_messages(tmp_path):
    r = run_node(
        tmp_path,
        FAKE_SOCKET
        + """
        const { MatrixWebSocket } = await import(CORE + '/ws.js');
        const timers = fakeTimers();
        const resyncs = [], messages = [], statuses = [];
        const w = new MatrixWebSocket({ url: 'ws://hub/ws', WebSocketImpl: FakeSocket, timers,
            onResync: (i) => resyncs.push(i), onMessage: (m) => messages.push(m),
            onStatusChange: (c) => statuses.push(c) });
        w.connect();
        sockets[0].open();
        const firstConnect = resyncs.length;
        sockets[0].onmessage({ data: JSON.stringify({ event: 'route_changed', data: { output: 1, input: 2 } }) });
        sockets[0].onmessage({ data: JSON.stringify({ event: 'pong' }) });
        sockets[0].onmessage({ data: 'not json' });
        sockets[0].fail();
        timers.fire();
        sockets[1].fail();
        timers.fire();
        sockets[2].open();
        // A late event from a replaced socket is ignored.
        sockets[0].onmessage({ data: JSON.stringify({ event: 'stale', data: {} }) });
        const sent = w.requestStatus();
        out({ firstConnect, resyncs, messages, statuses, sent, lastSent: sockets[2].sent.at(-1),
              status: w.status, attempts: w.reconnectAttempts });
        """,
        dom=True,
    )
    assert r["firstConnect"] == 0
    assert r["resyncs"] == [{"attempts": 2}]
    assert r["messages"] == [{"type": "route_changed", "data": {"output": 1, "input": 2}}]
    assert r["statuses"] == [True, False, True]
    assert r["sent"] is True
    assert r["lastSent"] == {"command": "get_status"}
    assert r["status"] == "connected"
    assert r["attempts"] == 0


# ----------------------------------------------------------------- api.js


def test_api_sends_key_and_dispatches_auth_required(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { MatrixApi, ApiError } = await import(CORE + '/api.js');
        const calls = [];
        const answers = {
            '/api/status': { status: 200, body: { success: true } },
            '/api/routing': { status: 401, body: { error: 'unauthorized' } },
            '/api/admin': { status: 403, body: { code: 'admin_pin_required' } },
            '/api/missing': { status: 404, body: { error: 'not_found' } },
        };
        const fetch = async (url, init) => {
            calls.push({ url, method: init.method, headers: init.headers, body: init.body });
            const a = answers[new URL(url).pathname];
            return { ok: a.status < 300, status: a.status, text: async () => JSON.stringify(a.body) };
        };
        const target = new EventTarget();
        const auth = [];
        target.addEventListener('auth:required', (e) => auth.push(e.detail));
        const api = new MatrixApi({ baseUrl: 'http://hub', apiKey: 'k-123', fetch, eventTarget: target });
        const ok = await api.get('/api/status');
        const errs = [];
        for (const [m, p] of [['post', '/api/routing'], ['put', '/api/admin'], ['get', '/api/missing']]) {
            try { await api[m](p, m === 'get' ? undefined : { output: 1 }); }
            catch (e) { errs.push({ isApiError: e instanceof ApiError, status: e.status, code: e.code, level: e.level ?? null }); }
        }
        api.setApiKey(null);
        await api.get('/api/status');
        out({ ok, calls, errs, auth });
        """,
    )
    assert r["ok"] == {"success": True}
    assert r["calls"][0]["headers"]["X-API-Key"] == "k-123"
    assert r["calls"][1]["method"] == "POST"
    assert r["calls"][1]["headers"]["Content-Type"] == "application/json"
    assert json.loads(r["calls"][1]["body"]) == {"output": 1}
    assert "X-API-Key" not in r["calls"][-1]["headers"]
    assert r["errs"] == [
        {"isApiError": True, "status": 401, "code": "unauthorized", "level": None},
        {"isApiError": True, "status": 403, "code": "admin_pin_required", "level": "admin"},
        {"isApiError": True, "status": 404, "code": "not_found", "level": None},
    ]
    assert r["auth"] == [
        {"status": 401, "code": "unauthorized", "method": "POST", "path": "/api/routing"},
        {"status": 403, "code": "admin_pin_required", "level": "admin", "method": "PUT", "path": "/api/admin"},
    ]


def test_api_timeout_and_window_delegation(tmp_path):
    r = run_node(
        tmp_path,
        """
        class LegacyApiError extends Error {
            constructor(message, fields = {}) { super(message); Object.assign(this, fields); }
        }
        const legacyApi = { legacy: true };
        globalThis.window = { api: legacyApi, ApiError: LegacyApiError, location: { origin: 'http://page' } };
        const { MatrixApi, ApiError, api } = await import(CORE + '/api.js');
        const hang = (url, init) => new Promise((_, reject) =>
            init.signal.addEventListener('abort', () => reject(Object.assign(new Error('aborted'), { name: 'AbortError' }))));
        const client = new MatrixApi({ fetch: hang, timeout: 20 });
        let err;
        try { await client.get('/api/slow'); } catch (e) { err = e; }
        const net = new MatrixApi({ fetch: async () => { throw new TypeError('Failed to fetch'); } });
        let netErr;
        try { await net.get('/api/x'); } catch (e) { netErr = e; }
        out({ delegated: api === legacyApi, sharedError: ApiError === LegacyApiError, baseUrl: client.baseUrl,
              timeout: { legacyClass: err instanceof LegacyApiError, code: err.code, status: err.status },
              network: netErr.code });
        """,
    )
    assert r == {
        "delegated": True,
        "sharedError": True,
        "baseUrl": "http://page",
        "timeout": {"legacyClass": True, "code": "timeout", "status": 0},
        "network": "network",
    }


# --------------------------------------------------------------- state.js


def test_state_store_standalone_and_bridged(tmp_path):
    r = run_node(
        tmp_path,
        """
        const { MatrixState } = await import(CORE + '/state.js');
        const s = new MatrixState();
        const log = [];
        const h = (v, prev) => log.push(['routing', v, prev]);
        const unsub = s.on('change:routing', h);
        s.on('change', (c) => log.push(['change', c.key]));
        const changed = s.set('routing', { 1: 2 });
        const same = s.set('connected', undefined); // no change
        unsub();
        s.set('routing', { 1: 3 });
        s.on('custom', h);
        s.off('custom', h);
        s.emit('custom', 1);

        // Bridged to an AppState-like object (web/js/state.js).
        const listeners = new Map();
        const appState = {
            routing: { 1: 1 },
            on(ev, cb) { (listeners.get(ev) || listeners.set(ev, new Set()).get(ev)).add(cb);
                         return () => listeners.get(ev).delete(cb); },
            emit(ev, d) { listeners.get(ev)?.forEach((cb) => cb(d)); },
        };
        const b = new MatrixState({ target: appState });
        const seen = [];
        const fn = (d) => seen.push(d);
        b.on('routing', fn);
        appState.emit('routing', 'from-classic');
        b.emit('routing', 'from-module');
        b.set('wsConnected', true);
        b.off('routing', fn);
        appState.emit('routing', 'after-off');
        out({ log, changed, same, bridged: b.bridged, get: b.get('routing'), written: appState.wsConnected,
              seen, remaining: listeners.get('routing').size });
        """,
    )
    assert r["log"] == [["routing", {"1": 2}, None], ["change", "routing"], ["change", "routing"]]
    assert r["changed"] is True and r["same"] is False
    assert r["bridged"] is True
    assert r["get"] == {"1": 1}
    assert r["written"] is True
    assert r["seen"] == ["from-classic", "from-module"]
    assert r["remaining"] == 0


# ----------------------------------------------------------------- index.js


def test_index_reexports_everything(tmp_path):
    r = run_node(
        tmp_path,
        """
        const m = await import(CORE + '/index.js');
        const parts = await Promise.all(['html', 'api', 'ws', 'state', 'overlay', 'toast']
            .map((n) => import(`${CORE}/${n}.js`)));
        const names = ['html', 'raw', 'escapeHtml', 'MatrixApi', 'ApiError', 'api', 'MatrixWebSocket', 'ws',
                       'MatrixState', 'state', 'OverlayStack', 'overlayStack', 'ToastManager', 'toast'];
        out({ missing: names.filter((n) => m[n] === undefined),
              sameObjects: names.every((n) => parts.some((p) => p[n] === m[n])),
              wsInstance: m.ws instanceof m.MatrixWebSocket, wsIdle: m.ws.ws === null });
        """,
    )
    assert r == {"missing": [], "sameObjects": True, "wsInstance": True, "wsIdle": True}


# --------------------------------------------------------- real browser


BROWSER_CHECK = r"""
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const { chromium } = await import(process.argv[3]);
const webRoot = path.resolve(process.argv[2]);
const server = http.createServer((req, res) => {
    if (req.url === '/') {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(`<!doctype html><button id="trigger">open</button>
            <div id="drawer"><button id="d1">d1</button></div>
            <div id="modal"><input id="m1"><button id="m2">m2</button></div>
            <div id="out"></div>
            <script type="module">
                import * as core from '/js/core/index.js';
                window.core = core;
                window.closeLog = [];
                document.addEventListener('keydown', (e) => { if (e.key === 'Escape') window.closeLog.push('page'); });
                window.ready = true;
            </script>`);
        return;
    }
    const file = path.resolve(webRoot, '.' + decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!file.startsWith(webRoot + path.sep) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': 'text/javascript' });
    res.end(fs.readFileSync(file));
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const browser = await chromium.launch();
try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('response', (r) => { if (r.status() !== 200) errors.push(`${r.status()} ${r.url()}`); });
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.waitForFunction(() => window.ready, null, { timeout: 10000 }).catch((e) => { throw new Error(`${e.message} ${errors}`); });
    const result = {};
    result.globals = await page.evaluate(() => window.OrcaHtml?.html === window.core.html && window.overlayStack === window.core.overlayStack);
    result.xss = await page.evaluate(async () => {
        const out = document.getElementById('out');
        out.innerHTML = window.core.html`<p title="${'"><img src=x onerror="window.pwned=1">'}">${'<img src=x onerror="window.pwned=1">'}</p>`;
        await new Promise((r) => setTimeout(r, 200));
        return { pwned: window.pwned === 1, imgs: out.querySelectorAll('img').length, text: out.textContent };
    });
    await page.focus('#trigger');
    await page.evaluate(() => {
        const s = window.core.overlayStack;
        s.push({ id: 'drawer', element: document.getElementById('drawer'), onClose: () => window.closeLog.push('drawer') });
        s.push({ id: 'modal', element: document.getElementById('modal'), onClose: () => window.closeLog.push('modal') });
    });
    const active = () => page.evaluate(() => document.activeElement.id);
    result.openFocus = await active();
    result.aria = await page.evaluate(() => [document.getElementById('modal').getAttribute('role'),
                                              document.getElementById('modal').getAttribute('aria-modal')]);
    const tabs = [];
    for (const k of ['Tab', 'Tab', 'Shift+Tab', 'Shift+Tab']) { await page.keyboard.press(k); tabs.push(await active()); }
    result.tabs = tabs;
    await page.keyboard.press('Escape');
    result.afterEsc1 = { closed: await page.evaluate(() => [...window.closeLog]), size: await page.evaluate(() => window.core.overlayStack.size), focus: await active() };
    await page.keyboard.press('Escape');
    result.afterEsc2 = { closed: await page.evaluate(() => [...window.closeLog]), focus: await active() };
    await page.keyboard.press('Escape');
    result.afterEsc3 = await page.evaluate(() => [...window.closeLog]);
    result.errors = errors;
    console.log(JSON.stringify(result));
} finally {
    await browser.close();
    server.close();
}
"""


def test_overlay_and_html_in_real_browser(tmp_path):
    if not (ROOT / "node_modules" / "@playwright" / "test").exists():
        pytest.skip("node_modules not installed (npm ci)")
    script = tmp_path / "browser_check.mjs"
    script.write_text(BROWSER_CHECK, encoding="utf-8")
    playwright = (ROOT / "node_modules" / "@playwright" / "test" / "index.mjs").as_uri()
    proc = subprocess.run(
        [NODE, str(script), str(ROOT / "web"), playwright],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    if proc.returncode != 0 and "Executable doesn't exist" in proc.stderr:
        pytest.skip("Playwright Chromium is not installed (npx playwright install chromium)")
    assert proc.returncode == 0, f"{proc.stdout}\n{proc.stderr}"
    r = json.loads(proc.stdout.strip().splitlines()[-1])
    assert r["errors"] == []
    assert r["globals"] is True
    assert r["xss"]["pwned"] is False
    assert r["xss"]["imgs"] == 0
    assert '<img src=x onerror="window.pwned=1">' in r["xss"]["text"]
    assert r["openFocus"] == "m1"
    assert r["aria"] == ["dialog", "true"]
    assert r["tabs"] == ["m2", "m1", "m2", "m1"]  # never leaves the modal
    assert r["afterEsc1"] == {"closed": ["modal"], "size": 1, "focus": "d1"}
    assert r["afterEsc2"] == {"closed": ["modal", "drawer"], "focus": "trigger"}
    assert r["afterEsc3"] == ["modal", "drawer", "page"]  # empty stack: page handlers run again


# ------------------------------------------------------------------- lint


def test_lint_js_passes_and_core_is_linted_as_modules():
    if NPM is None or not (ROOT / "node_modules" / "eslint").exists():
        pytest.skip("npm / node_modules not installed (npm ci)")
    lint = subprocess.run([NPM, "run", "lint:js"], cwd=ROOT, capture_output=True, text=True, timeout=300)
    assert lint.returncode == 0, f"{lint.stdout}\n{lint.stderr}"

    eslint = ROOT / "node_modules" / "eslint" / "bin" / "eslint.js"
    cfg = subprocess.run(
        [NODE, str(eslint), "--print-config", "web/js/core/html.js"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert cfg.returncode == 0, cfg.stderr
    options = json.loads(cfg.stdout)["languageOptions"]
    assert options["sourceType"] == "module"
    assert "escapeHtml" not in options["globals"], "core modules must not see classic-script globals"

    report = subprocess.run(
        [NODE, str(eslint), "--format", "json", "web/js/core"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert report.returncode == 0, report.stdout
    files = json.loads(report.stdout)
    assert {Path(f["filePath"]).name for f in files} == {
        "html.js",
        "api.js",
        "ws.js",
        "state.js",
        "overlay.js",
        "toast.js",
        "index.js",
    }
    assert all(f["errorCount"] == 0 and f["warningCount"] == 0 for f in files)

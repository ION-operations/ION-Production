from pathlib import Path


PANEL_PATH = Path(__file__).resolve().parents[1] / "08_ui/joc_cockpit_shell/BrowserGptDomTwinPanel.tsx"
CSS_PATH = Path(__file__).resolve().parents[1] / "08_ui/joc_cockpit_shell/ion-runtime-cockpit.css"


def test_browser_gpt_panel_keeps_optimistic_pending_send_contract():
    source = PANEL_PATH.read_text(encoding="utf-8")

    assert "const beginOptimisticSend = (textToSend: string)" in source
    assert "optimistic_kind: 'user_send'" in source
    assert "state: 'sending'" in source
    assert "const markOptimisticSent = (optimisticId: string, textToSend: string)" in source
    assert "optimistic_kind: 'assistant_pending'" in source
    assert "text_full: 'Waiting for ChatGPT response'" in source
    assert "syncOptimisticTurn(options.expectedText ?? '', syncState)" in source
    assert "state: 'received'" in source
    assert "state: 'streaming'" in source
    assert "requestVisibleConversation({ expectedText: textToSend" in source
    assert "sendStatus.includes('reply')" in source
    assert "sendStatus.includes('pending')" in source
    assert "sendStatus.includes('requested')" in source


def test_browser_gpt_panel_keeps_keyboard_and_autoscroll_contract():
    source = PANEL_PATH.read_text(encoding="utf-8")

    assert "const handleDraftKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>)" in source
    assert "event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing" in source
    assert "sendDraftToChatGpt()" in source
    assert "const handleNativeThreadScroll = ()" in source
    assert "setNativeThreadAutoScroll(distanceFromBottom < 96)" in source
    assert "bottom.scrollIntoView({ block: 'end' })" in source


def test_browser_gpt_panel_keeps_compact_status_toolbar_contract():
    source = PANEL_PATH.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")

    assert "ion-browser-gpt-native-head is-compact" in source
    assert "ion-browser-gpt-native-kpis is-compact" in source
    assert source.count("<CompactStatusChip") >= 10
    assert source.count("<CompactToolbarButton") >= 9
    assert "composerToolbar.map" in source
    assert "composerToolbarIcon(surfaceId)" in source
    assert "function CompactStatusChip" in source
    assert "function CompactToolbarButton" in source
    assert "function ToolbarStatusMark" in source
    assert "<CheckIcon />" in source
    assert "<CloseIcon />" in source
    assert "title={`${toolLabel(surfaceId, control)}" in source
    assert ".ion-browser-gpt-native-head.is-compact" in css
    assert ".ion-browser-gpt-native-kpis.is-compact" in css
    assert ".ion-browser-gpt-toolbar-status.is-ready" in css
    assert ".ion-browser-gpt-toolbar-status.is-missing" in css
    assert ".ion-browser-gpt-toolbar-status.is-watch" in css

/**
 * AIM-OS SEER — Universal DOM Spatial Mapper
 *
 * Injected on ALL pages. Extracts a spatial map of interactive DOM elements
 * with precise getBoundingClientRect() coordinates. This is SEER's primary
 * sense — reading the environment's structural skeleton instead of pixels.
 *
 * Responds to messages from background.js:
 *   SEER_GET_MAP   → returns full spatial map JSON
 *   SEER_PING      → heartbeat / presence check
 */

(() => {
    'use strict';

    // ── Config ────────────────────────────────────────────────────────

    const INTERACTIVE_SELECTORS = [
        'button', 'a[href]', 'input', 'select', 'textarea',
        '[role="button"]', '[role="link"]', '[role="tab"]',
        '[role="menuitem"]', '[role="checkbox"]', '[role="radio"]',
        '[role="switch"]', '[role="slider"]', '[role="textbox"]',
        '[contenteditable="true"]', '[onclick]', '[tabindex]',
        'summary', 'details', 'label[for]'
    ].join(', ');

    const MAX_TEXT_LENGTH = 80;
    const MAX_ELEMENTS = 500; // Safety cap

    // ── Spatial Map Extraction ────────────────────────────────────────

    function extractSpatialMap(options = {}) {
        const {
            includeHidden = false,
            viewport = getViewport(),
            selector = INTERACTIVE_SELECTORS
        } = options;

        const elements = document.querySelectorAll(selector);
        const map = [];

        let count = 0;
        for (const el of elements) {
            if (count >= MAX_ELEMENTS) break;

            const rect = el.getBoundingClientRect();

            // Skip zero-size elements (invisible)
            if (rect.width === 0 && rect.height === 0) continue;

            // Skip off-screen unless includeHidden
            const inViewport = (
                rect.bottom > 0 &&
                rect.right > 0 &&
                rect.top < viewport.height &&
                rect.left < viewport.width
            );

            if (!includeHidden && !inViewport) continue;

            // Skip truly hidden elements
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden') continue;
            if (!includeHidden && parseFloat(style.opacity) === 0) continue;

            const node = {
                idx: count,
                tag: el.tagName.toLowerCase(),
                rect: {
                    x: Math.round(rect.x),
                    y: Math.round(rect.y),
                    w: Math.round(rect.width),
                    h: Math.round(rect.height)
                },
                text: getElementText(el),
                interactable: isInteractable(el)
            };

            // Optional properties — only include if present (keeps payload small)
            if (el.id) node.id = el.id;
            if (el.ariaLabel) node.aria = el.ariaLabel;
            if (el.href) node.href = el.href;
            if (el.type) node.type = el.type;
            if (el.name) node.name = el.name;
            if (el.value && el.tagName === 'INPUT') node.value = el.value.substring(0, MAX_TEXT_LENGTH);
            if (el.placeholder) node.placeholder = el.placeholder;
            if (el.disabled) node.disabled = true;
            if (el.checked !== undefined) node.checked = el.checked;
            if (!inViewport) node.offscreen = true;

            // CSS selector path for future targeting
            node.selector = getCssSelector(el);

            map.push(node);
            count++;
        }

        return map;
    }

    function extractPageMeta() {
        return {
            url: window.location.href,
            title: document.title,
            viewport: getViewport(),
            scroll: {
                x: Math.round(window.scrollX),
                y: Math.round(window.scrollY)
            },
            docHeight: Math.round(document.documentElement.scrollHeight),
            docWidth: Math.round(document.documentElement.scrollWidth),
            timestamp: Date.now()
        };
    }

    // ── Helpers ───────────────────────────────────────────────────────

    function getViewport() {
        return {
            width: window.innerWidth,
            height: window.innerHeight
        };
    }

    function getElementText(el) {
        // Prefer aria-label, then textContent, then title, then placeholder
        const text = el.ariaLabel
            || el.textContent?.trim()
            || el.title
            || el.placeholder
            || '';
        return text.substring(0, MAX_TEXT_LENGTH);
    }

    function isInteractable(el) {
        if (el.disabled) return false;
        const style = window.getComputedStyle(el);
        if (style.pointerEvents === 'none') return false;
        const rect = el.getBoundingClientRect();
        if (rect.width < 2 || rect.height < 2) return false;
        return true;
    }

    function getCssSelector(el) {
        // Build a minimal unique selector
        if (el.id) return `#${CSS.escape(el.id)}`;

        const parts = [];
        let current = el;
        let depth = 0;

        while (current && current !== document.body && depth < 4) {
            let sel = current.tagName.toLowerCase();

            if (current.id) {
                sel = `#${CSS.escape(current.id)}`;
                parts.unshift(sel);
                break;
            }

            // Add distinguishing class if available
            const uniqueClass = Array.from(current.classList)
                .find(c => !c.startsWith('ng-') && !c.startsWith('mat-') && c.length < 30);
            if (uniqueClass) {
                sel += `.${CSS.escape(uniqueClass)}`;
            } else {
                // Use nth-child for disambiguation
                const parent = current.parentElement;
                if (parent) {
                    const siblings = Array.from(parent.children).filter(
                        c => c.tagName === current.tagName
                    );
                    if (siblings.length > 1) {
                        const idx = siblings.indexOf(current) + 1;
                        sel += `:nth-of-type(${idx})`;
                    }
                }
            }

            parts.unshift(sel);
            current = current.parentElement;
            depth++;
        }

        return parts.join(' > ');
    }

    // ── Message Listener ─────────────────────────────────────────────

    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.type === 'SEER_GET_MAP') {
            try {
                const map = extractSpatialMap(message.options || {});
                const meta = extractPageMeta();
                sendResponse({
                    success: true,
                    page: meta,
                    elements: map,
                    count: map.length
                });
            } catch (err) {
                sendResponse({
                    success: false,
                    error: err.message
                });
            }
            return true; // Keep port open for async response
        }

        if (message.type === 'SEER_PING') {
            sendResponse({
                alive: true,
                url: window.location.href,
                title: document.title,
                timestamp: Date.now()
            });
            return true;
        }
    });

    // ── SEER Indicator Badge ─────────────────────────────────────────

    function createSeerBadge() {
        // Don't show on Gemini (bridge badge is already there)
        if (window.location.hostname === 'gemini.google.com') return;

        // Don't show on chrome:// or extension pages
        if (window.location.protocol === 'chrome:' ||
            window.location.protocol === 'chrome-extension:') return;

        const badge = document.createElement('div');
        badge.id = 'seer-indicator';
        badge.innerHTML = '👁 SEER';
        badge.title = 'AIM-OS SEER — Spatial mapping active';
        document.body.appendChild(badge);

        // Pulse briefly on load to show activation
        badge.classList.add('seer-active');
        setTimeout(() => badge.classList.remove('seer-active'), 3000);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createSeerBadge);
    } else {
        createSeerBadge();
    }

    console.log(`[SEER] Spatial mapper active on ${window.location.hostname}`);
})();

from __future__ import annotations

from jarvis_injector.capture.models import BlockType, InlineSpan, InlineSpanType, MessageBlock


def spans_to_plaintext(spans: list[InlineSpan]) -> str:
    return "".join(span.text for span in spans).strip()


def spans_to_markdown(spans: list[InlineSpan]) -> str:
    chunks: list[str] = []
    for span in spans:
        if span.type == InlineSpanType.INLINE_CODE:
            chunks.append(f"`{span.text}`")
        elif span.type == InlineSpanType.LINK and span.href:
            chunks.append(f"[{span.text}]({span.href})")
        elif span.type == InlineSpanType.CITATION:
            chunks.append(f"[{span.text}]")
        else:
            chunks.append(span.text)
    return "".join(chunks).strip()


def blocks_to_plaintext(blocks: list[MessageBlock]) -> str:
    rendered = [_block_to_plaintext(block) for block in blocks]
    return "\n\n".join(chunk for chunk in rendered if chunk).strip()


def blocks_to_markdown(blocks: list[MessageBlock]) -> str:
    rendered = [_block_to_markdown(block) for block in blocks]
    return "\n\n".join(chunk for chunk in rendered if chunk).strip()


def _block_to_plaintext(block: MessageBlock) -> str:
    if block.type in {BlockType.PARAGRAPH, BlockType.QUOTE, BlockType.STATUS_LINE}:
        return block.text or spans_to_plaintext(block.spans)
    if block.type == BlockType.HEADING:
        return block.text or spans_to_plaintext(block.spans)
    if block.type == BlockType.CODE_BLOCK:
        return block.text or ""
    if block.type == BlockType.LIST:
        prefix = (lambda i: f"{i + 1}. " if block.ordered else "- ")
        return "\n".join(prefix(i) + spans_to_plaintext(item) for i, item in enumerate(block.items))
    if block.type == BlockType.TABLE:
        return "\n".join("\t".join(row) for row in block.rows)
    if block.type in {BlockType.TOOL_CALL, BlockType.TOOL_RESULT}:
        header = block.tool_name or block.type.value
        status = f" [{block.tool_status}]" if block.tool_status else ""
        body = block.text or ""
        return f"{header}{status}\n{body}".strip()
    if block.children:
        return blocks_to_plaintext(block.children)
    return block.text or spans_to_plaintext(block.spans)


def _block_to_markdown(block: MessageBlock) -> str:
    if block.type == BlockType.HEADING:
        level = max(1, min(block.level or 1, 6))
        return f"{'#' * level} {block.text or spans_to_markdown(block.spans)}".strip()
    if block.type == BlockType.PARAGRAPH:
        return block.text or spans_to_markdown(block.spans)
    if block.type == BlockType.QUOTE:
        content = block.text or spans_to_markdown(block.spans)
        return "\n".join(f"> {line}" for line in content.splitlines())
    if block.type == BlockType.STATUS_LINE:
        return f"**{block.text or spans_to_markdown(block.spans)}**".strip()
    if block.type == BlockType.CODE_BLOCK:
        language = block.language or ""
        return f"```{language}\n{block.text or ''}\n```".strip()
    if block.type == BlockType.LIST:
        prefix = (lambda i: f"{i + 1}. " if block.ordered else "- ")
        return "\n".join(prefix(i) + spans_to_markdown(item) for i, item in enumerate(block.items))
    if block.type == BlockType.TABLE:
        if not block.rows:
            return ""
        header = "| " + " | ".join(block.rows[0]) + " |"
        divider = "| " + " | ".join("---" for _ in block.rows[0]) + " |"
        rows = ["| " + " | ".join(row) + " |" for row in block.rows[1:]]
        return "\n".join([header, divider, *rows])
    if block.type in {BlockType.TOOL_CALL, BlockType.TOOL_RESULT}:
        title = block.tool_name or block.type.value
        status = f" ({block.tool_status})" if block.tool_status else ""
        body = block.text or ""
        return f"**{title}{status}**\n\n```text\n{body}\n```".strip()
    if block.children:
        return blocks_to_markdown(block.children)
    return block.text or spans_to_markdown(block.spans)


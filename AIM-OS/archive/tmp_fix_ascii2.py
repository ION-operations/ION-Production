import pathlib
files = [
    'north_star_project/chapters/03_proof/chapter.md',
    'north_star_project/chapters/03_proof/evidence.jsonl',
    'north_star_project/chapters/04_possible/chapter.md',
    'north_star_project/chapters/05_cmc/chapter.md',
    'north_star_project/chapters/06_hhni/chapter.md',
    'north_star_project/chapters/06_hhni/evidence.jsonl',
]
replacements = {
    '\u2019': "'",
    '\u2018': "'",
    '\u201c': '"',
    '\u201d': '"',
    '\u2013': '-',
    '\u2014': '--',
    '\u2011': '-',
    '\u2026': '...',
    '\u2022': '- ',
    '\u2122': ' (TM)',
    '\u00b1': '+/-',
    '\u03ba': 'k',
    '\u2192': '->',
    '\u2713': 'check',
    '\u0153': 'oe',
    '\u0131': 'i',
    '\u2020': '*',
    '\u20ac': ' EUR',
    '\u2030': ' per mille'
}
mojibake = {
    '\u00e2\u0080\u0099': "'",
    '\u00e2\u0080\u0098': "'",
    '\u00e2\u0080\u009c': '"',
    '\u00e2\u0080\u009d': '"',
    '\u00e2\u0080\u0093': '-',
    '\u00e2\u0080\u0094': '--',
    '\u00e2\u0080\u00a2': '- ',
    '\u00e2\u0080\u00a6': '...',
    '\u00ef\u00bf\u00bd': '',
}
for path_str in files:
    path = pathlib.Path(path_str)
    if not path.exists():
        continue
    data = path.read_bytes()
    text = data.decode('utf-8', errors='replace')
    for old, new in mojibake.items():
        text = text.replace(old.encode('latin1', errors='ignore').decode('latin1'), new)
    for old, new in replacements.items():
        text = text.replace(old.encode('latin1', errors='ignore').decode('latin1'), new)
    # replace by direct unicode (escape form) as well
    for old, new in replacements.items():
        text = text.replace(old.encode('utf-8', errors='ignore').decode('utf-8'), new)
    if text != data.decode('utf-8', errors='replace'):
        path.write_text(text, encoding='utf-8')

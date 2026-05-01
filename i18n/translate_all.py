#!/usr/bin/env python3
"""Translate all .ts files using Google Translate free API."""

import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# File suffix -> Google Translate target language code
LANG_MAP = {
    "fr": "fr",
    "es": "es",
    "it": "it",
    "pt": "pt",
    "br": "pt-BR",
    "nl": "nl",
    "pl": "pl",
    "ru": "ru",
    "ja": "ja",
    "zh": "zh-CN",
    "dk": "da",
    "sv": "sv",
    "fi": "fi",
    "cs": "cs",
    "sk": "sk",
    "sl": "sl",
    "bg": "bg",
    "ro": "ro",
    "el": "el",
    "he": "iw",
    "tr": "tr",
    "hu": "hu",
    "et": "et",
    "lt": "lt",
    "lv": "lv",
    "uk": "uk",
}

VERSION_RE = re.compile(r"^\d+[\.\d]*$")


def should_skip(src: str) -> bool:
    """Return True for strings that must be copied verbatim."""
    s = src.strip()
    # HTML blocks containing CSS (translating CSS property names breaks rendering)
    if s.startswith("<!DOCTYPE"):
        return True
    # Pure version/number literals used as field defaults or examples
    if VERSION_RE.match(s):
        return True
    # Ellipsis placeholder
    if s == "...":
        return True
    # Lowercase 'python' is a tag value, keep it as-is
    if s == "python":
        return True
    return False


def translate(text: str, target: str, retries: int = 3) -> str:
    url = "https://translate.googleapis.com/translate_a/single"
    params = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": target, "dt": "t", "q": text}
    )
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                f"{url}?{params}", headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            return "".join(part[0] for part in data[0] if part[0])
        except Exception as exc:
            if attempt == retries - 1:
                raise
            print(f"    Retry {attempt + 1} after error: {exc}")
            time.sleep(.3)
    return text


def process_file(ts_path: Path, target: str) -> None:
    print(f"  {ts_path.name} -> {target}", flush=True)
    tree = ET.parse(ts_path)
    root = tree.getroot()

    count = 0
    for context in root.findall("context"):
        for message in context.findall("message"):
            source = message.find("source")
            translation = message.find("translation")
            if source is None or translation is None:
                continue

            src_text = source.text or ""
            trans_text = translation.text or ""
            trans_type = translation.get("type", "")

            # Skip already-translated entries
            if trans_text and trans_type != "unfinished":
                continue

            if should_skip(src_text):
                translation.text = src_text
            else:
                try:
                    translation.text = translate(src_text, target)
                    time.sleep(0.25)
                except Exception as exc:
                    print(f"    ERROR on '{src_text[:50]}': {exc}")
                    continue

            translation.attrib.pop("type", None)
            count += 1

    tree.write(ts_path, encoding="unicode", xml_declaration=False)

    # Prepend standard XML declaration manually to match Qt Linguist format
    content = ts_path.read_text(encoding="utf-8")
    ts_path.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n' + content,
        encoding="utf-8",
    )

    print(f"    {count} strings translated", flush=True)


def main() -> None:
    i18n_dir = Path(__file__).parent

    for suffix, target in LANG_MAP.items():
        ts_file = i18n_dir / f"pluginbuilder4_{suffix}.ts"
        if not ts_file.exists():
            print(f"  Missing: {ts_file.name}")
            continue
        process_file(ts_file, target)

    print("\nDone.")


if __name__ == "__main__":
    main()

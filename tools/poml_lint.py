from __future__ import annotations

import json
import sys
from pathlib import Path

try:  # pragma: no cover - optional dependency
    from defusedxml import ElementTree as ET
except ModuleNotFoundError:  # pragma: no cover - CI fallback
    import xml.etree.ElementTree as ET  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "prompts"


def validate_prompt(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [f"{path.name}: invalid XML ({exc})"]

    root = tree.getroot()
    template = root.find("template")
    output = root.find("output")
    if template is None or not (template.text or "").strip():
        errors.append(f"{path.name}: missing <template> text")
    if output is None or not (output.text or "").strip():
        errors.append(f"{path.name}: missing <output> text")
    else:
        try:
            json.loads(output.text)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: output block must contain valid JSON ({exc})")

    for var in root.findall("./variables/var"):
        if not var.attrib.get("name"):
            errors.append(f"{path.name}: <var> missing name attribute")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(PROMPT_DIR.glob("*.poml")):
        errors.extend(validate_prompt(path))
    if errors:
        for err in errors:
            print(err)
        return 1
    print("All prompts valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

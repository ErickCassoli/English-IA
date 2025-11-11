from __future__ import annotations

import json
from pathlib import Path

from defusedxml import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"


def lint_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [f"{path.name}: XML parse error {exc}"]
    root = tree.getroot()
    template = root.find("template")
    output = root.find("output")
    if template is None or not (template.text or "").strip():
        errors.append(f"{path.name}: template block is missing or empty")
    if output is None or not (output.text or "").strip():
        errors.append(f"{path.name}: output block is missing or empty")
    else:
        try:
            json.loads(output.text)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid JSON contract ({exc})")
    for var in root.findall("./variables/var"):
        if not var.attrib.get("name"):
            errors.append(f"{path.name}: found <var> without name attribute")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(PROMPTS_DIR.glob("*.poml")):
        errors.extend(lint_file(path))
    if errors:
        for err in errors:
            print(err)
        return 1
    print("All POML files look good.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

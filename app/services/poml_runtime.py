from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from defusedxml import ElementTree as ET

from app.utils.logger import get_logger

log = get_logger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[2]
PROMPTS_DIR = ROOT_DIR / "prompts"


@dataclass
class PromptTemplate:
    name: str
    template: str
    variables: dict[str, dict[str, Any]]
    output_contract: str

    def render(self, data: dict[str, Any]) -> str:
        rendered = self.template
        for name, meta in self.variables.items():
            value = data.get(name) if data.get(name) is not None else meta.get("default", "")
            if meta.get("required", False) and (value is None or str(value).strip() == ""):
                raise ValueError(f"Missing required prompt variable '{name}' for '{self.name}'")
            rendered = rendered.replace(f"{{{{{name}}}}}", str(value))
        return rendered.strip() + "\n"


@lru_cache(maxsize=32)
def load_prompt(name: str) -> PromptTemplate:
    path = PROMPTS_DIR / f"{name}.poml"
    if not path.exists():
        raise FileNotFoundError(f"Prompt {name} not found at {path}")

    tree = ET.parse(path)
    root = tree.getroot()
    template_node = root.find("template")
    output_node = root.find("output")
    variable_nodes = root.findall("./variables/var")

    variables: dict[str, dict[str, Any]] = {}
    for node in variable_nodes:
        var_name = node.attrib.get("name")
        if not var_name:
            raise ValueError(f"Prompt {name} has a variable without a name attribute")
        variables[var_name] = {
            "required": node.attrib.get("required", "true").lower() == "true",
            "default": node.attrib.get("default"),
        }

    template = (template_node.text or "").strip()
    output_contract = (output_node.text or "").strip() if output_node is not None else "{}"
    return PromptTemplate(
        name=name,
        template=template,
        variables=variables,
        output_contract=output_contract,
    )


def render_prompt(name: str, variables: dict[str, Any]) -> str:
    prompt = load_prompt(name)
    log.debug("rendering prompt", extra={"prompt": name})
    return prompt.render(variables)

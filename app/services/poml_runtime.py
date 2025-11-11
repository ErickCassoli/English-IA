from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from defusedxml import ElementTree as ET

from app.utils.logger import get_logger

log = get_logger(__name__)
PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


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
            if meta.get("required", True) and (value is None or str(value).strip() == ""):
                raise ValueError(f"Missing required prompt variable '{name}' for '{self.name}'")
            rendered = rendered.replace(f"{{{{{name}}}}}", str(value))
        return rendered.strip()


@lru_cache(maxsize=16)
def load_prompt(name: str) -> PromptTemplate:
    path = PROMPTS_DIR / f"{name}.poml"
    if not path.exists():
        raise FileNotFoundError(f"Prompt {name} not found at {path}")
    tree = ET.parse(path)
    root = tree.getroot()
    template_node = root.find("template")
    output_node = root.find("output")
    variable_nodes = root.findall("./variables/var")
    if template_node is None or (template_node.text or "").strip() == "":
        raise ValueError(f"Prompt {name} is missing a <template> block")
    if output_node is None or (output_node.text or "").strip() == "":
        raise ValueError(f"Prompt {name} is missing an <output> block")
    variables: dict[str, dict[str, Any]] = {}
    for node in variable_nodes:
        var_name = node.attrib.get("name")
        if not var_name:
            raise ValueError(f"Prompt {name} has a <var> without a name attribute")
        variables[var_name] = {
            "required": node.attrib.get("required", "true").lower() == "true",
            "default": node.attrib.get("default"),
        }
    return PromptTemplate(
        name=name,
        template=(template_node.text or "").strip(),
        variables=variables,
        output_contract=(output_node.text or "{}").strip(),
    )


def render_prompt(name: str, variables: dict[str, Any]) -> str:
    prompt = load_prompt(name)
    log.debug("rendering prompt", extra={"trace_id": variables.get("trace_id", "poml"), "prompt": name})
    return prompt.render(variables)

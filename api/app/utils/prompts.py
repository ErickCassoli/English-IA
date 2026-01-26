from __future__ import annotations
import re
from pathlib import Path
from typing import Any

class PomlParser:
    def __init__(self):
        pass

    def load(self, path: Path, variables: dict[str, Any] | None = None) -> str:
        """Loads a POML file and returns the rendered template string."""
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
            
        content = path.read_text(encoding="utf-8")
        
        # Extract template content (CDATA or inner text of <template>)
        template_match = re.search(r"<template>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</template>", content, re.DOTALL)
        if not template_match:
             # Fallback: treat whole file as template if no tags found (legacy support)
             if "<prompt" not in content:
                 return content
             raise ValueError(f"Invalid POML: No <template> tag found in {path.name}")
        
        template = template_match.group(1).strip()
        
        # Apply variable substitution if provided
        if variables:
            for key, value in variables.items():
                # Simple substitution {{key}}
                template = template.replace(f"{{{{{key}}}}}", str(value))
                
        return template

poml = PomlParser()

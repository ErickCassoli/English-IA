# Prompt Orchestration Markup Language (POML)

POML is a small XML dialect used by English IA to make prompts explicit, versionable, and testable.

## Anatomy of a POML File

```xml
<prompt id="chat-correct" version="1.0">
  <meta>
    <description>Human-readable summary</description>
  </meta>
  <variables>
    <var name="message" required="true" />
    <var name="learner_level" required="false" default="B1" />
  </variables>
  <template><![CDATA[
System / instructions with {{placeholders}}.
  ]]></template>
  <output><![CDATA[
{
  "contract": "expressed as JSON"
}
  ]]></output>
</prompt>
```

- `<variables>` entries declare the `name`, whether it is `required`, and an optional `default`.
- `<template>` contains the actual instructions and placeholders. Rendering is naive string substitution via `app/services/poml_runtime.py` to keep prompts deterministic.
- `<output>` includes canonical JSON that `tools/poml_lint.py` validates and `docs` can reference.

## Prompt Contracts

### Chat Correct (`prompts/chat-correct.poml`)

```json
{
  "corrected": "string",
  "explanation": "string",
  "highlights": [
    {"from_index": 0, "to_index": 0, "note": "string"}
  ],
  "tags": ["string"]
}
```

### Quiz Generator (`prompts/quiz-gen.poml`)

```json
{
  "questions": [
    {
      "id": "string",
      "prompt": "string",
      "options": ["string"],
      "answer": "string",
      "rationale": "string"
    }
  ]
}
```

### Flashcard Generator (`prompts/flashcard-gen.poml`)

```json
{
  "flashcards": [
    {
      "id": "string",
      "front": "string",
      "back": "string",
      "tag": "string"
    }
  ]
}
```

### Call Coach (`prompts/call-coach.poml`)

```json
{
  "reply": "string",
  "tips": ["string"],
  "focus_tags": ["string"]
}
```

## Linting

`tools/poml_lint.py` enumerates every `.poml` file, ensures valid XML, validates that all `<var>` elements contain names, and confirms the `<output>` block is parseable JSON. The lint job runs in `.github/workflows/poml-lint.yml`.

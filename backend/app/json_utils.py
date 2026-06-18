import json
import re
from typing import Any


class JSONExtractionError(ValueError):
    pass


def extract_json_payload(text: str) -> Any:
    normalized = text.strip()

    choice_text = _extract_choice_text(normalized)
    if choice_text is not None:
        return extract_json_payload(choice_text)

    for source in _candidate_sources(normalized):
        for candidate in _candidate_json_strings(source):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                repaired = _escape_unquoted_string_quotes(candidate)
                if repaired != candidate:
                    try:
                        return json.loads(repaired)
                    except json.JSONDecodeError:
                        continue
                continue

    raise JSONExtractionError("模型返回内容不是有效 JSON")


def _candidate_sources(text: str) -> list[str]:
    sources = [
        _strip_closed_thinking(text).strip(),
        _text_after_last_closed_thinking(text).strip(),
        text,
    ]
    result: list[str] = []
    seen: set[str] = set()
    for source in sources:
        if source and source not in seen:
            result.append(source)
            seen.add(source)
    return result


def _strip_closed_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)


def _text_after_last_closed_thinking(text: str) -> str:
    match = list(re.finditer(r"</think>", text, flags=re.IGNORECASE))
    if not match:
        return text
    return text[match[-1].end() :]


def _extract_choice_text(text: str) -> str | None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return None

    message = first_choice.get("message")
    candidates: list[Any] = []
    if isinstance(message, dict):
        candidates.append(message.get("content"))
        candidates.append(message.get("reasoning_content"))

    candidates.append(first_choice.get("text"))
    candidates.append(first_choice.get("content"))

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate

    return None


def _candidate_json_strings(text: str) -> list[str]:
    candidates = [text]
    fence_matches = re.findall(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    candidates.extend(match.strip() for match in reversed(fence_matches))

    for opener, closer in (("{", "}"), ("[", "]")):
        candidates.extend(reversed(_balanced_blocks(text, opener, closer)))

    return [candidate for candidate in candidates if candidate]


def _balanced_blocks(text: str, opener: str, closer: str) -> list[str]:
    blocks: list[str] = []
    depth = 0
    in_string = False
    escape = False
    start: int | None = None

    for index, char in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == opener:
            if depth == 0:
                start = index
            depth += 1
        elif char == closer:
            if depth == 0:
                continue
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(text[start : index + 1])
                start = None

    return blocks


def _escape_unquoted_string_quotes(text: str) -> str:
    result: list[str] = []
    in_string = False
    escape = False

    for index, char in enumerate(text):
        if not in_string:
            result.append(char)
            if char == '"':
                in_string = True
            continue

        if escape:
            result.append(char)
            escape = False
            continue

        if char == "\\":
            result.append(char)
            escape = True
            continue

        if char == '"':
            next_char = _next_non_whitespace(text, index + 1)
            if next_char in {":", ",", "}", "]", None}:
                result.append(char)
                in_string = False
            else:
                result.append('\\"')
            continue

        result.append(char)

    return "".join(result)


def _next_non_whitespace(text: str, start: int) -> str | None:
    for char in text[start:]:
        if not char.isspace():
            return char
    return None

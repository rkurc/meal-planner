"""Strip pasted HTML and pull schema.org Recipe JSON-LD. Stdlib only."""

import json
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

_JSONLD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)

_HTML_HINT_RE = re.compile(
    r"<\s*(html|body|script|div|article|h1|head|!doctype)\b",
    re.IGNORECASE,
)

_SKIP_TAGS = frozenset({"script", "style", "nav", "footer", "noscript", "svg", "head"})

_ALREADY_NUMBERED = re.compile(r"^\s*\d+[\.\)]\s+")


def looks_like_html(text: str) -> bool:
    """True when the paste looks like markup rather than a plain recipe."""
    if not text or not str(text).strip():
        return False
    stripped = str(text).lstrip()
    lower = stripped[:32].lower()
    if lower.startswith("<!doctype") or lower.startswith("<html"):
        return True
    return bool(_HTML_HINT_RE.search(stripped))


class _VisibleTextParser(HTMLParser):
    """Collect visible text, skipping script/style/nav/footer/head."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._skip_stack: List[str] = []
        self._parts: List[str] = []

    def error(self, message):
        # html.parser.ParserBase declares this abstract on some Python 3.9 builds.
        raise RuntimeError(message)

    def handle_starttag(self, tag, attrs):  # pylint: disable=unused-argument
        if tag in _SKIP_TAGS:
            self._skip_stack.append(tag)

    def handle_endtag(self, tag):
        if self._skip_stack and tag == self._skip_stack[-1]:
            self._skip_stack.pop()

    def handle_data(self, data):
        if self._skip_stack:
            return
        text = data.strip()
        if text:
            self._parts.append(text)

    def text(self) -> str:
        return "\n".join(self._parts)


def extract_visible_text(text: str) -> str:
    """Return readable text. HTML drops script/nav/footer; plain text is unchanged."""
    raw = text if text is not None else ""
    if not looks_like_html(raw):
        return raw.strip()
    parser = _VisibleTextParser()
    try:
        parser.feed(raw)
        parser.close()
    except (ValueError, TypeError):
        return raw.strip()
    visible = parser.text().strip()
    return visible if visible else raw.strip()


def _as_type_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _is_recipe_type(node: Dict[str, Any]) -> bool:
    types = _as_type_list(node.get("@type"))
    return any(item.rsplit("/", 1)[-1].lower() == "recipe" for item in types)


def _walk_nodes(obj: Any) -> List[Dict[str, Any]]:
    found: List[Dict[str, Any]] = []
    if isinstance(obj, dict):
        if _is_recipe_type(obj):
            found.append(obj)
        for key, val in obj.items():
            if key == "@context":
                continue
            if isinstance(val, (dict, list)):
                found.extend(_walk_nodes(val))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_walk_nodes(item))
    return found


def _loads_jsonld(raw: str) -> Optional[Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = re.sub(r"^\s*//.*$", "", raw, flags=re.MULTILINE)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None


def extract_jsonld_recipe(html: str) -> Optional[Dict[str, Any]]:
    """First schema.org Recipe object in application/ld+json scripts, if any."""
    if not html:
        return None
    for match in _JSONLD_RE.finditer(html):
        data = _loads_jsonld(match.group(1).strip())
        if data is None:
            continue
        recipes = _walk_nodes(data)
        if recipes:
            return recipes[0]
    return None


def textish(value: Any) -> str:  # pylint: disable=too-many-return-statements
    """Flatten schema.org text / HowToStep / list values to a string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = [textish(item) for item in value]
        return "\n".join(part for part in parts if part)
    if not isinstance(value, dict):
        return str(value).strip()
    nested = value.get("itemListElement")
    if nested is not None:
        return textish(nested)
    for key in ("text", "name", "description", "@value"):
        if key in value:
            return textish(value[key])
    return ""


def jsonld_instructions(node: Dict[str, Any]) -> str:
    """Join recipeInstructions into a newline-separated, numbered string."""
    raw = node.get("recipeInstructions")
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if not isinstance(raw, list):
        return textish(raw)
    steps: List[str] = []
    for item in raw:
        if isinstance(item, dict) and item.get("itemListElement") is not None:
            nested = item.get("itemListElement")
            elements = nested if isinstance(nested, list) else [nested]
            for sub in elements:
                subtext = textish(sub)
                if subtext:
                    steps.append(subtext)
            continue
        text = textish(item)
        if text:
            steps.append(text)
    numbered: List[str] = []
    for index, step in enumerate(steps, start=1):
        stripped = step.strip()
        if _ALREADY_NUMBERED.match(stripped):
            numbered.append(stripped)
        else:
            numbered.append(f"{index}. {stripped}")
    return "\n".join(numbered)


def jsonld_ingredient_lines(node: Dict[str, Any]) -> List[str]:
    raw = node.get("recipeIngredient")
    if raw is None:
        raw = node.get("ingredients")
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = [raw]
    lines: List[str] = []
    for item in raw:
        text = textish(item)
        if text:
            lines.append(text)
    return lines


def jsonld_partial(node: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic fields from a Recipe JSON-LD node (ingredients still lines)."""
    return {
        "name": textish(node.get("name")),
        "description": textish(node.get("description")),
        "instructions": jsonld_instructions(node),
        "ingredient_lines": jsonld_ingredient_lines(node),
    }

from __future__ import annotations

from typing import TYPE_CHECKING

import nh3
from bs4 import BeautifulSoup, NavigableString

if TYPE_CHECKING:
    from app.models.annotation import Annotation

_ALLOWED_TAGS = frozenset(
    {
        "p",
        "br",
        "b",
        "strong",
        "i",
        "em",
        "u",
        "span",
        "mark",
        "h1",
        "h2",
        "h3",
        "ul",
        "ol",
        "li",
        "a",
        "blockquote",
        "code",
        "pre",
    }
)

_ATTRIBUTES = {
    "span": {"class", "data-annotation-id", "data-annotation-type", "role", "tabindex"},
    "a": {"href", "rel", "target", "class"},
    "mark": {"class"},
}


def _iter_text_nodes(soup: BeautifulSoup):
    for node in soup.descendants:
        if (
            isinstance(node, NavigableString)
            and node.parent
            and node.parent.name
            not in (
                "script",
                "style",
            )
        ):
            yield node


def _build_plain_mapping(soup: BeautifulSoup) -> list[tuple[NavigableString, int]]:
    mapping: list[tuple[NavigableString, int]] = []
    for text_node in _iter_text_nodes(soup):
        chunk = str(text_node)
        for i in range(len(chunk)):
            mapping.append((text_node, i))
    return mapping


def plain_text_length(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return len(_build_plain_mapping(soup))


def slice_plain_text(html: str, start: int, end: int) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    m = _build_plain_mapping(soup)
    if start < 0 or end > len(m) or start > end:
        raise ValueError("Offsets out of range for plain text extraction.")
    return "".join(str(m[i][0])[m[i][1] : m[i][1] + 1] for i in range(start, end))


def offsets_use_single_text_node(html: str, start: int, end: int) -> bool:
    if start >= end:
        return True
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    m = _build_plain_mapping(soup)
    if end > len(m) or start < 0:
        return False
    first = m[start][0]
    last = m[end - 1][0]
    return first is last


def _wrap_single_text_node(
    soup: BeautifulSoup,
    start: int,
    end: int,
    attrs: dict[str, str],
) -> None:
    mapping = _build_plain_mapping(soup)
    if start < 0 or end > len(mapping) or start >= end:
        raise ValueError("Invalid annotation span.")
    n0, i0 = mapping[start]
    n1, i1 = mapping[end - 1]
    if n0 is not n1:
        raise ValueError("Annotation spans multiple DOM text nodes.")
    text = str(n0)
    before = text[:i0]
    middle = text[i0 : i1 + 1]
    after = text[i1 + 1 :]
    span = soup.new_tag("span", attrs=attrs)
    span.append(NavigableString(middle))
    if before:
        before_node = NavigableString(before)
        n0.replace_with(before_node)
        before_node.insert_after(span)
    else:
        n0.replace_with(span)
    if after:
        span.insert_after(NavigableString(after))


def build_interactive_html(raw_html: str, annotations: list[Annotation]) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    for ann in sorted(annotations, key=lambda a: a.start_offset, reverse=True):
        attrs = {
            "class": "anno-term",
            "data-annotation-id": str(ann.id),
            "data-annotation-type": ann.annotation_type,
            "role": "button",
            "tabindex": "0",
        }
        try:
            _wrap_single_text_node(soup, ann.start_offset, ann.end_offset, attrs)
        except ValueError:
            continue

    dirty = str(soup)
    return nh3.clean(
        dirty,
        tags=_ALLOWED_TAGS,
        attributes=_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        link_rel=None,
    )

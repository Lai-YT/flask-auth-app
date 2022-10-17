from __future__ import annotations
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple

from flask import template_rendered
from jinja2 import Template

if TYPE_CHECKING:
    from flask import Flask


@contextmanager
def captured_templates(app: Flask) -> Generator[List[Tuple[Template, Dict[str, Any]]], None, None]:
    records: List[Tuple[Template, Dict[str, Any]]] = []

    def record(sender: Flask, template: Template, context: Dict, **extra) -> None:
        records.append((template, context))

    template_rendered.connect(sender=app, receiver=record)
    try:
        yield records
    finally:
        template_rendered.disconnect(sender=app, receiver=record)

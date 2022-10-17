from __future__ import annotations
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple

from flask import message_flashed, template_rendered
from jinja2 import Template

if TYPE_CHECKING:
    from flask import Flask


@contextmanager
def captured_flash_messages(app: Flask) -> Generator[List[Tuple[str, str]], None, None]:
    records: List[Tuple[str, str]] = []

    def record(sender: Flask, message: str, category: str, **extra) -> None:
        records.append((message, category))

    message_flashed.connect(sender=app, receiver=record)
    try:
        yield records
    finally:
        message_flashed.disconnect(sender=app, receiver=record)


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

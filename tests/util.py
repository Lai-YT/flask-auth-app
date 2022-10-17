from __future__ import annotations
from contextlib import contextmanager
from typing import TYPE_CHECKING, Dict, Generator, List

from flask import message_flashed, template_rendered
from jinja2 import Template

if TYPE_CHECKING:
    from flask import Flask


@contextmanager
def captured_flash_messages(app: Flask) -> Generator[List[str], None, None]:
    messages: List[str] = []

    def record_message(sender: Flask, message: str, category: str, **extra) -> None:
        messages.append(message)

    message_flashed.connect(sender=app, receiver=record_message)
    try:
        yield messages
    finally:
        message_flashed.disconnect(sender=app, receiver=record_message)


@contextmanager
def captured_templates(app: Flask) -> Generator[List[Template], None, None]:
    templates: List[Template] = []

    def record_template(sender: Flask, template: Template, context: Dict, **extra) -> None:
        templates.append(template)

    template_rendered.connect(sender=app, receiver=record_template)
    try:
        yield templates
    finally:
        template_rendered.disconnect(sender=app, receiver=record_template)

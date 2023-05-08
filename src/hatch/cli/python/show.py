from __future__ import annotations

from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from hatch.cli.application import Application


@click.command(short_help='Show the available Python distributions')
@click.pass_obj
def show(app: Application):
    """Show the available Python distributions."""

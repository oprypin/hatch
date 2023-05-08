import click

from hatch.cli.python.show import show


@click.group(short_help='Manage Python installations')
def python():
    pass


python.add_command(show)

import pytest

from hatch.python.core import PythonManager
from hatch.python.distributions import DISTRIBUTIONS
from hatch.python.resolve import get_distribution


def test_get_installed(temp_dir):
    manager = PythonManager(temp_dir)

    (temp_dir / 'bar').touch()
    path_foo = temp_dir / 'foo'
    path_foo.mkdir()
    (path_foo / 'file.txt').touch()

    dist = get_distribution('3.10')
    path_310 = temp_dir / dist.name
    path_310.mkdir()
    python_path = path_310 / dist.python_path
    python_path.parent.ensure_dir_exists()
    python_path.touch()

    dist = get_distribution('3.9')
    path_39 = temp_dir / dist.name
    path_39.mkdir()
    python_path = path_39 / dist.python_path
    python_path.parent.ensure_dir_exists()
    python_path.touch()

    assert list(manager.get_installed()) == ['3.9', '3.10']


@pytest.mark.requires_internet
@pytest.mark.parametrize('name', DISTRIBUTIONS)
def test_installation(temp_dir, platform, name):
    manager = PythonManager(temp_dir)
    dist = manager.install(name)

    python_path = dist.python_path
    assert python_path.is_file()

    output = platform.check_command_output([python_path, '-c', 'import sys;print(sys.executable)']).strip()
    assert output == str(python_path)

    major_minor = name.replace('pypy', '')

    output = platform.check_command_output([python_path, '--version']).strip()
    assert output.startswith(f'Python {major_minor}.')
    if name.startswith('pypy'):
        assert 'PyPy' in output

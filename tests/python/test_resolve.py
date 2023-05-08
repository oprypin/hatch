import pytest

from hatch.python.resolve import get_distribution
from hatch.utils.structures import EnvVars


def test_unknown_distribution():
    with pytest.raises(ValueError, match='Unknown distribution: foo'):
        get_distribution('foo')


class TestDistributionVersions:
    def test_cpython_standalone(self):
        url = 'https://github.com/indygreg/python-build-standalone/releases/download/20230507/cpython-3.11.3%2B20230507-aarch64-unknown-linux-gnu-install_only.tar.gz'  # noqa: E501
        dist = get_distribution('3.11', url)
        version = dist.version

        assert version.epoch == 0
        assert version.base_version == '20230507'

    def test_pypy(self):
        url = 'https://downloads.python.org/pypy/pypy3.10-v7.3.12-aarch64.tar.bz2'
        dist = get_distribution('pypy3.10', url)
        version = dist.version

        assert version.epoch == 0
        assert version.base_version == '7.3.12'


@pytest.mark.parametrize(
    'system, variant',
    [
        ('windows', 'shared'),
        ('windows', 'static'),
        ('linux', 'v1'),
        ('linux', 'v2'),
        ('linux', 'v3'),
        ('linux', 'v4'),
    ],
)
def test_variants(platform, system, variant):
    if platform.name != system:
        pytest.skip(f'Skipping test for: {system}')

    with EnvVars({f'HATCH_PYTHON_VARIANT_{system.upper()}': variant}):
        dist = get_distribution('3.11')

    assert variant in dist.source

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from hatch.python.distributions import DISTRIBUTIONS, ORDERED_DISTRIBUTIONS
from hatch.python.resolve import get_distribution
from hatch.utils.fs import temp_directory

if TYPE_CHECKING:
    from hatch.python.resolve import Distribution
    from hatch.utils.fs import Path


class InstalledDistribution:
    def __init__(self, path: Path, distribution: Distribution) -> None:
        self.__path = path
        self.__new_dist = distribution

    @property
    def path(self) -> Path:
        return self.__path

    @cached_property
    def python_path(self) -> Path:
        return self.path / self.__new_dist.python_path

    @cached_property
    def metadata_file(self) -> Path:
        return self.path / 'hatch-dist.json'

    @cached_property
    def metadata(self) -> dict[str, Any]:
        import json

        if not self.metadata_file.is_file():
            return {}

        return json.loads(self.metadata_file.read_text())

    def needs_update(self) -> bool:
        source = self.metadata.get('source')
        if not source:
            return True

        installed_dist = get_distribution(self.path.name, source)
        return self.__new_dist.version > installed_dist.version


class PythonManager:
    def __init__(self, directory: Path) -> None:
        self.__directory = directory

    @property
    def directory(self) -> Path:
        return self.__directory

    def get_installed(self) -> dict[str, InstalledDistribution]:
        distributions: list[tuple[Path, Distribution]] = []
        for path in self.directory.iterdir():
            if path.is_dir() and path.name in DISTRIBUTIONS:
                dist = get_distribution(path.name)
                if (path / dist.python_path).is_file():
                    distributions.append((path, dist))

        distributions.sort(key=lambda d: ORDERED_DISTRIBUTIONS.index(d[1].name))
        return {dist.name: InstalledDistribution(path, dist) for path, dist in distributions}

    def install(self, identifier: str) -> InstalledDistribution:
        import json

        from hatch.utils.network import download_file

        dist = get_distribution(identifier)
        path = self.directory / identifier

        with temp_directory() as temp_dir:
            archive_path = temp_dir / dist.archive_name
            unpack_path = temp_dir / identifier
            download_file(archive_path, dist.source, follow_redirects=True)
            dist.unpack(archive_path, unpack_path)

            backup_path = path.with_suffix('.bak')
            if backup_path.is_dir():
                backup_path.wait_for_dir_removed()

            if path.is_dir():
                path.replace(backup_path)

            try:
                unpack_path.replace(path)
            except OSError:
                import shutil

                try:
                    shutil.move(unpack_path, path)
                except OSError:
                    path.wait_for_dir_removed()
                    if backup_path.is_dir():
                        backup_path.replace(path)

                    raise

        installed_dist = InstalledDistribution(path, dist)
        installed_dist.metadata_file.write_text(json.dumps({'source': dist.source}))

        return installed_dist

    def remove(self, dist: InstalledDistribution) -> None:
        dist.path.wait_for_dir_removed()

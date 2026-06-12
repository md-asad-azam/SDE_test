"""
Update the build "point" version number in two files as part of the build process.

Reads the new point version from the "BuildNum" environment variable and updates:
  - $SourcePath/develop/global/src/SConstruct   (line: "point=123,")
  - $SourcePath/develop/global/src/VERSION      (line: "ADLMSDK_VERSION_POINT=123")

Set the SourcePath in env variable, here - `./Solution2/test`
Set the BuildNum in env variable, anything is fine.
"""

import os
import re
import sys
import tempfile
from pathlib import Path


class BuildVersionUpdater:
    """Updates the build "point" version number in source-tree version files."""

    # Each entry: (filename, regex pattern, replacement template)
    # The pattern's capture group 1 is the numeric value to be replaced.
    FILE_PATTERNS = {
        "SConstruct": re.compile(r"(point\s*=\s*)\d+"),
        "VERSION": re.compile(r"(ADLMSDK_VERSION_POINT\s*=\s*)\d+"),
    }

    def __init__(self, source_path: Path, build_num: str):
        if not build_num.isdigit():
            raise ValueError(f"BuildNum must be a non-negative integer, got {build_num!r}")

        self.src_dir = source_path / "develop" / "global" / "src"
        self.build_num = build_num

    def update_all(self) -> None:
        """Update the point version in every known file."""
        for filename, pattern in self.FILE_PATTERNS.items():
            self._update_file(self.src_dir / filename, pattern)

    def _update_file(self, file_path: Path, pattern: re.Pattern) -> None:
        """Replace the version number in `file_path` matched by `pattern`, in place."""
        if not file_path.is_file():
            raise FileNotFoundError(f"Expected version file not found: {file_path}")

        original_text = file_path.read_text()
        updated_text, num_subs = pattern.subn(rf"\g<1>{self.build_num}", original_text)

        if num_subs == 0:
            raise ValueError(
                f"No version line matching pattern found in {file_path}; "
                "file format may have changed."
            )

        self._atomic_write(file_path, updated_text)
        print(f"Updated {file_path} ({num_subs} occurrence(s)) -> point {self.build_num}")

    @staticmethod
    def _atomic_write(file_path: Path, content: str) -> None:
        """
        Write `content` to `file_path` atomically by writing to a temporary
        file in the same directory and then renaming it over the original.
        This avoids leaving a corrupt/partial file if the process is
        interrupted mid-write, and preserves the original file's permissions.
        """
        original_mode = file_path.stat().st_mode

        fd, tmp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w") as tmp_file:
                tmp_file.write(content)
            os.chmod(tmp_path, original_mode)
            os.replace(tmp_path, file_path)  # atomic on POSIX and Windows
        except Exception:
            os.unlink(tmp_path)
            raise


def main() -> int:
    try:
        source_path = Path(os.environ["SourcePath"])
    except KeyError:
        print("Error: SourcePath environment variable is not set.", file=sys.stderr)
        return 1

    try:
        build_num = os.environ["BuildNum"]
    except KeyError:
        print("Error: BuildNum environment variable is not set.", file=sys.stderr)
        return 1

    try:
        updater = BuildVersionUpdater(source_path, build_num)
        updater.update_all()
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
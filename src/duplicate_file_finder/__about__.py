# -*- coding: utf-8 -*-
"""
# duplicate-file-finder
https://github.com/dougthor42/duplicate-file-finder
Plan out the reorganization of your file systems.
"""
from pathlib import Path

__all__ = [
    "__author__",
    "__author_email__",
    "__maintainer__",
    "__maintainer_email__",
    "__license__",
    "__version__",
    "__released__",
    "__created__",
    "__project_name__",
    "__project_url__",
    "__package_name__",
    "__description__",
    "__long_descr__",
]

__author__ = "Douglas Thor"
__author_email__ = "doug.thor@gmail.com"

__maintainer__ = ""
__maintainer_email__ = ""

__license__ = "MIT"
__version__ = "0.0.0"
__released__ = ""
__created__ = "2020-11-01"

__project_name__ = "duplicate-file-finder"
__project_url__ = "https://github.com/dougthor42/duplicate-file-finder"
__package_name__ = "duplicate_file_finder"

__description__ = "Find all files with matching md5 checksums."
__long_descr__ = __doc__

# Try to read the README file and use that as our long description.
try:
    base_dir = Path(__file__).parent.parent
    readme = base_dir / "README.md"
    __long_descr__ = readme.read_text()
except Exception:
    pass

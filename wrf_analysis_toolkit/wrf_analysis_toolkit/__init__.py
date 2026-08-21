# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

from importlib.metadata import PackageNotFoundError, version

from .api import (
    diagnostic,
    terrain,
    csv,
    wrfdiff,
    mp4diff,
    mp4stitch,
)

__all__ = [
    "diagnostic",
    "terrain",
    "csv",
    "wrfdiff",
    "mp4diff",
    "mp4stitch",
]

try:
    __version__ = version("wrf_analysis_toolkit")
except PackageNotFoundError:
    __version__ = "dev_local_install"

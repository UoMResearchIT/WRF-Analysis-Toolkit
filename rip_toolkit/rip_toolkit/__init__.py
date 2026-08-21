# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

from importlib.metadata import PackageNotFoundError, version


from .utils import (
    get_model_times,
    date_model_times,
    print_model_times,
    diagnostic_groups,
    colors,
)
from .api import (
    run_rip_container,
    preprocess,
    point_trajectory,
    swarm_trajectories,
    plot_trajectories,
)

__all__ = [
    "get_model_times",
    "date_model_times",
    "print_model_times",
    "diagnostic_groups",
    "colors",
    "preprocess",
    "point_trajectory",
    "swarm_trajectories",
    "plot_trajectories",
    "run_rip_container",
]

try:
    __version__ = version("rip_toolkit")
except PackageNotFoundError:
    __version__ = "dev_local_install"

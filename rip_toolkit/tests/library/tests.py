# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import rip_toolkit as ript

mt = ript.utils.get_model_times("/wrfdata")

print("Model times:", mt)

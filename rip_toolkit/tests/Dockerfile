# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

FROM mambaorg/micromamba:1.5.8

COPY environment.yml /tmp/environment.yml

RUN micromamba create -y -n rip-py-env -f /tmp/environment.yml \
    && micromamba run -n rip-py-env python -m pip install --no-cache-dir pytest coverage \
    && micromamba clean --all --yes

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Ensure container commands execute inside the project environment.
ENV ENV_NAME=rip-py-env

WORKDIR /memory
WORKDIR /wrf-analysis
COPY rip_toolkit /wrf-analysis/rip_toolkit
COPY pyproject.toml /wrf-analysis/pyproject.toml
RUN micromamba run -n rip-py-env python -m pip install .
COPY tests /wrf-analysis/tests
COPY pytest.ini /wrf-analysis/pytest.ini
COPY .coveragerc /wrf-analysis/.coveragerc

CMD ["python", "-u", "rip_toolkit/cli.py"]

#!/bin/bash

# Exit the script with the first non-zero return code
# i.e. if any command fails, stop and return from this script.
set -e

flake8 ccc_client_dev.py setup.py tests ccc_client

python -m nose tests  \
           --with-coverage \
           --cover-package ccc_client \
           --cover-inclusive \
           --cover-min-percentage 80 \
           --cover-branches  \
           --cover-erase

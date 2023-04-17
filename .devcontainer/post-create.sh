#!/usr/bin/env bash

# Fixes: https://github.com/microsoft/vscode-remote-release/issues/7982
echo "{}" > ~/.docker/config.json

# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Development dependencies
pip install -r dev-requirements.txt
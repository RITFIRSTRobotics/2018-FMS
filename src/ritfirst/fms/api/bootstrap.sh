#!/bin/sh
export FLASK_APP=./fmsapi/index.py
export PYTHONPATH=../../../../
source $(pipenv --venv)/bin/activate
flask run -h 0.0.0.0
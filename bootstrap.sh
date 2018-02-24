#!/bin/sh
export FLASK_APP=./src/ritfirst/fms/api/fmsapi/index.py
export PYTHONPATH=${PYTHONPATH}:./
cd ./src/ritfirst/fms/api/
source $(pipenv --venv)/bin/activate
cd ../../../../
flask run -h 0.0.0.0
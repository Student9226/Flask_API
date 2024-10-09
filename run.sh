#!/bin/bash
#pip install -r requirements.txt
gunicorn --workers 4 --bind 0.0.0.0:5000 main:app

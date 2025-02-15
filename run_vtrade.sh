#!/bin/bash

cd $(dirname "$0")
source ./vtrade_venv/bin/activate
python3 scanner/scan.py

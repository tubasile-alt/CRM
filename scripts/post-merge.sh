#!/bin/bash
set -e

pip install -r requirements.txt -q
python migrate_db.py

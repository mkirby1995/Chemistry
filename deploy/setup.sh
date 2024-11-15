#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/pyisru

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
pip install gunicorn

# Deactivate virtual environment
deactivate

echo "Virtual environment set up successfully."

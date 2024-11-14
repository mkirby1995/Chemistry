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

# Deactivate virtual environment
deactivate

echo "Virtual environment set up successfully."

# Copy service and Nginx configuration files
sudo cp deploy/pyisru.service /etc/systemd/system/pyisru.service
sudo cp deploy/pyisru_nginx.conf /etc/nginx/sites-available/pyisru

echo "Service and Nginx configuration files copied successfully."

# Enable the Nginx site
sudo ln -s /etc/nginx/sites-available/pyisru /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default

echo "Nginx site enabled successfully."

# Set permissions
sudo chown -R ubuntu:www-data /home/ubuntu/pyisru
sudo chmod -R 755 /home/ubuntu/pyisru

echo "Permissions set successfully."

# Start and enable Gunicorn service
sudo systemctl daemon-reload
sudo systemctl start pyisru
sudo systemctl enable pyisru

echo "Gunicorn service started and enabled successfully."

# Test Nginx configuration and restart service
sudo nginx -t
sudo systemctl restart nginx

echo "Nginx configuration tested and service restarted successfully."

echo "Deployment script executed successfully."

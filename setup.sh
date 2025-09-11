#!/bin/bash
echo "Welcome to ScoutingAPI!!!"
echo "Creating and activating a virtual environment for Flask..."
python3 -m venv .venv
source .venv/bin/activate
echo "Virtual environment finished!"

echo "Upgrading pip and installing Flask..."
pip install --upgrade pip
pip install Flask
echo "Package install successful!"

echo "Please enter the super secret password:"
read thePassword
echo "Creating the super secret secrets file..."
echo $thePassword > super_duper_secret_password.txt

echo "All operations Komplett!"
echo "To start, run: source .venv/bin/activate"

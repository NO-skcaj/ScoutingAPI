#!/bin/bash

echo "Creating a virtual environment for Flask."
python3 -m venv .venv

echo "Activating the virtual environment..."
source .venv/bin/activate

echo "Upgrading pip and installing Flask..."
pip install --upgrade pip
pip install Flask
pip install sqlite3

echo "Operation Komplett!"
echo "To start development, run: source .venv/bin/activate"

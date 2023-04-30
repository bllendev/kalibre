#!/bin/bash

# Clear pipenv cache
echo "Clearing pipenv cache..."
pipenv --rm

# Remove current pipenv virtual environment
echo "Removing current pipenv virtual environment..."
pipenv --venv | xargs rm -rf

# Remove Pipfile.lock
echo "Removing Pipfile.lock..."
rm -f Pipfile.lock

# Reinstall packages from Pipfile
echo "Reinstalling packages from Pipfile..."
pipenv install

echo "Pipenv environment setup complete!"

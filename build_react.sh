#!/bin/bash

# Exit on error
set -e

echo "Starting React build process..."

# Change to the React project directory
cd "$(dirname "$0")/hello-ui-feedback"

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the React app
echo "Building React application..."
npm run build

# Create the destination directory for the bundle if it doesn't exist
mkdir -p ../catalog/static/catalog/js/dist/

# Copy the built files to Django's static directory
echo "Copying built files to Django static directory..."
cp -r dist/assets/index-*.js ../catalog/static/catalog/js/dist/bundle.js
cp -r dist/assets/index-*.css ../catalog/static/catalog/css/bundle.css

echo "Build completed successfully!"
echo "React bundle available at: catalog/static/catalog/js/dist/bundle.js"
echo "CSS bundle available at: catalog/static/catalog/css/bundle.css"
#!/bin/bash

# Exit on error
set -e

echo "Starting React build process..."

# Change to the project root directory
cd "$(dirname "$0")"

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the React app
echo "Building React application..."
npm run build

# Create the destination directories if they don't exist
mkdir -p catalog/static/catalog/js/dist/
mkdir -p catalog/static/catalog/css/

# Copy the bundle files
echo "Copying build files to Django static directories..."
if [ -d "dist/assets" ]; then
  # Find JS and CSS files
  JS_FILE=$(find dist/assets -name "*.js" | head -n 1)
  CSS_FILE=$(find dist/assets -name "*.css" | head -n 1)
  
  if [ -n "$JS_FILE" ]; then
    cp "$JS_FILE" catalog/static/catalog/js/dist/bundle.js
    echo "✅ JavaScript bundle copied"
  else
    echo "⚠️ No JavaScript bundle found"
  fi
  
  if [ -n "$CSS_FILE" ]; then
    cp "$CSS_FILE" catalog/static/catalog/css/bundle.css
    echo "✅ CSS bundle copied"
  else
    echo "⚠️ No CSS bundle found"
  fi
  
  # Copy other assets
  cp -r dist/assets catalog/static/catalog/js/dist/
  echo "✅ Assets copied"
else
  echo "⚠️ No assets directory found in build output"
fi

echo "Build process completed!"
echo "To view the React UI, visit: http://localhost:8001/react-ui/"
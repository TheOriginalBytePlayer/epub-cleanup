#!/bin/bash
# Script to package the Calibre plugin

cd "$(dirname "$0")/calibre-plugin"

echo "Packaging EPUB Cleanup Calibre Plugin..."

# Create the plugin ZIP file
zip -r ../epub-cleanup-plugin.zip __init__.py cleanup.py config_dialog.py plugin.json

echo "Plugin packaged as epub-cleanup-plugin.zip"
echo ""
echo "To install in Calibre:"
echo "1. Open Calibre"
echo "2. Go to Preferences → Plugins → Load plugin from file"
echo "3. Select epub-cleanup-plugin.zip"
echo "4. Restart Calibre"

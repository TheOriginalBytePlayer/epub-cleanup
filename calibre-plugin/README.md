# EPUB Cleanup Calibre Plugin

This plugin for Calibre processes EPUB files to clean up redundant spans and add chapter headings.

## Features

1. **Merge Redundant Spans**: Automatically merges consecutive `<span>` elements that have the same `style` attribute.
   
   Example:
   ```html
   <!-- Before -->
   <span style="char_one">is a </span><span style="char_one">stupid </span><span style="char_one">paragraph</span>
   
   <!-- After -->
   <span style="char_one">is a stupid paragraph</span>
   ```

2. **Add Chapter Headings**: Finds empty paragraphs immediately after `<body>` tags and replaces them with "Chapter X" where X is an incrementing number.

## Installation

### Method 1: From Source

1. Navigate to the `calibre-plugin` directory
2. Create a ZIP file containing all the plugin files:
   ```bash
   cd calibre-plugin
   zip -r epub-cleanup-plugin.zip __init__.py cleanup.py plugin.json
   ```

3. In Calibre:
   - Go to **Preferences** → **Plugins** → **Load plugin from file**
   - Select the `epub-cleanup-plugin.zip` file
   - Restart Calibre when prompted

### Method 2: Direct Installation

You can also install by selecting all files in the `calibre-plugin` directory and adding them as a plugin.

## Usage

1. Open an EPUB file in Calibre's **Edit Book** mode
2. Go to **Tools** → **EPUB Cleanup** (or use the toolbar button if added)
3. The plugin will process all HTML/XHTML files in the EPUB
4. Save the file when done

## Requirements

- Calibre 5.0 or higher
- BeautifulSoup4 and lxml (usually included with Calibre)

## Development

The plugin uses the same core logic as the standalone script but integrates with Calibre's book editing infrastructure.

## Troubleshooting

If the plugin doesn't appear after installation:
1. Check that you're using Calibre 5.0 or higher
2. Make sure all files are properly included in the plugin ZIP
3. Check Calibre's plugin debug log for any errors

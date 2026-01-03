# EPUB Cleanup Calibre Plugin

This plugin for Calibre processes EPUB files to clean up redundant spans and add chapter headings with extensive configuration options.

## Features

### 1. Merge Redundant Spans
Automatically merges consecutive `<span>` elements that have the same `style` attribute.

Example:
```html
<!-- Before -->
<span style="char_one">is a </span><span style="char_one">stupid </span><span style="char_one">paragraph</span>

<!-- After -->
<span style="char_one">is a stupid paragraph</span>
```

### 2. Add/Renumber Chapter Headings
Finds empty paragraphs immediately after `<body>` tags and replaces them with configurable chapter headings.

Features include:
- Customizable chapter text prefix (default: "Chapter")
- Multiple numbering styles:
  - Numeric (1, 2, 3...)
  - Words (One, Two, Three...)
  - Roman Numerals (I, II, III...)
- Optional text following the number
- Auto-detection of starting chapter number from filename or content
- Option to insert chapter headings even in files without empty paragraphs

## Configuration Dialog

When you run the plugin, a configuration dialog will appear with the following options:

### Span Cleanup Options
- **Clean-up Redundant Spans in text**: Enable/disable span cleanup
- **Perform Clean-Up in**: Choose scope:
  - All Text Files
  - Current File Only
  - Current File Onwards

### Chapter Heading Options
- **Add/Renumber Chapter Headings**: Enable/disable chapter heading modification
- **Add/Modify Chapter Headings**: Choose scope:
  - All Text Files
  - Current File Only
  - Current File Onwards
- **Start Numbering at**: Starting chapter number (auto-detected from filename or content)
- **Initial Chapter Text**: Text prefix for chapters (default: "Chapter", remembered between sessions)
- **Numbering Style**: Choose from Numeric, Words, or Roman Numerals (remembered between sessions)
- **Text Following Number**: Optional text after the number (remembered between sessions)
- **Insert Chapter Heading as `<p>`**: Insert chapter headings even in files where the first paragraph is neither blank nor an existing chapter heading

### Buttons
- **Apply**: Execute the cleanup with selected options (only enabled when at least one checkbox is checked)
- **Cancel**: Cancel without making changes

All user preferences (except scope selections) are remembered between sessions for convenience.

## Installation

### Method 1: From Source

1. Navigate to the `calibre-plugin` directory
2. Create a ZIP file containing all the plugin files:
   ```bash
   cd calibre-plugin
   zip -r epub-cleanup-plugin.zip __init__.py main.py cleanup.py config_dialog.py plugin.json
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
3. Configure the desired options in the dialog
4. Click **Apply** to process the selected files
5. Save the file when done

## Examples

### Example 1: Clean up spans in all files
1. Check "Clean-up Redundant Spans in text"
2. Select "All Text Files" in the cleanup scope
3. Click Apply

### Example 2: Add chapter headings starting from Chapter 5
1. Check "Add/Renumber Chapter Headings"
2. Set "Start Numbering at" to 5
3. Set "Initial Chapter Text" to "Chapter"
4. Select "Numeric (eg 1, 2, 3...)" as the numbering style
5. Click Apply

### Example 3: Add Roman numeral chapters from current file onwards
1. Check "Add/Renumber Chapter Headings"
2. Select "Current File Onwards" in the chapter scope
3. Select "Roman Numerals (eg I, II, III...)" as the numbering style
4. Click Apply

## Requirements

- Calibre 5.0 or higher
- BeautifulSoup4 and lxml (usually included with Calibre)
- PyQt5 (included with Calibre)

## Development

The plugin follows calibre's modern EditBookToolPlugin architecture:
- `__init__.py` - Plugin metadata
- `main.py` - Tool implementation (EPUBCleanupTool class)
- `cleanup.py` - Core cleanup functions
- `config_dialog.py` - Configuration dialog
- `plugin.json` - Plugin menu/toolbar configuration

The plugin uses the same core logic as the standalone script but integrates with Calibre's book editing infrastructure through the Tool-based architecture and provides a rich configuration dialog.

## Plugin Architecture

This plugin follows calibre's recommended best practices for EditBookToolPlugin:
- Uses the Tool class pattern from `calibre.gui2.tweak_book.plugin`
- Tool implementation is in `main.py` (as required by calibre conventions)
- Minimal `__init__.py` with only metadata
- Integrates with editor's container and boss APIs

## Troubleshooting

If the plugin doesn't appear after installation:
1. Check that you're using Calibre 5.0 or higher
2. Make sure all files are properly included in the plugin ZIP
3. Check Calibre's plugin debug log for any errors

If the dialog doesn't appear or shows errors:
1. Make sure PyQt5 is available (should be included with Calibre)
2. Check that config_dialog.py is included in the plugin
3. Look for error messages in Calibre's debug log

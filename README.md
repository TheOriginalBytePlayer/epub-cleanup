# epub-cleanup

Clean-up of EPUB's redundant styles and adding manual chapter headings.

## Features

1. **Merge Redundant Spans**: Automatically merges consecutive `<span>` elements that have the same `style` attribute.
2. **Add Chapter Headings**: Finds empty paragraphs immediately after `<body>` tags and replaces them with "Chapter X" headings.

## Usage

### Standalone Script

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the script:
```bash
python epub_cleanup.py input.epub [output.epub]
```

If no output file is specified, the input file will be overwritten.

### Calibre Plugin

The functionality is also available as a Calibre plugin for integration with Calibre's book editor.

See [calibre-plugin/README.md](calibre-plugin/README.md) for installation and usage instructions.

## Testing

Run the test suite:
```bash
python test_epub_cleanup.py
```

## Requirements

- Python 3.6+
- BeautifulSoup4
- lxml

## License

See [LICENSE](LICENSE) file for details.


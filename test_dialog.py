#!/usr/bin/env python3
"""
Basic smoke test for the configuration dialog
"""

import sys
import os

# Check if we can import PyQt5 (required for Calibre plugin)
try:
    from PyQt5.Qt import QApplication
    HAS_QT = True
except ImportError:
    print("PyQt5 not available - this is expected in CI/CD environment")
    print("The dialog will be tested when installed in Calibre")
    HAS_QT = False
    sys.exit(0)

# Add the calibre-plugin directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'calibre-plugin'))

from config_dialog import ConfigDialog


def test_dialog_instantiation():
    """Test that the dialog can be instantiated."""
    print("Testing dialog instantiation...")
    
    app = QApplication(sys.argv)
    
    # Test with no file info
    dialog = ConfigDialog(None, None, None)
    assert dialog is not None
    print("  ✓ Dialog instantiated without file info")
    
    # Test with file name
    dialog = ConfigDialog(None, "chapter_5.xhtml", None)
    assert dialog is not None
    # Should detect chapter 5 from filename
    assert dialog.start_number_spin.value() == 5
    print("  ✓ Dialog instantiated with filename and detected chapter number")
    
    # Test with file content
    content = '''<?xml version="1.0"?>
<html>
<body>
<p>Chapter 3</p>
<p>Some content</p>
</body>
</html>'''
    
    dialog = ConfigDialog(None, "test.xhtml", content)
    assert dialog is not None
    # Should detect chapter 3 from content
    assert dialog.start_number_spin.value() == 3
    print("  ✓ Dialog instantiated with content and detected chapter number")
    
    # Test get_config
    config = dialog.get_config()
    assert config is not None
    assert 'cleanup_spans' in config
    assert 'add_chapters' in config
    assert 'start_number' in config
    print("  ✓ Dialog config retrieval works")
    
    print("All dialog tests passed!\n")


if __name__ == '__main__':
    if HAS_QT:
        print("Running dialog smoke tests...\n")
        test_dialog_instantiation()
        print("All tests passed! ✓")

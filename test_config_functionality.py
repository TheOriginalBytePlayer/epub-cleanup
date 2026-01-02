#!/usr/bin/env python3
"""
Test script for EPUB cleanup configuration functionality
"""

import sys
import os

# Add the calibre-plugin directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'calibre-plugin'))

from cleanup import (
    number_to_words, number_to_roman, format_chapter_number,
    is_existing_chapter_heading, add_chapter_headings_with_config,
    process_xhtml_content_with_config
)
from bs4 import BeautifulSoup


def test_number_to_words():
    """Test number to words conversion."""
    print("Testing number_to_words...")
    
    assert number_to_words(1) == "One"
    assert number_to_words(5) == "Five"
    assert number_to_words(10) == "Ten"
    assert number_to_words(15) == "Fifteen"
    assert number_to_words(20) == "Twenty"
    assert number_to_words(25) == "Twenty Five"
    assert number_to_words(99) == "Ninety Nine"
    
    print("  ✓ Number to words conversion works correctly")


def test_number_to_roman():
    """Test number to Roman numerals conversion."""
    print("Testing number_to_roman...")
    
    assert number_to_roman(1) == "I"
    assert number_to_roman(4) == "IV"
    assert number_to_roman(5) == "V"
    assert number_to_roman(9) == "IX"
    assert number_to_roman(10) == "X"
    assert number_to_roman(50) == "L"
    assert number_to_roman(100) == "C"
    assert number_to_roman(500) == "D"
    assert number_to_roman(1000) == "M"
    assert number_to_roman(1994) == "MCMXCIV"
    
    print("  ✓ Number to Roman numerals conversion works correctly")


def test_format_chapter_number():
    """Test chapter number formatting."""
    print("Testing format_chapter_number...")
    
    assert format_chapter_number(5, "Numeric (eg 1, 2, 3...)") == "5"
    assert format_chapter_number(5, "Words (eg One, Two, Three...)") == "Five"
    assert format_chapter_number(5, "Roman Numerals (eg I, II, III...)") == "V"
    
    print("  ✓ Chapter number formatting works correctly")


def test_is_existing_chapter_heading():
    """Test existing chapter heading detection."""
    print("Testing is_existing_chapter_heading...")
    
    assert is_existing_chapter_heading("Chapter 1", "Chapter") == True
    assert is_existing_chapter_heading("Chapter 5", "Chapter") == True
    assert is_existing_chapter_heading("Chapter I", "Chapter") == True
    assert is_existing_chapter_heading("Chapter V", "Chapter") == True
    assert is_existing_chapter_heading("Chapter One", "Chapter") == True
    assert is_existing_chapter_heading("Chapter Five", "Chapter") == True
    assert is_existing_chapter_heading("Some other text", "Chapter") == False
    assert is_existing_chapter_heading("Random paragraph", "Chapter") == False
    
    print("  ✓ Existing chapter heading detection works correctly")


def test_add_chapter_headings_with_config():
    """Test adding chapter headings with configuration."""
    print("Testing add_chapter_headings_with_config...")
    
    # Test case 1: Empty paragraph should be marked
    html = '''<?xml version="1.0"?>
<html>
<body>
<p></p>
<p>Some content</p>
</body>
</html>'''
    
    soup = BeautifulSoup(html, 'lxml-xml')
    config = {'initial_chapter_text': 'Chapter'}
    changes, count = add_chapter_headings_with_config(soup, config, False)
    
    assert changes == True
    assert count == 1
    placeholder = soup.find(attrs={'data-chapter-placeholder': 'true'})
    assert placeholder is not None
    print("  ✓ Empty paragraph marked for chapter heading")
    
    # Test case 2: Insert chapter heading when paragraph is not empty and insert_as_p is True
    html = '''<?xml version="1.0"?>
<html>
<body>
<p>Some content</p>
</body>
</html>'''
    
    soup = BeautifulSoup(html, 'lxml-xml')
    config = {'initial_chapter_text': 'Chapter'}
    changes, count = add_chapter_headings_with_config(soup, config, True)
    
    assert changes == True
    assert count == 1
    placeholder = soup.find(attrs={'data-chapter-placeholder': 'true'})
    assert placeholder is not None
    print("  ✓ Chapter heading inserted before non-empty paragraph")
    
    # Test case 3: Should not insert if paragraph already has chapter heading
    html = '''<?xml version="1.0"?>
<html>
<body>
<p>Chapter 1</p>
</body>
</html>'''
    
    soup = BeautifulSoup(html, 'lxml-xml')
    config = {'initial_chapter_text': 'Chapter'}
    changes, count = add_chapter_headings_with_config(soup, config, True)
    
    assert changes == False
    assert count == 0
    print("  ✓ Existing chapter heading not replaced")
    
    print("All add_chapter_headings_with_config tests passed!\n")


def test_process_xhtml_content_with_config():
    """Test the full processing pipeline with configuration."""
    print("Testing process_xhtml_content_with_config...")
    
    # Test case 1: Both cleanup and chapter heading with numeric style
    html = '''<?xml version="1.0"?>
<html>
<body>
<p></p>
<p>this <span style="char_one">is a</span><span style="char_one"> test</span></p>
</body>
</html>'''
    
    config = {
        'initial_chapter_text': 'Chapter',
        'numbering_style': 'Numeric (eg 1, 2, 3...)',
        'text_following_number': ''
    }
    
    result, new_chapter_num = process_xhtml_content_with_config(html, 5, config, True, True)
    
    soup = BeautifulSoup(result, 'lxml-xml')
    
    # Check chapter was added
    body = soup.find('body')
    first_p = None
    for child in body.children:
        if hasattr(child, 'name') and child.name == 'p':
            first_p = child
            break
    
    assert first_p is not None
    assert first_p.get_text().strip() == "Chapter 5"
    
    # Check spans were merged
    spans = soup.find_all('span')
    assert len(spans) == 1
    
    # Check chapter number incremented
    assert new_chapter_num == 6
    
    print("  ✓ Both cleanup and chapter heading work with numeric style")
    
    # Test case 2: Chapter heading with Roman numerals and text following
    html = '''<?xml version="1.0"?>
<html>
<body>
<p></p>
</body>
</html>'''
    
    config = {
        'initial_chapter_text': 'Chapter',
        'numbering_style': 'Roman Numerals (eg I, II, III...)',
        'text_following_number': '- The Beginning'
    }
    
    result, new_chapter_num = process_xhtml_content_with_config(html, 1, config, False, True)
    
    soup = BeautifulSoup(result, 'lxml-xml')
    body = soup.find('body')
    first_p = None
    for child in body.children:
        if hasattr(child, 'name') and child.name == 'p':
            first_p = child
            break
    
    assert first_p is not None
    assert first_p.get_text().strip() == "Chapter I - The Beginning"
    assert new_chapter_num == 2
    
    print("  ✓ Chapter heading works with Roman numerals and text following")
    
    # Test case 3: Chapter heading with words style
    html = '''<?xml version="1.0"?>
<html>
<body>
<p>  </p>
</body>
</html>'''
    
    config = {
        'initial_chapter_text': 'Chapter',
        'numbering_style': 'Words (eg One, Two, Three...)',
        'text_following_number': ''
    }
    
    result, new_chapter_num = process_xhtml_content_with_config(html, 3, config, False, True)
    
    soup = BeautifulSoup(result, 'lxml-xml')
    body = soup.find('body')
    first_p = None
    for child in body.children:
        if hasattr(child, 'name') and child.name == 'p':
            first_p = child
            break
    
    assert first_p is not None
    assert first_p.get_text().strip() == "Chapter Three"
    assert new_chapter_num == 4
    
    print("  ✓ Chapter heading works with words style")
    
    # Test case 4: Only cleanup, no chapter heading
    html = '''<?xml version="1.0"?>
<html>
<body>
<p>this <span style="char_one">is a</span><span style="char_one"> test</span></p>
</body>
</html>'''
    
    config = {}
    result, new_chapter_num = process_xhtml_content_with_config(html, 1, config, True, False)
    
    soup = BeautifulSoup(result, 'lxml-xml')
    
    # Check spans were merged
    spans = soup.find_all('span')
    assert len(spans) == 1
    
    # Check chapter number didn't increment
    assert new_chapter_num == 1
    
    print("  ✓ Only cleanup works without chapter heading")
    
    print("All process_xhtml_content_with_config tests passed!\n")


if __name__ == '__main__':
    print("Running EPUB cleanup configuration tests...\n")
    test_number_to_words()
    test_number_to_roman()
    test_format_chapter_number()
    test_is_existing_chapter_heading()
    test_add_chapter_headings_with_config()
    test_process_xhtml_content_with_config()
    print("All tests passed! ✓")

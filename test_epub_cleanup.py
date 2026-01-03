#!/usr/bin/env python3
"""
Test script for EPUB cleanup functionality
"""

from epub_cleanup import merge_consecutive_spans, add_chapter_headings, process_xhtml_content
from bs4 import BeautifulSoup


def test_merge_consecutive_spans():
    """Test merging consecutive spans with the same style."""
    print("Testing merge_consecutive_spans...")
    
    # Test case 1: Basic consecutive spans (with spaces in content)
    html = '''<div>this <span style="char_one">is a </span><span style="char_one">stupid </span><span style="char_one">paragraph</span></div>'''
    soup = BeautifulSoup(html, 'lxml-xml')
    merge_consecutive_spans(soup)
    result = str(soup)
    
    # Should have only one span
    soup_result = BeautifulSoup(result, 'lxml-xml')
    spans = soup_result.find_all('span')
    assert len(spans) == 1, f"Expected 1 span, got {len(spans)}"
    assert spans[0].get_text() == "is a stupid paragraph", f"Unexpected text: {spans[0].get_text()}"
    print("  ✓ Basic consecutive spans merged correctly")
    
    # Test case 2: Spans with different styles should not merge
    html = '''<div><span style="char_one">text1</span><span style="char_two">text2</span></div>'''
    soup = BeautifulSoup(html, 'lxml-xml')
    merge_consecutive_spans(soup)
    result = str(soup)
    
    soup_result = BeautifulSoup(result, 'lxml-xml')
    spans = soup_result.find_all('span')
    assert len(spans) == 2, f"Expected 2 spans, got {len(spans)}"
    print("  ✓ Spans with different styles not merged")
    
    # Test case 3: Non-consecutive spans should not merge
    html = '''<div><span style="char_one">text1</span> some text <span style="char_one">text2</span></div>'''
    soup = BeautifulSoup(html, 'lxml-xml')
    merge_consecutive_spans(soup)
    result = str(soup)
    
    soup_result = BeautifulSoup(result, 'lxml-xml')
    spans = soup_result.find_all('span')
    assert len(spans) == 2, f"Expected 2 spans, got {len(spans)}"
    print("  ✓ Non-consecutive spans not merged")
    
    # Test case 4: Multiple groups of consecutive spans
    html = '''<div><span style="s1">a</span><span style="s1">b</span> text <span style="s2">c</span><span style="s2">d</span></div>'''
    soup = BeautifulSoup(html, 'lxml-xml')
    merge_consecutive_spans(soup)
    result = str(soup)
    
    soup_result = BeautifulSoup(result, 'lxml-xml')
    spans = soup_result.find_all('span')
    assert len(spans) == 2, f"Expected 2 spans, got {len(spans)}"
    print("  ✓ Multiple groups merged correctly")
    
    # Test case 5: Spans separated by newlines (hard returns) should merge with normalized whitespace
    # Testing the exact scenario from the problem statement where spans are separated by hard returns
    html = '<div><span style="span2">I</span> \n<span style="span2">am badly</span><span style="span2"> formatted</span></div>'
    soup = BeautifulSoup(html, 'lxml-xml')
    merge_consecutive_spans(soup)
    result = str(soup)
    
    soup_result = BeautifulSoup(result, 'lxml-xml')
    spans = soup_result.find_all('span')
    assert len(spans) == 1, f"Expected 1 span, got {len(spans)}"
    # Check that newline was converted to space
    assert spans[0].get_text() == "I am badly formatted", f"Expected 'I am badly formatted', got '{spans[0].get_text()}'"
    print("  ✓ Spans separated by newlines merged with normalized whitespace")
    
    print("All merge_consecutive_spans tests passed!\n")


def test_add_chapter_headings():
    """Test adding chapter headings to empty paragraphs."""
    print("Testing add_chapter_headings...")
    
    # Test case 1: Empty paragraph after body
    html = '''<?xml version="1.0"?>
<html>
<body>
<p></p>
<p>Some content</p>
</body>
</html>'''
    
    soup = BeautifulSoup(html, 'lxml-xml')
    changes, count = add_chapter_headings(soup)
    assert changes == True, "Expected changes to be made"
    
    # Check that placeholder was added
    placeholder = soup.find(attrs={'data-chapter-placeholder': 'true'})
    assert placeholder is not None, "Expected placeholder to be added"
    print("  ✓ Empty paragraph marked for chapter heading")
    
    # Test case 2: Paragraph with only whitespace
    html = '''<?xml version="1.0"?>
<html>
<body>
<p>   </p>
<p>Some content</p>
</body>
</html>'''
    
    soup = BeautifulSoup(html, 'lxml-xml')
    changes, count = add_chapter_headings(soup)
    assert changes == True, "Expected changes for whitespace-only paragraph"
    print("  ✓ Whitespace-only paragraph marked for chapter heading")
    
    # Test case 3: Non-empty paragraph should not be changed
    html = '''<?xml version="1.0"?>
<html>
<body>
<p>Existing content</p>
<p>Some content</p>
</body>
</html>'''
    
    soup = BeautifulSoup(html, 'lxml-xml')
    changes, count = add_chapter_headings(soup)
    assert changes == False, "Expected no changes for non-empty paragraph"
    print("  ✓ Non-empty paragraph not changed")
    
    print("All add_chapter_headings tests passed!\n")


def test_process_xhtml_content():
    """Test the full processing pipeline."""
    print("Testing process_xhtml_content...")
    
    # Test with both features
    html = '''<?xml version="1.0"?>
<html>
<body>
<p>  </p>
<p>this <span style="char_one">is a</span><span style="char_one"> test</span></p>
</body>
</html>'''
    
    result, new_chapter_num = process_xhtml_content(html, 5)
    
    # Parse result
    soup = BeautifulSoup(result, 'lxml-xml')
    
    # Check chapter was added
    body = soup.find('body')
    first_p = None
    for child in body.children:
        if hasattr(child, 'name') and child.name == 'p':
            first_p = child
            break
    
    assert first_p is not None, "Expected to find first paragraph"
    assert first_p.get_text().strip() == "Chapter 5", f"Expected 'Chapter 5', got '{first_p.get_text().strip()}'"
    print("  ✓ Chapter heading added with correct number")
    
    # Check spans were merged
    spans = soup.find_all('span')
    assert len(spans) == 1, f"Expected 1 span after merge, got {len(spans)}"
    print("  ✓ Consecutive spans merged")
    
    # Check chapter number incremented
    assert new_chapter_num == 6, f"Expected chapter number 6, got {new_chapter_num}"
    print("  ✓ Chapter number incremented")
    
    print("All process_xhtml_content tests passed!\n")


if __name__ == '__main__':
    print("Running EPUB cleanup tests...\n")
    test_merge_consecutive_spans()
    test_add_chapter_headings()
    test_process_xhtml_content()
    print("All tests passed! ✓")

#!/usr/bin/env python3
"""
EPUB Cleanup Script

This script processes EPUB files to:
1. Merge consecutive spans with the same style attribute
2. Replace empty paragraphs after <body> tags with "Chapter X" headings
"""

import sys
import os
import zipfile
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag


def merge_consecutive_spans(soup):
    """
    Merge consecutive span elements that have the same style attribute.
    
    Args:
        soup: BeautifulSoup object containing the HTML/XHTML content
    
    Returns:
        Boolean indicating if any changes were made
    """
    changes_made = False
    
    # Find all span elements
    spans = soup.find_all('span')
    
    i = 0
    while i < len(spans):
        current_span = spans[i]
        
        # Check if current span has a style attribute
        if not current_span.has_attr('style'):
            i += 1
            continue
        
        current_style = current_span.get('style')
        
        # Look for consecutive spans with the same style
        spans_to_merge = [current_span]
        next_sibling = current_span.next_sibling
        
        # Check immediate next siblings
        while next_sibling:
            # Allow text nodes that are only whitespace between spans
            if isinstance(next_sibling, NavigableString):
                if str(next_sibling).strip() == '':
                    # Continue past whitespace
                    next_sibling = next_sibling.next_sibling
                    continue
                else:
                    # Non-empty text node breaks the chain
                    break
            
            # Check if it's a span with the same style
            if (isinstance(next_sibling, Tag) and 
                next_sibling.name == 'span' and 
                next_sibling.has_attr('style') and
                next_sibling.get('style') == current_style):
                
                spans_to_merge.append(next_sibling)
                next_sibling = next_sibling.next_sibling
            else:
                # Different element or different style breaks the chain
                break
        
        # If we found consecutive spans to merge
        if len(spans_to_merge) > 1:
            changes_made = True
            
            # Strategy: collect all nodes between first and last span (inclusive)
            first_span = spans_to_merge[0]
            last_span = spans_to_merge[-1]
            
            # Collect everything from first span to last span
            merged_content = []
            current = first_span
            
            while current:
                if current == last_span:
                    # Include last span's content and break
                    for content in current.contents:
                        merged_content.append(content.extract() if isinstance(content, Tag) else str(content))
                    break
                elif current == first_span:
                    # Include first span's content
                    for content in current.contents:
                        merged_content.append(content.extract() if isinstance(content, Tag) else str(content))
                elif current in spans_to_merge:
                    # Include other span's content
                    for content in current.contents:
                        merged_content.append(content.extract() if isinstance(content, Tag) else str(content))
                elif isinstance(current, NavigableString):
                    # Include whitespace text nodes
                    merged_content.append(str(current))
                
                current = current.next_sibling
            
            # Clear and repopulate the first span with all merged content
            first_span.clear()
            for content in merged_content:
                if isinstance(content, str):
                    first_span.append(NavigableString(content))
                else:
                    first_span.append(content)
            
            # Remove intermediate whitespace and other spans
            for span in spans_to_merge[1:]:
                # Remove whitespace before this span
                prev = span.previous_sibling
                while prev and isinstance(prev, NavigableString) and str(prev).strip() == '':
                    to_remove = prev
                    prev = prev.previous_sibling
                    to_remove.extract()
                # Remove the span itself
                span.decompose()
            
            # Update the spans list since we modified the tree
            spans = soup.find_all('span')
            # Don't increment i, check the same position again
            continue
        
        i += 1
    
    return changes_made


def add_chapter_headings(soup):
    """
    Find empty paragraphs immediately after <body> tags and replace them
    with "Chapter X" where X is an incrementing number.
    
    Args:
        soup: BeautifulSoup object containing the HTML/XHTML content
    
    Returns:
        Tuple of (changes_made, chapter_number) for tracking across documents
    """
    changes_made = False
    
    # Find body tag
    body = soup.find('body')
    if not body:
        return changes_made, 0
    
    # Get the first child element after body
    first_child = None
    for child in body.children:
        if isinstance(child, Tag):
            first_child = child
            break
    
    # Check if it's an empty paragraph
    if first_child and first_child.name == 'p':
        # Check if paragraph is empty or contains only whitespace
        text_content = first_child.get_text().strip()
        if text_content == '':
            changes_made = True
            # This will be replaced with chapter numbering by the caller
            # Mark it with a special attribute for now
            first_child['data-chapter-placeholder'] = 'true'
    
    return changes_made, 1 if changes_made else 0


def process_xhtml_content(content, chapter_number):
    """
    Process XHTML content to merge spans and add chapter headings.
    
    Args:
        content: String containing XHTML content
        chapter_number: Current chapter number for incrementing
    
    Returns:
        Tuple of (processed_content, new_chapter_number)
    """
    soup = BeautifulSoup(content, 'lxml-xml')
    
    # First, merge consecutive spans
    merge_consecutive_spans(soup)
    
    # Then, handle chapter headings
    changes_made, chapter_added = add_chapter_headings(soup)
    
    # Replace placeholder with actual chapter text
    if chapter_added:
        placeholder = soup.find(attrs={'data-chapter-placeholder': 'true'})
        if placeholder:
            placeholder.clear()
            placeholder.string = f"Chapter {chapter_number}"
            del placeholder['data-chapter-placeholder']
            chapter_number += 1
    
    return str(soup), chapter_number


def process_epub(input_path, output_path=None):
    """
    Process an EPUB file to clean up spans and add chapter headings.
    
    Args:
        input_path: Path to input EPUB file
        output_path: Path to output EPUB file (if None, overwrites input)
    """
    if output_path is None:
        output_path = input_path
    
    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract EPUB (which is a ZIP file)
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_path)
        
        # Process all XHTML/HTML files
        chapter_number = 1
        for file_path in temp_path.rglob('*.xhtml'):
            chapter_number = process_file(file_path, chapter_number)
        
        for file_path in temp_path.rglob('*.html'):
            chapter_number = process_file(file_path, chapter_number)
        
        # Create new EPUB
        create_epub(temp_path, output_path)


def process_file(file_path, chapter_number):
    """Process a single XHTML/HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    processed_content, new_chapter_number = process_xhtml_content(content, chapter_number)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    return new_chapter_number


def create_epub(source_dir, output_path):
    """Create an EPUB file from a directory."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
        # The mimetype file must be first and uncompressed
        mimetype_path = source_dir / 'mimetype'
        if mimetype_path.exists():
            epub.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
        
        # Add all other files
        for file_path in source_dir.rglob('*'):
            if file_path.is_file() and file_path.name != 'mimetype':
                arcname = file_path.relative_to(source_dir)
                epub.write(file_path, arcname)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: epub_cleanup.py <input.epub> [output.epub]")
        print("\nProcesses an EPUB file to:")
        print("  - Merge consecutive spans with the same style")
        print("  - Replace empty paragraphs after <body> with 'Chapter X'")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)
    
    process_epub(input_path, output_path)
    print(f"Processed EPUB saved to: {output_path or input_path}")


if __name__ == '__main__':
    main()

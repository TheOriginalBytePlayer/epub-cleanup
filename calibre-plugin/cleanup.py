"""
Core cleanup functions for EPUB processing.
Shared between standalone script and Calibre plugin.
"""

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
                    # Include whitespace text nodes, but normalize newlines to spaces
                    # since hard returns have no effect on HTML display
                    text = str(current).replace('\n', ' ').replace('\r', ' ')
                    merged_content.append(text)
                
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


def number_to_words(n):
    """
    Convert a number to its word representation (1-100).
    
    Args:
        n: Integer to convert
    
    Returns:
        String representation of the number as words
    """
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 
             'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    
    if n < 10:
        return ones[n]
    elif n < 20:
        return teens[n - 10]
    elif n < 100:
        return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
    else:
        return str(n)  # Fall back to numeric for large numbers


def number_to_roman(n):
    """
    Convert a number to Roman numerals (1-3999).
    
    Args:
        n: Integer to convert
    
    Returns:
        String representation of the number as Roman numerals
    """
    values = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    
    result = ''
    for value, numeral in values:
        count = n // value
        if count:
            result += numeral * count
            n -= value * count
    return result


def format_chapter_number(number, numbering_style):
    """
    Format a chapter number according to the specified style.
    
    Args:
        number: Integer chapter number
        numbering_style: Style string ("Numeric", "Words", or "Roman Numerals")
    
    Returns:
        Formatted chapter number string
    """
    if 'Words' in numbering_style:
        return number_to_words(number)
    elif 'Roman' in numbering_style:
        return number_to_roman(number)
    else:  # Numeric
        return str(number)


def is_existing_chapter_heading(text, initial_chapter_text):
    """
    Check if text appears to be an existing chapter heading.
    
    Args:
        text: Text to check
        initial_chapter_text: The chapter text prefix (e.g., "Chapter")
    
    Returns:
        Boolean indicating if this looks like a chapter heading
    """
    import re
    text = text.strip()
    
    # Check for patterns like "Chapter 1", "Chapter I", "Chapter One", etc.
    patterns = [
        rf'^{re.escape(initial_chapter_text)}\s+\d+',  # Chapter 1
        rf'^{re.escape(initial_chapter_text)}\s+[IVX]+',  # Chapter I
        rf'^{re.escape(initial_chapter_text)}\s+[A-Z][a-z]+',  # Chapter One
    ]
    
    for pattern in patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    
    return False


def add_chapter_headings_with_config(soup, config, insert_as_p=False):
    """
    Find empty paragraphs immediately after <body> tags and replace them
    with chapter headings according to configuration.
    
    Args:
        soup: BeautifulSoup object containing the HTML/XHTML content
        config: Configuration dictionary with chapter heading settings
        insert_as_p: If True, insert heading even when first para is not empty/existing heading
    
    Returns:
        Tuple of (changes_made, chapter_added) where chapter_added is 1 if a chapter was added
    """
    changes_made = False
    chapter_added = 0
    
    # Find body tag
    body = soup.find('body')
    if not body:
        return changes_made, chapter_added
    
    # Get the first child element after body
    first_child = None
    for child in body.children:
        if isinstance(child, Tag):
            first_child = child
            break
    
    # Check if it's an empty paragraph or if we should insert
    if first_child and first_child.name == 'p':
        text_content = first_child.get_text().strip()
        
        # Check if paragraph is empty or contains only whitespace
        if text_content == '':
            changes_made = True
            chapter_added = 1
            first_child['data-chapter-placeholder'] = 'true'
        elif insert_as_p:
            # Check if it's NOT an existing chapter heading
            if not is_existing_chapter_heading(text_content, config.get('initial_chapter_text', 'Chapter')):
                # Insert a new <p> before the first paragraph
                changes_made = True
                chapter_added = 1
                new_p = soup.new_tag('p')
                new_p['data-chapter-placeholder'] = 'true'
                first_child.insert_before(new_p)
    
    return changes_made, chapter_added


def process_xhtml_content_with_config(content, chapter_number, config, should_cleanup, should_add_chapters):
    """
    Process XHTML content with configuration options.
    
    Args:
        content: String containing XHTML content
        chapter_number: Current chapter number for incrementing
        config: Configuration dictionary
        should_cleanup: Boolean, whether to clean up spans in this file
        should_add_chapters: Boolean, whether to add/modify chapters in this file
    
    Returns:
        Tuple of (processed_content, new_chapter_number)
    """
    soup = BeautifulSoup(content, 'lxml-xml')
    
    # Cleanup spans if requested
    if should_cleanup:
        merge_consecutive_spans(soup)
    
    # Add/modify chapter headings if requested
    chapter_added = 0
    if should_add_chapters:
        insert_as_p = config.get('insert_heading', False)
        changes_made, chapter_added = add_chapter_headings_with_config(soup, config, insert_as_p)
        
        # Replace placeholder with actual chapter text
        if chapter_added:
            placeholder = soup.find(attrs={'data-chapter-placeholder': 'true'})
            if placeholder:
                placeholder.clear()
                
                # Build the chapter heading string
                initial_text = config.get('initial_chapter_text', 'Chapter')
                numbering_style = config.get('numbering_style', 'Numeric (eg 1, 2, 3...)')
                text_following = config.get('text_following_number', '')
                
                chapter_num_str = format_chapter_number(chapter_number, numbering_style)
                
                # Combine parts
                heading_parts = [initial_text, chapter_num_str]
                if text_following:
                    heading_parts.append(text_following)
                
                heading_text = ' '.join(heading_parts)
                placeholder.string = heading_text
                del placeholder['data-chapter-placeholder']
                chapter_number += 1
    
    return str(soup), chapter_number

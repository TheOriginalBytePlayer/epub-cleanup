#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EPUB Cleanup Plugin for Calibre

This plugin processes EPUB files to:
1. Merge consecutive spans with the same style attribute
2. Replace empty paragraphs after <body> tags with "Chapter X" headings
"""

from calibre.customize import EditBookToolPlugin

class EPUBCleanupPlugin(EditBookToolPlugin):
    
    name = 'EPUB Cleanup'
    version = (1, 0, 0)
    author = 'EPUB Cleanup'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Clean up redundant spans and add chapter headings to EPUB files'
    minimum_calibre_version = (5, 0, 0)
    
    def run(self, path_to_ebook):
        """
        Run the plugin on an ebook.
        
        Args:
            path_to_ebook: Path to the ebook file being edited
        """
        from calibre.ebooks.oeb.polish.container import get_container
        from calibre.ebooks.oeb.base import OEB_DOCS
        from calibre_plugins.epub_cleanup.cleanup import process_xhtml_content
        
        # Get the book container
        container = get_container(path_to_ebook)
        
        chapter_number = 1
        
        # Process all HTML/XHTML files in the EPUB
        for name, mt in container.mime_map.items():
            if mt in OEB_DOCS:
                # Get the file content
                with container.open(name, 'rb') as f:
                    content = f.read().decode('utf-8')
                
                # Process the content
                processed_content, chapter_number = process_xhtml_content(content, chapter_number)
                
                # Write back the processed content
                with container.open(name, 'wb') as f:
                    f.write(processed_content.encode('utf-8'))
        
        # Commit changes to the container
        container.commit()
        
        return True

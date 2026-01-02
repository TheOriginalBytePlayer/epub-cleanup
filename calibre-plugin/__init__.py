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
        from calibre_plugins.epub_cleanup.config_dialog import ConfigDialog
        from calibre_plugins.epub_cleanup.cleanup import process_xhtml_content_with_config
        
        # Get the book container
        container = get_container(path_to_ebook)
        
        # Get all text files in reading order
        text_files = [name for name, mt in container.mime_map.items() if mt in OEB_DOCS]
        
        # Try to get the currently open file from the editor
        current_file_name = None
        current_file_content = None
        current_file_index = 0
        
        try:
            # Try to get the currently editing file
            from calibre.gui2.tweak_book.boss import get_boss
            boss = get_boss()
            if boss and hasattr(boss, 'currently_editing'):
                current_file_name = boss.currently_editing
                if current_file_name and current_file_name in text_files:
                    current_file_index = text_files.index(current_file_name)
                    with container.open(current_file_name, 'rb') as f:
                        current_file_content = f.read().decode('utf-8')
        except:
            pass
        
        # If we couldn't get current file, use the first one
        if not current_file_name and text_files:
            current_file_name = text_files[0]
            try:
                with container.open(current_file_name, 'rb') as f:
                    current_file_content = f.read().decode('utf-8')
            except:
                pass
        
        # Show configuration dialog
        try:
            from calibre.gui2.tweak_book.boss import get_boss
            parent = get_boss()
        except:
            parent = None
        
        dialog = ConfigDialog(parent, current_file_name, current_file_content)
        
        if dialog.exec_() != dialog.Accepted:
            # User cancelled
            return False
        
        # Get configuration from dialog
        config = dialog.get_config()
        
        # Determine which files to process based on scope
        files_to_process = []
        
        # Handle cleanup scope
        if config['cleanup_spans']:
            cleanup_scope = config['cleanup_scope']
            if cleanup_scope == "All Text Files":
                cleanup_files = text_files
            elif cleanup_scope == "Current File Only":
                cleanup_files = [current_file_name] if current_file_name else []
            else:  # Current File Onwards
                cleanup_files = text_files[current_file_index:] if current_file_name else text_files
        else:
            cleanup_files = []
        
        # Handle chapter scope
        if config['add_chapters']:
            chapter_scope = config['chapter_scope']
            if chapter_scope == "All Text Files":
                chapter_files = text_files
            elif chapter_scope == "Current File Only":
                chapter_files = [current_file_name] if current_file_name else []
            else:  # Current File Onwards
                chapter_files = text_files[current_file_index:] if current_file_name else text_files
        else:
            chapter_files = []
        
        # Combine the file lists (union of both)
        files_to_process = list(set(cleanup_files + chapter_files))
        # Sort to maintain original order
        files_to_process.sort(key=lambda x: text_files.index(x) if x in text_files else 0)
        
        # Process files
        chapter_number = config['start_number']
        
        for name in text_files:
            # Only process files that are in our processing list
            if name not in files_to_process:
                continue
            
            # Get the file content
            with container.open(name, 'rb') as f:
                content = f.read().decode('utf-8')
            
            # Determine what operations to perform on this file
            should_cleanup = name in cleanup_files
            should_add_chapters = name in chapter_files
            
            # Process the content
            processed_content, chapter_number = process_xhtml_content_with_config(
                content, 
                chapter_number,
                config,
                should_cleanup,
                should_add_chapters
            )
            
            # Write back the processed content
            with container.open(name, 'wb') as f:
                f.write(processed_content.encode('utf-8'))
        
        # Commit changes to the container
        container.commit()
        
        return True

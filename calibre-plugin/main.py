#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EPUB Cleanup Tool for Calibre Book Editor

This module defines the tool that appears in the Edit Book plugins menu.
"""

from calibre.gui2.tweak_book.plugin import Tool
from calibre.ebooks.oeb.polish.container import get_container
from calibre.ebooks.oeb.base import OEB_DOCS


class EPUBCleanupTool(Tool):
    """
    Tool for cleaning up EPUB files: merging redundant spans and adding chapter headings.
    """
    
    #: Set this to a unique name it will be used as a key
    name = 'epub-cleanup-tool'
    
    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True
    
    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True
    
    def create_action(self, for_toolbar=True):
        """
        Create the QAction that will trigger this tool.
        
        Args:
            for_toolbar: Boolean indicating if this is for the toolbar or menu
            
        Returns:
            QAction object
        """
        from qt.core import QAction
        from calibre.gui2 import get_icons
        
        # Create an action for the tool
        ac = QAction(get_icons('images/icon.png', allow_user_override=False), 'EPUB Cleanup', self.gui)
        
        if not for_toolbar:
            # Register a keyboard shortcut for the menu action only
            self.register_shortcut(ac, 'epub-cleanup-tool', default_keys=())
        
        ac.triggered.connect(self.run_tool)
        return ac
    
    def run_tool(self):
        """
        Execute the EPUB cleanup tool.
        Shows configuration dialog and processes selected files.
        """
        from calibre_plugins.epub_cleanup.config_dialog import ConfigDialog
        from calibre_plugins.epub_cleanup.cleanup import process_xhtml_content_with_config
        
        # Get the book container
        container = self.current_container
        if container is None:
            from calibre.gui2 import error_dialog
            return error_dialog(self.gui, 'No book open', 
                              'You must first open a book to edit.', show=True)
        
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
        dialog = ConfigDialog(self.gui, current_file_name, current_file_content)
        
        if dialog.exec_() != dialog.Accepted:
            # User cancelled
            return
        
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
        
        # Ensure any in-progress editing is saved to the container
        self.boss.commit_all_editors_to_container()
        
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
        
        # Mark the book as modified
        self.boss.mark_book_as_modified()
        
        # Show success message
        from calibre.gui2 import info_dialog
        info_dialog(self.gui, 'EPUB Cleanup Complete',
                   f'Successfully processed {len(files_to_process)} file(s).', show=True)

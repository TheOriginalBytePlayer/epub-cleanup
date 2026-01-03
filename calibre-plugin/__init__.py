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
    """
    Plugin entry point for EPUB Cleanup tool.
    The actual tool implementation is in main.py following calibre best practices.
    """
    
    name = 'EPUB Cleanup'
    version = (1, 0, 0)
    author = 'EPUB Cleanup'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Clean up redundant spans and add chapter headings to EPUB files'
    minimum_calibre_version = (5, 0, 0)
    
    #: This field defines the GUI plugin class that contains all the code
    #: that actually does something. Its format is module_path:class_name
    #: The specified class must be defined in the specified module.
    actual_plugin = 'calibre_plugins.epub_cleanup.main:EPUBCleanupTool'

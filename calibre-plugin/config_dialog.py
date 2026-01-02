#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration dialog for EPUB Cleanup Plugin
"""

from PyQt5.Qt import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QComboBox,
                       QLabel, QPushButton, QSpinBox, QLineEdit, QGroupBox,
                       QGridLayout)

from calibre.gui2 import error_dialog, info_dialog
from calibre.utils.config import JSONConfig


# Plugin configuration
prefs = JSONConfig('plugins/epub_cleanup')

# Set default values
prefs.defaults['initial_chapter_text'] = 'Chapter'
prefs.defaults['numbering_style'] = 'Numeric (eg 1, 2, 3...)'
prefs.defaults['text_following_number'] = ''


class ConfigDialog(QDialog):
    """Configuration dialog for EPUB Cleanup operations."""
    
    def __init__(self, parent, current_file_name=None, current_file_content=None):
        """
        Initialize the configuration dialog.
        
        Args:
            parent: Parent widget
            current_file_name: Name of the currently open file
            current_file_content: Content of the currently open file for chapter detection
        """
        QDialog.__init__(self, parent)
        self.setWindowTitle('EPUB Cleanup Configuration')
        self.current_file_name = current_file_name
        self.current_file_content = current_file_content
        
        self.setup_ui()
        self.load_preferences()
        self.update_control_states()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Section 1: Clean-up Redundant Spans
        cleanup_group = QGroupBox("Span Cleanup Options")
        cleanup_layout = QGridLayout()
        cleanup_group.setLayout(cleanup_layout)
        
        self.cleanup_checkbox = QCheckBox("Clean-up Redundant Spans in text")
        cleanup_layout.addWidget(self.cleanup_checkbox, 0, 0, 1, 2)
        
        cleanup_scope_label = QLabel("Perform Clean-Up in:")
        cleanup_layout.addWidget(cleanup_scope_label, 1, 0)
        
        self.cleanup_scope_combo = QComboBox()
        self.cleanup_scope_combo.addItems([
            "All Text Files",
            "Current File Only",
            "Current File Onwards"
        ])
        cleanup_layout.addWidget(self.cleanup_scope_combo, 1, 1)
        
        layout.addWidget(cleanup_group)
        
        # Section 2: Add/Renumber Chapter Headings
        chapter_group = QGroupBox("Chapter Heading Options")
        chapter_layout = QGridLayout()
        chapter_group.setLayout(chapter_layout)
        
        self.chapter_checkbox = QCheckBox("Add/Renumber Chapter Headings")
        chapter_layout.addWidget(self.chapter_checkbox, 0, 0, 1, 2)
        
        chapter_scope_label = QLabel("Add/Modify Chapter Headings:")
        chapter_layout.addWidget(chapter_scope_label, 1, 0)
        
        self.chapter_scope_combo = QComboBox()
        self.chapter_scope_combo.addItems([
            "All Text Files",
            "Current File Only",
            "Current File Onwards"
        ])
        chapter_layout.addWidget(self.chapter_scope_combo, 1, 1)
        
        start_num_label = QLabel("Start Numbering at:")
        chapter_layout.addWidget(start_num_label, 2, 0)
        
        self.start_number_spin = QSpinBox()
        self.start_number_spin.setMinimum(1)
        self.start_number_spin.setMaximum(9999)
        self.start_number_spin.setValue(self.detect_chapter_number())
        chapter_layout.addWidget(self.start_number_spin, 2, 1)
        
        initial_text_label = QLabel("Initial Chapter Text:")
        chapter_layout.addWidget(initial_text_label, 3, 0)
        
        self.initial_chapter_text = QLineEdit()
        self.initial_chapter_text.setText(prefs['initial_chapter_text'])
        chapter_layout.addWidget(self.initial_chapter_text, 3, 1)
        
        numbering_style_label = QLabel("Numbering Style:")
        chapter_layout.addWidget(numbering_style_label, 4, 0)
        
        self.numbering_style_combo = QComboBox()
        self.numbering_style_combo.addItems([
            "Numeric (eg 1, 2, 3...)",
            "Words (eg One, Two, Three...)",
            "Roman Numerals (eg I, II, III...)"
        ])
        chapter_layout.addWidget(self.numbering_style_combo, 4, 1)
        
        text_following_label = QLabel("Text Following Number:")
        chapter_layout.addWidget(text_following_label, 5, 0)
        
        self.text_following_number = QLineEdit()
        self.text_following_number.setText(prefs['text_following_number'])
        chapter_layout.addWidget(self.text_following_number, 5, 1)
        
        self.insert_heading_checkbox = QCheckBox(
            "Insert Chapter Heading as <p> in any file where the first paragraph "
            "of the file is neither blank nor an existing chapter heading"
        )
        chapter_layout.addWidget(self.insert_heading_checkbox, 6, 0, 1, 2)
        
        layout.addWidget(chapter_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals for conditional enabling
        self.cleanup_checkbox.stateChanged.connect(self.update_control_states)
        self.chapter_checkbox.stateChanged.connect(self.update_control_states)
        
        # Store references to chapter-related controls for easy enabling/disabling
        self.chapter_controls = [
            self.chapter_scope_combo,
            self.start_number_spin,
            self.initial_chapter_text,
            self.numbering_style_combo,
            self.text_following_number,
            self.insert_heading_checkbox
        ]
        
        self.chapter_labels = [
            chapter_scope_label,
            start_num_label,
            initial_text_label,
            numbering_style_label,
            text_following_label
        ]
    
    def detect_chapter_number(self):
        """
        Detect the starting chapter number from filename or file content.
        
        Returns:
            Integer starting chapter number (defaults to 1)
        """
        # Try to extract from filename first (e.g., "chapter_5.xhtml" -> 5)
        if self.current_file_name:
            import re
            # Look for numbers in the filename
            match = re.search(r'(\d+)', self.current_file_name)
            if match:
                return int(match.group(1))
        
        # Try to extract from content (look for "Chapter X" in first paragraph after body)
        if self.current_file_content:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(self.current_file_content, 'lxml-xml')
                body = soup.find('body')
                if body:
                    # Find first paragraph
                    first_p = None
                    for child in body.children:
                        if hasattr(child, 'name') and child.name == 'p':
                            first_p = child
                            break
                    
                    if first_p:
                        text = first_p.get_text().strip()
                        # Look for "Chapter X" pattern
                        import re
                        match = re.search(r'Chapter\s+(\d+)', text, re.IGNORECASE)
                        if match:
                            return int(match.group(1))
            except:
                pass
        
        # Default to 1
        return 1
    
    def load_preferences(self):
        """Load saved preferences."""
        self.initial_chapter_text.setText(prefs['initial_chapter_text'])
        self.text_following_number.setText(prefs['text_following_number'])
        
        # Set the numbering style from preferences
        numbering_style = prefs['numbering_style']
        index = self.numbering_style_combo.findText(numbering_style)
        if index >= 0:
            self.numbering_style_combo.setCurrentIndex(index)
    
    def save_preferences(self):
        """Save user preferences for next time."""
        prefs['initial_chapter_text'] = self.initial_chapter_text.text()
        prefs['numbering_style'] = self.numbering_style_combo.currentText()
        prefs['text_following_number'] = self.text_following_number.text()
    
    def update_control_states(self):
        """Update the enabled state of controls based on checkbox states."""
        # Enable/disable cleanup scope based on cleanup checkbox
        self.cleanup_scope_combo.setEnabled(self.cleanup_checkbox.isChecked())
        
        # Enable/disable chapter controls based on chapter checkbox
        chapter_enabled = self.chapter_checkbox.isChecked()
        for control in self.chapter_controls:
            control.setEnabled(chapter_enabled)
        for label in self.chapter_labels:
            label.setEnabled(chapter_enabled)
        
        # Enable Apply button only if at least one checkbox is checked
        at_least_one_checked = (self.cleanup_checkbox.isChecked() or 
                                self.chapter_checkbox.isChecked())
        self.apply_button.setEnabled(at_least_one_checked)
    
    def accept(self):
        """Handle Apply button click."""
        # Save preferences before accepting
        self.save_preferences()
        QDialog.accept(self)
    
    def get_config(self):
        """
        Get the configuration selected by the user.
        
        Returns:
            Dictionary with configuration options
        """
        return {
            'cleanup_spans': self.cleanup_checkbox.isChecked(),
            'cleanup_scope': self.cleanup_scope_combo.currentText(),
            'add_chapters': self.chapter_checkbox.isChecked(),
            'chapter_scope': self.chapter_scope_combo.currentText(),
            'start_number': self.start_number_spin.value(),
            'initial_chapter_text': self.initial_chapter_text.text(),
            'numbering_style': self.numbering_style_combo.currentText(),
            'text_following_number': self.text_following_number.text(),
            'insert_heading': self.insert_heading_checkbox.isChecked()
        }

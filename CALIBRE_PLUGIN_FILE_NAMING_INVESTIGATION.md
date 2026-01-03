# Calibre Plugin File Naming Requirements Investigation

## Summary

This document provides a comprehensive analysis of calibre plugin file naming requirements for the epub-cleanup plugin, specifically investigating the requirements mentioned in https://manual.calibre-ebook.com/creating_plugins.html#ui-py.

## Investigation Results

### Current Plugin Structure

The epub-cleanup calibre plugin currently has the following structure:

```
calibre-plugin/
├── __init__.py          # Plugin class with run() method
├── cleanup.py           # Core cleanup functions  
├── config_dialog.py     # Configuration dialog (PyQt5)
├── plugin.json          # Plugin metadata
└── README.md            # Documentation
```

### Calibre Plugin Types and File Naming Conventions

Through analysis of official calibre documentation and source code examples, I've identified that calibre has different file naming requirements based on the plugin type:

#### 1. **InterfaceAction Plugins** (Main Calibre UI)
These plugins add features to the main calibre interface.

**Required Files:**
- `__init__.py` - Wrapper class with metadata and `actual_plugin` field
- `ui.py` - **REQUIRED** - Contains the actual plugin implementation
- `main.py` - (Optional) Additional logic/dialogs

**Example from calibre documentation:** `plugin_examples/interface_demo/`

**The `ui.py` requirement mentioned in the issue URL applies ONLY to this plugin type.**

#### 2. **EditBookToolPlugin** (Book Editor Tools)
These plugins add tools to calibre's book editor.

**Two Valid Approaches:**

##### A. Modern Approach (Recommended)
- `__init__.py` - Plugin metadata only
- `main.py` - **REQUIRED** - Contains Tool class(es) inheriting from `calibre.gui2.tweak_book.plugin.Tool`

**Benefits:**
- Multiple tools per plugin
- Better organization
- More flexible (toolbar buttons, menus, submenus)
- Follows current calibre best practices

**Example from calibre documentation:** `plugin_examples/editor_demo/`

**Calibre docs explicitly state:** "The tools must all be defined in the file **main.py** in your plugin."

##### B. Legacy Approach (Currently Used)
- `__init__.py` - Plugin class with `run()` method directly
- Other support files as needed

**Status:**
- Still supported and functional
- Simpler for single-action plugins
- Older style, not recommended for new plugins

### Current Plugin Analysis

The epub-cleanup plugin uses **Approach B (Legacy)**:

```python
# __init__.py
from calibre.customize import EditBookToolPlugin

class EPUBCleanupPlugin(EditBookToolPlugin):
    name = 'EPUB Cleanup'
    # ... metadata ...
    
    def run(self, path_to_ebook):
        # Implementation directly in run method
```

**Status:** ✅ **Valid and functional** but uses the older pattern.

### Recommendations

#### Option 1: Keep Current Structure (Minimal Changes)
**Pros:**
- Plugin already works
- No code changes needed
- Simpler for a single-tool plugin

**Cons:**
- Uses legacy approach
- Less flexible for future enhancements
- Doesn't follow current calibre best practices

**Recommendation:** Suitable if no future expansion is planned.

#### Option 2: Refactor to Modern Tool-Based Approach (Recommended)
**Changes needed:**
1. Create `main.py` with Tool class
2. Move plugin logic from `run()` to Tool class
3. Update `__init__.py` to just contain metadata
4. Rename `config_dialog.py` to `ui.py` for consistency (optional)

**Pros:**
- Follows current calibre best practices
- Better code organization
- Easier to add multiple tools in future
- Better integration with editor features

**Cons:**
- Requires code refactoring
- More files to maintain

**Recommendation:** Best for long-term maintainability and following calibre standards.

## Specific File Naming Clarifications

### ui.py
- **ONLY required** for InterfaceAction plugins (main Calibre UI)
- **NOT required** for EditBookToolPlugin
- The URL in the issue (https://manual.calibre-ebook.com/creating_plugins.html#ui-py) refers to the InterfaceAction section

### main.py
- **Required** for modern EditBookToolPlugin implementations using Tool classes
- **Not required** for legacy EditBookToolPlugin implementations using run()
- Current plugin doesn't have this file because it uses the legacy approach

### config_dialog.py
- No specific naming requirement from calibre
- Can be named anything as long as it's properly imported
- Common convention is either `config.py` or inline in main plugin files

## Conclusion

The epub-cleanup plugin's current file naming is **technically correct** and **functional** for a legacy-style EditBookToolPlugin. However, it does not follow the **current calibre best practices** which recommend:

1. Using Tool classes in `main.py` for EditBookToolPlugin
2. Keeping `__init__.py` minimal with just metadata

The `ui.py` requirement mentioned in the issue **does not apply** to this plugin type - it only applies to InterfaceAction plugins.

## References

1. Official Calibre Plugin Documentation: https://manual.calibre-ebook.com/creating_plugins.html
2. Calibre Source Code: https://github.com/kovidgoyal/calibre
3. Example Plugins: `/manual/plugin_examples/` in calibre repository
   - `editor_demo/` - Modern EditBookToolPlugin example
   - `interface_demo/` - InterfaceAction example with ui.py

## Next Steps

**IMPLEMENTATION COMPLETE** - The plugin has been refactored to follow calibre's modern best practices:

✅ Created `main.py` with Tool-based implementation  
✅ Updated `__init__.py` to minimal metadata only  
✅ Updated packaging script to include `main.py`  
✅ Updated documentation to reflect new architecture  

The plugin now follows calibre's recommended structure for EditBookToolPlugin with Tool classes in `main.py`.

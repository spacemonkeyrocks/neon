# Release Notes

## Neon v0.2.1 - Help Formatting Fix

### What's new
- Added error formatting and improve argument group inheritance
- Introduced configurable error prefix in NeonConfig for better error messages
- Enhanced NeonArgumentParser to support inherited argument groups and subparsers
- Updated NeonFormatter to handle default argparse groups with custom error messages
- Improved theme management by ensuring themes are always merged with the default theme
- Moved all examples into a single file

### Bug Fixes
- Fixed help output formatting to always end with newline

## Neon v0.2.0 - API Rename & Installation Improvements

🔧 Major API rename and significant improvements to installation and release processes.

### What's New
- Smart dependency management in install script with version conflict detection
- Improved release packaging with exact dependency versions included
- Better installation experience with fixed interactive prompts

### Bug Fixes
- Fixed install script prompts not appearing when executed via `curl | bash`
- Fixed dependency conflict detection in install script

### Breaking Changes
- Complete API rename: All classes renamed from `Rich*` to `Neon*` prefix
- Import statements must be updated: `from neon import NeonArgumentParser`

## Neon v0.1.0 - Initial Release

🎉 First release of Neon - A Rich-based ArgumentParser with beautiful theming and complete layout control.

### What's New
- Rich integration for superior text rendering and theming capabilities
- Built-in color themes (default, green, blue, purple) with INI-based customization
- Smart text highlighting with automatic option and program name detection
- Table-based layout system with perfect alignment across all sections
- Custom sections support (Examples, Notes, and user-defined sections)
- Flexible configuration system - all parameters work directly or via Config object
- Method chaining API for fluent parser configuration
- Dynamic bullet standardization - recognizes multiple types, displays consistently
- Custom regex patterns for highlighting specific text (ERROR, WARNING, etc.)
- Backtick syntax highlighting for precise text formatting control
- Automatic column width calculation for optimal display
- One-line installation script with dependency management

### Bug Fixes
- N/A (Initial release)

### Breaking Changes
- N/A (Initial release)
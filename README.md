# neon

A powerful, Rich-based ArgumentParser formatter with beautiful color themes and complete layout control. Built with the `rich` library for superior text rendering and theming capabilities.

## ✨ Features

- 🎨 **Rich Integration** - Built on the powerful Rich library for superior text rendering
- 📦 **Lightweight** - Clean, maintainable code with minimal dependencies
- 🎯 **Better Defaults** - Works beautifully out of the box with minimal configuration
- 🔧 **Simple Themes** - Easy INI-based themes instead of complex configurations
- ⚡ **Better Performance** - Leverages Rich's optimized rendering engine
- 🧹 **Clean API** - Intuitive method chaining and configuration

## Features

- 🎨 **Rich Color Themes** - Beautiful themed output with built-in presets
- 📝 **Custom Sections** - Add Examples, Notes, and any custom sections to your help
- 🔧 **Table-Based Layout** - Perfect alignment across all sections automatically
- 🎯 **Smart Text Highlighting** - Dynamic option and program name highlighting
- 📏 **Consistent Alignment** - All sections align perfectly with no manual calculations
- ⚡ **Lightweight** - Only depends on `rich` library
- 🎨 **Custom Patterns** - Define custom regex patterns for highlighting specific text
- 🧹 **Smart Spacing** - Configurable indentation and section spacing

## Installation

### Quick Install (Recommended)

```bash
# Install to ./lib/neon in your current project
curl -sSL https://raw.githubusercontent.com/spacemonkeyrocks/neon/main/scripts/install.sh | bash
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/spacemonkeyrocks/neon.git neon
cd neon

# Create environment and install deps
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install rich

# Test
python examples.py
```

## Quick Start

```python
from neon import NeonArgumentParser

# Simple usage with beautiful defaults
parser = NeonArgumentParser(
    prog="mytool",
    description="A powerful CLI tool with beautiful help formatting",
    theme="blue"  # Built-in theme
)

# Add arguments
parser.add_argument('-u', '--user', required=True, help='Username for authentication')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
parser.add_argument('input', help='Input file to process')

# Add custom sections with method chaining
parser.add_examples("""
  mytool -u john file.txt
  mytool --user admin --verbose data.csv
""").add_notes("""
  • Configuration is read from ~/.mytool/config
  • Use `--user` and `--verbose` for detailed output
""").add_help_argument()

parser.print_help()
```

## Configuration

### Simple Configuration

```python
from neon import NeonArgumentParser, NeonConfig

# Custom configuration
config = NeonConfig(
    indent=4,                    # 4 spaces instead of default 2
    section_gap=2,               # More spacing between sections
    bullet_char="→",             # All bullets become arrows
    bullet_list=['•', '-', '*']  # Recognize these as bullets
    dyn_format=True,             # Enable dynamic highlighting
    max_width=100                # Custom terminal width
)

parser = NeonArgumentParser(
    prog="mytool",
    theme="green",
    config=config
)
```

### Available Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `indent` | `int` | `2` | Line indentation (number of spaces) |
| `section_gap` | `int` | `1` | Blank lines between sections |
| `dyn_format` | `bool` | `True` | Dynamic text highlighting |
| `bullet_char` | `str` | `"•"` | Standardize all bullets to this character (None to keep original) |
| `bullet_list` | `List[str]` | `['•', '◦', '▪', '▫', '-', '*']` | List of characters recognized as bullet points |
| `preserve_backticks` | `bool` | `False` | Keep backticks visible when highlighting backtick content |
| `max_width` | `Optional[int]` | `None` | Terminal width override (auto-detect if None) |
| `no_wrap_usage` | `bool` | `True` | Keep usage line unwrapped |
| `arg_column_width` | `Optional[int]` | `None` | Fixed width for argument/command column (None for auto-calculation) |

## Built-in Themes

### Available Presets

- **default** - Classic argparse colors (cyan args, orange groups)
- **green** - Nature-themed green palette
- **blue** - Ocean-themed blue palette  
- **purple** - Royal-themed purple/magenta palette

```python
# Use built-in themes
parser = NeonArgumentParser(theme="blue")
parser = NeonArgumentParser(theme="green")
```

### Custom Themes

Create custom themes with simple INI files:

```ini
# my_theme.ini
[theme]
argparse.args=bright_cyan bold
argparse.groups=yellow bold
argparse.help=white
argparse.metavar=green
argparse.text=grey70
argparse.prog=blue
argparse.syntax=magenta italic
argparse.default=grey50 italic
```

```python
# Load custom theme
parser = NeonArgumentParser(theme="my_theme.ini")
```

### Theme Elements

| Element | Description | Example |
|---------|-------------|---------|
| `argparse.args` | Argument names | `-u`, `--user` |
| `argparse.default` | Default values | `(default: value)` |
| `argparse.groups` | Group headers | `"Required Arguments:"` |
| `argparse.help` | Help text | `"Show this help message"` |
| `argparse.metavar` | Metavariables | `FILE` in `--file FILE` |
| `argparse.prog` | Program name | `mytool` in usage line |
| `argparse.syntax` | Backtick highlighted text | `` `code` `` |
| `argparse.text` | Descriptions and general text | Description, epilog |

## Dynamic Text Formatting

### Automatic Option Detection

When `dyn_format=True` (default), options in help text are automatically highlighted:

```python
parser.add_argument('--verbose', help='Use --verbose or -v for detailed output')
# Result: "Use --verbose or -v for detailed output"
#              ~~~~~~~~    ~~ (automatically colored)
```

### Backtick Syntax

Use backticks for precise highlighting control:

```python
parser.add_notes("""
  • Use `--user` to specify username
  • Edit `~/.config/mytool/config` for settings
  • Run `mytool --help` for more information
""")
```

### Program Name Highlighting

Program names are automatically colored when mentioned:

```python
parser = NeonArgumentParser(prog="mytool")
parser.add_examples('mytool input.txt --verbose')
# Result: "mytool input.txt --verbose"
#          ~~~~~~ (automatically colored)
```

### Custom Patterns

Define custom regex patterns for highlighting:

```python
parser = NeonArgumentParser(
    prog="tool",
    custom_patterns={
        r'-v{2,3}': 'args',          # Match -vv, -vvv
        r'\d+\.\d+\.\d+': 'metavar', # Version numbers
        r'\bERROR\b': 'groups'       # ERROR keyword
    }
)

# Or add patterns later
parser.add_pattern(r'\bWARNING\b', 'groups')
```

## Advanced Usage

### Method Chaining

```python
parser = NeonArgumentParser(prog="deploy") \
    .with_theme("purple") \
    .with_config(indent=4, bullet_char="→") \
    .add_header("Deploy Tool v2.0") \
    .add_examples("deploy --env production") \
    .add_notes("• Requires valid credentials") \
    .add_pattern(r'\bERROR\b', 'groups') \
    .add_help_argument()
```

### Custom Sections

```python
parser.add_examples("""
  deploy --env production --config prod.yml
  deploy --env staging --dry-run
""")

parser.add_notes("""
  • Requires valid credentials in ~/.deploy/auth
  • Use --dry-run to preview changes
""")

parser.add_custom_section("Environment Variables", """
  DEPLOY_API_KEY    API key for deployment service
  DEPLOY_LOG_LEVEL  Set to 'debug' for verbose logging
""")
```

### Argument Groups

```python
# Create custom argument groups
auth_group = parser.add_argument_group("Authentication")
auth_group.add_argument("--user", required=True, help="Username")
auth_group.add_argument("--token", help="API token (optional)")

backup_group = parser.add_argument_group("Backup Options")
backup_group.add_argument("--format", choices=['tar', 'zip'], help="Archive format")
backup_group.add_argument("--compress", action='store_true', help="Enable compression")
```

### Subcommands

```python
parser = NeonArgumentParser(prog="tool")

# Add subcommands
subparsers = parser.add_subparsers(dest="command", title="Commands")

# Create subcommand parsers
deploy_parser = subparsers.add_parser("deploy", description="Deploy application")
status_parser = subparsers.add_parser("status", description="Check deployment status")

# Add arguments to subcommands
deploy_parser.add_argument("--env", required=True, help="Target environment")
status_parser.add_argument("--format", choices=['json', 'table'], help="Output format")
```

## Best Practices

### 1. Use Built-in Themes First
```python
# Start with a preset
parser = NeonArgumentParser(theme="blue")

# Create custom theme only if needed
parser = NeonArgumentParser(theme="my_custom.ini")
```

### 2. Leverage Method Chaining
```python
parser = NeonArgumentParser(prog="tool") \
    .with_theme("green") \
    .add_examples("tool --input file.txt") \
    .add_notes("• Important notes here") \
    .add_help_argument()
```

### 3. Use Backticks for Precise Control
```python
# Good: Precise control
parser.add_notes("Use `--verbose` for detailed output")

# Automatic: May format unexpectedly in prose
parser.add_notes("Use --verbose for detailed output")
```

### 4. Group Related Arguments
```python
input_group = parser.add_argument_group("Input Options")
input_group.add_argument("--input", help="Input file")
input_group.add_argument("--format", help="Input format")

output_group = parser.add_argument_group("Output Options")
output_group.add_argument("--output", help="Output file")
output_group.add_argument("--quiet", help="Suppress output")
```

## Package Structure

```
neon/
├── neon/      # Main package
│   ├── __init__.py       # Main exports
│   ├── parser.py         # NeonArgumentParser
│   ├── formatter.py      # Rich-based formatter
│   ├── theme.py          # Theme management
│   ├── highlighting.py   # Smart text highlighting
│   ├── config.py         # Configuration
│   └── presets/          # Built-in themes
│       ├── default.ini
│       ├── green.ini
│       ├── blue.ini
│       └── purple.ini
└── examples.py           # Test examples
```

Import the main class:
```python
from lib.neon import NeonArgumentParser
```

## Requirements

- Python 3.8+ (for Rich library support)
- `rich` library for text rendering and theming
- ANSI color support in terminal

## Limitations

- Requires Rich library (single dependency)
- ANSI colors may not work in all terminals
- Rich markup in text should be escaped if not intended for formatting

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

MIT License. See [LICENSE.md](LICENSE.md) for details.
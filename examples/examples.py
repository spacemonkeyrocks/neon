#!/usr/bin/env python3
"""
Test examples for NeonArgumentParser demonstrating complete formatting control.
Updated for neon v3.0 with Rich-based implementation.
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neon import NeonArgumentParser, NeonConfig

def test_simple_usage():
    """Test simple usage example to verify basic functionality."""
    print(f"\n\n{pad_center('Simple Example Test', 100, '=')}")
    
    parser = NeonArgumentParser(
        prog="simple-tool",
        description="A simple example to test the Neon formatter.",
        add_help=False,
        # Library specific parameters can be set directly or in config, which is the preferred way
        config=NeonConfig(
            theme="default",
            max_width=60,
            dyn_format=True
        )
    )
    
    args_group = parser.add_argument_group("Options")
    args_group.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    args_group.add_argument("-v", "--verbose", action="count", default=argparse.SUPPRESS, help="Enable verbose output (verbose: -v, debug: -vv, trace: -vvv)")
    args_group.add_argument("-f", "--file", metavar="FILE", help="Input file path")
    args_group.add_argument("input", help="Input data to process")
    
    parser.add_notes("""
        - If --help or `--file` is --file /this/is/a/path not specified, it tries to read it from a config file located in `.env` or `~/.config/bh/bh.config`
        - Default values for `--file` and `--verbose` can be set in the config file of simple-tool
    """)
    
    parser.print_help()
    print()

def test_basic_example():
    """Test basic example with complete formatting control."""
    print(f"\n\n{pad_center('Basic Example Test', 100, '=')}")
    
    version = "1.0.1"
    version_text = f"substoforced {version}"
    
    # Custom examples and notes with preserved formatting
    examples = """
substoforced foo --folder /path/to/folder
substoforced baz
"""
    
    notes = """  - This substoforced tool is awesome.
  • Additional note here."""
    
    parser = NeonArgumentParser(
        prog="substoforced",
        description="A tool for Subtitle processing with complete formatting control.",
        epilog="To get help for a specific subcommand: substoforced <subcommand> --help",
        add_help=False,
        theme="purple",
        dyn_format=True
    )
    
    # Add custom sections
    parser.add_examples(examples)
    parser.add_notes(notes)
    parser.add_custom_section("Additional Info", "More information can be found in the documentation.")
    
    # Create argument groups
    required_group = parser.add_argument_group("Required Arguments")
    required_group.add_argument(
        "-s", "--sub", 
        metavar="SUB",
        required=True,
        help="Specifies the input SRT file."
    )

    optional_group = parser.add_argument_group("Optional Arguments")
    optional_group.add_argument(
        "-f", "--folder",
        metavar="DIR",
        help="Specifies a folder where generated timecodes are located (optional).\nThis text demonstrates multi-line help that should be correctly indented."
    )

    # Add help and version to their own group
    other_group = parser.add_argument_group("Other")
    other_group.add_argument('-h', '--help', action='help', help="Show this help message and exit")
    other_group.add_argument('--version', action='version', version=version_text, help="Show program's version number and exit")

    parser.add_notes([
        "• [red]IMPORTANT[/red]: The following two lines contain options that do NOT exist in the parser and therefore they are NOT highlighted:",
        "• If `--user` or `--pass` is not specified, it tries to read it from a config file located in `.env` or `~/.config/bh/bh.config`",
        "• Default values for `--ttl` and `--verbose` can be set in the config file",
        "• The should be highlighted without metavars `-f` or `--sub` is not specified, and this one with metavars --folder /this/is/a/path."  
    ])
    
    parser.add_examples([
        "substoforced -f /this/is/a/path --sub test.srv",
        "substoforced  --folder me -s test.srv",
        "substoforced --version",
        "substoforced --i-do-not-exist"
    ])

    parser.print_help()
    print()

def test_complex_example():
    """Test complex example with subcommands."""
    print(f"\n\n{pad_center('Complex Example Test (Main Command)', 100, '=')}")
    
    version = "1.1.1"
    header = f"bh v{version} - bhosted.nl DNS Tool"
    
    # Create main parser with custom patterns
    main_parser = NeonArgumentParser(
        prog="bh",
        header=header,
        description="Manage DNS records of bhosted.nl using the web services API.",
        theme="green",
        max_width=80,
        add_help=False,
        dyn_format=True,
        bullet_char="→",
        custom_patterns={
            r'-v{2,3}': 'args'  # Matches -vv or -vvv
        }
    )
    
    notes = """
    • If `--user` or `--pass` is not specified, they are read from a config file located in `.env` or `~/.config/bh/bh.config`
    - If `--user` or `--pass` is not specified, they are read from a config file located in `.env` or `~/.config/bh/bh.config`
    """
    main_parser.add_notes(notes)
    main_parser.add_custom_section("More Info", "To get help for a specific subcommand: bh <subcommand> --help")
    
    # Global options group (will be inherited by subcommands)def test_complex_example():
    """Test complex example with subcommands."""
    print(f"\n\n{pad_center('Complex Example Test (Main Command)', 100, '=')}")
    
    version = "1.1.1"
    header = f"bh v{version} - bhosted.nl DNS Tool"
    
    # Create main parser with custom patterns
    main_parser = NeonArgumentParser(
        prog="bh",
        header=header,
        description="Manage DNS records of bhosted.nl using the web services API.",
        theme="green",
        max_width=80,
        add_help=False,
        dyn_format=True,
        bullet_char="→",
        custom_patterns={
            r'-v{2,3}': 'args'  # Matches -vv or -vvv
        }
    )
    
    notes = """
    • If `--user` or `--pass` is not specified, they are read from a config file located in `.env` or `~/.config/bh/bh.config`
    - If `--user` or `--pass` is not specified, they are read from a config file located in `.env` or `~/.config/bh/bh.config`
    """
    main_parser.add_notes(notes)
    main_parser.add_custom_section("More Info", "To get help for a specific subcommand: bh <subcommand> --help")
    
    # Global options group (will be inherited by subcommands)
    global_group = main_parser.add_argument_group("Global Options", inherit=True)
    global_group.add_argument("-u", "--user", metavar="USER", help="Username for bhosted.nl control panel")
    global_group.add_argument("-p", "--pass", dest="password", metavar="PASS", help="Password for bhosted.nl control panel")
    global_group.add_argument("-v", "--verbose", action="count", default=argparse.SUPPRESS, help="Show debug messages (verbose: -v, debug: -vv, trace: -vvv)")
    
    # Other options group (NOT inherited)
    other_group = main_parser.add_argument_group("Other Options")
    other_group.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    other_group.add_argument("--version", action="version", version=header, help="Show program's version number and exit")
    
    # Add subcommands
    subparsers = main_parser.add_subparsers(
        dest="command",
        title="Commands",
        help="Available commands"
    )
    
    # Define subparsers with their own content
    add_parser = subparsers.add_parser(
        "add", 
        description="Add a new DNS record to the specified domain",
        help="Add a new DNS record"
    )
    add_parser.add_argument("domain", help="Domain name (e.g., example.com)")
    
    # Command-specific options for add
    cmd_group = add_parser.add_argument_group("Command Options")
    cmd_group.add_argument("-t", "--type", required=True, 
                           help="DNS record type (A, AAAA, MX, CNAME, SRV, TXT)")
    cmd_group.add_argument("--ip", help="IP address for A/AAAA records")
    cmd_group.add_argument("--content", help="Content for non-IP record types")
    cmd_group.add_argument("--ttl", type=int, default=3600, help="Time to live in seconds")
    cmd_group.add_argument("--prio", type=int, help="Priority for MX records")
    
    # Add subcommand-specific notes and examples
    add_parser.add_notes([
        "• If `--content` is not specified for MX records, use `--ip` parameter",
        "• Default TTL is 3600 seconds if not specified"
    ])
    
    add_parser.add_examples([
        "bh add -t A --ip 192.168.1.2 example.com",
        "bh add -t MX --content mail.example.com --prio 10 example.com"
    ])
    
    # Edit subparser
    edit_parser = subparsers.add_parser(
        "edit", 
        description="Edit an existing DNS record",
        help="Edit an existing DNS record"
    )
    edit_parser.add_argument("domain", help="Domain name")
    edit_group = edit_parser.add_argument_group("Edit Options")
    edit_group.add_argument("--id", required=True, help="Record ID to edit")
    edit_group.add_argument("-t", "--type", help="New record type")
    
    # Delete subparser
    delete_parser = subparsers.add_parser(
        "delete", 
        description="Delete an existing DNS record",
        help="Delete an existing DNS record"
    )
    delete_parser.add_argument("domain", help="Domain name")
    delete_group = delete_parser.add_argument_group("Delete Options")
    delete_group.add_argument("-t", "--type", required=True, help="Record type to delete")
    
    # Show subparser  
    show_parser = subparsers.add_parser(
        "show", 
        description="Display DNS records for the specified domain",
        help="Display DNS records"
    )
    show_parser.add_argument("domain", help="Domain name")
    show_group = show_parser.add_argument_group("Display Options")
    show_group.add_argument("--filter", help="Filter by record type")
    show_group.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    
    main_parser.add_examples([
        "• [red]IMPORTANT[/red]: The following lines contain options that do NOT exist in the parser and therefore they are NOT highlighted:",
        "bh --user $USER --pass $PASS add --type A --ip 192.168.1.2 example.com       Add an A record",
        "bh --user $USER --pass $PASS add --type MX --prio 1 --content mail.example.com example.com    Add MX record with priority",
        "bh --user $USER --pass $PASS show example.com --filter A   Show only A records",
        "bh --version"
    ])
    
    main_parser.print_help()
    print()
    
    # Test subcommand help to verify inheritance
    print(f"\n{pad_center('Subcommand Help Test (bh add --help)', 100, '-')}\n")
    try:
        # Simulate 'bh add --help'
        test_args = ['add', '--help']
        main_parser.parse_args(test_args)
    except SystemExit:
        # Help was printed, this is expected
        pass
    
    # Test error handling
    print(f"\n{pad_center('Error Handling Test (bh add)', 100, '-')}\n")
    try:
        # Simulate 'bh add' without required arguments
        test_args = ['add']
        main_parser.parse_args(test_args)
    except SystemExit:
        # Error was printed, this is expected
        pass
    
    # Test another error case
    print(f"\n{pad_center('Error Handling Test (bh add example.com)', 100, '-')}\n")
    try:
        # Simulate 'bh add example.com' without required --type
        test_args = ['add', 'example.com']
        main_parser.parse_args(test_args)
    except SystemExit:
        # Error was printed, this is expected
        pass

def test_subcommand_example():
    """Test subcommand example with custom configuration."""
    print(f"\n\n{pad_center('Complex Example Test (Subcommand)', 100, '=')}")
    
    version = "0.2.5"
    header = f"bh v{version} - bhosted.nl DNS Tool"
    
    # Create custom config
    config = NeonConfig(
        max_width=100,
        indent=2,
        section_gap=1,
        dyn_format=True,
        bullet_char="•",
        preserve_backticks=False,
        debug=False
    )
    
    # Create subcommand parser
    add_parser = NeonArgumentParser(
        prog="bh add",
        description="Add a new DNS record to bhosted.nl.",
        epilog="For more details, see the official API documentation.",
        theme="blue",
        config=config,
        header=header,
        custom_patterns={
            r'-v{2,3}': 'args'
        },
        add_help=False
    )
    
    add_parser.add_notes([
        "• If `--user` or `--pass` is not specified, it tries to read it from a config file located in `.env` or `~/.config/bh/bh.config`",
        "• Default values for `--ttl` and `--verbose` can be set in the config file, using --user name is cool"
    ])
    
    add_parser.add_examples([
        "bh add --type A --ip 192.168.1.2 example.com              Add an A record",
        "bh add --type MX --prio 1 --ip 192.168.1.2 example.com    Add MX record with priority",
        "bh add --type A --ttl 7200 --ip 192.168.1.2 example.com   Add an A record with custom TTL"
    ])
    
    # Arguments group
    args_group = add_parser.add_argument_group("Arguments")
    args_group.add_argument("domain", metavar="domain", help="Domain name (e.g., example.com)")
        
    # Global options group
    global_group = add_parser.add_argument_group("Global Options")
    global_group.add_argument("-u", "--user", metavar="USER", help="Username for bhosted.nl control panel")
    global_group.add_argument("-p", "--pass", dest="password", metavar="PASS", help="Password for bhosted.nl control panel")
    global_group.add_argument("-v", "--verbose", action="count", default=argparse.SUPPRESS, help="Show debug messages (verbose: -v, debug: -vv, trace: -vvv)")
    
    # Other options group
    other_group = add_parser.add_argument_group("Other Global Options")
    other_group.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    # Command specific options
    cmd_group = add_parser.add_argument_group("Required Options")
    cmd_group.add_argument("-t", "--type", metavar="TYPE", required=True, choices=["A", "AAAA", "CNAME", "MX", "SRV", "TXT"], help="DNS record type (valid: %(choices)s)")

    # Optional command options
    opt_cmd_group = add_parser.add_argument_group("Optional Options")
    opt_cmd_group.add_argument("-c", "--content", metavar="CONTENT", help="Content for `CNAME`, `MX`, `SRV`, and `TXT` records. Examples:"
         "\n- `www.example.com` (CNAME)\n- `mail.example.com` (MX), "
         "\n- `target.example.com:443` (SRV)\n- `\"SPF record text\"` (TXT).")
    opt_cmd_group.add_argument("--ip", metavar="IP", help="IP address for `A` and `AAAA` records, required for `--type` `A` or `AAAA`.")
    opt_cmd_group.add_argument("--prio", metavar="PRIO", type=int, default=10, help="Priority for MX records (default: %(default)s).")
    opt_cmd_group.add_argument("--ttl", metavar="TTL", type=int, default=3600, help="Time to live in seconds (default: %(default)s).")
    
    add_parser.print_help()
    print()

def test_extra_example():
    """Test method chaining and custom configuration."""
    print(f"\n\n{pad_center('Method Chaining Example', 100, '=')}")

    # Create parser with method chaining
    parser = NeonArgumentParser(
            prog="myapp",
            dyn_format=True
        ) \
        .with_theme("default") \
        .with_config(
            indent=4,                                     # 4 spaces instead of 2
            section_gap=2,                                # 2 lines between sections
            max_width=60,                                 # 60 characters wide
            bullet_char="→",                              # Different bullet
            bullet_list=['→', '▶', '★', '✓', '-', '*']   # Custom bullet list
        ) \
        .add_header("myapp 1.0.9 - File Processor") \
        .add_pattern(r'\bERROR\b', 'groups') \
        .add_pattern(r'\bWARNING\b', 'default')
    
    parser.description = "A sample application to demonstrate Neon ArgumentParser"
    
    # Add arguments
    args_group = parser.add_argument_group("Arguments")
    args_group.add_argument('input_file',  metavar='FILE', help='Input file to process')

    opts_group = parser.add_argument_group("Options")
    opts_group.add_argument('-o', '--output', metavar='FILE', help='Output file (default: stdout)')
    opts_group.add_argument('-v', '--verbose', action='count', default=argparse.SUPPRESS, help='Enable verbose output (verbose: -v, debug: -vv, trace: -vvv)')
    opts_group.add_argument('--format', choices=['json', 'xml', 'csv'], default='json', help='Output format (default: %(default)s)')
    
    # Add custom sections with method chaining
    parser.add_examples("""
Process a file with default settings:
    myapp input.txt

Process with custom output and format:
    myapp input.txt --output result.xml --format xml

Enable verbose mode:
    myapp input.txt --verbose
""").add_notes([
        "→ The input file must be readable and in a supported format.",
        "→ Use `--verbose` for detailed processing information.",
        "→ ERROR and WARNING messages will be highlighted.",
        "• Primary bullet point",
        "  ○ Secondary bullet point", 
        "    ▪ Tertiary bullet point",
        "→ Arrow bullet point",
        "★ Star bullet point"
    ]).add_help_argument()
    
    parser.print_help()
    
    print(f"\n\n\n{pad_center('Theme Parsing Test Arguments', 100, '=')}")
    test_args = ['test.txt', '--output', 'out.xml', '--format', 'xml', '--verbose']
    args = parser.parse_args(test_args)
    print(f"Parsed args: {args}")

def test_theme_showcase():
    """Showcase different themes."""
    print(f"\n\n{pad_center('Theme Showcase', 100, '=')}")
    
    themes = ["default", "green", "blue", "purple"]
    
    for theme_name in themes:
        print(f"\n{pad_center(theme_name.upper() + ' THEME', 100, '-')}\n")
        
        parser = NeonArgumentParser(
            prog="demo",
            description=f"Demonstration of {theme_name} theme",
            theme=theme_name,
            dyn_format=True
        )
        
        parser.add_header(theme_name.capitalize() + " Theme Showcase")
        parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
        parser.add_argument("--input", metavar="FILE", help="Input file")
        parser.add_notes(f"• This shows the {theme_name} theme with `--verbose` option highlighting")
        
        parser.print_help()
        
        print()

def test_subcommand_error_handling():
    """Test error handling in subcommands."""
    print(f"\n\n{pad_center('Testing Subcommand Error Handling', 100, '=')}")
    
    parser = NeonArgumentParser(
        prog="mytool",
        description="Test error handling in subcommands",
        theme="purple"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    test_parser = subparsers.add_parser("test", help="Test command")
    test_parser.add_argument("required_arg", help="This is required")
    test_parser.add_argument("-t", "--type", required=True, help="This is also required")
    
    print("Testing with missing arguments...")
    try:
        # This should trigger error handling
        parser.parse_args(['test'])
    except SystemExit:
        print("Error handling worked!")        

def test_inheritance_features():
    """Test inheritance features specifically."""
    print(f"\n\n{pad_center('Testing Inheritance Features', 100, '=')}")
    
    parser = NeonArgumentParser(
        prog="bh",
        description="DNS management tool",
        header="bh v1.0.0 - DNS Tool",
        theme="default",
        add_help=False
    )
    
    # Global options that will be inherited
    global_group = parser.add_argument_group("Global Options", inherit=True)
    global_group.add_argument("-h", "--help", action="help", help="Show help")
    global_group.add_argument("-u", "--user", help="Username")
    global_group.add_argument("-p", "--pass", dest="password", help="Password")
    global_group.add_argument("-v", "--verbose", action="count", help="Verbosity level")
    
    # Local options that won't be inherited  
    local_group = parser.add_argument_group("Other Options")
    local_group.add_argument("--version", action="version", version="1.0.0")
    
    parser.add_notes([
        "• Global options are inherited by all subcommands",
        "• Other options are only available on the main command"
    ])
    
    subparsers = parser.add_subparsers(dest="command",  title="Commands", help="Commands")
    
    add_parser = subparsers.add_parser("add", 
                                       description="Add a new DNS record",
                                       help="Add DNS record")
    add_parser.add_argument("domain", help="Domain name")
    add_parser.add_argument("-t", "--type", required=True, help="Record type")
    
    add_parser.add_notes([
        "• This subcommand has its own notes",
        "• But inherits Global Options from parent"
    ])
    
    print("=== Main Parser ===")
    parser.print_help()
    
    print("\n=== Subcommand Parser (shows inherited Global Options) ===")
    try:
        parser.parse_args(['add', '--help'])
    except SystemExit:
        pass

def test_auto_width():
    """Test automatic column width calculation."""
    print(f"\n\n{pad_center('Testing Automatic Column Width', 100, '=')}")
    
    parser = NeonArgumentParser(
        prog="mytool",
        description="A CLI tool demonstrating consistent column width.",
        theme="blue",
        add_help=False
    )
    
    # Add arguments with varying lengths
    global_group = parser.add_argument_group("Global Options", inherit=True)
    global_group.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    global_group.add_argument("-s", "--show", metavar="TYPE", help="Show information of specified type")
    global_group.add_argument("--do-not-speak", metavar="VERY_LONG_STUFF", help="Do not speak the very long stuff")
    global_group.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    global_group.add_argument("--config-file", metavar="PATH", help="Configuration file path")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", title="Commands", help="Available commands")
    
    build_parser = subparsers.add_parser("build", help="Build the project", description="Build the project with specified options.")
    build_parser.add_argument("--target", help="Build target")
    build_parser.add_argument("--optimization-level", metavar="LEVEL", help="Optimization level")
    
    run_parser = subparsers.add_parser("run", help="Run the application", description="Run the application with specified options.")
    run_parser.add_argument("--config-file-2", help="Configuration file")
    
    # Add argument groups
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--input-file", metavar="FILE", help="Input file path")
    input_group.add_argument("--input-format", metavar="FORMAT", help="Input format specification")
    
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("-o", "--output", metavar="FILE", help="Output file path")
    output_group.add_argument("--output-format", metavar="FORMAT", help="Output format")
    
    print(parser.format_help())

def test_fixed_width():
    """Test fixed column width."""
    print(f"\n\n{pad_center('Testing Fixed Column Width (30 chars)', 100, '=')}")
    
    config = NeonConfig(arg_column_width=30)
    parser = NeonArgumentParser(
        prog="mytool",
        description="A CLI tool with fixed column width.",
        config=config,
        theme="green"
    )
    
    # Add the same arguments
    global_group = parser.add_argument_group("Global Options", inherit=True)
    global_group.add_argument("-s", "--show", metavar="TYPE", help="Show information of specified type")
    global_group.add_argument("--do-not-speak", metavar="VERY_LONG_STUFF", help="Do not speak the very long stuff")
    global_group.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", title="Commands", help="Available commands")
    build_parser = subparsers.add_parser("build", help="Build the project", description="Available commands for mytool.")
    run_parser = subparsers.add_parser("run", help="Run the application", description="Run the application with specified options.")
    
    # Add argument groups
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--input-file", metavar="FILE", help="Input file path")
    
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("-o", "--output", metavar="FILE", help="Output file path")
    
    print(parser.format_help())

def test_error_def_group_arguments():
    """Test error handling for default group arguments."""
    print(f"\n\n{pad_center('Testing Error Handling for Arguments default group', 100, '=')}")
    
    parser = NeonArgumentParser(
        prog="mytool",
        description="A CLI tool demonstrating error handling for default group arguments.",
        theme="default"
    )
    
    # Add an argument to the default group
    parser.add_argument("input", help="Input file to process")
    
    # Add an optional argument
    opts_group = parser.add_argument_group("Options")
    opts_group.add_argument("-o", "--output", help="Output file path")
    
    try:
        # Simulate missing custom group
        parser.parse_args([])
    except SystemExit as e:
        print(f"Error: {e}")

def test_error_def_group_options():
    """Test error handling for default group options."""
    print(f"\n\n{pad_center('Testing Error Handling for Options default group', 100, '=')}")
    
    parser = NeonArgumentParser(
        prog="mytool",
        description="A CLI tool demonstrating error handling for default group options.",
        theme="default"
    )
    
    # Add an argument to a custom group
    args_group = parser.add_argument_group("Arguments")
    args_group.add_argument("input", help="Input file to process")
    
    # Add an option to the default group
    parser.add_argument("-o", "--output", help="Output file path")
    
    try:
        # Simulate missing custom group
        parser.parse_args([])
    except SystemExit as e:
        print(f"Error: {e}")

def pad_center(text: str, width: int, pad_char: str = '#') -> str:
    if len(text) >= width:
        return text
    
    # Add spaces for padding
    text = " " + text + " "  
    
    # Calculate total padding needed
    total_padding = width - len(text)
    
    # Split padding between left and right
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    
    # Build the centered string
    return pad_char * left_padding + text + pad_char * right_padding


if __name__ == "__main__":
    test_simple_usage()
    test_basic_example()
    test_complex_example() 
    test_subcommand_example()
    test_extra_example()
    test_theme_showcase()
    test_subcommand_error_handling()
    test_inheritance_features()
    test_auto_width()
    test_fixed_width()
    test_error_def_group_arguments()
    test_error_def_group_options()
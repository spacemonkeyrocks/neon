#!/usr/bin/env python3
"""
Test script to demonstrate consistent column width across argument groups.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neon import NeonArgumentParser, NeonConfig

def test_auto_width():
    """Test automatic column width calculation."""
    print("=== Testing Automatic Column Width ===")
    
    parser = NeonArgumentParser(
        prog="mytool",
        description="A CLI tool demonstrating consistent column width.",
        theme="blue",
        add_help=False
    )
    
    # Add arguments with varying lengths
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument("-s", "--show", metavar="TYPE", help="Show information of specified type")
    parser.add_argument("--do-not-speak", metavar="VERY_LONG_STUFF", help="Do not speak the very long stuff")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--config-file", metavar="PATH", help="Configuration file path")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    build_parser = subparsers.add_parser("build", help="Build the project", description="Build the project with specified options.")
    build_parser.add_argument("--target", help="Build target")
    build_parser.add_argument("--optimization-level", metavar="LEVEL", help="Optimization level")
    
    run_parser = subparsers.add_parser("run", help="Run the application", description="Run the application with specified options.")
    run_parser.add_argument("--config-file", help="Configuration file")
    
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
    print("\n=== Testing Fixed Column Width (30 chars) ===")
    
    config = NeonConfig(arg_column_width=30)
    parser = NeonArgumentParser(
        prog="mytool",
        description="A CLI tool with fixed column width.",
        config=config,
        theme="green"
    )
    
    # Add the same arguments
    parser.add_argument("-s", "--show", metavar="TYPE", help="Show information of specified type")
    parser.add_argument("--do-not-speak", metavar="VERY_LONG_STUFF", help="Do not speak the very long stuff")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    build_parser = subparsers.add_parser("build", help="Build the project", description="Available commands for mytool.")
    run_parser = subparsers.add_parser("run", help="Run the application", description="Run the application with specified options.")
    
    # Add argument groups
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--input-file", metavar="FILE", help="Input file path")
    
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("-o", "--output", metavar="FILE", help="Output file path")
    
    print(parser.format_help())

if __name__ == "__main__":
    test_auto_width()
    test_fixed_width()
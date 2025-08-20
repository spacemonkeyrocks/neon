import argparse
import re

from typing import Dict, Iterable, Optional
from rich.highlighter import RegexHighlighter
from rich.text import Text

class NeonHighlighter(RegexHighlighter):
    base_style = "argparse."

    # allow hyphenated long options and short options
    _OPT_TOKEN = r"--?[A-Za-z0-9][A-Za-z0-9-]*"

    def __init__(self, parser: argparse.ArgumentParser, config, custom_patterns: Optional[Dict[str, str]] = None):
        super().__init__()
        self.parser = parser
        self.config = config
        self._custom_patterns: Dict[str, str] = custom_patterns or {}

        # To ensure we do not start initializing while the argparser is not fully configured,
        # we use lazy initialization for options and compiled regex and initialize them
        # only when the first highlight() is called.
        self._options: Optional[Dict[str, dict]] = None        
        self._compiled = None

    # ----- public pattern API -----
    def add_pattern(self, pattern: str, style: str) -> None:
        self._custom_patterns[pattern] = self._normalize_style(style)

    def set_patterns(self, patterns: Dict[str, str]) -> None:
        self._custom_patterns = {p: self._normalize_style(s) for p, s in patterns.items()}

    # ----- RegexHighlighter hook -----
    def highlight(self, text: Text) -> None:
        # Ensure regex is compiled lazily (after parser is fully built)
        if self._compiled is None:
            self._build_regex()
            
        # If regex still isn't ready (parser not fully initialized), skip highlighting
        if self._compiled is None:
            return
        
        # Ensure options are collected lazily (after parser is fully built)
        if self._options is None or len(self._options) == 0:
            self._collect_options(self.parser)

        backtick_replacements = False

        # 1) custom patterns first (allow overrides)
        for pattern, style in self._custom_patterns.items():
            try:
                text.highlight_regex(pattern, style)
            except re.error:
                pass

        # 2) built-ins
        for match in self._compiled.finditer(text.plain):
            last = match.lastgroup
            
            if last == "prog" and match.group("prog"):
                # Highlight the prog
                prog_a, prog_b = match.span("prog")
                text.stylize(self.base_style + "prog", prog_a, prog_b)
                continue

            if last == "command":
                # Handle case where command is the last group matched
                if match.group("prog"):
                    prog_a, prog_b = match.span("prog")
                    text.stylize(self.base_style + "prog", prog_a, prog_b)
                
                if match.group("command"):
                    cmd_a, cmd_b = match.span("command")
                    text.stylize(self.base_style + "prog", cmd_a, cmd_b)
                continue

            if last == "version":
                a, b = match.span("version")
                text.stylize(self.base_style + "metavar", a, b)
                continue

            if last == "backtick":
                a, b = match.span("backtick")
                content = match.group("bt_content") or ""
                
                # Option-like? style as args; otherwise treat as code-ish
                if content in self._options:
                    # Exclude the backticks from styling
                    text.stylize(self.base_style + "args", a + 1, b - 1)
                    backtick_replacements = True
                elif re.fullmatch(self._OPT_TOKEN, content):
                    # It looks like an option but isn't defined - don't highlight
                    pass
                else:
                    # Exclude the backticks from styling
                    text.stylize(self.base_style + "syntax", a + 1 , b - 1)
                    backtick_replacements = True

            if (last == "args" or last == "metavar") and match.group("args"):
                opt = match.group("args")
                args_a, args_b = match.span("args")
                entry = self._options.get(opt) if self._options else None
                if entry:
                    text.stylize(self.base_style + "args", args_a, args_b)
                    # Only style metavar if action takes a value and metavar exists
                    mv = match.group("metavar")
                    if mv and entry["action"].metavar:
                        mv_a, mv_b = match.span("metavar")
                        text.stylize(self.base_style + "metavar", mv_a, mv_b)

        # 3) If preserve is disabled, remove the backticks
        if not self.config.preserve_backticks and backtick_replacements:
            new_text = self._remove_backticks_preserve_style(text)
            # Copy the new content back to the original text object
            text.plain = new_text.plain
            text._spans = new_text._spans
        
    # ----- internals -----
    def _remove_backticks_preserve_style(self, rich_text: Text) -> Text:
        combined_text = Text()
        last_end = 0
        
        for span in rich_text.spans:
            # Add any unstyled text before this span
            if last_end < span.start:
                plain_segment = rich_text.plain[last_end:span.start].replace('`', '')
                combined_text.append(plain_segment)
            
            # Add the styled segment with backticks removed
            styled_segment = rich_text.plain[span.start:span.end].replace('`', '')
            combined_text.append(styled_segment, style=span.style)  # Use span.style, not get_style_at()
            
            last_end = span.end
        
        # Add any remaining unstyled text after the last span
        if last_end < len(rich_text):
            trailing_text = rich_text.plain[last_end:].replace('`', '')
            combined_text.append(trailing_text)
        
        return combined_text

    def _build_regex(self) -> None:
        """Build the regex pattern based on current parser state."""
        parts = []
        
        if not self._initialization_complete(parser=self.parser):
            return

        # Build prog pattern based on current parser.prog
        if getattr(self.parser, "prog", None):
            prog_parts = self.parser.prog.split()
            
            if len(prog_parts) > 1:
                # This is a subcommand parser (e.g., "bh add")
                main_prog_escaped = re.escape(prog_parts[0])
                command_escaped = re.escape(prog_parts[1])
                prog_part = rf"(?P<prog>\b{main_prog_escaped}\b)(?:\s+(?P<command>\b{command_escaped}\b))?"
            else:
                # This is a main parser (e.g., "bh")
                prog_escaped = re.escape(self.parser.prog)
                prog_part = rf"(?P<prog>\b{prog_escaped}\b)"
            
            parts.append(prog_part)
        
        # Capture ANY backticked content (not only options)
        backtick_part = r"(?P<backtick>`(?P<bt_content>[^`]+)`)"
        parts.append(backtick_part)
        
        # Options with optional metavar
        option_part = rf"(?P<args>{self._OPT_TOKEN})(?:\s+(?P<metavar>\S+))?"
        parts.append(option_part)
        
        # Version pattern (e.g., v1.2.3)
        version_part = r"(?P<version>\bv?\d+\.\d+\.\d+\b)"
        parts.append(version_part)
        
        # Compile the final regex
        self._compiled = re.compile("|".join(parts))

    def _collect_options(self, parser: argparse.ArgumentParser) -> None:
        self._options = {}
        
        def actions_from(p: argparse.ArgumentParser):
            # Get actions from all action groups, not just p._actions
            all_actions = []
            
            # First, collect from the main parser actions
            all_actions.extend(p._actions)
            
            # Then collect from all action groups
            for group in p._action_groups:
                all_actions.extend(group._group_actions)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_actions = []
            for action in all_actions:
                if id(action) not in seen:
                    seen.add(id(action))
                    unique_actions.append(action)
            
            for i, act in enumerate(unique_actions):
                yield act
                
                if isinstance(act, argparse._SubParsersAction):
                    for sub_name, sub in act.choices.items():
                        yield from actions_from(sub)

        if not self._initialization_complete(parser):
            return

        for action in actions_from(parser):
            if not getattr(action, "option_strings", None):
                continue
            for opt in action.option_strings:
                self._options[opt] = {"action": action}    

    def _initialization_complete(self, parser: argparse.ArgumentParser) -> bool:
        # Check if parser is fully initialized
        total_actions = sum(len(group._group_actions) for group in parser._action_groups)
        if total_actions == 0:
            return False

        return True
        
    def _normalize_style(self, style: str) -> str:
        return style if style.startswith(self.base_style) else self.base_style + style.lstrip(".")
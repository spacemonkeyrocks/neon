# Contributing

Thanks for your interest in contributing! This library is designed for maintainability with clean, modular architecture.

## Setup

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows  
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Local Development

```bash
# Clone and setup
git clone https://github.com/spacemonkeyrocks/neon
cd neon

# Create environment and install deps
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt

# Test
python examples/examples.py

# Debug with ANSI output capture
script -c "python examples/examples.py" output.txt
```

## Making Changes

### Module Structure

- **Main API**: `neon/parser.py`
- **Core formatting**: `neon/formatter.py`  
- **Colors/styling**: `neon/theme.py`
- **Text processing**: `neon/highlighting.py`
- **Configuration**: `neon/config.py`

### Testing

1. **Edit** the appropriate module
2. **Test** with `examples/examples.py`
3. **Debug** with `config=NeonConfig(debug=True)` if needed

```bash
# Run all examples
python examples/examples.py

# Test specific example
python -c "
from examples.examples import test_simple_usage
test_simple_usage()
"
```

## Guidelines

- **Modular design**: Keep components focused and separate
- **Minimal dependencies**: Only `rich` library
- **Backward compatible**: Don't break existing APIs  
- **Clean interfaces**: Maintain clear module boundaries
- **Test manually**: Run examples to verify changes

## What to Contribute

- **Bug fixes**: Fix issues you encounter
- **Features**: Add useful functionality
- **Performance**: Make it faster
- **Documentation**: Improve README or docstrings
- **Themes**: Add new color presets

## What NOT to Contribute

- **Complex tooling**: Keep development simple
- **Over-engineering**: Maintain clean, readable code
- **Breaking changes**: Don't break existing APIs
- **Dependencies**: Don't add more dependencies

## Submitting

1. Fork the repo
2. Make your changes in the appropriate module
3. Test with the examples
4. Submit a PR with a clear description

Keep it clean! 🚀

## Creating Releases

### Prerequisites

Install GitHub CLI if you haven't already:
```bash
# macOS
brew install gh

# Linux/WSL
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh

# Windows
winget install --id GitHub.cli
```

Authenticate with GitHub:
```bash
gh auth login
```

### Release Process

1. **Update version** in `neon/__version__.py`:
   ```python
   __version__ = "0.2.0"  # Update to new version
   ```

2. **Create the distribution zip**:
   ```bash
   # Create clean zip with only library files
   cd neon
   zip -r ../neon.zip neon/
   cd ..
   ```

3. **Create and publish the release**:
   ```bash
   # Create release with zip asset
   gh release create v0.2.0 neon.zip \
     --title "Neon v0.2.0" \
     --notes "Release notes go here" \
     --latest
   ```

4. **Verify the release**:
   ```bash
   # Test that the install script works
   curl -sSL https://raw.githubusercontent.com/spacemonkeyrocks/neon/main/scripts/install.sh | bash
   ```

### Release Notes Template

Use this template for consistent release notes:
```markdown
## What's New
- Feature 1
- Feature 2

## Bug Fixes  
- Fix 1
- Fix 2

## Breaking Changes
- Change 1 (if any)

## Installation
```bash
curl -sSL https://raw.githubusercontent.com/spacemonkeyrocks/neon/main/scripts/install.sh | bash
```
```

### Automation

For frequent releases, use the included release script:
```bash
# Create a new release
./scripts/release.sh v0.2.0
```

The script automatically:
- Updates neon/__version__.py
- Commits the version change to git
- Creates an annotated git tag
- Pushes commits and tags to origin
- Creates the distribution zip
- Publishes the GitHub release
- Cleans up temporary files
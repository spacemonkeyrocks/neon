#!/bin/bash
# 🎨 styled-argparse installer script
# Downloads and installs styled-argparse from GitHub

set -e  # Exit on any error

REPO_URL="https://github.com/spacemonkeyrocks/styled-argparse"
DOWNLOAD_URL="https://github.com/spacemonkeyrocks/styled-argparse/archive/refs/heads/main.zip"
INSTALL_DIR="./lib"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  [INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ [SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  [WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}❌ [ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}🎨 styled-argparse installer${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check if curl or wget is available
if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
    print_error "curl or wget is required to download files. Please install one of them first."
    exit 1
fi

# Check if unzip is available
if ! command -v unzip &> /dev/null; then
    print_error "unzip is required to extract files. Please install unzip first."
    exit 1
fi

print_header
print_status "Installing styled-argparse to current directory..."

# Create lib directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Remove existing installation
if [ -d "$INSTALL_DIR/styled_argparse" ]; then
    print_status "🧹 Removing existing installation..."
    rm -rf "$INSTALL_DIR/styled_argparse"
fi

# Download the repository
print_status "📥 Downloading from $REPO_URL..."
if command -v curl &> /dev/null; then
    curl -L "$DOWNLOAD_URL" -o styled-argparse.zip
elif command -v wget &> /dev/null; then
    wget "$DOWNLOAD_URL" -O styled-argparse.zip
fi

# Extract files
print_status "📦 Extracting files..."
unzip -q styled-argparse.zip
mv styled-argparse-main/styled_argparse "$INSTALL_DIR/"
rm -rf styled-argparse-main styled-argparse.zip

# Add rich to requirements.txt
print_status "📋 Updating requirements.txt..."
if [ -f "requirements.txt" ]; then
    # Check if rich is already in requirements.txt
    if ! grep -q "^rich" requirements.txt; then
        echo "rich" >> requirements.txt
        print_status "Added 'rich' to existing requirements.txt"
    else
        print_status "'rich' already exists in requirements.txt"
    fi
else
    # Create requirements.txt with rich
    echo "rich" > requirements.txt
    print_status "Created requirements.txt with 'rich' dependency"
fi

# Dependencies will be installed manually by user

# Check if the module structure exists
print_status "🔍 Verifying download..."
if [ -f "$INSTALL_DIR/styled_argparse/__init__.py" ]; then
    print_success "styled-argparse downloaded successfully!"
else
    print_error "Download verification failed. Please check the installation manually."
    exit 1
fi

# Provide usage instructions
echo
print_success "🎉 Installation complete!"
echo
echo -e "${PURPLE}📚 Next Steps:${NC}"
echo
echo "  # Create environment and install deps"
echo "  uv venv"
echo "  source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows"
echo "  uv pip install rich"
echo
echo "  # Import in your Python code:"
echo "  from styled_argparse import RichArgumentParser"
echo
echo "  # Create your parser:"
echo "  parser = RichArgumentParser(description='🚀 My awesome CLI')"
echo "  parser.add_argument('--verbose', help='Enable verbose output')"
echo "  parser.add_help_argument()"
echo "  parser.print_help()"
echo
echo -e "${BLUE}📖 Documentation:${NC}"
echo "  Full documentation and examples: $REPO_URL/blob/main/README.md"
echo
print_warning "Downloaded to: $INSTALL_DIR/styled_argparse"
echo -e "${GREEN}🎨 Happy coding!${NC}"
#!/bin/bash
# 🎨 neon installer script
# Downloads and installs neon from GitHub

set -e  # Exit on any error

REPO_URL="https://github.com/spacemonkeyrocks/neon"
DOWNLOAD_URL="https://github.com/spacemonkeyrocks/neon/releases/latest/download/neon.zip"
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
    echo -e "${PURPLE}🎨 neon installer${NC}"
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
print_status "Installing neon to current directory..."

# Create lib directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Remove existing installation
if [ -d "$INSTALL_DIR/neon" ]; then
    print_status "🧹 Removing existing installation..."
    rm -rf "$INSTALL_DIR/neon"
fi

# Download the repository
print_status "📥 Downloading from $REPO_URL..."
if command -v curl &> /dev/null; then
    curl -L "$DOWNLOAD_URL" -o neon.zip
elif command -v wget &> /dev/null; then
    wget "$DOWNLOAD_URL" -O neon.zip
fi

# Extract files
print_status "📦 Extracting files..."
unzip -q neon.zip
mv neon-main/neon "$INSTALL_DIR/"
rm -rf neon-main neon.zip

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
if [ -f "$INSTALL_DIR/neon/__init__.py" ]; then
    print_success "neon downloaded successfully!"
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
echo "  from neon import RichArgumentParser"
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
print_warning "Downloaded to: $INSTALL_DIR/neon"
echo -e "${GREEN}🎨 Happy coding!${NC}"
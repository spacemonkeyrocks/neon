#!/bin/bash
# 🎨 neon installer script
# Downloads and installs neon from GitHub

set -e  # Exit on any error

REPO_URL="https://github.com/spacemonkeyrocks/neon"
DOWNLOAD_URL="https://github.com/spacemonkeyrocks/neon/archive/refs/heads/main.zip"
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

# Check for existing installation
if [ -d "$INSTALL_DIR/neon" ]; then
    print_warning "neon is already installed in $INSTALL_DIR/neon"
    read -p "Remove existing installation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "🧹 Removing existing installation..."
        rm -rf "$INSTALL_DIR/neon"
    else
        print_error "Installation cancelled"
        exit 1
    fi
fi

# Download the repository
print_status "📥 Downloading from $REPO_URL..."
if command -v curl &> /dev/null; then
    curl -s -L "$DOWNLOAD_URL" -o neon.zip
elif command -v wget &> /dev/null; then
    wget -q "$DOWNLOAD_URL" -O neon.zip
fi

# Extract files
print_status "📦 Extracting files..."
unzip -q neon.zip
mv neon-main/neon "$INSTALL_DIR/"
rm -rf neon-main neon.zip

# Dependencies will be installed manually by user
# Check if the module structure exists
print_status "🔍 Verifying download..."
if [ -f "$INSTALL_DIR/neon/__init__.py" ]; then
    print_success "neon downloaded successfully!"
else
    print_error "Download verification failed. Please check the installation manually."
    exit 1
fi

# Smart requirements.txt handling
print_status "📋 Managing dependencies..."

if [ -f "requirements.txt" ]; then
    print_warning "requirements.txt already exists"
    
    # Check if neon includes requirements.txt
    if [ -f "$INSTALL_DIR/neon/requirements.txt" ]; then
        print_status "Neon requires these dependencies:"
        cat "$INSTALL_DIR/neon/requirements.txt"
        echo
        
        # Process each dependency
        while IFS= read -r dep; do
            # Extract package name (before ==, >=, etc.)
            pkg_name=$(echo "$dep" | sed 's/[>=<!=].*//')
            
            if grep -q "^${pkg_name}[>=<!=]" requirements.txt 2>/dev/null; then
                # Package exists - check for version conflicts
                existing_line=$(grep "^${pkg_name}[>=<!=]" requirements.txt)
                if [ "$existing_line" != "$dep" ]; then
                    # Ask user about version conflict
                    print_warning "Version conflict detected:"
                    print_status "  Existing: $existing_line"
                    print_status "  Neon needs: $dep"
                    read -p "Replace with neon's version? (y/N): " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        # Create backup and replace the line
                        cp requirements.txt requirements.txt.bak
                        sed "s/^${pkg_name}[>=<!=].*/$dep/" requirements.txt.bak > requirements.txt
                        print_status "Updated '$pkg_name' to neon's version"
                    else
                        print_warning "Keeping existing version - neon may not work correctly"
                    fi
                else
                    print_success "'$pkg_name' already at correct version"
                fi
            else
                # Package missing - auto-add it
                echo "$dep" >> requirements.txt
                print_status "Added '$dep' to requirements.txt"
            fi
        done < "$INSTALL_DIR/neon/requirements.txt"
    else
        # Fallback to just rich if no requirements.txt in neon package
        if ! grep -q "^rich" requirements.txt; then
            echo "rich" >> requirements.txt
            print_status "Added 'rich' to existing requirements.txt"
        else
            print_status "'rich' already exists in requirements.txt"
        fi
    fi
else
    # No requirements.txt exists - create one
    if [ -f "$INSTALL_DIR/neon/requirements.txt" ]; then
        cp "$INSTALL_DIR/neon/requirements.txt" requirements.txt
        print_status "Created requirements.txt with neon dependencies"
    else
        # Fallback to just rich
        echo "rich" > requirements.txt
        print_status "Created requirements.txt with 'rich' dependency"
    fi
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
echo "  uv pip install -r requirements.txt"
echo
echo "  # Import in your Python code:"
echo "  from lib.neon import NeonArgumentParser"
echo
echo "  # Create your parser:"
echo "  parser = NeonArgumentParser(description='🚀 My awesome CLI')"
echo "  parser.add_argument('--verbose', help='Enable verbose output')"
echo "  parser.add_help_argument()"
echo "  parser.print_help()"
echo
echo -e "${BLUE}📖 Documentation:${NC}"
echo "  Full documentation and examples: $REPO_URL"
echo

print_warning "Downloaded to: $INSTALL_DIR/neon"

echo -e "${GREEN}🎨 Happy coding!${NC}"
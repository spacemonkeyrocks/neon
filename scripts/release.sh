#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./release.sh v0.1.0"
    exit 1
fi

# Extract version number without 'v' prefix
VERSION_NUMBER=${VERSION#v}

echo "🚀 Processing release $VERSION..."

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: You're on branch '$CURRENT_BRANCH', not 'main'"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted"
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted"
        exit 1
    fi
fi

# Check for untracked files
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have untracked or unstaged files:"
    git status --porcelain
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted"
        exit 1
    fi
fi

# Check if GitHub release already exists
echo "🔍 Checking if release $VERSION already exists..."
if gh release view "$VERSION" &>/dev/null; then
    echo "✅ Release $VERSION already exists - skipping creation"
    RELEASE_EXISTS=true
else
    echo "📝 Release $VERSION doesn't exist - will create"
    RELEASE_EXISTS=false
fi

# Check if git tag exists
if git tag -l | grep -q "^${VERSION}$"; then
    echo "✅ Git tag $VERSION already exists - skipping tag creation"
    TAG_EXISTS=true
else
    echo "🏷️  Git tag $VERSION doesn't exist - will create"
    TAG_EXISTS=false
fi

# Update version file if needed
CURRENT_VERSION=$(cat neon/__version__.py | grep -o '"[^"]*"' | sed 's/"//g')
if [ "$CURRENT_VERSION" != "$VERSION_NUMBER" ]; then
    echo "📝 Updating version from $CURRENT_VERSION to $VERSION_NUMBER..."
    echo "__version__ = \"$VERSION_NUMBER\"" > neon/__version__.py
    
    # Commit version change
    echo "📋 Committing version update..."
    git add neon/__version__.py
    git commit -m "Bump version to $VERSION_NUMBER"
    
    # Push the commit
    echo "⬆️  Pushing version commit..."
    git push origin main
else
    echo "✅ Version already set to $VERSION_NUMBER - skipping version update"
fi

# Create git tag if it doesn't exist
if [ "$TAG_EXISTS" = false ]; then
    echo "🏷️  Creating git tag $VERSION..."
    git tag -a "$VERSION" -m "Release $VERSION"
    
    # Push the tag
    echo "⬆️  Pushing tag..."
    git push origin "$VERSION"
else
    echo "✅ Tag already exists - skipping tag creation"
fi

# Create GitHub release if it doesn't exist
if [ "$RELEASE_EXISTS" = false ]; then
    # Create zip
    echo "📦 Creating distribution zip..."
    cd neon && zip -r ../neon.zip neon/ && cd ..
    
    # Create GitHub release
    echo "🎉 Creating GitHub release..."
    gh release create "$VERSION" neon.zip \
        --title "Neon $VERSION" \
        --generate-notes \
        --latest
    
    # Cleanup
    rm neon.zip
    
    echo "✅ Created release $VERSION successfully!"
else
    echo "✅ Release already exists - nothing to do!"
fi

echo "🔗 Release URL: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/releases/tag/$VERSION"
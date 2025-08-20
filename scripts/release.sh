#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./release.sh v0.2.0"
    exit 1
fi

# Extract version number without 'v' prefix
VERSION_NUMBER=${VERSION#v}

echo "🚀 Creating release $VERSION..."

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

# Update version file
echo "📝 Updating version to $VERSION_NUMBER..."
echo "__version__ = \"$VERSION_NUMBER\"" > neon/__version__.py

# Commit version change
echo "📋 Committing version update..."
git add neon/__version__.py
git commit -m "Bump version to $VERSION_NUMBER"

# Create git tag
echo "🏷️  Creating git tag $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION"

# Push changes and tag
echo "⬆️  Pushing to origin..."
git push origin main
git push origin "$VERSION"

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

echo "✅ Released $VERSION successfully!"
echo "🔗 Release URL: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/releases/tag/$VERSION"
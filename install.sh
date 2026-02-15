#!/bin/bash

# Antigravity Intelligence Matrix - Installation Script
# This script will backup your old files and install the fixed versions

set -e  # Exit on error

echo "🚀 Antigravity Intelligence Matrix - Installation Script"
echo "========================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "deepseek_client.py" ] || [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the antigravity_fix directory"
    exit 1
fi

# Get project path from user
echo "📂 Enter your Antigravity project path (e.g., /home/user/antigravity):"
read -r PROJECT_PATH

# Validate project path
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Error: Directory $PROJECT_PATH does not exist"
    exit 1
fi

# Create backup directory
BACKUP_DIR="$PROJECT_PATH/backup_$(date +%Y%m%d_%H%M%S)"
echo ""
echo "📦 Creating backup in: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR/services"

# Backup existing files
if [ -f "$PROJECT_PATH/app.py" ]; then
    cp "$PROJECT_PATH/app.py" "$BACKUP_DIR/"
    echo "✅ Backed up app.py"
fi

if [ -f "$PROJECT_PATH/services/search_agent.py" ]; then
    cp "$PROJECT_PATH/services/search_agent.py" "$BACKUP_DIR/services/"
    echo "✅ Backed up services/search_agent.py"
fi

if [ -f "$PROJECT_PATH/services/database.py" ]; then
    cp "$PROJECT_PATH/services/database.py" "$BACKUP_DIR/services/"
    echo "✅ Backed up services/database.py"
fi

if [ -f "$PROJECT_PATH/deepseek_client.py" ]; then
    cp "$PROJECT_PATH/deepseek_client.py" "$BACKUP_DIR/"
    echo "✅ Backed up deepseek_client.py"
fi

# Create services directory if it doesn't exist
mkdir -p "$PROJECT_PATH/services"

# Install new files
echo ""
echo "📥 Installing fixed files..."

cp deepseek_client.py "$PROJECT_PATH/"
echo "✅ Installed deepseek_client.py"

cp services/search_agent.py "$PROJECT_PATH/services/"
echo "✅ Installed services/search_agent.py"

cp services/database.py "$PROJECT_PATH/services/"
echo "✅ Installed services/database.py"

cp app.py "$PROJECT_PATH/"
echo "✅ Installed app.py"

cp README.md "$PROJECT_PATH/UPGRADE_README.md"
echo "✅ Installed UPGRADE_README.md"

# Check for .env file
echo ""
if [ -f "$PROJECT_PATH/.env" ]; then
    echo "✅ .env file found"
    
    # Check for required variables
    if ! grep -q "DEEPSEEK_API_KEY" "$PROJECT_PATH/.env"; then
        echo "⚠️  Warning: DEEPSEEK_API_KEY not found in .env"
    fi
    if ! grep -q "SUPABASE_URL" "$PROJECT_PATH/.env"; then
        echo "⚠️  Warning: SUPABASE_URL not found in .env"
    fi
    if ! grep -q "SUPABASE_KEY" "$PROJECT_PATH/.env"; then
        echo "⚠️  Warning: SUPABASE_KEY not found in .env"
    fi
else
    echo "⚠️  Warning: .env file not found"
    echo "   Create one with:"
    echo "   SUPABASE_URL=your_url"
    echo "   SUPABASE_KEY=your_key"
    echo "   DEEPSEEK_API_KEY=your_key"
fi

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade streamlit supabase openai duckduckgo-search beautifulsoup4 requests python-dotenv

echo ""
echo "========================================================="
echo "✅ Installation Complete!"
echo "========================================================="
echo ""
echo "📋 Next Steps:"
echo "1. Navigate to your project: cd $PROJECT_PATH"
echo "2. Verify your .env file has all required keys"
echo "3. Run the app: streamlit run app.py"
echo "4. Test the 🔍 Scavenge Data button"
echo ""
echo "📖 For troubleshooting, see: $PROJECT_PATH/UPGRADE_README.md"
echo ""
echo "🎉 Happy hunting!"

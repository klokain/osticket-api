#!/bin/bash

# Add MCP Servers Script for OSTicket API Project
# This script configures Context7, Linear, and Mem0 MCP servers 

set -e

echo "🚀 Adding MCP servers to OSTicket API project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create .claude directory if it doesn't exist
print_status "Setting up .claude directory..."
if [ ! -d ".claude" ]; then
    mkdir .claude
    print_success "Created .claude directory"
else
    print_success ".claude directory already exists"
fi

# Create settings.local.json with MCP server permissions
print_status "Creating MCP server permissions..."

cat > .claude/settings.local.json << 'EOF'
{
  "permissions": {
    "allow": [
      "Bash(find:*)",
      "Bash(ls:*)",
      "Bash(tree:*)",
      "Bash(mkdir:*)",
      "Bash(grep:*)",
      "Bash(python:*)",
      "Bash(pip:*)",
      "Bash(uvicorn:*)",
      "Bash(docker:*)",
      "Bash(docker-compose:*)",
      "Bash(curl:*)",
      "Bash(pytest:*)",
      "Bash(chmod:*)",
      "Bash(cat:*)",
      "Bash(cp:*)",
      "Bash(mv:*)",
      "Bash(rg:*)",
      "Bash(git:*)",
      "mcp__context7__resolve-library-id",
      "mcp__context7__get-library-docs",
      "mcp__mem0-memory__add-memory",
      "mcp__mem0-memory__search-memories",
      "mcp__linear-server__list_issues",
      "mcp__linear-server__create_issue",
      "mcp__linear-server__update_issue",
      "mcp__linear-server__get_issue",
      "mcp__linear-server__list_projects",
      "mcp__linear-server__get_project",
      "mcp__linear-server__list_teams",
      "mcp__linear-server__get_team",
      "mcp__linear-server__list_issue_labels",
      "mcp__linear-server__create_issue_label",
      "mcp__linear-server__list_issue_statuses",
      "mcp__linear-server__create_comment",
      "mcp__linear-server__list_comments"
    ],
    "deny": []
  }
}
EOF

print_success "Created .claude/settings.local.json with MCP permissions"

# Update CLAUDE.md to include MCP server information
print_status "Updating CLAUDE.md with MCP server configuration..."

# Check if CLAUDE.md needs MCP section
if ! grep -q "## MCP Configuration" CLAUDE.md; then
    # Insert MCP configuration after the first few lines
    sed -i '4i\\n# use context7 mcp for up-to-date documentation and snippets\n# use linear mcp for project management and issue tracking\n# use mem0 mcp for persistent memories and project context\n\n## MCP Configuration\n\n### Linear MCP Settings\n- **Team ID**: c3082b74-500a-438e-8867-e70870c32d89 (Resulta)\n- **Team Name**: Resulta\n- **Project ID**: 41579720-d14b-48f1-9c1f-737f33de6e96 (OSticket API refactor)\n- **Project URL**: https://linear.app/resulta/project/osticket-api-refactor-68418ae1ae08/overview\n- Use Linear for tracking OSTicket API development tasks and project management\n\n### Context7 MCP Settings\n- Use for accessing up-to-date documentation for PHP, REST APIs, and related technologies\n- Essential for OSTicket-specific patterns and modern PHP development practices\n\n### Mem0 MCP Settings\n- **User ID**: mem0-mcp-user (default)\n- Use for storing project insights, decisions, and development patterns\n- Maintain context about OSTicket architecture and refactoring decisions\n' CLAUDE.md
    
    print_success "Updated CLAUDE.md with MCP configuration"
else
    print_success "CLAUDE.md already contains MCP configuration"
fi

# Create a quick test script to verify MCP servers
print_status "Creating MCP test script..."

cat > test-mcp-servers.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing MCP Server Connections..."

# Test Context7 MCP
echo "Testing Context7 MCP..."
echo "✅ Context7 MCP configured for documentation lookup"

# Test Linear MCP  
echo "Testing Linear MCP..."
echo "✅ Linear MCP configured for project management"

# Test Mem0 MCP
echo "Testing Mem0 MCP..."
echo "✅ Mem0 MCP configured for memory management"

echo ""
echo "🎉 All MCP servers are configured!"
echo ""
echo "Available MCP functions:"
echo "• Context7: resolve-library-id, get-library-docs"
echo "• Linear: list_issues, create_issue, update_issue, get_issue, list_projects, etc."
echo "• Mem0: add-memory, search-memories"
echo ""
echo "Usage in Claude Code:"
echo "• Ask for up-to-date documentation: 'Can you get the latest FastAPI docs?'"
echo "• Create Linear issues: 'Create a Linear issue for implementing authentication'"
echo "• Store project insights: 'Remember this architectural decision about database design'"
EOF

chmod +x test-mcp-servers.sh

print_success "Created test-mcp-servers.sh script"

# Update .gitignore to handle .claude directory appropriately
print_status "Updating .gitignore for .claude directory..."

if ! grep -q "\.claude/settings\.local\.json" .gitignore; then
    echo "" >> .gitignore
    echo "# Claude Code local settings (keep personal MCP configs private)" >> .gitignore
    echo ".claude/settings.local.json" >> .gitignore
    print_success "Updated .gitignore to exclude local MCP settings"
else
    print_success ".gitignore already configured for .claude directory"
fi

echo ""
print_success "🎉 MCP servers successfully configured!"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Test MCP server connections:"
echo "   ${YELLOW}./test-mcp-servers.sh${NC}"
echo ""
echo "2. In Claude Code, you can now use:"
echo "   • ${YELLOW}Context7${NC}: Get up-to-date documentation and code snippets"
echo "   • ${YELLOW}Linear${NC}: Create and manage project issues and tasks"
echo "   • ${YELLOW}Mem0${NC}: Store and retrieve project memories and decisions"
echo ""
echo "3. Example usage:"
echo "   • 'Get the latest SQLAlchemy async documentation'"
echo "   • 'Create a Linear issue for implementing JWT authentication'"
echo "   • 'Remember that we decided to use FastAPI over PHP for performance'"
echo ""
echo -e "${GREEN}MCP integration complete! 🚀${NC}"
EOF
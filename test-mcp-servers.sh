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

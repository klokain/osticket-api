#!/bin/bash

# OSTicket API - Development Environment Setup Script
# This script sets up the development environment for OSTicket API project

set -e  # Exit on any error

echo "🚀 Setting up OSTicket API development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check if python3 is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    REQUIRED_VERSION="3.11"
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_warning "Python version $PYTHON_VERSION detected. Python 3.11+ is recommended."
    else
        print_success "Python version $PYTHON_VERSION is compatible."
    fi
}

# Setup OSTicket repository
setup_osticket() {
    print_status "Setting up OSTicket repository..."
    
    if [ ! -d "osTicket" ]; then
        print_status "Cloning OSTicket v1.18.x..."
        git clone -b 1.18.x https://github.com/osTicket/osTicket.git osTicket
        if [ $? -eq 0 ]; then
            print_success "OSTicket cloned successfully."
        else
            print_error "Failed to clone OSTicket repository."
            exit 1
        fi
    else
        print_status "OSTicket directory already exists, updating..."
        cd osTicket
        
        # Check if it's a git repository
        if [ ! -d ".git" ]; then
            print_error "osTicket directory exists but is not a git repository."
            print_status "Please remove the osTicket directory and run this script again."
            exit 1
        fi
        
        # Get current branch
        CURRENT_BRANCH=$(git branch --show-current)
        print_status "Current branch: $CURRENT_BRANCH"
        
        # Fetch latest changes
        git fetch origin
        
        # Switch to or update 1.18.x branch
        if [ "$CURRENT_BRANCH" != "1.18.x" ]; then
            print_status "Switching to 1.18.x branch..."
            git checkout -b 1.18.x origin/1.18.x 2>/dev/null || git checkout 1.18.x
        fi
        
        # Pull latest changes
        print_status "Pulling latest changes..."
        git pull origin 1.18.x
        
        cd ..
        print_success "OSTicket updated to latest 1.18.x version."
    fi
}

# Setup environment configuration
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example template."
            print_warning "Please edit .env file with your database credentials before running the API server."
        else
            print_warning ".env.example not found. Creating basic .env file..."
            cat > .env << EOF
# OSTicket Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=osticket
DB_USER=osticket
DB_PASSWORD=your_password_here
DB_PREFIX=ost_

# OSTicket Installation Path (for reference)
OSTICKET_PATH=./osTicket

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# FastAPI Configuration
API_V2_PREFIX=/api/v2
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"]

# Redis (for caching - optional)
REDIS_URL=redis://localhost:6379/0
EOF
            print_success "Created basic .env file."
            print_warning "Please edit .env file with your actual database credentials."
        fi
    else
        print_success ".env file already exists."
    fi
}

# Create api-server directory structure if it doesn't exist
setup_api_structure() {
    print_status "Setting up API server directory structure..."
    
    if [ ! -d "api-server" ]; then
        print_status "Creating api-server directory structure..."
        mkdir -p api-server/{app/{api/{v1,v2},core,models,schemas,services,utils},tests,docs}
        
        # Create basic __init__.py files
        touch api-server/app/__init__.py
        touch api-server/app/api/__init__.py
        touch api-server/app/api/v1/__init__.py
        touch api-server/app/api/v2/__init__.py
        touch api-server/app/core/__init__.py
        touch api-server/app/models/__init__.py
        touch api-server/app/schemas/__init__.py
        touch api-server/app/services/__init__.py
        touch api-server/app/utils/__init__.py
        touch api-server/tests/__init__.py
        
        print_success "API server directory structure created."
    else
        print_success "API server directory already exists."
    fi
}

# Create requirements.txt if it doesn't exist
create_requirements() {
    if [ ! -f "api-server/requirements.txt" ]; then
        print_status "Creating requirements.txt..."
        cat > api-server/requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
cryptography==41.0.7
pydantic==2.5.0
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
python-dotenv==1.0.0
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
alembic==1.12.1
EOF
        print_success "requirements.txt created."
    else
        print_success "requirements.txt already exists."
    fi
}

# Setup Python virtual environment
setup_python_env() {
    if [ ! -d "api-server" ]; then
        print_warning "api-server directory doesn't exist yet. Skipping Python environment setup."
        return
    fi
    
    cd api-server
    
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        if [ $? -eq 0 ]; then
            print_success "Virtual environment created."
        else
            print_error "Failed to create virtual environment."
            cd ..
            exit 1
        fi
    else
        print_success "Virtual environment already exists."
    fi
    
    # Check if requirements.txt exists before installing
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            print_success "Python dependencies installed."
        else
            print_error "Failed to install Python dependencies."
        fi
        deactivate
    else
        print_warning "requirements.txt not found. Skipping dependency installation."
    fi
    
    cd ..
}

# Create docs directory and move planning documents
organize_documentation() {
    print_status "Organizing documentation..."
    
    if [ ! -d "docs" ]; then
        mkdir docs
        print_success "Created docs directory."
    fi
    
    # Move planning documents to docs directory if they exist in root
    for doc in API_DEVELOPMENT_PLAN.md FASTAPI_IMPLEMENTATION_PLAN.md FASTAPI_VS_PHP_ANALYSIS.md COEXISTENCE_GUIDE.md; do
        if [ -f "$doc" ] && [ ! -f "docs/$doc" ]; then
            mv "$doc" "docs/"
            print_success "Moved $doc to docs/ directory."
        fi
    done
}

# Display final instructions
show_final_instructions() {
    echo ""
    print_success "🎉 Development environment setup complete!"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Edit .env file with your database credentials:"
    echo "   ${YELLOW}nano .env${NC}"
    echo ""
    echo "2. Start the FastAPI development server (when implemented):"
    echo "   ${YELLOW}cd api-server${NC}"
    echo "   ${YELLOW}source venv/bin/activate${NC}"
    echo "   ${YELLOW}uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
    echo ""
    echo "3. Access API documentation at:"
    echo "   ${YELLOW}http://localhost:8000/api/docs${NC}"
    echo ""
    echo -e "${BLUE}Development resources:${NC}"
    echo "• OSTicket installation: ${YELLOW}./osTicket/${NC}"
    echo "• API server code: ${YELLOW}./api-server/${NC}"
    echo "• Documentation: ${YELLOW}./docs/${NC}"
    echo "• Project context: ${YELLOW}./CLAUDE.md${NC}"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
}

# Main execution
main() {
    echo ""
    echo "=================================================="
    echo "   OSTicket API Development Environment Setup"
    echo "=================================================="
    echo ""
    
    check_prerequisites
    setup_osticket
    setup_environment
    organize_documentation
    setup_api_structure
    create_requirements
    setup_python_env
    show_final_instructions
}

# Run main function
main
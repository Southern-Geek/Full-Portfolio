# Document Format Converter

## Overview

This is a Flask-based document format converter application that allows users to upload documents in various formats (ODF, PDF, Word, Excel, PowerPoint) and convert them to different formats. The application provides a modern web interface with drag-and-drop functionality for file uploads.

## System Architecture

### Frontend Architecture
- **HTML Templates**: Jinja2 templating engine with Bootstrap dark theme
- **CSS Framework**: Bootstrap with Replit Agent dark theme for consistent UI
- **JavaScript**: Vanilla JavaScript for file upload handling and drag-and-drop functionality
- **UI Components**: 
  - Drag-and-drop upload zone
  - Format selection grid
  - File information display
  - Progress indicators

### Backend Architecture
- **Framework**: Flask web framework
- **WSGI Server**: Gunicorn for production deployment
- **File Handling**: Werkzeug utilities for secure file uploads
- **Middleware**: ProxyFix for proper header handling behind reverse proxies

### Data Storage Solutions
- **File Storage**: Local filesystem with organized directory structure
  - `uploads/` - Temporary storage for uploaded files
  - `converted/` - Temporary storage for converted files
- **Session Management**: Flask sessions with configurable secret key
- **No Database**: Application uses filesystem-only storage approach

## Key Components

### File Upload System
- **Max File Size**: 50MB limit
- **Supported Formats**: ODF (odt, ods, odp, odg, odf), PDF, Word (doc, docx), Excel (xls, xlsx), PowerPoint (ppt, pptx)
- **Security**: Secure filename handling and file type validation
- **Storage**: Organized temporary file storage with automatic directory creation

### Format Conversion Engine
- **Conversion Mappings**: Predefined format mappings for supported conversions
- **Processing**: Uses external conversion tools (likely LibreOffice/OpenOffice based on supported formats)
- **Output Management**: Organized output file handling with unique identifiers

### Web Interface
- **Responsive Design**: Bootstrap-based responsive layout
- **Dark Theme**: Consistent dark theme implementation
- **Interactive Elements**: Drag-and-drop file upload with visual feedback
- **File Management**: Real-time file information display and format selection

## Data Flow

1. **File Upload**: User drags/drops or selects file through web interface
2. **Validation**: File type and size validation on client and server side
3. **Storage**: Secure file storage in uploads directory with unique naming
4. **Format Selection**: User selects target conversion format
5. **Conversion**: Backend processes file conversion using external tools
6. **Output**: Converted file stored in converted directory
7. **Download**: User downloads converted file through web interface
8. **Cleanup**: Temporary files cleaned up after processing

## External Dependencies

### Python Packages
- **Flask**: Web framework (v3.1.1+)
- **Werkzeug**: WSGI utilities and security (v3.1.3+)
- **Gunicorn**: WSGI HTTP server (v23.0.0+)
- **Flask-SQLAlchemy**: ORM capabilities (v3.1.1+) - configured but not actively used
- **psycopg2-binary**: PostgreSQL adapter (v2.9.10+) - configured but not actively used
- **email-validator**: Email validation utilities (v2.2.0+)

### System Dependencies
- **OpenSSL**: SSL/TLS support
- **PostgreSQL**: Database server (configured but not used in current implementation)
- **LibreOffice/OpenOffice**: Document conversion engine (implied by supported formats)

### Frontend Dependencies
- **Bootstrap**: CSS framework via CDN
- **Feather Icons**: Icon library via CDN

## Deployment Strategy

### Container Configuration
- **Environment**: Nix-based development environment with Python 3.11
- **Channel**: Stable Nix channel (24_05)
- **Autoscale Deployment**: Configured for automatic scaling based on demand

### Server Configuration
- **WSGI Server**: Gunicorn with auto-reload for development
- **Binding**: All interfaces (0.0.0.0) on port 5000
- **Process Management**: Reuse-port configuration for better performance
- **Development Mode**: Hot reload enabled for development workflow

### Workflow Management
- **Run Button**: Integrated project startup
- **Parallel Execution**: Support for parallel task execution
- **Port Monitoring**: Automatic port availability checking

## Changelog

```
Changelog:
- June 25, 2025. Initial setup
- June 25, 2025. Enhanced with batch conversion, quality settings, preview functionality, and additional formats (RTF, CSV, TXT, HTML)
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## Notes for Development

- The application is set up with PostgreSQL and SQLAlchemy dependencies but currently uses filesystem-only storage
- Database integration can be added later for user management, conversion history, or file metadata
- The conversion engine is abstracted and can be extended to support additional formats
- Security measures include file type validation, size limits, and secure filename handling
- The interface is designed for both technical and non-technical users with intuitive drag-and-drop functionality
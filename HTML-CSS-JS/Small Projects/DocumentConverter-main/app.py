import os
import logging
import subprocess
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import mimetypes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    'odt', 'ods', 'odp', 'odg', 'odf',  # ODF formats
    'pdf',  # PDF
    'doc', 'docx', 'rtf',  # Word documents
    'xls', 'xlsx', 'csv',  # Excel spreadsheets
    'ppt', 'pptx',   # PowerPoint presentations
    'txt', 'html', 'htm'  # Additional text formats
}

# Conversion format mappings
FORMAT_MAPPINGS = {
    'pdf': 'pdf',
    'odt': 'odt',
    'ods': 'ods',
    'odp': 'odp',
    'doc': 'doc',
    'docx': 'docx',
    'rtf': 'rtf',
    'xls': 'xls',
    'xlsx': 'xlsx',
    'csv': 'csv',
    'ppt': 'ppt',
    'pptx': 'pptx',
    'txt': 'txt',
    'html': 'html'
}

# Quality settings for different formats
QUALITY_SETTINGS = {
    'pdf': {
        'high': ['--export-quality', '95'],
        'medium': ['--export-quality', '75'],
        'low': ['--export-quality', '50']
    },
    'jpg': {
        'high': ['--export-quality', '95'],
        'medium': ['--export-quality', '75'],
        'low': ['--export-quality', '50']
    }
}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_format(filename):
    """Get the format of a file from its extension."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else None

def convert_document(input_path, output_path, target_format, quality='medium'):
    """
    Convert document using LibreOffice headless mode.
    Returns True on success, False on failure.
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Build LibreOffice command
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', target_format,
            '--outdir', output_dir
        ]
        
        # Add quality settings if available
        if target_format in QUALITY_SETTINGS and quality in QUALITY_SETTINGS[target_format]:
            cmd.extend(QUALITY_SETTINGS[target_format][quality])
        
        cmd.append(input_path)
        
        logging.debug(f"Running LibreOffice conversion: {' '.join(cmd)}")
        
        # Run the conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # Increased timeout for batch processing
        )
        
        if result.returncode == 0:
            logging.info(f"Conversion successful: {input_path} -> {output_path}")
            return True
        else:
            logging.error(f"LibreOffice conversion failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error("LibreOffice conversion timed out")
        return False
    except Exception as e:
        logging.error(f"Error during conversion: {str(e)}")
        return False

def convert_batch_documents(file_paths, target_format, quality='medium'):
    """
    Convert multiple documents in batch.
    Returns list of results with success/failure status.
    """
    results = []
    
    for input_path in file_paths:
        try:
            # Generate output path
            original_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{original_name}.{target_format}"
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
            
            # Convert the document
            success = convert_document(input_path, output_path, target_format, quality)
            
            results.append({
                'input_file': os.path.basename(input_path),
                'output_file': output_filename if success else None,
                'success': success,
                'error': None if success else 'Conversion failed'
            })
            
        except Exception as e:
            results.append({
                'input_file': os.path.basename(input_path),
                'output_file': None,
                'success': False,
                'error': str(e)
            })
    
    return results

@app.route('/')
def index():
    """Main page with upload interface."""
    return render_template('index.html', formats=FORMAT_MAPPINGS.keys())

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and conversion."""
    try:
        # Check for batch upload
        files = request.files.getlist('file')
        if not files or (len(files) == 1 and files[0].filename == ''):
            flash('No files selected', 'error')
            return redirect(url_for('index'))
        
        target_format = request.form.get('target_format')
        quality = request.form.get('quality', 'medium')
        
        if not target_format or target_format not in FORMAT_MAPPINGS:
            flash('Invalid target format', 'error')
            return redirect(url_for('index'))
        
        # Handle single file upload
        if len(files) == 1:
            return handle_single_file_upload(files[0], target_format, quality)
        
        # Handle batch upload
        return handle_batch_upload(files, target_format, quality)
            
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        flash('An error occurred during upload. Please try again.', 'error')
        return redirect(url_for('index'))

def handle_single_file_upload(file, target_format, quality):
    """Handle single file upload and conversion."""
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a supported document format.', 'error')
        return redirect(url_for('index'))
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    input_filename = f"{file_id}_{original_filename}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    
    # Save uploaded file
    file.save(input_path)
    logging.info(f"File uploaded: {input_path}")
    
    # Determine output filename
    original_name = os.path.splitext(original_filename)[0]
    output_filename = f"{original_name}.{target_format}"
    output_path = os.path.join(app.config['CONVERTED_FOLDER'], f"{file_id}_{output_filename}")
    
    # Convert the file
    if convert_document(input_path, output_path, target_format, quality):
        # Clean up uploaded file
        try:
            os.remove(input_path)
        except Exception as e:
            logging.warning(f"Failed to remove uploaded file: {e}")
        
        flash('File converted successfully!', 'success')
        return redirect(url_for('preview_file', filename=f"{file_id}_{output_filename}"))
    else:
        # Clean up uploaded file on conversion failure
        try:
            os.remove(input_path)
        except Exception as e:
            logging.warning(f"Failed to remove uploaded file: {e}")
        
        flash('Conversion failed. Please try again or check if the file is valid.', 'error')
        return redirect(url_for('index'))

def handle_batch_upload(files, target_format, quality):
    """Handle batch file upload and conversion."""
    uploaded_files = []
    batch_id = str(uuid.uuid4())
    
    # Save all uploaded files
    for file in files:
        if file.filename and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            input_filename = f"{batch_id}_{original_filename}"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
            file.save(input_path)
            uploaded_files.append(input_path)
    
    if not uploaded_files:
        flash('No valid files to convert', 'error')
        return redirect(url_for('index'))
    
    # Convert files in batch
    results = convert_batch_documents(uploaded_files, target_format, quality)
    
    # Clean up uploaded files
    for file_path in uploaded_files:
        try:
            os.remove(file_path)
        except Exception as e:
            logging.warning(f"Failed to remove uploaded file: {e}")
    
    # Generate batch results page
    return render_template('batch_results.html', 
                         results=results, 
                         batch_id=batch_id,
                         target_format=target_format)

@app.route('/download/<filename>')
def download_file(filename):
    """Download converted file."""
    try:
        file_path = os.path.join(app.config['CONVERTED_FOLDER'], secure_filename(filename))
        
        if not os.path.exists(file_path):
            flash('File not found or has expired.', 'error')
            return redirect(url_for('index'))
        
        # Extract original filename (remove UUID prefix)
        parts = filename.split('_', 1)
        if len(parts) > 1:
            download_name = parts[1]
        else:
            download_name = filename
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        flash('Error downloading file.', 'error')
        return redirect(url_for('index'))

@app.route('/preview/<filename>')
def preview_file(filename):
    """Preview converted file before download."""
    try:
        file_path = os.path.join(app.config['CONVERTED_FOLDER'], secure_filename(filename))
        
        if not os.path.exists(file_path):
            flash('File not found or has expired.', 'error')
            return redirect(url_for('index'))
        
        # Get file info
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        file_format = get_file_format(filename)
        
        # Extract original filename (remove UUID prefix)
        parts = filename.split('_', 1)
        display_name = parts[1] if len(parts) > 1 else filename
        
        return render_template('preview.html',
                             filename=filename,
                             display_name=display_name,
                             file_size=file_size,
                             file_format=file_format.upper())
    except Exception as e:
        logging.error(f"Preview error: {str(e)}")
        flash('Error previewing file.', 'error')
        return redirect(url_for('index'))

@app.route('/batch_download/<batch_id>')
def batch_download(batch_id):
    """Download all files from a batch conversion as a ZIP."""
    try:
        import zipfile
        import io
        
        # Find all files with the batch ID
        converted_files = []
        for filename in os.listdir(app.config['CONVERTED_FOLDER']):
            if filename.startswith(f"{batch_id}_"):
                file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
                if os.path.exists(file_path):
                    converted_files.append((filename, file_path))
        
        if not converted_files:
            flash('No converted files found for this batch.', 'error')
            return redirect(url_for('index'))
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, file_path in converted_files:
                # Remove batch ID from filename for ZIP
                archive_name = filename.split('_', 1)[1] if '_' in filename else filename
                zip_file.write(file_path, archive_name)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'converted_documents_{batch_id[:8]}.zip'
        )
        
    except Exception as e:
        logging.error(f"Batch download error: {str(e)}")
        flash('Error creating download archive.', 'error')
        return redirect(url_for('index'))

@app.route('/check_formats')
def check_formats():
    """API endpoint to check supported formats."""
    return jsonify({
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'conversion_formats': list(FORMAT_MAPPINGS.keys()),
        'quality_settings': list(QUALITY_SETTINGS.keys()) if QUALITY_SETTINGS else []
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

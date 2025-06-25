// Document Format Converter - Upload Interface

let selectedFile = null;
let selectedFiles = [];
let selectedFormat = null;
let isBatchMode = false;

// Initialize drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');

    // Drag and drop events
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // File input change event
    fileInput.addEventListener('change', handleFileSelect);
    
    // Form submission
    uploadForm.addEventListener('submit', handleFormSubmit);
    
    // Prevent default drag behaviors on the entire page
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.addEventListener(eventName, preventDefaults, false);
    });
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDragOver(e) {
    preventDefaults(e);
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    preventDefaults(e);
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    preventDefaults(e);
    const dropZone = e.currentTarget;
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length === 1) {
        isBatchMode = false;
        handleFile(files[0]);
    } else if (files.length > 1) {
        isBatchMode = true;
        handleMultipleFiles(files);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length === 1) {
        isBatchMode = false;
        handleFile(files[0]);
    } else if (files.length > 1) {
        isBatchMode = true;
        handleMultipleFiles(files);
    }
}

function handleFile(file) {
    // Validate file type
    const allowedExtensions = ['odt', 'ods', 'odp', 'odg', 'odf', 'pdf', 'doc', 'docx', 'rtf', 'xls', 'xlsx', 'csv', 'ppt', 'pptx', 'txt', 'html', 'htm'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
        showAlert('Invalid file type. Please select a supported document format.', 'danger');
        return;
    }
    
    // Check file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
        showAlert('File size too large. Please select a file smaller than 50MB.', 'danger');
        return;
    }
    
    selectedFile = file;
    displayFileInfo(file);
    updateConvertButton();
}

function handleMultipleFiles(files) {
    const fileArray = Array.from(files);
    const allowedExtensions = ['odt', 'ods', 'odp', 'odg', 'odf', 'pdf', 'doc', 'docx', 'rtf', 'xls', 'xlsx', 'csv', 'ppt', 'pptx', 'txt', 'html', 'htm'];
    const maxSize = 50 * 1024 * 1024; // 50MB
    
    // Validate all files
    const validFiles = fileArray.filter(file => {
        const fileExtension = file.name.split('.').pop().toLowerCase();
        return allowedExtensions.includes(fileExtension) && file.size <= maxSize;
    });
    
    if (validFiles.length === 0) {
        showAlert('No valid files found. Please check file types and sizes.', 'danger');
        return;
    }
    
    if (validFiles.length !== fileArray.length) {
        showAlert(`${validFiles.length} of ${fileArray.length} files are valid and will be processed.`, 'warning');
    }
    
    selectedFiles = validFiles;
    displayMultipleFileInfo(validFiles);
    updateConvertButton();
}

function displayFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    fileName.textContent = file.name;
    fileSize.textContent = `${formatFileSize(file.size)} • ${file.type || 'Unknown type'}`;
    
    fileInfo.style.display = 'block';
}

function displayMultipleFileInfo(files) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    const totalSize = files.reduce((sum, file) => sum + file.size, 0);
    
    fileName.innerHTML = `
        <strong>Batch Upload - ${files.length} files</strong><br>
        <small class="text-muted">
            ${files.slice(0, 3).map(f => f.name).join(', ')}
            ${files.length > 3 ? ` and ${files.length - 3} more...` : ''}
        </small>
    `;
    fileSize.textContent = `Total: ${formatFileSize(totalSize)}`;
    
    fileInfo.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function clearFile() {
    selectedFile = null;
    selectedFiles = [];
    isBatchMode = false;
    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').style.display = 'none';
    updateConvertButton();
}

function selectFormat(format) {
    // Remove previous selection
    document.querySelectorAll('.format-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Add selection to clicked format
    document.querySelector(`[data-format="${format}"]`).classList.add('selected');
    
    selectedFormat = format;
    document.getElementById('targetFormat').value = format;
    updateConvertButton();
}

function updateConvertButton() {
    const convertBtn = document.getElementById('convertBtn');
    const hasFiles = isBatchMode ? selectedFiles.length > 0 : selectedFile !== null;
    const canConvert = hasFiles && selectedFormat;
    
    convertBtn.disabled = !canConvert;
    
    if (canConvert) {
        if (isBatchMode) {
            convertBtn.innerHTML = `
                <i data-feather="refresh-cw" class="me-2"></i>
                Convert ${selectedFiles.length} files to ${selectedFormat.toUpperCase()}
            `;
        } else {
            convertBtn.innerHTML = `
                <i data-feather="refresh-cw" class="me-2"></i>
                Convert to ${selectedFormat.toUpperCase()}
            `;
        }
        feather.replace();
    } else {
        convertBtn.innerHTML = `
            <i data-feather="refresh-cw" class="me-2"></i>
            Convert Document${isBatchMode ? 's' : ''}
        `;
        feather.replace();
    }
}

function handleFormSubmit(e) {
    if (!selectedFile || !selectedFormat) {
        e.preventDefault();
        showAlert('Please select a file and target format.', 'danger');
        return;
    }
    
    // Show progress indicator
    const progressSection = document.getElementById('progressSection');
    const convertBtn = document.getElementById('convertBtn');
    
    convertBtn.disabled = true;
    convertBtn.innerHTML = `
        <div class="spinner-border spinner-border-sm me-2" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        Converting...
    `;
    
    progressSection.style.display = 'block';
    
    // Form will submit normally - progress will be handled by server response
}

function showAlert(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert at the top of the container
    const container = document.querySelector('.container');
    const header = container.querySelector('.row');
    container.insertBefore(alertDiv, header.nextSibling);
    
    // Auto-remove alert after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Utility function to detect file format from filename
function getFileFormat(filename) {
    return filename.split('.').pop().toLowerCase();
}

// Check if source and target formats are the same
function isSameFormat(sourceFile, targetFormat) {
    const sourceFormat = getFileFormat(sourceFile.name);
    return sourceFormat === targetFormat;
}

// Add format validation
function validateConversion(sourceFile, targetFormat) {
    if (isSameFormat(sourceFile, targetFormat)) {
        showAlert('Source and target formats are the same. Please choose a different output format.', 'warning');
        return false;
    }
    return true;
}

// Enhanced form submission with validation
function handleFormSubmit(e) {
    const hasFiles = isBatchMode ? selectedFiles.length > 0 : selectedFile !== null;
    
    if (!hasFiles || !selectedFormat) {
        e.preventDefault();
        showAlert('Please select files and target format.', 'danger');
        return;
    }
    
    // Validate single file conversion
    if (!isBatchMode && !validateConversion(selectedFile, selectedFormat)) {
        e.preventDefault();
        return;
    }
    
    // Show progress indicator
    const progressSection = document.getElementById('progressSection');
    const convertBtn = document.getElementById('convertBtn');
    
    convertBtn.disabled = true;
    convertBtn.innerHTML = `
        <div class="spinner-border spinner-border-sm me-2" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        Converting${isBatchMode ? ` ${selectedFiles.length} files` : ''}...
    `;
    
    progressSection.style.display = 'block';
}

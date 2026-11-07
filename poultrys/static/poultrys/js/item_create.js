document.addEventListener('DOMContentLoaded', function() {
    // Image upload and preview
    const fileInput = document.querySelector('#id_sub_images');
    const previewContainer = document.getElementById('imagePreview');
    
    if (fileInput && previewContainer) {
        fileInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            const files = this.files;
            const uploadLabel = this.parentElement;
            const uploadText = uploadLabel.querySelector('.upload-text');
            const fileInfo = uploadLabel.querySelector('.file-info');
            
            if (files.length > 0) {
                uploadText.textContent = `${files.length} ${files.length === 1 ? 'file' : 'files'} selected`;
                fileInfo.textContent = Array.from(files).map(file => file.name).join(', ');
                
                Array.from(files).forEach(file => {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const previewWrapper = document.createElement('div');
                            previewWrapper.className = 'preview-wrapper';
                            
                            const preview = document.createElement('img');
                            preview.src = e.target.result;
                            preview.className = 'preview-image';
                            preview.title = file.name;
                            
                            const removeBtn = document.createElement('button');
                            removeBtn.className = 'preview-remove';
                            removeBtn.innerHTML = '&times;';
                            removeBtn.addEventListener('click', function(e) {
                                e.stopPropagation();
                                previewWrapper.remove();
                                updateFileInput(files, file);
                            });
                            
                            previewWrapper.appendChild(preview);
                            previewWrapper.appendChild(removeBtn);
                            previewContainer.appendChild(previewWrapper);
                        }
                        reader.readAsDataURL(file);
                    }
                });
            } else {
                resetUploadLabel();
            }
        });
        
        const uploadLabel = fileInput.parentElement;
        
        uploadLabel.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadLabel.querySelector('.upload-content').style.borderColor = 'var(--primary-color)';
            uploadLabel.querySelector('.upload-content').style.backgroundColor = 'var(--primary-light)';
        });
        
        uploadLabel.addEventListener('dragleave', () => {
            uploadLabel.querySelector('.upload-content').style.borderColor = 'var(--border-color)';
            uploadLabel.querySelector('.upload-content').style.backgroundColor = 'white';
        });
        
        uploadLabel.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadLabel.querySelector('.upload-content').style.borderColor = 'var(--border-color)';
            uploadLabel.querySelector('.upload-content').style.backgroundColor = 'white';
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                const event = new Event('change');
                fileInput.dispatchEvent(event);
            }
        });
        
        function resetUploadLabel() {
            const uploadText = uploadLabel.querySelector('.upload-text');
            const fileInfo = uploadLabel.querySelector('.file-info');
            uploadText.textContent = 'Click to upload images';
            fileInfo.textContent = 'PNG, JPG up to 5MB';
        }
        
        function updateFileInput(originalFiles, fileToRemove) {
            const newFiles = Array.from(originalFiles).filter(file => file !== fileToRemove);
            const dataTransfer = new DataTransfer();
            
            newFiles.forEach(file => {
                dataTransfer.items.add(file);
            });
            
            fileInput.files = dataTransfer.files;
            
            if (newFiles.length === 0) {
                resetUploadLabel();
            } else {
                const event = new Event('change');
                fileInput.dispatchEvent(event);
            }
        }
    }
    
    // Character counter for textarea
    const textarea = document.querySelector('.item-form textarea');
    if (textarea) {
        const counter = textarea.parentElement.querySelector('.char-counter');
        
        textarea.addEventListener('input', function() {
            counter.textContent = `${this.value.length} characters`;
        });
    }
    
    // Form submission validation
    const form = document.getElementById('itemForm');
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Clear previous errors
        this.querySelectorAll('.errorlist').forEach(el => el.remove());
        this.querySelectorAll('input, textarea, select').forEach(field => {
            field.style.borderColor = '';
        });
        
        // Validate all required fields
        const requiredFields = this.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = 'var(--error-color)';
                isValid = false;
                
                const error = document.createElement('ul');
                error.className = 'errorlist';
                error.innerHTML = '<li>This field is required</li>';
                
                if (field.type === 'file') {
                    field.parentNode.insertBefore(error, field.nextSibling);
                } else {
                    field.parentNode.appendChild(error);
                }
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            
            // Scroll to the first error
            const firstError = this.querySelector('.errorlist');
            if (firstError) {
                firstError.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }
        }
    });
});
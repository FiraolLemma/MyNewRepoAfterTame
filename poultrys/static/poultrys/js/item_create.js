document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('itemForm');
    const fileInput = document.getElementById('id_sub_images');
    const dropZone = document.getElementById('imageDropZone');
    const previewContainer = document.getElementById('imagePreview');
    const description = document.getElementById('id_description');
    const counter = document.querySelector('.item-create__char-counter');
    const mainImageInput = document.getElementById('id_main_image');
    const mainImagePreview = document.getElementById('mainImagePreview');
    let previewUrls = [];
    let mainImageUrl = null;

    function clearPreviews() {
        previewUrls.forEach(function (url) {
            URL.revokeObjectURL(url);
        });
        previewUrls = [];
        previewContainer.replaceChildren();
    }

    function renderPreviews() {
        clearPreviews();

        const files = Array.from(fileInput.files || []);
        const uploadLabel = dropZone.querySelector('[data-upload-label]');
        const uploadHelp = dropZone.querySelector('[data-upload-help]');

        if (files.length === 0) {
            uploadLabel.textContent = uploadLabel.dataset.defaultText;
            uploadHelp.textContent = uploadHelp.dataset.defaultText;
            return;
        }

        const countLabel = files.length === 1
            ? dropZone.dataset.selectedOne
            : dropZone.dataset.selectedMany;
        uploadLabel.textContent = files.length + ' ' + countLabel;
        uploadHelp.textContent = files.map(function (file) {
            return file.name;
        }).join(', ');

        files.forEach(function (file, index) {
            if (!file.type || file.type.indexOf('image/') !== 0) {
                return;
            }

            const imageUrl = URL.createObjectURL(file);
            previewUrls.push(imageUrl);

            const card = document.createElement('div');
            card.className = 'item-create__preview-card';

            const image = document.createElement('img');
            image.src = imageUrl;
            image.alt = file.name;
            image.loading = 'lazy';

            const name = document.createElement('span');
            name.className = 'item-create__preview-name';
            name.textContent = file.name;

            card.appendChild(image);
            card.appendChild(name);

            if (typeof DataTransfer !== 'undefined') {
                const removeButton = document.createElement('button');
                removeButton.className = 'item-create__preview-remove';
                removeButton.type = 'button';
                removeButton.setAttribute('aria-label', dropZone.dataset.removeLabel + ' ' + file.name);
                removeButton.textContent = '\u00d7';
                removeButton.addEventListener('click', function () {
                    const updatedFiles = new DataTransfer();
                    Array.from(fileInput.files).forEach(function (selectedFile, selectedIndex) {
                        if (selectedIndex !== index) {
                            updatedFiles.items.add(selectedFile);
                        }
                    });
                    fileInput.files = updatedFiles.files;
                    fileInput.dispatchEvent(new Event('change', { bubbles: true }));
                });
                card.appendChild(removeButton);
            }

            previewContainer.appendChild(card);
        });
    }

    if (fileInput && dropZone && previewContainer) {
        const uploadLabel = dropZone.querySelector('[data-upload-label]');
        const uploadHelp = dropZone.querySelector('[data-upload-help]');
        uploadLabel.dataset.defaultText = uploadLabel.textContent;
        uploadHelp.dataset.defaultText = uploadHelp.textContent;
        fileInput.setAttribute('accept', 'image/*');
        fileInput.addEventListener('change', renderPreviews);

        ['dragenter', 'dragover'].forEach(function (eventName) {
            dropZone.addEventListener(eventName, function (event) {
                event.preventDefault();
                dropZone.classList.add('is-dragging');
            });
        });

        ['dragleave', 'drop'].forEach(function (eventName) {
            dropZone.addEventListener(eventName, function (event) {
                if (eventName === 'drop' || !dropZone.contains(event.relatedTarget)) {
                    dropZone.classList.remove('is-dragging');
                }
            });
        });

        dropZone.addEventListener('drop', function (event) {
            event.preventDefault();
            if (event.dataTransfer && event.dataTransfer.files.length && typeof DataTransfer !== 'undefined') {
                const droppedFiles = new DataTransfer();
                Array.from(fileInput.files || []).forEach(function (file) {
                    droppedFiles.items.add(file);
                });
                Array.from(event.dataTransfer.files).forEach(function (file) {
                    droppedFiles.items.add(file);
                });
                fileInput.files = droppedFiles.files;
                fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }

    if (description && counter) {
        function updateCharacterCount() {
            const count = description.value.length;
            const unit = count === 1 ? counter.dataset.singular : counter.dataset.plural;
            counter.textContent = count + ' ' + unit;
        }

        description.addEventListener('input', updateCharacterCount);
        updateCharacterCount();
    }

    if (mainImageInput && mainImagePreview) {
        mainImageInput.setAttribute('accept', 'image/*');
        mainImageInput.addEventListener('change', function () {
            if (mainImageUrl) {
                URL.revokeObjectURL(mainImageUrl);
                mainImageUrl = null;
            }
            mainImagePreview.replaceChildren();

            const file = mainImageInput.files && mainImageInput.files[0];
            if (!file || !file.type || file.type.indexOf('image/') !== 0) {
                return;
            }

            mainImageUrl = URL.createObjectURL(file);
            const image = document.createElement('img');
            image.src = mainImageUrl;
            image.alt = file.name;

            const fileName = document.createElement('span');
            fileName.textContent = file.name;
            mainImagePreview.appendChild(image);
            mainImagePreview.appendChild(fileName);
        });
    }

    if (form) {
        form.addEventListener('submit', function () {
            if (!form.checkValidity()) {
                return;
            }

            const submitButton = form.querySelector('.item-create__submit');
            if (!submitButton) {
                return;
            }

            const buttonText = submitButton.querySelector('span');
            submitButton.disabled = true;
            submitButton.setAttribute('aria-busy', 'true');
            if (buttonText) {
                buttonText.textContent = submitButton.dataset.savingText;
            }
        });
    }
});

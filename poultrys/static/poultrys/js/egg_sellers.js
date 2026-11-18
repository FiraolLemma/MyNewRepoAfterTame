document.addEventListener('DOMContentLoaded', function () {
    const orderModal = document.getElementById('orderModal');
    const deleteModal = document.getElementById('deleteEggModal');
    const orderForm = document.getElementById('orderForm');
    const notificationArea = document.querySelector('.seller-notifications');
    const deleteName = document.getElementById('eggSellerName');
    const confirmDelete = document.getElementById('confirmEggDelete');
    const quantityInput = document.getElementById('quantity');
    const minimumOrderHint = document.getElementById('minimumOrderHint');
    let activeModal = null;
    let returnFocusTo = null;
    let selectedSellerId = null;
    let selectedDeleteUrl = null;

    document.querySelectorAll('.order-btn').forEach(function (button) {
        button.addEventListener('click', function () {
            const sellerId = document.getElementById('modalSellerId');
            if (!orderModal || !sellerId) return;
            sellerId.value = button.dataset.sellerId;
            const minimumOrder = Number(button.dataset.minimumOrder) || 1;
            if (quantityInput) {
                quantityInput.min = String(minimumOrder);
                quantityInput.value = String(minimumOrder);
            }
            if (minimumOrderHint) {
                minimumOrderHint.textContent = button.dataset.minimumLabel + ': ' +
                    minimumOrder + ' ' + button.dataset.dozenLabel;
            }
            showModal(orderModal);
        });
    });

    document.querySelectorAll('.btn-delete').forEach(function (button) {
        button.addEventListener('click', function () {
            if (!deleteModal || !deleteName) return;
            deleteName.textContent = button.dataset.sellerName || '';
            showModal(deleteModal);
            selectedSellerId = button.dataset.sellerId;
            selectedDeleteUrl = button.dataset.deleteUrl;
        });
    });

    document.querySelectorAll('.close-modal, .close, #cancelEggDelete').forEach(function (button) {
        button.addEventListener('click', closeActiveModal);
    });

    [orderModal, deleteModal].forEach(function (modal) {
        if (!modal) return;
        modal.addEventListener('click', function (event) {
            if (event.target === modal) closeActiveModal();
        });
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') closeActiveModal();
    });

    if (confirmDelete) {
        confirmDelete.addEventListener('click', function () {
            if (selectedSellerId && selectedDeleteUrl) {
                deleteSeller(selectedSellerId, selectedDeleteUrl);
            }
        });
    }

    if (orderForm) {
        orderForm.addEventListener('submit', function (event) {
            event.preventDefault();
            submitOrder(orderForm);
        });
    }

    function showModal(modal) {
        if (activeModal) closeActiveModal();
        returnFocusTo = document.activeElement;
        activeModal = modal;
        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        const firstInput = modal.querySelector('input:not([type="hidden"]), button');
        if (firstInput) firstInput.focus();
    }

    function closeActiveModal() {
        if (!activeModal) return;
        activeModal.classList.remove('is-open');
        activeModal.setAttribute('aria-hidden', 'true');
        activeModal = null;
        selectedSellerId = null;
        selectedDeleteUrl = null;
        document.body.style.overflow = '';
        if (returnFocusTo && typeof returnFocusTo.focus === 'function') {
            returnFocusTo.focus();
        }
        returnFocusTo = null;
    }

    function deleteSeller(sellerId, deleteUrl) {
        const button = document.querySelector('.btn-delete[data-seller-id="' + sellerId + '"]');
        const csrfToken = getCsrfToken();
        if (confirmDelete) confirmDelete.disabled = true;

        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
            .then(readJsonResponse)
            .then(function (data) {
                if (!data.success) {
                    throw new Error(data.error || 'Unable to delete this egg seller.');
                }
                const card = button ? button.closest('.seller-card') : null;
                if (card) card.remove();
                showNotification(data.message, 'success');
                closeActiveModal();
            })
            .catch(function (error) {
                showNotification(error.message || 'Error deleting egg seller.', 'error');
            })
            .finally(function () {
                if (confirmDelete) confirmDelete.disabled = false;
            });
    }

    function submitOrder(form) {
        const submitButton = form.querySelector('.submit-btn');
        const originalText = submitButton ? submitButton.textContent : '';
        const formData = new FormData(form);
        const payload = {};
        formData.forEach(function (value, key) {
            payload[key] = value;
        });
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = submitButton.dataset.processingLabel || 'Processing...';
        }

        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken') || getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        })
            .then(readJsonResponse)
            .then(function (data) {
                if (!data.success) {
                    const firstError = data.errors
                        ? Object.values(data.errors).flat().map(function (error) {
                            return typeof error === 'string' ? error : error.message;
                        }).filter(Boolean).join(' ')
                        : data.message;
                    throw new Error(firstError || 'Please check your order details.');
                }
                showNotification(data.message, 'success');
                form.reset();
                closeActiveModal();
            })
            .catch(function (error) {
                showNotification(error.message || 'An error occurred. Please try again.', 'error');
            })
            .finally(function () {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }
            });
    }

    function readJsonResponse(response) {
        return response.json().then(function (data) {
            if (!response.ok) {
                const message = data.message || data.error || 'The request could not be completed.';
                throw new Error(message);
            }
            return data;
        });
    }

    function showNotification(message, type) {
        if (!notificationArea) return;
        const notification = document.createElement('div');
        notification.className = 'notification ' + type;
        notification.textContent = message;
        notificationArea.appendChild(notification);
        window.setTimeout(function () {
            notification.remove();
        }, 4500);
    }

    function getCsrfToken() {
        const csrfInput = document.querySelector('#orderForm [name="csrfmiddlewaretoken"]');
        if (csrfInput) return csrfInput.value;
        const csrfCookie = document.cookie.split(';').map(function (cookie) {
            return cookie.trim();
        }).find(function (cookie) {
            return cookie.indexOf('csrftoken=') === 0;
        });
        return csrfCookie ? decodeURIComponent(csrfCookie.slice('csrftoken='.length)) : '';
    }
});

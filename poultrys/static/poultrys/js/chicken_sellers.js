document.addEventListener('DOMContentLoaded', function () {
    const page = document.querySelector('.chicken-sellers');
    const searchInput = document.getElementById('seller-search');
    const locationFilter = document.getElementById('seller-location');
    const sellerGrid = document.getElementById('sellerList');
    const count = document.getElementById('sellerCount');
    const emptyState = document.getElementById('sellerEmptyState');
    const deleteModal = document.getElementById('deleteModal');
    const sellerName = document.getElementById('sellerName');
    const confirmDelete = document.getElementById('confirmDelete');
    const notificationArea = document.querySelector('.chicken-sellers__notifications');
    let sellerCards = Array.from(document.querySelectorAll('[data-seller-card]'));
    let selectedSellerButton = null;
    let previousFocus = null;
    let originalConfirmText = '';

    function updateCount(visibleCount) {
        if (!count) return;
        const number = count.querySelector('.chicken-sellers__count-number');
        const label = count.querySelector('.chicken-sellers__count-label');
        if (!number || !label) return;
        number.textContent = visibleCount;
        label.textContent = visibleCount === 1 ? count.dataset.oneLabel : count.dataset.manyLabel;
    }

    function filterSellers() {
        if (!sellerGrid) return;
        const searchTerm = searchInput ? searchInput.value.trim().toLocaleLowerCase() : '';
        const location = locationFilter ? locationFilter.value.trim().toLocaleLowerCase() : '';
        let visibleCount = 0;

        sellerCards = sellerCards.filter(function (card) {
            return card.isConnected;
        });

        sellerCards.forEach(function (card) {
            const searchableText = (card.dataset.search || '').toLocaleLowerCase();
            const cardLocation = (card.dataset.location || '').toLocaleLowerCase();
            const matchesSearch = !searchTerm || searchableText.includes(searchTerm);
            const matchesLocation = !location || cardLocation === location;
            const isVisible = matchesSearch && matchesLocation;
            card.hidden = !isVisible;
            if (isVisible) visibleCount += 1;
        });

        updateCount(visibleCount);
        if (emptyState) emptyState.hidden = visibleCount !== 0;
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterSellers);
    }
    if (locationFilter) {
        locationFilter.addEventListener('change', filterSellers);
    }
    filterSellers();

    document.querySelectorAll('[data-delete-button]').forEach(function (button) {
        button.addEventListener('click', function () {
            if (!deleteModal || !sellerName || !confirmDelete) return;
            selectedSellerButton = button;
            previousFocus = document.activeElement;
            sellerName.textContent = button.dataset.sellerName || '';
            originalConfirmText = confirmDelete.textContent;
            deleteModal.classList.add('is-open');
            deleteModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
            const cancelButton = deleteModal.querySelector('[data-close-modal]');
            if (cancelButton) cancelButton.focus();
        });
    });

    function closeDeleteModal() {
        if (!deleteModal) return;
        deleteModal.classList.remove('is-open');
        deleteModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        selectedSellerButton = null;
        if (previousFocus && previousFocus.isConnected) {
            previousFocus.focus();
        }
        previousFocus = null;
    }

    document.querySelectorAll('[data-close-modal]').forEach(function (button) {
        button.addEventListener('click', closeDeleteModal);
    });

    if (deleteModal) {
        deleteModal.addEventListener('click', function (event) {
            if (event.target === deleteModal) closeDeleteModal();
        });
    }

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && deleteModal && deleteModal.classList.contains('is-open')) {
            closeDeleteModal();
        }
    });

    if (confirmDelete) {
        confirmDelete.addEventListener('click', function () {
            if (!selectedSellerButton || confirmDelete.disabled) return;

            const deleteButton = selectedSellerButton;
            const deleteUrl = deleteButton.dataset.deleteUrl;
            const csrfToken = getCsrfToken();
            if (!deleteUrl || !csrfToken) {
                showNotification(deleteModal.dataset.errorMessage, 'error');
                return;
            }

            confirmDelete.disabled = true;
            confirmDelete.textContent = deleteModal.dataset.removingLabel;

            fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        if (!response.ok || !data.success) {
                            throw new Error(data.error || deleteModal.dataset.errorMessage);
                        }
                        return data;
                    });
                })
                .then(function () {
                    const card = deleteButton.closest('[data-seller-card]');
                    if (card) card.remove();
                    filterSellers();
                    closeDeleteModal();
                    showNotification(deleteModal.dataset.successMessage, 'success');
                })
                .catch(function (error) {
                    showNotification(error.message || deleteModal.dataset.errorMessage, 'error');
                })
                .finally(function () {
                    confirmDelete.disabled = false;
                    confirmDelete.textContent = originalConfirmText;
                });
        });
    }

    function getCsrfToken() {
        const cookieToken = document.cookie.split(';').map(function (cookie) {
            return cookie.trim();
        }).find(function (cookie) {
            return cookie.indexOf('csrftoken=') === 0;
        });
        if (cookieToken) {
            return decodeURIComponent(cookieToken.slice('csrftoken='.length));
        }
        return page ? page.dataset.csrfToken : '';
    }

    function showNotification(message, type) {
        if (!notificationArea || !message) return;
        const notification = document.createElement('div');
        notification.className = 'chicken-sellers__notification';
        if (type === 'error') {
            notification.classList.add('chicken-sellers__notification--error');
        }
        notification.textContent = message;
        notificationArea.appendChild(notification);
        window.setTimeout(function () {
            notification.remove();
        }, 4500);
    }
});

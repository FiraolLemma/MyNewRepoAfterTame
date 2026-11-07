document.addEventListener('DOMContentLoaded', function() {
    const orderButtons = document.querySelectorAll('.order-btn');
    const orderModal = document.getElementById('orderModal');
    const orderForm = document.getElementById('orderForm');
    const closeModal = document.querySelector('.close-modal');

    const eggDeleteButtons = document.querySelectorAll('.btn-delete');
    const eggDeleteModal = document.getElementById('deleteEggModal');
    const eggSellerNameSpan = document.getElementById('eggSellerName');
    const confirmEggDeleteBtn = document.getElementById('confirmEggDelete');
    const cancelEggDeleteBtn = document.getElementById('cancelEggDelete');
    const closeEggModalBtn = eggDeleteModal.querySelector('.close');

    const searchInput = document.getElementById('sellerSearch');
    const locationFilter = document.getElementById('locationFilter');
    const filterBtn = document.getElementById('filterBtn');

    let currentEggSellerId = null;
    let currentDeleteUrl = null;

    // ---- Order Modal ----
    orderButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sellerId = this.dataset.sellerId;
            document.getElementById('modalSellerId').value = sellerId;
            orderModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
    });

    if (closeModal) {
        closeModal.addEventListener('click', closeOrderModal);
    }

    window.addEventListener('click', function(event) {
        if (event.target === orderModal) closeOrderModal();
        if (event.target === eggDeleteModal) closeEggModal();
    });

    function closeOrderModal() {
        orderModal.style.display = 'none';
        document.body.style.overflow = '';
    }

    // ---- Delete Modal ----
    eggDeleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            currentEggSellerId = this.dataset.sellerId;
            currentDeleteUrl = this.dataset.deleteUrl;  // ✅ Django-generated URL
            const sellerName = this.dataset.sellerName;
            eggSellerNameSpan.textContent = sellerName;
            eggDeleteModal.style.display = 'block';
        });
    });

    confirmEggDeleteBtn.addEventListener('click', function() {
        if (currentEggSellerId && currentDeleteUrl) {
            deleteEggSeller(currentEggSellerId, currentDeleteUrl);
        }
    });
    cancelEggDeleteBtn.addEventListener('click', closeEggModal);
    closeEggModalBtn.addEventListener('click', closeEggModal);

    function closeEggModal() {
        eggDeleteModal.style.display = 'none';
        currentEggSellerId = null;
        currentDeleteUrl = null;
    }

    // ---- Delete Request ----
    function deleteEggSeller(sellerId, deleteUrl) {
        const csrfToken = getCookie('csrftoken');

        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`.btn-delete[data-seller-id="${sellerId}"]`)
                    ?.closest('.seller-card')
                    ?.remove();
                showNotification(data.message, 'success');
            } else {
                showNotification('Error: ' + data.error, 'error');
            }
        })
        .catch(() => showNotification('Error deleting egg seller', 'error'))
        .finally(closeEggModal);
    }

    // ---- Order Form Submit ----
    if (orderForm) {
        orderForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitOrderForm(this);
        });
    }

    function submitOrderForm(form) {
        const submitBtn = form.querySelector('.submit-btn');
        const originalText = submitBtn.textContent;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());

        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': jsonData.csrfmiddlewaretoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(jsonData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                closeOrderModal();
                form.reset();
            } else {
                showNotification(data.message || 'Please check your input', 'error');
            }
        })
        .catch(() => showNotification('An error occurred. Please try again.', 'error'))
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        });
    }

    // ---- Search & Filter ----
    filterBtn.addEventListener('click', function() {
        const searchValue = searchInput.value.toLowerCase();
        const locationValue = locationFilter.value.toLowerCase();
        filterSellers(searchValue, locationValue);
    });

    searchInput.addEventListener('input', function() {
        filterSellers(this.value.toLowerCase(), locationFilter.value.toLowerCase());
    });

    function filterSellers(searchTerm, locationTerm) {
        const sellers = document.querySelectorAll('.seller-card');
        sellers.forEach(seller => {
            const name = seller.querySelector('h3').textContent.toLowerCase();
            const location = seller.querySelector('p strong')?.nextSibling?.textContent?.toLowerCase() || '';
            const matchesSearch = name.includes(searchTerm);
            const matchesLocation = !locationTerm || location.includes(locationTerm);
            seller.style.display = matchesSearch && matchesLocation ? '' : 'none';
        });
    }

    // ---- Helper: Notification ----
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => notification.remove(), 4000);
    }
  
    // ---- Helper: CSRF ----
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let c of cookies) {
                const cookie = c.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

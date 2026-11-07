document.addEventListener('DOMContentLoaded', function() {
    const sellerItems = document.querySelectorAll('.user-card');
    const searchInput = document.getElementById('searchInput');
    const locationFilter = document.getElementById('locationFilter');
    const sellerList = document.getElementById('sellerList');
    const noResults = document.querySelector('.no-results');

    // 🔍 Filter sellers
    function filterSellers() {
        const searchTerm = searchInput.value.toLowerCase();
        const locationValue = locationFilter.value;
        let visibleCount = 0;

        sellerItems.forEach(item => {
            const sellerText = item.textContent.toLowerCase();
            const itemLocation = item.getAttribute('data-location');
            const matchesSearch = sellerText.includes(searchTerm);
            const matchesLocation = !locationValue || itemLocation === locationValue;

            if (matchesSearch && matchesLocation) {
                item.style.display = 'block';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        if (noResults) {
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    if (searchInput && locationFilter) {
        searchInput.addEventListener('input', filterSellers);
        locationFilter.addEventListener('change', filterSellers);
    }

    // 🎬 Fade-in animation for cards
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.05 });

    sellerItems.forEach(item => {
        item.style.opacity = 0;
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(item);
    });

    // ✨ Social links hover effect
    document.querySelectorAll('.social-link').forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.1)';
        });
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // 🗑 Delete modal
    const deleteButtons = document.querySelectorAll('.btn-delete[data-seller-id]');
    const deleteModal = document.getElementById('deleteModal');
    const sellerNameSpan = document.getElementById('sellerName');
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    const cancelDeleteBtn = document.getElementById('cancelDelete');
    const closeModalBtn = document.querySelector('.close');

    let currentSellerId = null;

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            currentSellerId = this.getAttribute('data-seller-id');
            const sellerName = this.getAttribute('data-seller-name');
            sellerNameSpan.textContent = sellerName;
            deleteModal.style.display = 'block';
        });
    });

    confirmDeleteBtn.addEventListener('click', function() {
        if (currentSellerId) {
            const csrfToken = getCookie('csrftoken');
            fetch(`/delete-seller-ajax/${currentSellerId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const sellerItem = document.querySelector(`.user-card[data-seller-id="${currentSellerId}"]`);
                    if (sellerItem) sellerItem.remove();
                    alert('Seller deleted successfully!');
                } else {
                    alert('Error deleting seller: ' + data.error);
                }
            })
            .catch(err => {
                console.error(err);
                alert('Error deleting seller');
            })
            .finally(() => {
                deleteModal.style.display = 'none';
                currentSellerId = null;
            });
        }
    });

    function closeModal() {
        deleteModal.style.display = 'none';
        currentSellerId = null;
    }

    cancelDeleteBtn.addEventListener('click', closeModal);
    closeModalBtn.addEventListener('click', closeModal);
    window.addEventListener('click', e => { if (e.target === deleteModal) closeModal(); });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                }
            });
        }
        return cookieValue;
    }
});

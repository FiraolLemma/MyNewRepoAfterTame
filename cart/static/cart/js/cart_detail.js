// cart/static/cart/js/cart_detail.js
document.addEventListener('DOMContentLoaded', function() {
    // Quantity controls functionality
    const quantityControls = document.querySelectorAll('.quantity-controls');
    
    quantityControls.forEach(control => {
        const decreaseBtn = control.querySelector('.quantity-btn:first-child');
        const increaseBtn = control.querySelector('.quantity-btn:last-child');
        const quantityInput = control.querySelector('.quantity-input');
        
        if (decreaseBtn && increaseBtn && quantityInput) {
            decreaseBtn.addEventListener('click', () => {
                let quantity = parseInt(quantityInput.value);
                if (quantity > 1) {
                    quantityInput.value = quantity - 1;
                    updateQuantity(quantityInput);
                }
            });
            
            increaseBtn.addEventListener('click', () => {
                let quantity = parseInt(quantityInput.value);
                quantityInput.value = quantity + 1;
                updateQuantity(quantityInput);
            });
            
            quantityInput.addEventListener('change', () => {
                updateQuantity(quantityInput);
            });
        }
    });
    
    // Remove item confirmation
    const removeButtons = document.querySelectorAll('.remove-btn');
    
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (confirm('Are you sure you want to remove this item from your cart?')) {
                // Add loading state
                this.classList.add('loading');
                this.textContent = 'Removing...';
                
                // Proceed with removal
                window.location.href = this.href;
            }
        });
    });
    
    // Update quantity function
    function updateQuantity(input) {
        const cartItem = input.closest('.cart-item');
        const itemId = input.dataset.itemId;
        const newQuantity = parseInt(input.value);
        
        if (newQuantity < 1) {
            input.value = 1;
            return;
        }
        
        // Add loading state
        input.classList.add('loading');
        
        // Send AJAX request to update quantity
        fetch('/cart/update-quantity/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                item_id: itemId,
                quantity: newQuantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the total price if needed
                updateCartTotals(data.cart_total);
            } else {
                alert('Error updating quantity: ' + data.error);
                input.value = input.dataset.oldValue;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error updating quantity');
            input.value = input.dataset.oldValue;
        })
        .finally(() => {
            input.classList.remove('loading');
        });
    }
    
    // Update cart totals (placeholder function)
    function updateCartTotals(total) {
        const totalElement = document.querySelector('.summary-value.total');
        if (totalElement) {
            totalElement.textContent = '$' + total.toFixed(2);
        }
    }
    
    // Get CSRF token function
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Smooth animations
    const cartItems = document.querySelectorAll('.cart-item');
    cartItems.forEach((item, index) => {
        item.style.animationDelay = (index * 0.1) + 's';
    });
    
    // Checkout button loading state
    const checkoutBtn = document.querySelector('.checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function(e) {
            if (this.classList.contains('loading')) {
                e.preventDefault();
                return;
            }
            
            this.classList.add('loading');
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        });
    }
    
    // Empty cart message animation
    const emptyCart = document.querySelector('.empty-cart');
    if (emptyCart) {
        emptyCart.style.opacity = '0';
        setTimeout(() => {
            emptyCart.style.transition = 'opacity 0.5s ease';
            emptyCart.style.opacity = '1';
        }, 100);
    }
    
    // Cart item hover effects
    cartItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'translateX(5px)';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.transform = 'translateX(0)';
        });
    });
});

// Utility function for currency formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Export for potential reuse
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { formatCurrency };
}
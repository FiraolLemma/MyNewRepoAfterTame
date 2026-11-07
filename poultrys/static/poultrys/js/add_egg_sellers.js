// poultrys/static/poultrys/js/add_egg_sellers.js

document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const form = document.querySelector('.add-egg-form');
    const submitButton = form.querySelector('button[type="submit"]');
    const clearButton = form.querySelector('.clear-form');
    
    // Price per dozen input
    const priceInput = document.getElementById('id_price_per_dozen');
    if (priceInput) {
        priceInput.classList.add('price-input');
        const priceContainer = document.createElement('div');
        priceContainer.className = 'price-input-container';
        priceInput.parentNode.insertBefore(priceContainer, priceInput);
        priceContainer.appendChild(priceInput);
    }
    
    // Form validation
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            // Show loading state
            submitButton.classList.add('loading');
            submitButton.disabled = true;
            
            // Submit form
            this.submit();
        }
    });
    
    // Clear form button
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear all form data?')) {
                form.reset();
            }
        });
    }
    
    // Real-time validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
    
    // Quantity validation (must be at least min order quantity)
    const quantityInput = document.getElementById('id_min_order_quantity');
    if (quantityInput) {
        quantityInput.addEventListener('blur', function() {
            const value = parseInt(this.value);
            if (value < 1) {
                showError(this, 'Minimum order quantity must be at least 1');
            } else {
                clearError(this);
            }
        });
    }
    
    // Price validation (must be positive)
    if (priceInput) {
        priceInput.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (value <= 0) {
                showError(this, 'Price must be greater than 0');
            } else {
                clearError(this);
            }
        });
    }
    
    // Auto-format phone number
    const phoneInput = document.getElementById('id_phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            formatPhoneNumber(this);
        });
    }
    
    // Form validation functions
    function validateForm() {
        let isValid = true;
        
        // Validate all required fields
        requiredFields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });
        
        // Custom validation for specific fields
        if (quantityInput && parseInt(quantityInput.value) < 1) {
            showError(quantityInput, 'Minimum order quantity must be at least 1');
            isValid = false;
        }
        
        if (priceInput && parseFloat(priceInput.value) <= 0) {
            showError(priceInput, 'Price must be greater than 0');
            isValid = false;
        }
        
        return isValid;
    }
    
    function validateField(field) {
        if (field.hasAttribute('required') && !field.value.trim()) {
            showError(field, 'This field is required');
            return false;
        }
        
        if (field.type === 'email' && field.value) {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(field.value)) {
                showError(field, 'Please enter a valid email address');
                return false;
            }
        }
        
        clearError(field);
        return true;
    }
    
    function showError(field, message) {
        clearError(field);
        field.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
    
    function formatPhoneNumber(input) {
        // Remove all non-digit characters
        let phoneNumber = input.value.replace(/\D/g, '');
        
        // Format based on length
        if (phoneNumber.length > 0) {
            phoneNumber = phoneNumber.match(new RegExp('.{1,4}', 'g')).join(' ');
        }
        
        // Update input value
        input.value = phoneNumber;
    }
    
    // Auto-calculate total price based on quantity
    const quantityAvailableInput = document.getElementById('id_quantity_available');
    const totalValueSpan = document.createElement('span');
    
    if (quantityAvailableInput && priceInput) {
        totalValueSpan.className = 'total-value';
        totalValueSpan.style.marginLeft = '10px';
        totalValueSpan.style.fontWeight = '600';
        totalValueSpan.style.color = '#28a745';
        
        quantityAvailableInput.parentNode.appendChild(totalValueSpan);
        
        const updateTotalValue = () => {
            const quantity = parseInt(quantityAvailableInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            const totalValue = quantity * price;
            
            if (quantity > 0 && price > 0) {
                totalValueSpan.textContent = `Total value: $${totalValue.toFixed(2)}`;
            } else {
                totalValueSpan.textContent = '';
            }
        };
        
        quantityAvailableInput.addEventListener('input', updateTotalValue);
        priceInput.addEventListener('input', updateTotalValue);
        
        // Initial calculation
        updateTotalValue();
    }
    
    // Enhance form with character counters for textareas
    const textareas = form.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'char-counter';
            counter.style.fontSize = '0.8rem';
            counter.style.color = '#6c757d';
            counter.style.textAlign = 'right';
            counter.style.marginTop = '5px';
            
            textarea.parentNode.appendChild(counter);
            
            const updateCounter = () => {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${remaining} characters remaining`;
                
                if (remaining < 10) {
                    counter.style.color = '#dc3545';
                } else {
                    counter.style.color = '#6c757d';
                }
            };
            
            textarea.addEventListener('input', updateCounter);
            updateCounter(); // Initial update
        }
    });
});
// poultrys/static/poultrys/js/veterinary_consultancy.js
document.addEventListener('DOMContentLoaded', function() {
    // Modal functionality
    const modal = document.getElementById('bookingModal');
    const closeModal = document.querySelector('.close-modal');
    const bookButtons = document.querySelectorAll('.book-btn');
    const bookingForm = document.getElementById('bookingForm');

    // Open modal with consultant and service data
    bookButtons.forEach(button => {
        button.addEventListener('click', function() {
            const consultantId = this.getAttribute('data-consultant-id');
            const consultantName = this.getAttribute('data-consultant-name');
            const serviceId = this.getAttribute('data-service-id');
            const serviceType = this.getAttribute('data-service-type');
            const servicePrice = this.getAttribute('data-service-price');

            document.getElementById('consultantId').value = consultantId;
            document.getElementById('serviceId').value = serviceId;
            document.getElementById('consultantName').value = consultantName;
            document.getElementById('serviceType').value = serviceType;
            document.getElementById('servicePrice').value = '$' + servicePrice;

            modal.style.display = 'block';
        });
    });

    // Close modal
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Handle form submission
    bookingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            consultant_id: document.getElementById('consultantId').value,
            service_id: document.getElementById('serviceId').value,
            user_name: document.getElementById('userName').value,
            user_email: document.getElementById('userEmail').value,
            user_phone: document.getElementById('userPhone').value,
            preferred_date: document.getElementById('consultationDate').value,
            preferred_time: document.getElementById('consultationTime').value,
            message: document.getElementById('message').value,
        };

        // AJAX request to submit the booking
        const csrfToken = bookingForm.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch(bookingForm.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                modal.style.display = 'none';
                bookingForm.reset();
            } else {
                alert('Error: ' + (data.message || 'Please check your input'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });

    // Consultant item dropdown functionality
    const consultantItems = document.querySelectorAll('.consultant-item');
    consultantItems.forEach(item => {
        const header = item.querySelector('.consultant-header');
        header.addEventListener('click', function() {
            item.classList.toggle('active');
        });
    });
});
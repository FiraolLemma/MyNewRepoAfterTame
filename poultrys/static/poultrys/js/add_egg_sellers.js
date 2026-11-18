document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.egg-seller-form');
    if (!form) return;

    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        form.addEventListener('submit', function () {
            submitButton.disabled = true;
            submitButton.setAttribute('aria-busy', 'true');
            submitButton.textContent = submitButton.dataset.savingLabel || 'Saving...';
        });
    }

    form.querySelectorAll('input, select, textarea').forEach(function (field) {
        field.addEventListener('input', function () {
            if (field.checkValidity()) {
                field.removeAttribute('aria-invalid');
            }
        });

        field.addEventListener('invalid', function () {
            field.setAttribute('aria-invalid', 'true');
        });
    });
});
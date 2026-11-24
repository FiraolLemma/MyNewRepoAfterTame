document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("[data-livestock-create-form]");
    if (!form) return;

    const fileInput = form.querySelector('input[type="file"]');
    const preview = form.querySelector("[data-livestock-image-preview]");
    const previewImage = form.querySelector("[data-livestock-preview-image]");
    if (!fileInput || !preview || !previewImage) return;

    let previewUrl = null;
    fileInput.addEventListener("change", function () {
        const file = fileInput.files && fileInput.files[0];
        if (previewUrl) URL.revokeObjectURL(previewUrl);

        if (!file || !file.type.startsWith("image/")) {
            preview.hidden = true;
            previewImage.removeAttribute("src");
            previewUrl = null;
            return;
        }

        previewUrl = URL.createObjectURL(file);
        previewImage.src = previewUrl;
        preview.hidden = false;
    });

    window.addEventListener("pagehide", function () {
        if (previewUrl) URL.revokeObjectURL(previewUrl);
    }, { once: true });
});
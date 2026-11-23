document.addEventListener("DOMContentLoaded", function () {
    const image = document.querySelector("[data-product-detail-image]");
    if (image && image.dataset.fallback) {
        image.addEventListener("error", function () {
            if (image.src !== image.dataset.fallback) image.src = image.dataset.fallback;
        });
    }

    const shareButton = document.querySelector("[data-product-share]");
    const status = document.querySelector("[data-share-status]");
    if (!shareButton || !status) return;

    shareButton.addEventListener("click", async function () {
        try {
            if (navigator.share) {
                await navigator.share({
                    title: document.title,
                    url: window.location.href
                });
                status.textContent = "Product shared.";
                return;
            }

            await navigator.clipboard.writeText(window.location.href);
            status.textContent = "Link copied to clipboard.";
        } catch (error) {
            if (error.name !== "AbortError") {
                status.textContent = "Unable to share this product from this browser.";
                console.error("Product sharing failed:", error);
            }
        }
    });
});
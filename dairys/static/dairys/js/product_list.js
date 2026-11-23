document.addEventListener("DOMContentLoaded", function () {
    const listing = document.querySelector("[data-dairy-products]");
    if (!listing) return;

    const grid = listing.querySelector("[data-product-grid]");
    const cards = Array.from(listing.querySelectorAll("[data-product-card]"));
    const filters = Array.from(listing.querySelectorAll("[data-filter]"));
    const search = listing.querySelector("[data-product-search]");
    const sort = listing.querySelector("[data-product-sort]");
    const resultCount = listing.querySelector("[data-product-count]");
    const noMatch = listing.querySelector("[data-product-no-match]");
    let activeCategory = "all";

    listing.querySelectorAll("[data-product-image][data-fallback]").forEach(function (image) {
        image.addEventListener("error", function () {
            if (image.src !== image.dataset.fallback) image.src = image.dataset.fallback;
        });
    });

    function render() {
        const query = search ? search.value.trim().toLocaleLowerCase() : "";
        let visibleCount = 0;

        cards.forEach(function (card) {
            const searchableText = (card.dataset.search || card.dataset.name || "").toLocaleLowerCase();
            const matchesCategory = activeCategory === "all" || card.dataset.category === activeCategory;
            const matchesSearch = !query || searchableText.includes(query);
            const isVisible = matchesCategory && matchesSearch;
            card.hidden = !isVisible;
            if (isVisible) visibleCount += 1;
        });

        if (resultCount) resultCount.textContent = String(visibleCount);
        if (noMatch) noMatch.hidden = visibleCount > 0 || cards.length === 0;
    }

    filters.forEach(function (button) {
        button.addEventListener("click", function () {
            activeCategory = button.dataset.filter || "all";
            filters.forEach(function (filter) {
                const isActive = filter === button;
                filter.classList.toggle("is-active", isActive);
                filter.setAttribute("aria-pressed", String(isActive));
            });
            render();
        });
    });

    if (search) search.addEventListener("input", render);

    if (sort && grid) {
        sort.addEventListener("change", function () {
            const sortedCards = cards.slice().sort(function (first, second) {
                const firstPrice = Number(first.dataset.price) || 0;
                const secondPrice = Number(second.dataset.price) || 0;
                const firstCreated = Number(first.dataset.created) || 0;
                const secondCreated = Number(second.dataset.created) || 0;

                if (sort.value === "price-low") return firstPrice - secondPrice;
                if (sort.value === "price-high") return secondPrice - firstPrice;
                if (sort.value === "name") {
                    return (first.dataset.name || "").localeCompare(second.dataset.name || "");
                }
                return secondCreated - firstCreated;
            });

            sortedCards.forEach(function (card) {
                grid.appendChild(card);
            });
        });
    }

    render();
});
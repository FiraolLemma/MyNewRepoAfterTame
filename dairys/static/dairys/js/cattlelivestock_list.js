document.addEventListener("DOMContentLoaded", function () {
    const listing = document.querySelector("[data-livestock-listing]");
    if (!listing) return;

    const grid = listing.querySelector("[data-livestock-grid]");
    const cards = Array.from(listing.querySelectorAll("[data-livestock-card]"));
    const filters = Array.from(listing.querySelectorAll("[data-filter]"));
    const search = listing.querySelector("[data-livestock-search]");
    const sort = listing.querySelector("[data-livestock-sort]");
    const resultCount = listing.querySelector("[data-result-count]");
    const noMatch = listing.querySelector("[data-no-match]");
    let activeCategory = "all";

    function render() {
        const query = search ? search.value.trim().toLocaleLowerCase() : "";
        let visibleCount = 0;

        cards.forEach(function (card) {
            const matchesCategory = activeCategory === "all" || card.dataset.category === activeCategory;
            const searchText = (card.dataset.search || card.dataset.name || "").toLocaleLowerCase();
            const matchesSearch = !query || searchText.includes(query);
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
(() => {
    const consultantSearch = document.querySelector("[data-consultant-search]");
    const consultantCards = Array.from(document.querySelectorAll("[data-consultant-card]"));
    const consultantCount = document.querySelector("[data-result-count]");
    const noConsultantsMatch = document.querySelector("[data-no-match]");

    if (consultantSearch && consultantCards.length) {
        consultantSearch.addEventListener("input", () => {
            const query = consultantSearch.value.trim().toLocaleLowerCase();
            let visibleCount = 0;

            consultantCards.forEach((card) => {
                const matches = card.dataset.search.toLocaleLowerCase().includes(query);
                card.hidden = !matches;
                if (matches) {
                    visibleCount += 1;
                }
            });

            if (consultantCount) {
                consultantCount.textContent = String(visibleCount);
            }
            if (noConsultantsMatch) {
                noConsultantsMatch.hidden = visibleCount > 0;
            }
        });
    }
})();

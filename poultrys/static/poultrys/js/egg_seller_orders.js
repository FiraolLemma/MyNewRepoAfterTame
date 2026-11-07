document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector(".orders-table");
    const headers = table.querySelectorAll("th");
    const rows = table.querySelectorAll("tbody tr");

    // ---------- Sorting ----------
    headers.forEach((header, index) => {
        header.addEventListener("click", () => {
            const rowsArray = Array.from(rows);
            const isAscending = header.classList.contains("asc");

            rowsArray.sort((a, b) => {
                const aText = a.children[index].innerText.trim();
                const bText = b.children[index].innerText.trim();

                if (!isNaN(aText) && !isNaN(bText)) {
                    return isAscending
                        ? bText - aText
                        : aText - bText;
                }
                return isAscending
                    ? bText.localeCompare(aText)
                    : aText.localeCompare(bText);
            });

            // Reorder rows
            rowsArray.forEach(row => table.querySelector("tbody").appendChild(row));

            headers.forEach(h => h.classList.remove("asc", "desc"));
            header.classList.toggle(isAscending ? "desc" : "asc");
        });
    });

    // ---------- Mobile Data Labels ----------
    if (window.innerWidth <= 768) {
        const headLabels = Array.from(headers).map(h => h.innerText);
        rows.forEach(row => {
            row.querySelectorAll("td").forEach((td, i) => {
                td.setAttribute("data-label", headLabels[i]);
            });
        });
    }

    // ---------- Search (optional) ----------
    const searchBox = document.createElement("input");
    searchBox.type = "text";
    searchBox.placeholder = "Search orders...";
    searchBox.className = "order-search";
    document.querySelector(".orders-page").insertBefore(searchBox, table);

    searchBox.addEventListener("keyup", () => {
        const query = searchBox.value.toLowerCase();
        rows.forEach(row => {
            row.style.display = row.innerText.toLowerCase().includes(query) ? "" : "none";
        });
    });
});

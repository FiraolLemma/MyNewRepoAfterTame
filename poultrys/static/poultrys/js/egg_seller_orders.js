document.addEventListener('DOMContentLoaded', function () {
    const table = document.querySelector('.orders-table');
    if (!table) return;

    const searchInput = document.getElementById('orderSearch');
    const statusFilter = document.getElementById('statusFilter');
    const noResults = document.querySelector('.orders-no-results');
    const body = table.querySelector('tbody');
    const headers = table.querySelectorAll('.sort-button');

    function filterOrders() {
        const query = searchInput ? searchInput.value.trim().toLocaleLowerCase() : '';
        const status = statusFilter ? statusFilter.value : '';
        let visibleCount = 0;

        body.querySelectorAll('tr').forEach(function (row) {
            const matchesQuery = !query || row.textContent.toLocaleLowerCase().includes(query);
            const matchesStatus = !status || row.dataset.orderStatus === status;
            const isVisible = matchesQuery && matchesStatus;
            row.hidden = !isVisible;
            if (isVisible) visibleCount += 1;
        });

        if (noResults) noResults.hidden = visibleCount > 0;
    }

    if (searchInput) searchInput.addEventListener('input', filterOrders);
    if (statusFilter) statusFilter.addEventListener('change', filterOrders);

    headers.forEach(function (button) {
        button.addEventListener('click', function () {
            const header = button.closest('th');
            const columnIndex = Array.from(header.parentElement.children).indexOf(header);
            const rows = Array.from(body.querySelectorAll('tr'));
            const ascending = button.dataset.direction !== 'ascending';
            const sortType = button.dataset.sort;

            rows.sort(function (left, right) {
                const leftCell = left.children[columnIndex];
                const rightCell = right.children[columnIndex];
                let leftValue;
                let rightValue;

                if (sortType === 'date') {
                    leftValue = Number(leftCell.dataset.orderTimestamp) || 0;
                    rightValue = Number(rightCell.dataset.orderTimestamp) || 0;
                } else if (sortType === 'number') {
                    leftValue = parseFloat(leftCell.textContent.replace(/[^\d.-]/g, '')) || 0;
                    rightValue = parseFloat(rightCell.textContent.replace(/[^\d.-]/g, '')) || 0;
                } else {
                    leftValue = leftCell.textContent.trim().toLocaleLowerCase();
                    rightValue = rightCell.textContent.trim().toLocaleLowerCase();
                }

                if (leftValue < rightValue) return ascending ? -1 : 1;
                if (leftValue > rightValue) return ascending ? 1 : -1;
                return 0;
            });

            rows.forEach(function (row) {
                body.appendChild(row);
            });

            headers.forEach(function (otherButton) {
                otherButton.removeAttribute('data-direction');
                otherButton.classList.remove('is-sorted');
                const icon = otherButton.querySelector('i');
                if (icon) icon.className = 'fas fa-sort';
            });
            button.dataset.direction = ascending ? 'ascending' : 'descending';
            button.classList.add('is-sorted');
            const icon = button.querySelector('i');
            if (icon) icon.className = ascending ? 'fas fa-sort-up' : 'fas fa-sort-down';
            filterOrders();
        });
    });
});

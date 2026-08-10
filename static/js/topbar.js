/* Smart Campus Global Topbar Live Search */
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("globalSearchInput");
    const searchResults = document.getElementById("globalSearchResults");

    if (!searchInput || !searchResults) return;

    let debounceTimer;

    searchInput.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length < 2) {
            searchResults.style.display = "none";
            searchResults.innerHTML = "";
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/dashboard/api/analytics/?search=${encodeURIComponent(query)}`)
                .then(response => response.ok ? response.json() : {})
                .then(data => {
                    let html = '';
                    if (data.courses && data.courses.length > 0) {
                        html += '<div class="fw-bold small text-muted px-2 py-1">Courses</div>';
                        data.courses.forEach(c => {
                            html += `<a href="/courses/${c.id}/" class="dropdown-item py-1 px-2 rounded small text-truncate"><i class="bi bi-book me-2 text-primary"></i>${c.name} (${c.code})</a>`;
                        });
                    }
                    if (!html) {
                        html = '<div class="text-center py-2 text-muted small"><i class="bi bi-search me-1"></i>No matching results</div>';
                    }
                    searchResults.innerHTML = html;
                    searchResults.style.display = "block";
                })
                .catch(() => {
                    searchResults.style.display = "none";
                });
        }, 300);
    });

    document.addEventListener("click", function (e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = "none";
        }
    });
});

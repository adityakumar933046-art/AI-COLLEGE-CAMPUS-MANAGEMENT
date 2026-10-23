/* Smart Campus Theme Toggle Logic */
document.addEventListener("DOMContentLoaded", function () {
    const themeToggleBtn = document.getElementById("themeToggle");
    const themeToggleMenu = document.getElementById("themeToggleMenu");
    const themeIcon = document.getElementById("themeIcon");

    function applyTheme(theme) {
        if (theme === "dark") {
            document.body.classList.add("dark-mode");
            if (themeIcon) themeIcon.className = "bi bi-sun fs-5 text-warning";
        } else {
            document.body.classList.remove("dark-mode");
            if (themeIcon) themeIcon.className = "bi bi-moon-stars fs-5";
        }
    }

    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem("theme") || "light";
    applyTheme(savedTheme);

    function toggleTheme() {
        const isDark = document.body.classList.contains("dark-mode");
        const newTheme = isDark ? "light" : "dark";
        localStorage.setItem("theme", newTheme);
        applyTheme(newTheme);
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function (e) {
            e.preventDefault();
            toggleTheme();
        });
    }

    if (themeToggleMenu) {
        themeToggleMenu.addEventListener("click", function (e) {
            e.preventDefault();
            toggleTheme();
        });
    }
});

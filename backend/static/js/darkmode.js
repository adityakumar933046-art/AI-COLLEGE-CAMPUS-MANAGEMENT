// ==========================================
// SMART CAMPUS ERP - DARK MODE CONTROLLER
// ==========================================

document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("themeToggle");
    const themeToggleMenu = document.getElementById("themeToggleMenu");
    const themeIcon = document.getElementById("themeIcon");

    function applyTheme(theme) {
        if (theme === "dark") {
            document.body.classList.add("dark-mode");
            if (themeIcon) {
                themeIcon.classList.remove("bi-moon-stars");
                themeIcon.classList.add("bi-sun");
            }
        } else {
            document.body.classList.remove("dark-mode");
            if (themeIcon) {
                themeIcon.classList.remove("bi-sun");
                themeIcon.classList.add("bi-moon-stars");
            }
        }
    }

    // Initialize from localStorage or default to light
    const savedTheme = localStorage.getItem("campus_theme") || "light";
    applyTheme(savedTheme);

    function toggleTheme(e) {
        if (e) e.preventDefault();
        const isDark = document.body.classList.contains("dark-mode");
        const newTheme = isDark ? "light" : "dark";
        try {
            localStorage.setItem("campus_theme", newTheme);
        } catch (err) {
            // Ignore if localStorage is unavailable
        }
        applyTheme(newTheme);
    }

    if (themeToggle) {
        themeToggle.addEventListener("click", toggleTheme);
    }

    if (themeToggleMenu) {
        themeToggleMenu.addEventListener("click", toggleTheme);
    }
});

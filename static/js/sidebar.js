document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar") || document.querySelector("#sidebar");
    const mainContent = document.querySelector(".main-content");
    const toggleBtns = document.querySelectorAll(".menu-toggle, .sidebar-toggle, #sidebarToggle, #sidebarToggleBtn");

    if (!sidebar) return;

    // Create or locate overlay
    let overlay = document.querySelector(".sidebar-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.className = "sidebar-overlay";
        document.body.appendChild(overlay);
    }

    // Restore desktop collapsed state from localStorage
    if (window.innerWidth > 992) {
        if (localStorage.getItem("sidebar") === "collapsed") {
            sidebar.classList.add("collapsed");
            if (mainContent) {
                mainContent.classList.add("expand");
            }
        }
    }

    // Toggle click listener for all menu buttons
    toggleBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            if (window.innerWidth <= 992) {
                // Mobile / Tablet: Smooth slide-in
                sidebar.classList.toggle("show");
                overlay.classList.toggle("show");
                overlay.classList.toggle("active");
            } else {
                // Desktop: Collapse / Expand
                sidebar.classList.toggle("collapsed");
                if (mainContent) {
                    mainContent.classList.toggle("expand");
                }
                if (sidebar.classList.contains("collapsed")) {
                    localStorage.setItem("sidebar", "collapsed");
                } else {
                    localStorage.setItem("sidebar", "expanded");
                }
            }
        });
    });

    // Close overlay on click (Mobile / Tablet)
    overlay.addEventListener("click", function () {
        sidebar.classList.remove("show");
        overlay.classList.remove("show");
        overlay.classList.remove("active");
    });

    // Reset mobile state on window resize
    window.addEventListener("resize", function () {
        if (window.innerWidth > 992) {
            sidebar.classList.remove("show");
            overlay.classList.remove("show");
            overlay.classList.remove("active");
        }
    });
});

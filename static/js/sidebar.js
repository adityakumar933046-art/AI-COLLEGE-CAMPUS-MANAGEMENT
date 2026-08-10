document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.querySelector(".sidebar");
    const mainContent = document.querySelector(".main-content");
    const toggleBtn = document.querySelector(".menu-toggle");

    if (!sidebar || !toggleBtn) return;

    let overlay = document.querySelector(".sidebar-overlay");

    if (!overlay) {
        overlay = document.createElement("div");
        overlay.className = "sidebar-overlay";
        document.body.appendChild(overlay);
    }

    // ==============================
    // Restore Sidebar State
    // ==============================

    if (localStorage.getItem("sidebar") === "collapsed") {
        sidebar.classList.add("collapsed");

        if (mainContent) {
            mainContent.classList.add("expand");
        }
    }

    // ==============================
    // Toggle Sidebar
    // ==============================

    toggleBtn.addEventListener("click", function () {

        // Blink Effect
        sidebar.classList.add("blink");

        setTimeout(() => {
            sidebar.classList.remove("blink");
        }, 500);

        // Rotate Icon
        const icon = toggleBtn.querySelector("i");

        if (icon) {
            icon.classList.toggle("rotate");
        }

        if (window.innerWidth <= 992) {

            sidebar.classList.toggle("show");
            overlay.classList.toggle("show");

        } else {

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

    // ==============================
    // Overlay Close
    // ==============================

    overlay.addEventListener("click", function () {

        sidebar.classList.remove("show");
        overlay.classList.remove("show");

    });

    // ==============================
    // Submenu
    // ==============================

    document.querySelectorAll(".menu-link").forEach(link => {

        link.addEventListener("click", function (e) {

            const parent = this.parentElement;
            const submenu = parent.querySelector(".submenu");

            if (submenu) {

                e.preventDefault();

                document.querySelectorAll(".menu-open").forEach(item => {

                    if (item !== parent) {
                        item.classList.remove("menu-open");
                    }

                });

                parent.classList.toggle("menu-open");

            }

        });

    });

    // ==============================
    // Active Menu
    // ==============================

    const menuItems = document.querySelectorAll(".sidebar-menu li");

    const activeIndex = localStorage.getItem("activeMenu");

    if (activeIndex !== null && menuItems[activeIndex]) {

        menuItems[activeIndex].classList.add("active");

    }

    menuItems.forEach((item, index) => {

        item.addEventListener("click", function () {

            menuItems.forEach(i => i.classList.remove("active"));

            this.classList.add("active");

            localStorage.setItem("activeMenu", index);

        });

    });

    // ==============================
    // Responsive
    // ==============================

    window.addEventListener("resize", function () {

        if (window.innerWidth > 992) {

            sidebar.classList.remove("show");
            overlay.classList.remove("show");

        }

    });

});
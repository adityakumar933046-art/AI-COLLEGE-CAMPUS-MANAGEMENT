// ==========================================
// SMART CAMPUS ERP - NOTIFICATIONS
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    const bellBtn = document.getElementById("notificationBtn");
    const dropdown = document.getElementById("notificationDropdown");
    const badge = document.getElementById("notificationBadge");
    const clearBtn = document.getElementById("clearNotifications");

    // Toggle Notification Dropdown
    if (bellBtn && dropdown) {

        bellBtn.addEventListener("click", function (e) {

            e.stopPropagation();

            dropdown.classList.toggle("show");

        });

    }

    // Close when clicking outside
    document.addEventListener("click", function () {

        if (dropdown) {

            dropdown.classList.remove("show");

        }

    });

    if (dropdown) {

        dropdown.addEventListener("click", function (e) {

            e.stopPropagation();

        });

    }

    // Mark notification as read
    const items = document.querySelectorAll(".notification-item");

    items.forEach(function (item) {

        item.addEventListener("click", function () {

            this.classList.add("read");

            updateBadge();

        });

    });

    // Clear All Notifications
    if (clearBtn) {

        clearBtn.addEventListener("click", function () {

            const list = document.getElementById("notificationList");

            if (list) {

                list.innerHTML = `
                    <div class="text-center p-3 text-muted">
                        No Notifications
                    </div>
                `;

            }

            if (badge) {

                badge.style.display = "none";

            }

        });

    }

    // Badge Count Update
    function updateBadge() {

        if (!badge) return;

        const unread = document.querySelectorAll(".notification-item:not(.read)");

        if (unread.length > 0) {

            badge.innerText = unread.length;

            badge.style.display = "flex";

        } else {

            badge.style.display = "none";

        }

    }

    updateBadge();

});
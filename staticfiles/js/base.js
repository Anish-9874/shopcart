/**
 * Global notification handling: one websocket connection for the whole
 * site, and a navbar badge that stays in sync with it.
 *
 * Include this on every page (e.g. from base.html), and put a badge
 * element with id="notification-badge" in the navbar wherever the bell
 * icon lives. Example markup:
 *
 *   <a href="{% url 'notifications:list' %}" class="notif-bell">
 *     🔔
 *     <span id="notification-badge" class="notif-badge" style="display:none;"></span>
 *   </a>
 */
(function () {
    let socket = null;
    let reconnectDelay = 1000;

    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }

        return cookieValue;
    }

    function getCsrfToken() {
        const cookieToken = getCookie("csrftoken");
        const formToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return cookieToken || (formToken && formToken.value);
    }

    function setBadgeCount(count) {
        const badge = document.getElementById("notification-badge");
        if (!badge) return;

        const safeCount = Math.max(0, count);

        if (safeCount > 0) {
            badge.textContent = safeCount > 99 ? "99+" : String(safeCount);
            badge.style.display = "inline-block";
        } else {
            badge.textContent = "0";
            badge.style.display = "none";
        }
    }

    function getBadgeCount() {
        const badge = document.getElementById("notification-badge");
        if (!badge) return 0;
        return parseInt(badge.textContent, 10) || 0;
    }

    function bumpBadge(delta) {
        setBadgeCount(getBadgeCount() + delta);
    }

    function fetchUnreadCount() {
        const url = (window.NOTIFICATIONS_CONFIG && window.NOTIFICATIONS_CONFIG.unreadCountUrl)
            || "/notifications/unread-count/";

        fetch(url)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`unread-count request failed: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => setBadgeCount(data.count))
            .catch((error) => console.error("Unable to fetch unread count.", error));
    }

    function markAsRead(notificationId, readUrl) {
        return fetch(readUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCsrfToken(),
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Request failed with status ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                // Only decrement if this notification actually flipped from
                // unread to read -- clicking an already-read item is a no-op.
                if (data.success && data.was_unread) {
                    bumpBadge(-1);
                }
                return data;
            })
            .catch((error) => {
                console.error("Unable to mark notification as read.", error);
                return { success: false };
            });
    }

    function connectSocket() {
        const protocol = location.protocol === "https:" ? "wss" : "ws";
        socket = new WebSocket(`${protocol}://${location.host}/ws/notifications/`);

        socket.onopen = () => {
            reconnectDelay = 1000; // reset backoff after a clean connect
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === "notification") {
                bumpBadge(1);

                // Let any page-specific script (e.g. the notifications list
                // page) react to a new notification without owning the socket.
                document.dispatchEvent(
                    new CustomEvent("notification:new", { detail: data })
                );
            }
        };

        socket.onclose = () => {
            // Reconnect with simple backoff, e.g. after a server restart
            // or the user's laptop waking from sleep.
            setTimeout(connectSocket, reconnectDelay);
            reconnectDelay = Math.min(reconnectDelay * 2, 30000);
        };

        socket.onerror = () => {
            console.error("Notification socket error.");
        };
    }

    window.Notifications = {
        fetchUnreadCount,
        setBadgeCount,
        bumpBadge,
        markAsRead,
    };

    document.addEventListener("DOMContentLoaded", () => {
        fetchUnreadCount();
        connectSocket();
    });
})();
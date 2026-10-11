
(function () {
    "use strict";

    let socket = null;
    let reconnectTimer = null;
    let reconnectDelay = 1000;
    let countRequestInProgress = false;

    function setBadgeCount(count) {
        const safeCount = Math.max(0, Number(count) || 0);

        [
            document.getElementById("notification-badge"),
            document.getElementById("admin-notification-badge")
        ].filter(Boolean).forEach(function (badge) {
            badge.textContent = safeCount > 99 ? "99+" : String(safeCount);
            badge.style.display = safeCount > 0 ? "inline-block" : "none";
        });
    }

    function getBadgeCount() {
        const badge =
            document.getElementById("admin-notification-badge") ||
            document.getElementById("notification-badge");

        return badge ? parseInt(badge.textContent, 10) || 0 : 0;
    }

    
    async function fetchUnreadCount() {
        try {
            const response = await fetch("/notifications/unread-count/", {
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error("Unread count request failed: " + response.status);
            }

            const data = await response.json();
            setBadgeCount(data.count);
        } catch (error) {
            console.error("Could not fetch unread notifications:", error);
        }
    }


    async function markAsRead(id, url) {
        const csrfToken = getCookie("csrftoken");

        const response = await fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok) {
            throw new Error("Mark-as-read request failed: " + response.status);
        }

        const data = await response.json();

        if (data.success && data.was_unread) {
            // The database has confirmed this notification was unread.
            setBadgeCount(Math.max(0, getBadgeCount() - 1));
        }

        return data;
    }

    function getCookie(name) {
        const prefix = name + "=";
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(prefix)) {
                return decodeURIComponent(cookie.substring(prefix.length));
            }
        }

        return "";
    }

    function connectWebSocket() {
        if (socket && (
            socket.readyState === WebSocket.OPEN ||
            socket.readyState === WebSocket.CONNECTING
        )) {
            return;
        }

        const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
        socket = new WebSocket(
            scheme + "//" + window.location.host + "/ws/notifications/"
        );

        socket.onopen = function () {
            console.log("Notification WebSocket connected.");
            reconnectDelay = 1000;
            fetchUnreadCount();
        };

        socket.onmessage = function (event) {
            let data;

            try {
                data = JSON.parse(event.data);
            } catch (error) {
                console.error("Invalid notification WebSocket data:", error);
                return;
            }

            if (data.type === "notification") {
                // Refresh from the database to avoid duplicate increments.
                fetchUnreadCount();

                document.dispatchEvent(new CustomEvent("notification:new", {
                    detail: data
                }));
            }
        };

        socket.onclose = function () {
            clearTimeout(reconnectTimer);

            reconnectTimer = setTimeout(function () {
                reconnectDelay = Math.min(reconnectDelay * 2, 30000);
                connectWebSocket();
            }, reconnectDelay);
        };

        socket.onerror = function (error) {
            console.error("Notification WebSocket error:", error);
            socket.close();
        };
    }

    window.Notifications = {
        fetchUnreadCount: fetchUnreadCount,
        setBadgeCount: setBadgeCount,
        getBadgeCount: getBadgeCount,
        markAsRead: markAsRead
    };

    document.addEventListener("DOMContentLoaded", function () {
        fetchUnreadCount();
        connectWebSocket();
    });
})();

/**
 * ChallengeHire - Core Client-Side Utilities
 * Handles dynamic notifications, alerts, modals, and responsive interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // 2. Fetch unread notification count
    const notifBadge = document.getElementById('notif-badge');
    if (notifBadge) {
        fetch('/api/notifications/unread-count')
            .then(res => res.json())
            .then(data => {
                if (data.count > 0) {
                    notifBadge.textContent = data.count;
                    notifBadge.style.display = 'inline-block';
                } else {
                    notifBadge.style.display = 'none';
                }
            })
            .catch(() => {});
    }

    // 3. Simple Notification Popover Toggle
    const notifBtn = document.getElementById('notif-bell-btn');
    const notifMenu = document.getElementById('notif-dropdown-menu');
    if (notifBtn && notifMenu) {
        notifBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = notifMenu.style.display === 'block';
            if (!isOpen) {
                // Fetch list
                fetch('/api/notifications')
                    .then(res => res.json())
                    .then(items => {
                        const listContainer = document.getElementById('notif-items-list');
                        if (listContainer) {
                            if (items.length === 0) {
                                listContainer.innerHTML = '<div style="padding: 16px; color: #94a3b8; text-align: center; font-size: 0.85rem;">No notifications yet.</div>';
                            } else {
                                listContainer.innerHTML = items.map(n => `
                                    <a href="${n.link || '#'}" style="display: block; padding: 12px 16px; border-bottom: 1px solid #f1f5f9; text-decoration: none; color: inherit; transition: background 0.2s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
                                        <div style="font-weight: 600; font-size: 0.85rem; color: #0f172a;">${n.title}</div>
                                        <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">${n.message}</div>
                                        <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 4px;">${n.created_at}</div>
                                    </a>
                                `).join('');
                            }
                        }
                    });
                notifMenu.style.display = 'block';
                // Mark as read
                fetch('/api/notifications/mark-read', { method: 'POST' });
                if (notifBadge) notifBadge.style.display = 'none';
            } else {
                notifMenu.style.display = 'none';
            }
        });

        document.addEventListener('click', () => {
            if (notifMenu) notifMenu.style.display = 'none';
        });
    }
});

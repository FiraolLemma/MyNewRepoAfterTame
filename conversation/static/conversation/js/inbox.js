document.addEventListener('DOMContentLoaded', function() {
    console.log('📨 Inbox page loaded');
    
    if (USER_ID) {
        initializeWebSocket(USER_ID);
        startPolling(); // Fallback polling
    }

    // Mark as read when page loads
    markConversationsAsRead();
});

let socket;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
let pollingInterval;

function initializeWebSocket(userId) {
    // FIXED: Use the correct URL pattern from your routing.py
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socketUrl = `${protocol}//${window.location.host}/ws/user/${userId}/notifications/`;
    
    console.log('🔌 Connecting to WebSocket:', socketUrl);
    
    socket = new WebSocket(socketUrl);

    socket.onopen = function() {
        console.log('✅ WebSocket connected successfully');
        reconnectAttempts = 0;
        clearInterval(pollingInterval); // Stop polling if WebSocket works
    };

    socket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);
            console.log('📩 WebSocket message received:', data);
            
            if (data.type === 'unread_update') {
                updateUnreadBadge(data.conversation_id, data.count);
                updateNavbarBadge(); // Also update the main navbar badge
            }
        } catch (error) {
            console.error('❌ Error processing WebSocket message:', error);
        }
    };

    socket.onerror = function(error) {
        console.error('❌ WebSocket error:', error);
    };

    socket.onclose = function(e) {
        console.log(`🔌 WebSocket closed: ${e.code} - ${e.reason}`);
        if (reconnectAttempts < maxReconnectAttempts) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
            console.log(`🔄 Reconnecting in ${delay}ms...`);
            setTimeout(() => {
                reconnectAttempts++;
                initializeWebSocket(userId);
            }, delay);
        } else {
            console.log('⚠️  Max reconnection attempts reached, using polling fallback');
            startPolling();
        }
    };
}

function startPolling() {
    console.log('🔄 Starting polling fallback');
    clearInterval(pollingInterval);
    
    pollingInterval = setInterval(() => {
        fetchUnreadCounts();
    }, 5000); // Poll every 5 seconds
    
    // Initial fetch
    fetchUnreadCounts();
}

function fetchUnreadCounts() {
    console.log('📡 Polling for unread counts...');
    
    fetch(UNREAD_API_URL, {
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        console.log('✅ Polling response:', data);
        
        // Update all conversation badges
        if (data.by_conversation) {
            Object.entries(data.by_conversation).forEach(([conversationId, count]) => {
                updateUnreadBadge(conversationId, count);
            });
        }
        
        // Update navbar badge
        updateNavbarBadge(data.total_unread);
    })
    .catch(error => {
        console.error('❌ Polling error:', error);
    });
}

function updateUnreadBadge(conversationId, count) {
    const badge = document.getElementById(`unread-${conversationId}`);
    const card = badge?.closest('.conversation-card');
    
    console.log(`🔄 Updating badge for conversation ${conversationId}:`, count);
    
    if (!badge) {
        console.warn(`⚠️  Badge not found for conversation ${conversationId}`);
        return;
    }

    badge.textContent = count;
    
    if (count > 0) {
        badge.style.display = 'inline-flex';
        if (card) card.classList.add('unread');
    } else {
        badge.style.display = 'none';
        if (card) card.classList.remove('unread');
    }
}

function updateNavbarBadge(count) {
    // Update the main navbar badge too
    const navbarBadge = document.getElementById('navbarUnread');
    if (navbarBadge) {
        if (count > 0) {
            navbarBadge.textContent = count > 9 ? '9+' : count;
            navbarBadge.style.display = 'flex';
        } else {
            navbarBadge.style.display = 'none';
        }
    }
}

function markConversationsAsRead() {
    console.log('📝 Marking all conversations as read');
    
    fetch(MARK_AS_READ_URL, {
        method: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN,
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            console.log('✅ All conversations marked as read');
            // Update UI to reflect read status
            document.querySelectorAll('.unread-count').forEach(badge => {
                badge.style.display = 'none';
            });
            document.querySelectorAll('.conversation-card').forEach(card => {
                card.classList.remove('unread');
            });
            
            // Also update navbar badge
            updateNavbarBadge(0);
        }
    })
    .catch(error => {
        console.error('❌ Error marking as read:', error);
    });
}

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible, refresh counts
        fetchUnreadCounts();
    }
});

// Refresh when page gains focus
window.addEventListener('focus', fetchUnreadCounts);
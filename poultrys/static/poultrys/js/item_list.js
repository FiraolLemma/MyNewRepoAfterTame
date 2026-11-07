document.addEventListener('DOMContentLoaded', function() {
    // Like button functionality
    document.querySelectorAll('[data-action="like"]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            toggleLike(itemId, this);
        });
    });

    // Share button functionality
    document.querySelectorAll('[data-action="share"]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            handleShare(itemId, this);
        });
    });
});

async function toggleLike(itemId, button) {
    try {
        const response = await fetch(`/en/poultrys/items/${itemId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            credentials: 'same-origin'
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();

        if (data.status === 'success') {
            const countElement = button.querySelector('.interaction-count');
            if (countElement) {
                countElement.textContent = data.like_count;
            }

            if (data.has_liked) {
                button.classList.add('liked');
            } else {
                button.classList.remove('liked');
            }
            
            button.classList.toggle('liked');
            button.style.backgroundColor = '#e3f2fd';
            setTimeout(() => {
                button.style.backgroundColor = '';
            }, 400);
        }
    } catch (error) {
        console.error('Like toggle error:', error);
        alert('Failed to like/unlike. Please try again.');
    }
}

async function handleShare(itemId, button) {
    try {
        // First try the Web Share API
        if (navigator.share) {
            await navigator.share({
                title: 'Check out this poultry item!',
                text: 'I found this amazing poultry item you might like',
                url: window.location.href,
            });
        } else {
            // Fallback for browsers without Web Share API
            copyToClipboard(window.location.href);
            alert('Link copied to clipboard!');
        }

        // Record the share
        const response = await fetch(`/en/poultrys/items/${itemId}/share/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        });

        if (response.ok) {
            const data = await response.json();
            if (data.status === 'success') {
                const countElement = button.querySelector('.interaction-count');
                countElement.textContent = data.share_count;
                
                // Visual feedback
                button.style.backgroundColor = '#e8f5e9';
                setTimeout(() => {
                    button.style.backgroundColor = '';
                }, 500);
            }
        }
    } catch (error) {
        console.error('Share error:', error);
        if (error.name !== 'AbortError') {
            alert('Failed to share. Please try again.');
        }
    }
}

function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
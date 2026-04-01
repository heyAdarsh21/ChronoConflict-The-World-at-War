// Main JavaScript for WW2 Intelligence Operations Simulator

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('INTEL OPS SYSTEM INITIALIZED');
    
    // Add terminal-style typing effect
    const terminalElements = document.querySelectorAll('.terminal-text');
    terminalElements.forEach(el => {
        typeWriter(el, el.textContent, 50);
    });
});

// Typewriter effect
function typeWriter(element, text, speed) {
    element.textContent = '';
    let i = 0;
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatNumber(num) {
    return num.toLocaleString('en-US');
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('SYSTEM ERROR:', e.error);
});


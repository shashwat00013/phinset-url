// Content script for real-time URL checking
let currentUrl = window.location.href;

// Check URL when page loads
checkCurrentPage();

// Monitor URL changes (for SPAs)
let lastUrl = currentUrl;
new MutationObserver(() => {
    if (window.location.href !== lastUrl) {
        lastUrl = window.location.href;
        setTimeout(checkCurrentPage, 1000);
    }
}).observe(document, { subtree: true, childList: true });

async function checkCurrentPage() {
    try {
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: window.location.href })
        });

        const data = await response.json();
        
        // Show warning for unsafe/suspicious sites
        if (data.prediction === 'unsafe' || data.prediction === 'suspicious') {
            showWarning(data);
        }
    } catch (error) {
        // Silent fail - don't interrupt user if backend is down
    }
}

function showWarning(data) {
    // Remove existing warnings
    const existingWarning = document.getElementById('phishing-warning');
    if (existingWarning) {
        existingWarning.remove();
    }

    const warning = document.createElement('div');
    warning.id = 'phishing-warning';
    warning.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #ff4444;
        color: white;
        padding: 15px;
        text-align: center;
        z-index: 999999;
        border-bottom: 3px solid #cc0000;
        font-family: Arial, sans-serif;
        font-size: 14px;
        font-weight: bold;
    `;

    warning.innerHTML = `
        <div style="max-width: 800px; margin: 0 auto;">
            <strong>⚠️ ${data.prediction.toUpperCase()} WEBSITE DETECTED</strong> - 
            Confidence: ${data.confidence}% - 
            ${data.reason}
            <button onclick="this.parentElement.parentElement.remove()" style="
                margin-left: 10px;
                padding: 2px 8px;
                background: white;
                color: #ff4444;
                border: none;
                border-radius: 3px;
                cursor: pointer;
                font-weight: bold;
            ">✕</button>
        </div>
    `;

    document.body.insertBefore(warning, document.body.firstChild);
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        if (warning.parentElement) {
            warning.remove();
        }
    }, 10000);
}

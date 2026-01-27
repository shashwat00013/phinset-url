document.addEventListener('DOMContentLoaded', function() {
    const currentUrlEl = document.getElementById('currentUrl');
    const checkBtn = document.getElementById('checkBtn');
    const loadingEl = document.getElementById('loading');
    const resultEl = document.getElementById('result');
    const resultCardEl = document.getElementById('resultCard');
    const detailsEl = document.getElementById('details');

    // Get current tab URL
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const url = tabs[0].url;
        currentUrlEl.textContent = url;
        
        // Auto-check on load
        checkUrl(url);
    });

    checkBtn.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            checkUrl(tabs[0].url);
        });
    });

    async function checkUrl(url) {
        loadingEl.style.display = 'block';
        resultEl.style.display = 'none';

        try {
            const response = await fetch('http://localhost:5000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();
            showResult(data);

        } catch (error) {
            showError('Backend not available. Make sure Flask server is running.');
        } finally {
            loadingEl.style.display = 'none';
        }
    }

    function showResult(data) {
        resultEl.style.display = 'block';
        
        let cardClass = '';
        let statusText = '';
        let confidence = data.confidence || '0';
        let reason = data.reason || 'No specific reason';

        if (data.prediction === 'safe') {
            cardClass = 'safe';
            statusText = '✅ SAFE';
        } else if (data.prediction === 'suspicious') {
            cardClass = 'suspicious';
            statusText = '⚠️ SUSPICIOUS';
        } else if (data.prediction === 'unsafe') {
            cardClass = 'unsafe';
            statusText = '🚨 UNSAFE';
        } else {
            cardClass = 'suspicious';
            statusText = '❓ UNKNOWN';
        }

        resultCardEl.className = `result ${cardClass}`;
        resultCardEl.innerHTML = `
            <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">
                ${statusText}
            </div>
            <div style="font-size: 14px; margin-bottom: 5px;">
                Confidence: ${confidence}%
            </div>
            <div style="font-size: 12px;">
                ${reason}
            </div>
        `;

        // Show details if available
        if (data.details) {
            detailsEl.style.display = 'grid';
            detailsEl.innerHTML = `
                <div class="detail-item">
                    <div style="font-size: 10px; color: #666;">ML Probability</div>
                    <div style="font-weight: bold;">${(data.details.ml_probability * 100).toFixed(1)}%</div>
                </div>
                <div class="detail-item">
                    <div style="font-size: 10px; color: #666;">Rule Adjustment</div>
                    <div style="font-weight: bold;">${(data.details.rule_adjustment * 100).toFixed(1)}%</div>
                </div>
            `;
        } else {
            detailsEl.style.display = 'none';
        }
    }

    function showError(message) {
        resultEl.style.display = 'block';
        resultCardEl.className = 'result suspicious';
        resultCardEl.innerHTML = `
            <div style="font-size: 14px; color: #856404;">
                ${message}
            </div>
        `;
        detailsEl.style.display = 'none';
    }
});

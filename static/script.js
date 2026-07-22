/* ============================================
   TRUSTLENS AI - MAIN JAVASCRIPT
   ============================================ */

// ============================================
// 1. UTILITY FUNCTIONS
// ============================================

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Get confidence color based on score
function getConfidenceColor(confidence) {
    if (confidence < 30) return 'success';
    if (confidence < 60) return 'warning';
    return 'danger';
}

// Show alert message
function showAlert(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.style.maxWidth = '400px';
    alertDiv.style.borderRadius = '15px';
    alertDiv.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'warning' ? 'fa-exclamation-triangle' : type === 'danger' ? 'fa-times-circle' : 'fa-info-circle'} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, duration);
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    }).catch(() => {
        showAlert('Failed to copy', 'danger');
    });
}

// Validate input based on type
function validateInput(input, type) {
    if (!input || input.trim().length === 0) {
        showAlert('Please enter content to verify', 'warning');
        return false;
    }
    
    if (type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input)) {
            showAlert('Please enter a valid email address', 'warning');
            return false;
        }
    }
    
    if (type === 'url') {
        try {
            new URL(input);
        } catch {
            showAlert('Please enter a valid URL (include https://)', 'warning');
            return false;
        }
    }
    
    return true;
}

// ============================================
// 2. VERIFICATION FUNCTIONS
// ============================================

// Handle verification
async function verifyContent(content, type) {
    try {
        const response = await fetch('/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content, type })
        });
        
        if (!response.ok) {
            throw new Error('Server error');
        }
        
        return await response.json();
    } catch (error) {
        showAlert('Error verifying: ' + error.message, 'danger');
        throw error;
    }
}

// Display verification results
function displayResults(data) {
    const resultArea = document.getElementById('resultArea');
    const resultAlert = document.getElementById('resultAlert');
    const resultTitle = document.getElementById('resultTitle');
    const resultExplanation = document.getElementById('resultExplanation');
    const confidenceBar = document.getElementById('confidenceBar');
    
    resultArea.style.display = 'block';
    resultTitle.textContent = data.result;
    resultExplanation.textContent = data.explanation || 'No detailed explanation available';
    
    // Set alert style
    resultAlert.className = 'alert';
    if (data.result === 'Safe') {
        resultAlert.classList.add('alert-success');
        resultTitle.innerHTML = `<i class="fas fa-check-circle result-icon"></i> ${data.result}`;
    } else if (data.result === 'Suspicious') {
        resultAlert.classList.add('alert-warning');
        resultTitle.innerHTML = `<i class="fas fa-exclamation-triangle result-icon"></i> ${data.result}`;
    } else if (data.result === 'Scam') {
        resultAlert.classList.add('alert-danger');
        resultTitle.innerHTML = `<i class="fas fa-times-circle result-icon"></i> ${data.result}`;
    }
    
    // Update confidence bar
    const confidence = data.confidence || 0;
    confidenceBar.style.width = confidence + '%';
    confidenceBar.textContent = Math.round(confidence) + '%';
    
    const colorClass = getConfidenceColor(confidence);
    confidenceBar.className = `progress-bar bg-${colorClass}`;
    
    // Scroll to results
    resultArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ============================================
// 3. DASHBOARD FUNCTIONS
// ============================================

// Update dashboard stats
async function updateDashboard() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('totalChecks').textContent = data.total;
        document.getElementById('safeChecks').textContent = data.safe;
        document.getElementById('suspiciousChecks').textContent = data.suspicious;
        document.getElementById('scamChecks').textContent = data.scam;
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// ============================================
// 4. SETUP VERIFICATION
// ============================================

function setupVerification() {
    const verifyButton = document.getElementById('verifyButton');
    const verificationInput = document.getElementById('verificationInput');
    
    if (!verifyButton || !verificationInput) return;
    
    async function handleVerification() {
        const content = verificationInput.value.trim();
        const type = document.querySelector('input[name="verification_type"]:checked')?.value || 'url';
        
        if (!validateInput(content, type)) return;
        
        // Show loading state
        verifyButton.disabled = true;
        verifyButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Verifying...';
        
        try {
            const data = await verifyContent(content, type);
            displayResults(data);
        } catch (error) {
            // Error already handled in verifyContent
        } finally {
            verifyButton.disabled = false;
            verifyButton.innerHTML = '<i class="fas fa-search me-2"></i> Verify';
        }
    }
    
    verifyButton.addEventListener('click', handleVerification);
    verificationInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleVerification();
        }
    });
}

// ============================================
// 5. INITIALIZE ON PAGE LOAD
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 TrustLens AI loaded successfully!');
    
    // Setup verification on index page
    setupVerification();
    
    // Setup tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-dismiss alerts
    document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
        setTimeout(function() {
            alert.classList.remove('show');
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Update dashboard stats if on dashboard page
    if (document.getElementById('totalChecks')) {
        updateDashboard();
        // Update every 30 seconds
        setInterval(updateDashboard, 30000);
    }
});

// ============================================
// 6. EXPOSE FUNCTIONS GLOBALLY
// ============================================

window.TrustLensAI = {
    formatDate,
    getConfidenceColor,
    showAlert,
    copyToClipboard,
    validateInput,
    verifyContent,
    displayResults,
    updateDashboard
};

console.log('✅ TrustLens AI utilities loaded');

// ============================================
// 7. ADDITIONAL FEATURES
// ============================================

// Auto-expand textarea if used
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// History page filter
document.addEventListener('DOMContentLoaded', function() {
    const filterInput = document.getElementById('historyFilter');
    if (filterInput) {
        filterInput.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const rows = document.querySelectorAll('#historyTable tbody tr');
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
});

// Chart placeholder for dashboard
document.addEventListener('DOMContentLoaded', function() {
    const chartCanvas = document.getElementById('verificationChart');
    if (chartCanvas) {
        console.log('📊 Chart placeholder ready');
    }
});

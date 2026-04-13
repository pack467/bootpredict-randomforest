/**
 * Prediction Form Module
 * Handles the prediction form on the dashboard page.
 */

/**
 * Handle prediction form submission.
 */
async function handlePredict(event) {
    event.preventDefault();
    
    const peminatan = document.getElementById('peminatan').value;
    const brand = document.getElementById('brand').value;
    const posisi = document.getElementById('posisi').value;
    const submitBtn = document.getElementById('btn-predict');
    
    if (!peminatan || !brand || !posisi) {
        showError('alert-container', 'Semua field harus dipilih');
        return;
    }
    
    submitBtn.disabled = true;
    if (window.AppUtil) AppUtil.showLoading('Menganalisis Permintaan AI...');
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ peminatan, brand, posisi })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Prediksi gagal');
        }
        
        // Store result and redirect
        localStorage.setItem('lastPrediction', JSON.stringify(data));
        window.location.href = '/result.html';
        
    } catch (error) {
        showError('alert-container', error.message);
    } finally {
        if (window.AppUtil) AppUtil.hideLoading();
        submitBtn.disabled = false;
    }
}

/**
 * Load user stats for the dashboard.
 */
async function loadDashboardStats() {
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/history/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            const totalEl = document.getElementById('stat-total');
            if (totalEl) totalEl.textContent = data.total_predictions || 0;
            
            // Show class distribution
            const distEl = document.getElementById('stat-distribution');
            if (distEl && data.class_distribution) {
                const entries = Object.entries(data.class_distribution);
                if (entries.length > 0) {
                    distEl.innerHTML = entries.map(([cls, count]) => {
                        const badgeClass = cls.includes('speed') ? 'badge-speed' : 
                                          cls.includes('control') ? 'badge-control' : 'badge-power';
                        return `<span class="badge ${badgeClass} me-1">${cls}: ${count}</span>`;
                    }).join('');
                } else {
                    distEl.innerHTML = '<span class="text-muted">Belum ada data</span>';
                }
            }
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

/**
 * Initialize dashboard page.
 */
function initDashboard() {
    if (!requireAuth()) return;
    
    const user = getUser();
    const greetingEl = document.getElementById('greeting-name');
    if (greetingEl && user) {
        greetingEl.textContent = user.username;
    }
    
    // Show/hide admin link
    const adminLink = document.getElementById('admin-link');
    if (adminLink && user && user.role === 'admin') {
        adminLink.style.display = 'block';
    }
    
    loadDashboardStats();
}

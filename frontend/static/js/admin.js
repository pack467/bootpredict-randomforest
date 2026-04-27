/**
 * Admin Dashboard Module
 * Handles admin panel functionality: stats, dataset upload, training, user management.
 */

/**
 * Initialize the admin page.
 */
function initAdmin() {
    if (!requireAuth()) return;
    if (!requireAdmin()) return;
    
    loadDashboard();
}

/**
 * Load admin dashboard stats.
 */
async function loadDashboard() {
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/admin/dashboard`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                window.location.href = '/dashboard';
                return;
            }
            throw new Error('Gagal memuat dashboard');
        }
        
        const data = await response.json();
        
        document.getElementById('stat-users').textContent = data.total_users || 0;
        document.getElementById('stat-predictions').textContent = data.total_predictions || 0;
        document.getElementById('stat-dataset').textContent = data.total_dataset_records || 0;
        
        if (data.latest_training) {
            document.getElementById('stat-accuracy').textContent = 
                (data.latest_training.accuracy * 100).toFixed(1) + '%';
            document.getElementById('last-trained').textContent = 
                data.latest_training.trained_at ? 
                new Date(data.latest_training.trained_at).toLocaleString('id-ID') : '-';
        } else {
            document.getElementById('stat-accuracy').textContent = '-';
            document.getElementById('last-trained').textContent = 'Belum pernah';
        }
        
    } catch (error) {
        console.error('Dashboard error:', error);
    }
}

/**
 * Handle CSV file upload.
 */
async function handleUploadDataset(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];
    const statusEl = document.getElementById('upload-status');
    const submitBtn = document.getElementById('btn-upload');
    
    if (!file) {
        statusEl.innerHTML = '<div class="alert alert-custom alert-danger">Pilih file CSV terlebih dahulu</div>';
        return;
    }
    
    if (!file.name.endsWith('.csv')) {
        statusEl.innerHTML = '<div class="alert alert-custom alert-danger">File harus berformat .csv</div>';
        return;
    }
    
    submitBtn.disabled = true;
    if (window.AppUtil) AppUtil.showLoading('Mengunggah Dataset...');
    
    try {
        const token = getToken();
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE}/api/admin/upload-dataset`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Upload gagal');
        }
        
        let msg = `<div class="alert alert-custom alert-success">
            <strong>✅ Berhasil!</strong> ${data.message}
        </div>`;
        
        if (data.errors && data.errors.length > 0) {
            msg += `<div class="alert alert-custom alert-warning mt-2">
                <strong>⚠️ Peringatan:</strong><br>
                ${data.errors.join('<br>')}
            </div>`;
        }
        
        statusEl.innerHTML = msg;
        fileInput.value = '';
        loadDashboard();
        
    } catch (error) {
        if (window.AppUtil) AppUtil.showToast('error', 'Upload Gagal', error.message);
        statusEl.innerHTML = `<div class="alert alert-custom alert-danger">${error.message}</div>`;
    } finally {
        if (window.AppUtil) AppUtil.hideLoading();
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-cloud-upload me-2"></i>Upload Dataset';
    }
}

/**
 * Trigger model training.
 */
async function handleTrain() {
    const btn = document.getElementById('btn-train');
    const statusEl = document.getElementById('training-status');
    
    if (!confirm('Mulai training model? Proses ini mungkin memakan beberapa detik.')) return;
    
    btn.disabled = true;
    if (window.AppUtil) AppUtil.showLoading('Melatih Model Random Forest... (Ini mungkin memakan waktu agak lama)');
    statusEl.innerHTML = '';
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/admin/train`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Training gagal');
        }
        
        const metrics = data.metrics;
        
        // Display training results
        const cvSection = metrics.cv_mean_accuracy ? `
            <div class="glass-card no-hover mt-3 mb-3">
                <div class="section-title"><span class="title-icon">🔄</span> Stratified K-Fold Cross-Validation (5-Fold)</div>
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="glass-card stat-card no-hover">
                            <div class="stat-value">${(metrics.cv_mean_accuracy * 100).toFixed(1)}%</div>
                            <div class="stat-label">CV Mean Accuracy</div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="glass-card stat-card no-hover">
                            <div class="stat-value">± ${(metrics.cv_std_accuracy * 100).toFixed(2)}%</div>
                            <div class="stat-label">CV Std Deviation</div>
                        </div>
                    </div>
                </div>
            </div>
        ` : '';

        statusEl.innerHTML = `
            <div class="alert alert-custom alert-success mb-3">
                <strong>✅ ${data.message}</strong>
            </div>
            <div class="row g-3">
                <div class="col-6 col-md-3">
                    <div class="glass-card stat-card no-hover">
                        <div class="stat-value">${(metrics.accuracy * 100).toFixed(1)}%</div>
                        <div class="stat-label">Accuracy</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="glass-card stat-card no-hover">
                        <div class="stat-value">${(metrics.precision * 100).toFixed(1)}%</div>
                        <div class="stat-label">Precision</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="glass-card stat-card no-hover">
                        <div class="stat-value">${(metrics.recall * 100).toFixed(1)}%</div>
                        <div class="stat-label">Recall</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="glass-card stat-card no-hover">
                        <div class="stat-value">${(metrics.f1_score * 100).toFixed(1)}%</div>
                        <div class="stat-label">F1-Score</div>
                    </div>
                </div>
            </div>
            ${cvSection}
            ${renderFeatureImportanceAdmin(metrics.feature_importance)}
            ${renderConfusionMatrix(metrics.confusion_matrix, metrics.class_names)}
        `;
        
        loadDashboard();
        loadTrainingLogs();
        
    } catch (error) {
        if (window.AppUtil) AppUtil.showToast('error', 'Training Gagal', error.message);
        statusEl.innerHTML = `<div class="alert alert-custom alert-danger">${error.message}</div>`;
    } finally {
        if (window.AppUtil) AppUtil.hideLoading();
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-lightning me-2"></i>Latih Model';
    }
}

/**
 * Render feature importance for admin training results.
 */
function renderFeatureImportanceAdmin(importance) {
    if (!importance) return '';
    
    const featureLabels = {
        'peminatan': 'Gaya Bermain',
        'brand': 'Merek',
        'posisi': 'Posisi'
    };
    
    const sorted = Object.entries(importance).sort((a, b) => b[1] - a[1]);
    const maxVal = Math.max(...sorted.map(([, v]) => v));
    
    let html = `
        <div class="glass-card no-hover mt-3">
            <div class="section-title"><span class="title-icon">📊</span> Feature Importance</div>
    `;
    
    const cssClasses = ['feat-peminatan', 'feat-brand', 'feat-posisi'];
    
    sorted.forEach(([feature, value], index) => {
        const label = featureLabels[feature] || feature;
        const pct = (value / maxVal) * 100;
        const displayPct = (value * 100).toFixed(1);
        
        html += `
            <div class="bar-container">
                <div class="bar-label">
                    <span>${label} (${feature})</span>
                    <span class="bar-value">${displayPct}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill fill-primary" 
                         style="width: ${pct}%"></div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

/**
 * Render confusion matrix.
 */
function renderConfusionMatrix(matrix, classNames) {
    if (!matrix || !classNames) return '';
    
    const n = classNames.length;
    const shortNames = classNames.map(n => n.replace('_boot', ''));
    
    let html = `
        <div class="glass-card no-hover mt-3">
            <div class="section-title"><span class="title-icon">🔢</span> Confusion Matrix</div>
            <div class="confusion-matrix" style="grid-template-columns: auto repeat(${n}, 1fr);">
                <div class="cm-cell cm-header">Actual↓ / Pred→</div>
    `;
    
    // Header row
    shortNames.forEach(name => {
        html += `<div class="cm-cell cm-header">${name}</div>`;
    });
    
    // Data rows
    matrix.forEach((row, i) => {
        html += `<div class="cm-cell cm-header">${shortNames[i]}</div>`;
        row.forEach((val, j) => {
            const isDiag = i === j;
            html += `<div class="cm-cell ${isDiag ? 'cm-diagonal' : ''}">${val}</div>`;
        });
    });
    
    html += '</div></div>';
    return html;
}

/**
 * Load training logs.
 */
async function loadTrainingLogs() {
    const container = document.getElementById('training-logs');
    if (!container) return;
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/admin/training-logs`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) return;
        
        const logs = await response.json();
        
        if (logs.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon">📝</div><h5>Belum ada log training</h5></div>';
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-custom">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Accuracy</th>
                            <th>Precision</th>
                            <th>Recall</th>
                            <th>F1-Score</th>
                            <th>Dataset</th>
                            <th>Tanggal</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        logs.forEach((log, index) => {
            const date = log.trained_at ? new Date(log.trained_at).toLocaleString('id-ID') : '-';
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${(log.accuracy * 100).toFixed(1)}%</strong></td>
                    <td>${(log.precision_score * 100).toFixed(1)}%</td>
                    <td>${(log.recall * 100).toFixed(1)}%</td>
                    <td>${(log.f1_score * 100).toFixed(1)}%</td>
                    <td>${log.dataset_size || '-'} data</td>
                    <td><small>${date}</small></td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Load training logs error:', error);
    }
}

/**
 * Load users list.
 */
async function loadUsers() {
    const container = document.getElementById('users-container');
    if (!container) return;
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/admin/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) return;
        
        const users = await response.json();
        
        let html = `
            <div class="table-responsive">
                <table class="table table-custom">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Terdaftar</th>
                            <th>Aksi</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        users.forEach(user => {
            const date = user.created_at ? new Date(user.created_at).toLocaleString('id-ID') : '-';
            const badgeClass = user.role === 'admin' ? 'badge-admin' : 'badge-user';
            
            html += `
                <tr>
                    <td>${user.id}</td>
                    <td><strong>${user.username}</strong></td>
                    <td><span class="badge ${badgeClass}">${user.role}</span></td>
                    <td><small>${date}</small></td>
                    <td>
                        ${user.role !== 'admin' ? 
                            `<button class="btn btn-sm btn-danger-custom" onclick="deleteUser(${user.id})">
                                <i class="bi bi-trash"></i> Hapus
                            </button>` : 
                            '<span class="text-muted">-</span>'
                        }
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Load users error:', error);
    }
}

/**
 * Delete a user.
 */
async function deleteUser(userId) {
    if (!confirm('Yakin ingin menghapus user ini? Semua riwayat prediksi user akan ikut terhapus.')) return;
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Gagal menghapus user');
        }
        
        loadUsers();
        loadDashboard();
        
    } catch (error) {
        if (window.AppUtil) AppUtil.showToast('error', 'Gagal', error.message);
        else alert('Error: ' + error.message);
    }
}

/**
 * Handle tab switching.
 */
function handleTabSwitch(tabName) {
    switch (tabName) {
        case 'training':
            loadTrainingLogs();
            break;
        case 'users':
            loadUsers();
            break;
        case 'dataset':
            loadDatasetRecords();
            break;
    }
}

/**
 * Load dataset records.
 */
async function loadDatasetRecords() {
    const container = document.getElementById('dataset-container');
    if (!container) return;
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/admin/dataset`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) return;
        
        const records = await response.json();
        
        if (records.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon">📊</div><h5>Dataset kosong</h5><p>Upload file CSV untuk menambahkan data.</p></div>';
            return;
        }
        
        let html = `
            <p class="text-secondary mb-3">Menampilkan ${records.length} data terbaru</p>
            <div class="table-responsive">
                <table class="table table-custom">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Peminatan</th>
                            <th>Brand</th>
                            <th>Posisi</th>
                            <th>Label</th>
                            <th>Sumber</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        records.forEach(record => {
            const badgeClass = record.label_sepatu.includes('speed') ? 'badge-speed' : 
                              record.label_sepatu.includes('control') ? 'badge-control' : 'badge-power';
            
            html += `
                <tr>
                    <td>${record.id}</td>
                    <td class="text-capitalize">${record.peminatan}</td>
                    <td class="text-capitalize">${record.brand}</td>
                    <td class="text-capitalize">${record.posisi}</td>
                    <td><span class="badge ${badgeClass}">${record.label_sepatu}</span></td>
                    <td><small>${record.source}</small></td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Load dataset error:', error);
    }
}

/**
 * Clear all dataset records.
 */
async function handleClearDataset() {
    if (!confirm('⚠️ PERINGATAN: Semua data latih akan dihapus permanen!\n\nAnda perlu mengupload CSV baru setelah reset.\n\nLanjutkan?')) return;
    if (!confirm('Konfirmasi sekali lagi: Hapus SEMUA dataset?')) return;
    
    const btn = document.getElementById('btn-clear-dataset');
    btn.disabled = true;
    if (window.AppUtil) AppUtil.showLoading('Menghapus dataset...');
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/admin/dataset`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Gagal menghapus dataset');
        }
        
        if (window.AppUtil) AppUtil.showToast('success', 'Berhasil', data.message);
        loadDashboard();
        loadDatasetRecords();
        
    } catch (error) {
        if (window.AppUtil) AppUtil.showToast('error', 'Gagal', error.message);
        else alert('Error: ' + error.message);
    } finally {
        if (window.AppUtil) AppUtil.hideLoading();
        btn.disabled = false;
    }
}

/**
 * Delete trained model and training logs.
 */
async function handleDeleteModel() {
    if (!confirm('⚠️ PERINGATAN: Model AI dan semua log training akan dihapus!\n\nPrediksi tidak akan berfungsi sampai model dilatih ulang.\n\nLanjutkan?')) return;
    if (!confirm('Konfirmasi sekali lagi: Hapus model dan log training?')) return;
    
    const btn = document.getElementById('btn-delete-model');
    btn.disabled = true;
    if (window.AppUtil) AppUtil.showLoading('Menghapus model...');
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/admin/model`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Gagal menghapus model');
        }
        
        if (window.AppUtil) AppUtil.showToast('success', 'Berhasil', data.message);
        loadDashboard();
        loadTrainingLogs();
        
    } catch (error) {
        if (window.AppUtil) AppUtil.showToast('error', 'Gagal', error.message);
        else alert('Error: ' + error.message);
    } finally {
        if (window.AppUtil) AppUtil.hideLoading();
        btn.disabled = false;
    }
}

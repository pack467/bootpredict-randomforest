/**
 * History Page Module
 * Displays and manages user prediction history.
 * Delete button now removes rows immediately with animation (no page refresh needed).
 */

/**
 * Initialize the history page.
 */
function initHistory() {
    if (!requireAuth()) return;
    loadHistory();
}

/**
 * Load prediction history from the API.
 */
async function loadHistory() {
    const container = document.getElementById('history-container');
    
    container.innerHTML = `
        <div class="spinner-container">
            <div class="spinner-border" role="status"></div>
            <div class="spinner-text">Memuat riwayat...</div>
        </div>
    `;
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE}/api/history`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                logout();
                return;
            }
            throw new Error('Gagal memuat riwayat');
        }
        
        const history = await response.json();
        renderHistory(history);
        
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-custom alert-danger">
                <strong>Error:</strong> ${error.message}
            </div>
        `;
    }
}

/**
 * Render the history table.
 */
function renderHistory(history) {
    const container = document.getElementById('history-container');
    
    if (!history || history.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <h5>Belum ada riwayat prediksi</h5>
                <p>Mulai dengan membuat prediksi pertama Anda.</p>
                <a href="/dashboard" class="btn btn-primary-custom mt-3">
                    <i class="bi bi-plus-lg me-2"></i>Buat Prediksi
                </a>
            </div>
        `;
        return;
    }
    
    const badgeMap = {
        'speed_boot': '<span class="badge badge-speed">⚡ Speed Boot</span>',
        'control_boot': '<span class="badge badge-control">🎯 Control Boot</span>',
        'power_boot': '<span class="badge badge-power">💪 Power Boot</span>'
    };
    
    let tableHTML = `
        <div class="table-responsive">
            <table class="table table-custom" id="history-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Peminatan</th>
                        <th>Brand</th>
                        <th>Posisi</th>
                        <th>Hasil Klasifikasi</th>
                        <th>Tanggal</th>
                        <th>Aksi</th>
                    </tr>
                </thead>
                <tbody id="history-tbody">
    `;
    
    history.forEach((item, index) => {
        const date = item.created_at ? new Date(item.created_at).toLocaleString('id-ID') : '-';
        const itemId = item.id;
        
        tableHTML += `
            <tr class="fade-slide-up" style="animation-delay: ${index * 0.05}s" id="history-row-${itemId}" data-history-id="${itemId}">
                <td class="row-number">${index + 1}</td>
                <td><span class="text-capitalize">${item.peminatan}</span></td>
                <td><span class="text-capitalize">${item.brand}</span></td>
                <td><span class="text-capitalize">${item.posisi}</span></td>
                <td>${badgeMap[item.predicted_class] || item.predicted_class}</td>
                <td><small>${date}</small></td>
                <td>
                    <button class="btn btn-sm btn-secondary-custom me-1" 
                            onclick="viewDetail(${index})" title="Detail" type="button">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-danger-custom" 
                            onclick="deleteHistory(${itemId}, this)" title="Hapus" type="button"
                            id="delete-btn-${itemId}">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
            <tr id="detail-row-${index}" class="detail-expansion-row" style="display:none;">
                <td colspan="7">
                    <div class="explanation-box">
                        <div class="explanation-title">🧠 Penjelasan AI</div>
                        <div class="explanation-text">${item.explanation || 'Tidak ada penjelasan'}</div>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tableHTML += '</tbody></table></div>';
    
    // Store history for detail view
    window._historyData = history;
    
    container.innerHTML = tableHTML;
}

/**
 * Toggle detail view for a history item.
 */
function viewDetail(index) {
    const row = document.getElementById(`detail-row-${index}`);
    if (row) {
        row.style.display = row.style.display === 'none' ? '' : 'none';
    }
}

/**
 * Delete a history entry.
 * Immediately removes the row from the DOM with animation — no page refresh needed.
 */
async function deleteHistory(predictionId, buttonElement) {
    if (!confirm('Yakin ingin menghapus riwayat ini?')) return;
    
    // Get references to the row elements
    const dataRow = document.getElementById(`history-row-${predictionId}`);
    const deleteBtn = buttonElement || document.getElementById(`delete-btn-${predictionId}`);
    
    // Immediately show loading state on button
    if (deleteBtn) {
        deleteBtn.disabled = true;
        deleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
    }
    
    try {
        const token = getToken();
        
        if (!token) {
            logout();
            return;
        }
        
        const response = await fetch(`${API_BASE}/api/history/${predictionId}`, {
            method: 'DELETE',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (!response.ok) {
            let errorMsg = 'Gagal menghapus riwayat';
            try {
                const data = await response.json();
                errorMsg = data.detail || data.message || errorMsg;
            } catch (e) {
                // Response may not be JSON
            }
            throw new Error(errorMsg);
        }
        
        // === SUCCESS: Immediately remove row from DOM with smooth animation ===
        
        // Find the corresponding detail row (it's the next sibling)
        let detailRow = null;
        if (dataRow && dataRow.nextElementSibling && dataRow.nextElementSibling.classList.contains('detail-expansion-row')) {
            detailRow = dataRow.nextElementSibling;
        }
        
        // Animate the row out
        if (dataRow) {
            dataRow.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            dataRow.style.opacity = '0';
            dataRow.style.transform = 'translateX(-30px)';
            dataRow.style.maxHeight = dataRow.offsetHeight + 'px';
            
            // After a brief delay, collapse the height
            setTimeout(() => {
                dataRow.style.maxHeight = '0';
                dataRow.style.padding = '0';
                dataRow.style.margin = '0';
                dataRow.style.borderColor = 'transparent';
                dataRow.style.overflow = 'hidden';
            }, 200);
        }
        
        // Also hide the detail row if visible
        if (detailRow) {
            detailRow.style.transition = 'all 0.3s ease';
            detailRow.style.opacity = '0';
            detailRow.style.maxHeight = '0';
            detailRow.style.overflow = 'hidden';
        }
        
        // Remove from DOM after animation completes and renumber remaining rows
        setTimeout(() => {
            if (dataRow) dataRow.remove();
            if (detailRow) detailRow.remove();
            
            // Also remove from local data cache
            if (window._historyData) {
                window._historyData = window._historyData.filter(item => item.id !== predictionId);
            }
            
            // Renumber the remaining rows
            renumberHistoryRows();
            
            // If no rows left, show empty state
            const tbody = document.getElementById('history-tbody');
            if (tbody && tbody.children.length === 0) {
                const container = document.getElementById('history-container');
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">📋</div>
                        <h5>Belum ada riwayat prediksi</h5>
                        <p>Mulai dengan membuat prediksi pertama Anda.</p>
                        <a href="/dashboard" class="btn btn-primary-custom mt-3">
                            <i class="bi bi-plus-lg me-2"></i>Buat Prediksi
                        </a>
                    </div>
                `;
            }
        }, 500);
        
        // Show success toast
        if (window.AppUtil) {
            AppUtil.showToast('success', 'Berhasil', 'Riwayat prediksi berhasil dihapus');
        }
        
    } catch (error) {
        console.error('Delete error:', error);
        if (window.AppUtil) {
            AppUtil.showToast('error', 'Gagal', error.message);
        } else {
            alert('Error: ' + error.message);
        }
        
        // Re-enable the button on error
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
        }
    }
}

/**
 * Re-number the remaining history rows after a deletion.
 * This updates the # column so numbers stay sequential.
 */
function renumberHistoryRows() {
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;
    
    // Get all data rows (exclude detail expansion rows)
    const dataRows = tbody.querySelectorAll('tr[data-history-id]');
    dataRows.forEach((row, index) => {
        const numberCell = row.querySelector('.row-number');
        if (numberCell) {
            numberCell.textContent = index + 1;
        }
    });
}

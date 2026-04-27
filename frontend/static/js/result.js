/**
 * Result Display Module
 * Renders prediction results with charts, boot images, stat bars,
 * and specific product recommendations with brand-specific imagery.
 * Products are sorted by match score (most suitable first).
 */

/**
 * Boot image mapping for each classification type (generic fallback).
 */
const BOOT_IMAGES = {
    'speed_boot': {
        image: '/static/images/boot_speed.png',
        label: 'Speed Boot',
        alt: 'Lightweight Speed Football Boot'
    },
    'control_boot': {
        image: '/static/images/boot_control.png',
        label: 'Control Boot',
        alt: 'Textured Control Football Boot'
    },
    'power_boot': {
        image: '/static/images/boot_power.png',
        label: 'Power Boot',
        alt: 'Strong Power Football Boot'
    }
};

/**
 * Brand color mapping for badges.
 */
const BRAND_COLORS = {
    'adidas': { bg: 'rgba(0,0,0,0.08)', text: '#000000', border: '#333333', icon: '▲' },
    'nike': { bg: 'rgba(245,130,32,0.08)', text: '#F58220', border: '#F58220', icon: '✓' },
    'puma': { bg: 'rgba(0,150,64,0.08)', text: '#009640', border: '#009640', icon: '◆' },
    'umbro': { bg: 'rgba(75,0,130,0.08)', text: '#4B0082', border: '#4B0082', icon: '◇' },
    'mizuno': { bg: 'rgba(0,70,140,0.08)', text: '#00468C', border: '#00468C', icon: '★' }
};

/**
 * Stat label mapping with icons.
 */
const STAT_LABELS = {
    speed: { label: 'Speed', icon: '⚡', color: '#f59e0b' },
    control: { label: 'Control', icon: '🎯', color: '#3b82f6' },
    power: { label: 'Power', icon: '💪', color: '#ef4444' },
    touch: { label: 'Touch', icon: '🤚', color: '#8b5cf6' },
    weight: { label: 'Weight', icon: '🪶', color: '#10b981' },
    durability: { label: 'Durability', icon: '🛡️', color: '#6366f1' }
};

/**
 * Initialize the result page.
 */
function initResult() {
    if (!requireAuth()) return;
    
    const data = localStorage.getItem('lastPrediction');
    if (!data) {
        window.location.href = '/dashboard';
        return;
    }
    
    const prediction = JSON.parse(data);
    renderResult(prediction);
}

/**
 * Render the full prediction result.
 */
function renderResult(data) {
    // Result Header
    const iconMap = {
        'speed_boot': '⚡',
        'control_boot': '🎯',
        'power_boot': '💪'
    };
    
    const nameMap = {
        'speed_boot': 'Speed Boot',
        'control_boot': 'Control Boot',
        'power_boot': 'Power Boot'
    };
    
    document.getElementById('result-icon').textContent = iconMap[data.predicted_class] || '👟';
    document.getElementById('result-class').textContent = nameMap[data.predicted_class] || data.predicted_class;
    document.getElementById('result-description').textContent = data.predicted_label;
    
    // Update boot image based on classification
    updateBootImage(data.predicted_class);
    
    // Input summary
    document.getElementById('input-peminatan').textContent = data.input.peminatan;
    document.getElementById('input-brand').textContent = data.input.brand;
    document.getElementById('input-posisi').textContent = data.input.posisi;
    
    // Probability bars
    renderProbabilityBars(data.probabilities);
    
    // Feature importance bars
    renderFeatureImportance(data.feature_importance);
    
    // AI Explanation
    document.getElementById('explanation-text').textContent = data.explanation;
    
    // Product recommendations with stats
    renderProducts(data.recommended_products || [], data.predicted_class, data.input.brand);
}

/**
 * Update the boot image display based on predicted class.
 */
function updateBootImage(predictedClass) {
    const bootData = BOOT_IMAGES[predictedClass];
    const imgEl = document.getElementById('result-boot-image');
    const labelEl = document.getElementById('result-boot-label');
    
    if (bootData && imgEl) {
        imgEl.src = bootData.image;
        imgEl.alt = bootData.alt;
    }
    
    if (bootData && labelEl) {
        labelEl.textContent = bootData.label;
    }
}

/**
 * Render probability bar charts.
 */
function renderProbabilityBars(probabilities) {
    const container = document.getElementById('probability-bars');
    container.innerHTML = '';
    
    const classStyles = {
        'speed_boot': { label: 'Speed Boot ⚡', cssClass: 'fill-primary' },
        'control_boot': { label: 'Control Boot 🎯', cssClass: 'fill-blue' },
        'power_boot': { label: 'Power Boot 💪', cssClass: 'fill-red' }
    };
    
    // Sort by probability (highest first)
    const sorted = Object.entries(probabilities).sort((a, b) => b[1] - a[1]);
    
    sorted.forEach(([cls, prob], index) => {
        const style = classStyles[cls] || { label: cls, cssClass: 'fill-primary' };
        
        const barHTML = `
            <div class="bar-container fade-slide-up stagger-${index + 1}">
                <div class="bar-label">
                    <span>${style.label}</span>
                    <span class="bar-value">${prob.toFixed(1)}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill ${style.cssClass}" id="prob-bar-${index}"></div>
                </div>
            </div>
        `;
        container.innerHTML += barHTML;
    });
    
    // Animate bars after render
    requestAnimationFrame(() => {
        setTimeout(() => {
            sorted.forEach(([cls, prob], index) => {
                const bar = document.getElementById(`prob-bar-${index}`);
                if (bar) bar.style.width = `${prob}%`;
            });
        }, 200);
    });
}

/**
 * Render feature importance bar charts.
 */
function renderFeatureImportance(importance) {
    const container = document.getElementById('feature-bars');
    container.innerHTML = '';
    
    const featureStyles = {
        'peminatan': { label: 'Gaya Bermain (Peminatan)', cssClass: 'fill-primary' },
        'brand': { label: 'Merek Sepatu (Brand)', cssClass: 'fill-blue' },
        'posisi': { label: 'Posisi Pemain (Posisi)', cssClass: 'fill-primary' }
    };
    
    // Sort by importance (highest first)
    const sorted = Object.entries(importance).sort((a, b) => b[1] - a[1]);
    const maxVal = Math.max(...sorted.map(([, v]) => v));
    
    sorted.forEach(([feature, value], index) => {
        const style = featureStyles[feature] || { label: feature, cssClass: 'fill-primary' };
        const percentage = (value / maxVal) * 100;
        const pctDisplay = (value * 100).toFixed(1);
        
        const barHTML = `
            <div class="bar-container fade-slide-up stagger-${index + 1}">
                <div class="bar-label">
                    <span>${style.label}</span>
                    <span class="bar-value">${pctDisplay}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill ${style.cssClass}" id="feat-bar-${index}"></div>
                </div>
            </div>
        `;
        container.innerHTML += barHTML;
    });
    
    // Animate
    requestAnimationFrame(() => {
        setTimeout(() => {
            sorted.forEach(([feature, value], index) => {
                const bar = document.getElementById(`feat-bar-${index}`);
                const percentage = (value / maxVal) * 100;
                if (bar) bar.style.width = `${percentage}%`;
            });
        }, 400);
    });
}

/**
 * Generate stat bars HTML for a product.
 */
function renderStatBars(stats, productIndex) {
    if (!stats) return '';
    
    const statEntries = Object.entries(STAT_LABELS);
    
    return `
        <div class="product-stats">
            <div class="product-stats-title">📊 Statistik Sepatu</div>
            ${statEntries.map(([key, meta]) => {
                const value = stats[key] || 0;
                return `
                    <div class="stat-row">
                        <div class="stat-label-mini">
                            <span class="stat-icon-mini">${meta.icon}</span>
                            <span>${meta.label}</span>
                        </div>
                        <div class="stat-bar-wrapper">
                            <div class="stat-bar-track">
                                <div class="stat-bar-fill" 
                                     data-stat-value="${value}" 
                                     data-stat-color="${meta.color}"
                                     style="width: 0%; background: linear-gradient(90deg, ${meta.color}88, ${meta.color});"></div>
                            </div>
                            <span class="stat-value-mini">${value}</span>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

/**
 * Generate brand badge HTML.
 */
function renderBrandBadge(brandName) {
    const brandKey = brandName.toLowerCase();
    const brandStyle = BRAND_COLORS[brandKey] || { bg: 'rgba(100,100,100,0.08)', text: '#666', border: '#999', icon: '●' };
    
    return `
        <div class="brand-badge" style="
            background: ${brandStyle.bg}; 
            color: ${brandStyle.text}; 
            border: 1px solid ${brandStyle.border}22;
        ">
            <span class="brand-badge-icon">${brandStyle.icon}</span>
            ${brandName}
        </div>
    `;
}

/**
 * Generate match score badge HTML.
 * Shows how well the shoe matches user criteria.
 */
function renderMatchScoreBadge(matchScore, rank) {
    if (!matchScore && matchScore !== 0) return '';
    
    let colorClass, label, icon;
    
    if (matchScore >= 85) {
        colorClass = 'match-excellent';
        label = 'Sangat Cocok';
        icon = '🏆';
    } else if (matchScore >= 75) {
        colorClass = 'match-great';
        label = 'Cocok';
        icon = '⭐';
    } else if (matchScore >= 65) {
        colorClass = 'match-good';
        label = 'Cukup Cocok';
        icon = '👍';
    } else {
        colorClass = 'match-fair';
        label = 'Alternatif';
        icon = '🔄';
    }
    
    return `
        <div class="match-score-badge ${colorClass}">
            <span class="match-score-icon">${icon}</span>
            <span class="match-score-label">${label}</span>
            <span class="match-score-value">${matchScore.toFixed(1)}%</span>
        </div>
    `;
}

/**
 * Generate rank badge HTML.
 */
function renderRankBadge(rank, isPrimary) {
    if (!rank) return '';
    
    const medals = ['🥇', '🥈', '🥉'];
    const medal = rank <= 3 ? medals[rank - 1] : `#${rank}`;
    
    return `
        <div class="rank-badge ${isPrimary ? 'rank-primary' : 'rank-secondary'}">
            <span class="rank-medal">${medal}</span>
        </div>
    `;
}

/**
 * Handle image load errors with fallback.
 */
function handleImageError(imgEl, predictedClass) {
    const fallback = BOOT_IMAGES[predictedClass] || BOOT_IMAGES['speed_boot'];
    imgEl.src = fallback.image;
    imgEl.onerror = null; // Prevent infinite loop
}

/**
 * Render product recommendation cards with unique images, brand badges, 
 * match scores, rank badges, and stat bars.
 * Products are pre-sorted by match score from the backend.
 */
function renderProducts(products, predictedClass, userBrand) {
    const container = document.getElementById('products-grid');
    
    if (!products || products.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="empty-state">
                    <div class="empty-icon">📦</div>
                    <h5>Tidak ada produk terkait</h5>
                    <p>Produk rekomendasi tidak tersedia saat ini.</p>
                </div>
            </div>
        `;
        return;
    }

    // Separate primary (user's brand) and secondary (other brands) recommendations
    const primaryProducts = products.filter(p => p.is_primary);
    const secondaryProducts = products.filter(p => !p.is_primary);

    let html = '';

    // Primary recommendations header
    if (primaryProducts.length > 0) {
        html += `
            <div class="col-12 mb-2">
                <div class="recommendation-section-header">
                    <span class="rec-section-icon">⭐</span>
                    <span>Rekomendasi Utama — <strong class="text-capitalize">${userBrand || 'Brand Pilihan'}</strong></span>
                    <span class="rec-section-count">${primaryProducts.length} sepatu ditemukan</span>
                </div>
                <div class="rec-section-subtitle">Diurutkan berdasarkan kesesuaian dengan kriteria Anda</div>
            </div>
        `;
        
        primaryProducts.forEach((product, index) => {
            html += renderProductCard(product, index, predictedClass, true);
        });
    }

    // Secondary recommendations header
    if (secondaryProducts.length > 0) {
        html += `
            <div class="col-12 mt-4 mb-2">
                <div class="recommendation-section-header secondary">
                    <span class="rec-section-icon">🔄</span>
                    <span>Alternatif dari Brand Lain</span>
                    <span class="rec-section-count">${secondaryProducts.length} alternatif</span>
                </div>
                <div class="rec-section-subtitle">Rekomendasi terbaik dari merek lain yang sesuai kriteria</div>
            </div>
        `;
        
        secondaryProducts.forEach((product, index) => {
            html += renderProductCard(product, index + primaryProducts.length, predictedClass, false);
        });
    }
    
    container.innerHTML = html;

    // Animate stat bars after DOM render
    requestAnimationFrame(() => {
        setTimeout(() => {
            document.querySelectorAll('.stat-bar-fill').forEach(bar => {
                const value = bar.getAttribute('data-stat-value');
                bar.style.width = `${value}%`;
            });
        }, 300);
    });
}

/**
 * Render a single product card with match score and rank.
 */
function renderProductCard(product, index, predictedClass, isPrimary) {
    const imageUrl = product.image || (BOOT_IMAGES[predictedClass] || BOOT_IMAGES['speed_boot']).image;
    const brandBadge = renderBrandBadge(product.brand || 'Unknown');
    const statBars = renderStatBars(product.stats, index);
    const matchBadge = renderMatchScoreBadge(product.match_score, product.rank);
    const rankBadge = renderRankBadge(product.rank, isPrimary);
    
    const primaryClass = isPrimary ? 'product-card-primary' : '';
    const topPickBadge = isPrimary && product.rank === 1 
        ? '<span class="primary-pick-badge">👑 Best Match</span>' 
        : '';
    
    return `
        <div class="col-md-6 col-lg-4 fade-slide-up stagger-${(index % 4) + 1}">
            <div class="product-card ${primaryClass}">
                ${topPickBadge}
                ${rankBadge}
                <div class="product-image-wrapper">
                    <img src="${imageUrl}" alt="${product.name}" 
                         onerror="handleImageError(this, '${predictedClass}')">
                </div>
                <div class="product-body">
                    <div class="product-header-row">
                        ${brandBadge}
                    </div>
                    <div class="product-name">${product.name}</div>
                    <div class="product-price">${product.price}</div>
                    ${matchBadge}
                    <div class="product-desc">${product.description}</div>
                    ${product.features ? `
                        <div class="product-features">
                            ${product.features.map(f => `<span class="badge-feature">${f}</span>`).join('')}
                        </div>
                    ` : ''}
                    ${statBars}
                </div>
            </div>
        </div>
    `;
}

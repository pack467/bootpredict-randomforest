/**
 * Catalog UI Scripts
 * Adds interactive and dynamic elements to the catalog and detail pages.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Staggered fade-up animation for product cards
    const cards = document.querySelectorAll('.product-card');
    if (cards.length > 0) {
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s cubic-bezier(0.165, 0.84, 0.44, 1)';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 + (index * 75)); // Stagger by 75ms
        });
    }

    // 2. Enhance filter selects (Auto-submit with loading state)
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', () => {
            const btn = filterForm.querySelector('button[type="submit"]');
            if (btn) {
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Memuat...';
                btn.disabled = true;
            }
        });
    }

    // 3. Search Bar Interactivity
    const searchInput = document.getElementById('catalog-search-input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.closest('.input-group').style.transform = 'scale(1.01)';
            this.closest('.input-group').style.transition = 'all 0.3s ease';
        });
        
        searchInput.addEventListener('blur', function() {
            this.closest('.input-group').style.transform = 'scale(1)';
        });

        // Keyboard shortcut: press / to focus search
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        });
    }

    // 4. Mobile sort dropdown
    const mobileSort = document.getElementById('quick-sort-mobile');
    if (mobileSort) {
        mobileSort.addEventListener('change', function() {
            const url = new URL(window.location.href);
            if (this.value) {
                url.searchParams.set('sort', this.value);
            } else {
                url.searchParams.delete('sort');
            }
            url.searchParams.delete('page'); // Reset to page 1 on sort change
            window.location.href = url.toString();
        });
    }

    // 5. Detail Page specific animations
    const detailImg = document.querySelector('.object-fit-contain.drop-shadow-lg');
    if (detailImg) {
        // Subtle floating animation for the main shoe image
        let start = Date.now();
        setInterval(() => {
            let timePassed = Date.now() - start;
            detailImg.style.transform = `translateY(${Math.sin(timePassed / 1000) * 8}px) scale(1.02)`;
        }, 20);
    }

    // 6. Animate count numbers
    const totalCount = document.querySelector('.text-primary-custom strong, strong.text-primary-custom');
    if (totalCount) {
        const target = parseInt(totalCount.textContent) || 0;
        if (target > 0) {
            let current = 0;
            const increment = Math.ceil(target / 30);
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                totalCount.textContent = current;
            }, 30);
        }
    }

    // 7. Brand pills hover ripple effect
    document.querySelectorAll('.brand-pill').forEach(pill => {
        pill.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1)';
        });
    });

    // 8. Category filter items interaction
    document.querySelectorAll('.category-filter-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.paddingLeft = '1rem';
            }
        });
        item.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.paddingLeft = '';
            }
        });
    });
});

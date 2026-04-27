/**
 * Admin Shoes Management Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initial render for sizes if the container exists
    if (document.getElementById('sizes-container')) {
        renderSizes();
        
        // Allow enter key in size input
        const newSizeInput = document.getElementById('new-size-input');
        if (newSizeInput) {
            newSizeInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    addSize();
                }
            });
        }
    }
});

// Image Preview Function
function previewImage(input) {
    const preview = document.getElementById('image-preview');
    const placeholder = document.getElementById('image-placeholder');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
            placeholder.classList.add('d-none');
            
            // Add subtle animation
            preview.style.opacity = 0;
            setTimeout(() => {
                preview.style.transition = 'opacity 0.5s ease';
                preview.style.opacity = 1;
            }, 50);
        }
        reader.readAsDataURL(input.files[0]);
    } else {
        // Reset if no file selected
        preview.src = '';
        preview.classList.add('d-none');
        placeholder.classList.remove('d-none');
    }
}

// Sizes Array Management
let sizes = [];
try {
    const sizesInput = document.getElementById('sizes_available');
    if (sizesInput && sizesInput.value) {
        sizes = JSON.parse(sizesInput.value);
    }
} catch (e) {
    console.error("Error parsing sizes:", e);
    sizes = [];
}

function renderSizes() {
    const container = document.getElementById('sizes-container');
    const hiddenInput = document.getElementById('sizes_available');
    
    if (!container || !hiddenInput) return;
    
    hiddenInput.value = JSON.stringify(sizes);
    
    if (sizes.length === 0) {
        container.innerHTML = '<span class="text-muted small w-100 d-block p-2 bg-light rounded text-center" style="border: 1px dashed var(--border-color);">Belum ada ukuran ditambahkan.</span>';
        return;
    }
    
    // Sort sizes numerically
    sizes.sort((a, b) => Number(a) - Number(b));
    
    container.innerHTML = sizes.map(size => `
        <span class="badge bg-white text-secondary border shadow-sm d-flex align-items-center gap-2 px-3 py-2" style="font-size: 0.85rem; border-radius: 8px;">
            <i class="bi bi-rulers text-primary-custom" style="opacity: 0.7;"></i> EU ${size}
            <button type="button" class="btn-close btn-close-sm ms-1" aria-label="Close" onclick="removeSize('${size}')" style="font-size: 0.5rem;"></button>
        </span>
    `).join('');
}

function addSize() {
    const input = document.getElementById('new-size-input');
    if (!input) return;
    
    const val = input.value.trim();
    
    if (val && !sizes.includes(val)) {
        sizes.push(val);
        renderSizes();
        input.value = '';
        input.focus();
        
        // Visual feedback
        const container = document.getElementById('sizes-container');
        const lastBadge = container.lastElementChild;
        if (lastBadge) {
            lastBadge.style.transform = 'scale(0.8)';
            lastBadge.style.transition = 'transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            setTimeout(() => {
                lastBadge.style.transform = 'scale(1)';
            }, 50);
        }
    } else if (sizes.includes(val)) {
        // Blink existing badge if already exists
        const badges = document.querySelectorAll('#sizes-container .badge');
        badges.forEach(b => {
            if (b.innerText.includes(`EU ${val}`)) {
                b.classList.add('bg-warning', 'text-white');
                setTimeout(() => b.classList.remove('bg-warning', 'text-white'), 500);
            }
        });
    }
}

function removeSize(sizeToRemove) {
    sizes = sizes.filter(s => s !== sizeToRemove);
    renderSizes();
}

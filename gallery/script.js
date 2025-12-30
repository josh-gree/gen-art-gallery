async function loadGallery() {
    const container = document.getElementById('gallery-container');

    try {
        const response = await fetch('gallery.json');
        const gallery = await response.json();

        if (gallery.length === 0) {
            container.innerHTML = '<div class="loading">No art generated yet. Add scripts to the scripts/ directory and push to main.</div>';
            return;
        }

        container.innerHTML = '';

        gallery.forEach(scriptData => {
            const section = document.createElement('div');
            section.className = 'script-section';

            const title = document.createElement('h2');
            title.textContent = scriptData.script.replace(/_/g, ' ');
            section.appendChild(title);

            const grid = document.createElement('div');
            grid.className = 'image-grid';

            scriptData.images.forEach(image => {
                const item = document.createElement('div');
                item.className = 'image-item';

                const img = document.createElement('img');
                img.src = image.path;
                img.alt = `${scriptData.script} - ${image.filename}`;
                img.loading = 'lazy';

                // Add click handler for modal
                img.addEventListener('click', () => openModal(image.path, img.alt));

                item.appendChild(img);
                grid.appendChild(item);
            });

            section.appendChild(grid);
            container.appendChild(section);
        });
    } catch (error) {
        container.innerHTML = '<div class="loading">Error loading gallery. Please try again later.</div>';
        console.error('Error loading gallery:', error);
    }
}

function openModal(imagePath, altText) {
    const modal = document.getElementById('modal');
    const modalImg = document.getElementById('modal-image');
    const caption = document.getElementById('modal-caption');

    modal.style.display = 'block';
    modalImg.src = imagePath;
    caption.textContent = altText;
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    loadGallery();

    // Close modal handlers
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.modal-close');

    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
});

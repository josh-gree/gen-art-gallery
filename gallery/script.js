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

document.addEventListener('DOMContentLoaded', loadGallery);

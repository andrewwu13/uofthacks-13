document.addEventListener('DOMContentLoaded', () => {
    const moduleContainer = document.getElementById('module-container');
    const genreButtons = document.querySelectorAll('.genre-btn');
    const genreTitle = document.getElementById('current-genre-title');
    const body = document.body;

    // Genre switching logic
    genreButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const genre = btn.getAttribute('data-genre');

            // Update active button
            genreButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update body class
            body.className = ''; // Clear existing classes
            body.classList.add(`genre-${genre}`);

            // Update title
            const genreDisplayNames = {
                'glassmorphism': 'Glassmorphism Workspace',
                'brutalism': 'Brutalism Workspace',
                'neumorphism': 'Neumorphism Workspace',
                'cyberpunk': 'Cyberpunk Workspace',
                'minimalist': 'Minimalist Workspace',
                'monoprint': 'Mono / Print Workspace'
            };
            genreTitle.textContent = genreDisplayNames[genre];

            // Add subtle ripple effect or animation
            animateGridSwitch();
        });
    });

    const jordanProduct = {
        title: "Air Jordan 1 Retro High OG",
        price: "185.00",
        handle: "jbfd2596-102",
        vendor: "Jordan",
        image: "https://cdn.shopify.com/s/files/1/0094/2252/files/AURORA_FD2596-102_PHSRH000-2000.jpg?v=1772837341",
        description: "Leather and synthetic upper with Nike Air-Sole unit."
    };

    function createModuleCard(index) {
        const card = document.createElement('div');
        card.className = 'module-card';
        card.setAttribute('data-id', index);

        if (index === 1) {
            card.classList.add('active-draft');
            card.innerHTML = `
                <div class="glass-panel" style="padding: 1rem;">
                    <div class="product-preview" style="background-image: url('${jordanProduct.image}');"></div>
                    <div class="product-info">
                        <div class="product-title">${jordanProduct.title}</div>
                        <div class="product-subtitle">${jordanProduct.handle}</div>
                    </div>
                    <div class="card-stats">
                        <div class="stat-item">
                            <span style="color: var(--accent); font-size: 1.1rem;">◆</span>
                            <span>${jordanProduct.price}</span>
                        </div>
                        <div class="stat-item">
                            <span style="font-size: 1rem; opacity: 0.6;">♡</span>
                            <span>421</span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            card.innerHTML = `
                <div class="module-index">MODULE # ${String(index).padStart(2, '0')}</div>
                <div class="module-add-icon">+</div>
                <div class="module-label">Draft Blueprint</div>
            `;
        }

        card.addEventListener('click', () => {
            console.log(`Clicked module ${index}`);
            // Future: Open draft editor for this specific module
        });

        return card;
    }

    function animateGridSwitch() {
        const cards = document.querySelectorAll('.module-card, .bento-item');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';

            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 15);
        });
    }

    // Export function placeholder
    document.getElementById('export-btn').addEventListener('click', () => {
        alert('Module metadata export coming soon...');
    });
});

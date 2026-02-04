/**
 * GAHENAX HUB
 * Static Application Gallery
 */

document.addEventListener('DOMContentLoaded', () => {
    loadCatalog();

    const searchInput = document.getElementById('appSearch');
    searchInput.addEventListener('input', (e) => filterApps(e.target.value));
});

let catalog = [];

async function loadCatalog() {
    try {
        const response = await fetch('apps.json');
        if (!response.ok) throw new Error("Fallo al cargar catálogo");

        catalog = await response.json();
        renderApps(catalog);
    } catch (err) {
        console.error(err);
        document.getElementById('gridContainer').innerHTML = `
            <div style="color:var(--hub-accent); text-align:center; padding:2rem; border:1px solid var(--hub-border);">
                ERROR DE CONEXIÓN AL HUBSPOT
                <br><br>
                <small>${err.message}</small>
            </div>
        `;
    }
}

function renderApps(apps) {
    const container = document.getElementById('gridContainer');
    container.innerHTML = '';

    if (apps.length === 0) {
        container.innerHTML = `<div style="color:var(--hub-muted); text-align:center; grid-column:1/-1;">Sin resultados.</div>`;
        return;
    }

    apps.forEach(app => {
        const card = document.createElement('div');
        card.className = 'app-card';

        card.innerHTML = `
            <div class="app-header">
                <div>
                    <h3 class="app-title">${app.name}</h3>
                    <div class="app-version">v${app.version} | ${app.updated || 'N/A'}</div>
                </div>
                <span class="app-status">${app.status}</span>
            </div>
            
            <p class="app-desc">${app.description}</p>
            
            <div class="app-actions">
                <a href="${app.downloads.url}" class="btn-download" download>
                    DESCARGAR ARTEFACTO
                </a>
                <a href="${app.downloads.sha256_url}" class="btn-sha" target="_blank" title="Ver SHA256">
                    SHA256
                </a>
            </div>

            <div class="doc-links">
                ${app.docs.readme ? `<a href="${app.docs.readme}" class="doc-link" target="_blank">LEER README</a>` : ''}
                ${app.docs.license ? `<a href="${app.docs.license}" class="doc-link" target="_blank">LICENCIA</a>` : ''}
            </div>
        `;

        container.appendChild(card);
    });
}

function filterApps(query) {
    const lower = query.toLowerCase();
    const filtered = catalog.filter(app =>
        app.name.toLowerCase().includes(lower) ||
        app.description.toLowerCase().includes(lower)
    );
    renderApps(filtered);
}

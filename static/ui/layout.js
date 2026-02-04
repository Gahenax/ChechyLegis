/**
 * GAHENAX LAYOUT - Single Render Authority
 * Idempotent rendering for header and sidebar
 */

const LayoutRenderer = {

    /**
     * Renders the header with all buttons/links
     * Idempotent: can be called multiple times safely
     */
    renderHeader() {
        const header = document.querySelector('.lex-header');
        if (!header) {
            console.warn('⚠️ Header container not found');
            return;
        }

        // Check if already rendered
        let navContainer = header.querySelector('[data-layout="header-nav"]');

        if (!navContainer) {
            // Create new nav container
            navContainer = document.createElement('nav');
            navContainer.setAttribute('data-layout', 'header-nav');
            navContainer.style.cssText = 'display:flex; align-items:center; gap:0.5rem; margin-right:2rem;';

            // Insert as first child of header
            header.insertBefore(navContainer, header.firstChild);
        }

        // Clear and rebuild (idempotent)
        navContainer.innerHTML = '';

        // Render header links
        const headerLinks = window.GahenaxNavigation.header;
        headerLinks.forEach(link => {
            const btn = this.createHeaderButton(link);
            navContainer.appendChild(btn);
        });

        console.log('✅ Header rendered');
    },

    /**
     * Creates a header button element
     */
    createHeaderButton(linkData) {
        const btn = document.createElement('a');
        btn.id = linkData.id;
        btn.setAttribute('data-id', linkData.id);

        if (linkData.external) {
            btn.href = linkData.href;
            btn.target = '_blank';
            btn.rel = 'noopener noreferrer';
        } else {
            btn.href = '#';
        }

        // Styling
        btn.style.cssText = `
            text-decoration: none;
            color: var(--lex-text-main);
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 1px;
            padding: 0.6rem 1.2rem;
            border-radius: 4px;
            transition: 0.3s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(79, 70, 229, 0.15));
            border: 1px solid rgba(99, 102, 241, 0.3);
            cursor: pointer;
        `;

        // Icon left
        if (link.icon) {
            const iconLeft = document.createElement('i');
            iconLeft.className = `fas ${linkData.icon}`;
            iconLeft.style.cssText = 'font-size:0.9rem; color:var(--lex-accent);';
            btn.appendChild(iconLeft);
        }

        // Label
        const label = document.createTextNode(linkData.label);
        btn.appendChild(label);

        // Icon right
        if (linkData.iconRight) {
            const iconRight = document.createElement('i');
            iconRight.className = `fas ${linkData.iconRight}`;
            iconRight.style.cssText = 'font-size:0.6rem; opacity:0.5;';
            btn.appendChild(iconRight);
        }

        // Hover effects
        btn.addEventListener('mouseover', () => {
            btn.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(79, 70, 229, 0.25))';
            btn.style.borderColor = 'rgba(99, 102, 241, 0.5)';
        });

        btn.addEventListener('mouseout', () => {
            btn.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(79, 70, 229, 0.15))';
            btn.style.borderColor = 'rgba(99, 102, 241, 0.3)';
        });

        return btn;
    },

    /**
     * Renders the sidebar with all navigation links
     * Idempotent: can be called multiple times safely
     */
    renderSidebar() {
        const sidebarNav = document.querySelector('.lex-sidebar nav');
        if (!sidebarNav) {
            console.warn('⚠️ Sidebar nav not found');
            return;
        }

        // Find or create ul
        let ul = sidebarNav.querySelector('ul');
        if (!ul) {
            ul = document.createElement('ul');
            ul.style.cssText = 'list-style:none; padding:0; margin:0;';
            sidebarNav.appendChild(ul);
        }

        // Clear and rebuild (idempotent)
        ul.innerHTML = '';

        const sidebarLinks = window.GahenaxNavigation.sidebar;

        // Group by section
        const mainLinks = sidebarLinks.filter(l => l.section === 'main');
        const footerLinks = sidebarLinks.filter(l => l.section === 'footer');

        // Render main links
        mainLinks.forEach(link => {
            const li = this.createSidebarItem(link);
            ul.appendChild(li);
        });

        // Add separator if there are footer links
        if (footerLinks.length > 0) {
            const separator = document.createElement('li');
            separator.style.cssText = 'margin: 1.5rem 0; border-top: 1px solid var(--lex-border);';
            ul.appendChild(separator);

            // Render footer links
            footerLinks.forEach(link => {
                const li = this.createSidebarItem(link);
                ul.appendChild(li);
            });
        }

        console.log('✅ Sidebar rendered');
    },

    /**
     * Creates a sidebar list item
     */
    createSidebarItem(linkData) {
        const li = document.createElement('li');
        li.style.marginBottom = '0.5rem';

        const a = document.createElement('a');
        a.id = linkData.id;
        a.setAttribute('data-id', linkData.id);

        if (linkData.external) {
            a.href = linkData.href;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
        } else {
            a.href = '#';
        }

        // Base styling
        let baseStyle = `
            text-decoration: none;
            color: inherit;
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            font-size: 0.85rem;
            letter-spacing: 1px;
            transition: 0.3s;
        `;

        // Special styling for footer links
        if (linkData.section === 'footer') {
            baseStyle += `
                background: rgba(99, 102, 241, 0.1);
                border-left: 3px solid var(--lex-accent);
            `;
        }

        a.style.cssText = baseStyle;

        // Icon
        if (linkData.icon) {
            const icon = document.createElement('i');
            icon.className = `fas ${linkData.icon}`;
            a.appendChild(icon);
        }

        // Label
        const label = document.createElement('span');
        label.textContent = linkData.label;
        label.style.flex = '1';
        a.appendChild(label);

        // Right icon
        if (linkData.iconRight) {
            const iconRight = document.createElement('i');
            iconRight.className = `fas ${linkData.iconRight}`;
            iconRight.style.cssText = 'font-size: 0.7rem; opacity: 0.5;';
            a.appendChild(iconRight);
        }

        li.appendChild(a);
        return li;
    },

    /**
     * Initialize complete layout
     * Call this once on app start
     */
    init() {
        this.renderHeader();
        this.renderSidebar();
        console.log('🎨 Layout initialized');
    }
};

window.GahenaxLayout = LayoutRenderer;

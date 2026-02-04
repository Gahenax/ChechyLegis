/* ============================================
   SOLUCIÓN RÁPIDA - ENLACE ECOSISTEMA GAHENAX
   ============================================
   
   INSTRUCCIONES:
   1. Copiar todo este código
   2. Pegar al final de index.html (antes de </body>)
   3. Reiniciar servidor
   4. Refrescar navegador
   
   TIEMPO: ~2 minutos
   EFECTIVIDAD: 90-95%
   ============================================ */

window.addEventListener('load', function () {
    console.log('🔧 Iniciando inyección de enlace Ecosistema GAHENAX...');

    // Esperar 2 segundos para asegurar que todo el DOM esté renderizado
    setTimeout(() => {

        // ==========================================
        // INYECCIÓN EN HEADER (Superior)
        // ==========================================
        const header = document.querySelector('.lex-header');

        if (header && !document.getElementById('injected-ecosystem-header')) {
            console.log('📍 Header encontrado, inyectando enlace...');

            const ecosystemLink = document.createElement('a');
            ecosystemLink.id = 'injected-ecosystem-header';
            ecosystemLink.href = 'https://gahenaxaisolutions.com';
            ecosystemLink.target = '_blank';
            ecosystemLink.rel = 'noopener noreferrer';

            ecosystemLink.innerHTML = `
                <i class="fas fa-cube" style="color:#b45309; margin-right:0.5rem; font-size:0.9rem;"></i>
                <span style="color:white; font-size:0.75rem; font-weight:600; letter-spacing:1px;">ECOSISTEMA</span>
                <i class="fas fa-external-link-alt" style="margin-left:0.5rem; font-size:0.6rem; opacity:0.5; color:white;"></i>
            `;

            ecosystemLink.style.cssText = `
                display: flex !important;
                align-items: center;
                justify-content: center;
                padding: 0.6rem 1.2rem;
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(79, 70, 229, 0.2));
                border: 1px solid rgba(99, 102, 241, 0.4);
                border-radius: 4px;
                margin-right: 2rem;
                text-decoration: none;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
                z-index: 100;
            `;

            // Efectos hover
            ecosystemLink.addEventListener('mouseover', function () {
                this.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.35), rgba(79, 70, 229, 0.35))';
                this.style.borderColor = 'rgba(99, 102, 241, 0.6)';
                this.style.transform = 'translateY(-1px)';
            });

            ecosystemLink.addEventListener('mouseout', function () {
                this.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(79, 70, 229, 0.2))';
                this.style.borderColor = 'rgba(99, 102, 241, 0.4)';
                this.style.transform = 'translateY(0)';
            });

            // Insertar como primer elemento del header
            header.insertBefore(ecosystemLink, header.firstChild);
            console.log('✅ Enlace ECOSISTEMA inyectado en HEADER');
        } else if (!header) {
            console.warn('⚠️ Header no encontrado');
        } else {
            console.log('ℹ️ Enlace ya existe en header');
        }

        // ==========================================
        // INYECCIÓN EN SIDEBAR (Lateral)
        // ==========================================
        const sidebar = document.querySelector('.lex-sidebar nav ul');

        if (sidebar && !document.getElementById('injected-ecosystem-sidebar')) {
            console.log('📍 Sidebar encontrado, inyectando enlace...');

            // Crear separador
            const separator = document.createElement('li');
            separator.style.cssText = 'margin: 1.5rem 0; border-top: 1px solid var(--lex-border);';

            // Crear elemento del menú
            const li = document.createElement('li');
            li.id = 'injected-ecosystem-sidebar';
            li.style.marginBottom = '0.5rem';

            const sidebarLink = document.createElement('a');
            sidebarLink.href = 'https://gahenaxaisolutions.com';
            sidebarLink.target = '_blank';
            sidebarLink.rel = 'noopener noreferrer';

            sidebarLink.innerHTML = `
                <i class="fas fa-th-large"></i> 
                <span style="flex:1;">ECOSISTEMA GAHENAX</span> 
                <i class="fas fa-external-link-alt" style="font-size: 0.7rem; opacity: 0.5;"></i>
            `;

            sidebarLink.style.cssText = `
                text-decoration: none;
                color: inherit;
                display: flex !important;
                align-items: center;
                gap: 1rem;
                padding: 1rem;
                font-size: 0.85rem;
                letter-spacing: 1px;
                background: rgba(99, 102, 241, 0.1);
                border-left: 3px solid #b45309;
                transition: all 0.3s ease;
            `;

            // Efectos hover para sidebar
            sidebarLink.addEventListener('mouseover', function () {
                this.style.background = 'rgba(99, 102, 241, 0.2)';
                this.style.borderLeftColor = '#d97706';
            });

            sidebarLink.addEventListener('mouseout', function () {
                this.style.background = 'rgba(99, 102, 241, 0.1)';
                this.style.borderLeftColor = '#b45309';
            });

            li.appendChild(sidebarLink);
            sidebar.appendChild(separator);
            sidebar.appendChild(li);

            console.log('✅ Enlace ECOSISTEMA inyectado en SIDEBAR');
        } else if (!sidebar) {
            console.warn('⚠️ Sidebar no encontrado');
        } else {
            console.log('ℹ️ Enlace ya existe en sidebar');
        }

        console.log('🎉 Inyección de enlaces ECOSISTEMA completada');

    }, 2000); // Delay de 2 segundos
});

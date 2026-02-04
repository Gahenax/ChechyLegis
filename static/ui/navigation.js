/**
 * GAHENAX NAVIGATION - Single Source of Truth
 * All navigation links defined here
 */

const NAVIGATION_LINKS = {
    sidebar: [
        {
            id: 'nav-list',
            label: 'EXPEDIENTES',
            icon: 'fa-archive',
            route: 'list',
            section: 'main'
        },
        {
            id: 'nav-create',
            label: 'RADICACIÓN',
            icon: 'fa-file-signature',
            route: 'form',
            section: 'main'
        },
        {
            id: 'nav-support',
            label: 'SOPORTE CRM',
            icon: 'fa-gavel',
            route: 'support',
            section: 'main'
        },
        {
            id: 'nav-settings',
            label: 'ARCHIVO CENTRAL',
            icon: 'fa-landmark',
            route: 'settings',
            section: 'main'
        },
        {
            id: 'nav-ecosystem',
            label: 'ECOSISTEMA GAHENAX',
            icon: 'fa-th-large',
            href: 'https://gahenaxaisolutions.com',
            external: true,
            section: 'footer',
            iconRight: 'fa-external-link-alt'
        }
    ],

    header: [
        {
            id: 'btn-ecosystem',
            label: 'ECOSISTEMA',
            icon: 'fa-cube',
            href: 'https://gahenaxaisolutions.com',
            external: true,
            iconRight: 'fa-external-link-alt',
            style: 'primary' // blue gradient
        }
    ]
};

window.GahenaxNavigation = NAVIGATION_LINKS;

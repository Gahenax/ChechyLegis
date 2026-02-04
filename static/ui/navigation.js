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
            label: 'LLAMAR A RECEPCIÓN',
            icon: 'fa-phone-alt',
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
            label: 'LOBBY DEL HOTEL',
            icon: 'fa-hotel',
            href: '/gahenax_hub.html',
            external: false,
            section: 'footer',
            iconRight: 'fa-door-open'
        }
    ],

    header: [
        {
            id: 'btn-ecosystem',
            label: 'IR AL LOBBY',
            icon: 'fa-hotel',
            href: '/gahenax_hub.html',
            external: false,
            style: 'primary'
        }
    ]
};

window.GahenaxNavigation = NAVIGATION_LINKS;

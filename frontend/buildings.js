const BUILDING_CATEGORIES = {
    science: { label: 'Science & Research', icon: '🔬' },
    technical: { label: 'Technical & Operations', icon: '⚙️' },
    living: { label: 'Living & Wellbeing', icon: '🏠' },
    energy: { label: 'Energy Infrastructure', icon: '⚡' },
    external: { label: 'External Facilities', icon: '🚁' }
};

// Grid unit = 8.1 meters
const BUILDINGS = [
    {
        id: 'energy_ring', name: 'Energy Ring', category: 'energy', icon: '⭕',
        shape: 'ring', cx: 0, cy: 0, radius: 10.5, z: 0, h_z: 0.2,
        basePower: -1000, description: '170m circular ring with 1,800m² PV panels and 10x 70kW Darrieus wind turbines.'
    },
    {
        id: 'vcv_base', name: 'VCV Technical Base', category: 'technical', icon: '🔧',
        shape: 'box', x: -4, y: -4, w: 8, h: 8, z: 0, h_z: 1.5,
        basePower: 120, description: '64.8m square technical rooms, workshops, snow groomer garages, and emergency groups.'
    },
    {
        id: 'vcv_living', name: 'VCV Living Floor', category: 'living', icon: '👥',
        shape: 'box', x: -5, y: -5, w: 10, h: 10, z: 1.5, h_z: 1.5,
        basePower: 180, description: '81m square living floor with bedrooms, kitchen, fitness, and central square.'
    },
    {
        id: 'vcv_dome', name: 'Bioclimatic Dome', category: 'science', icon: '🌐',
        shape: 'dome', cx: 0, cy: 0, radius: 6.5, z: 0, h_z: 4,
        basePower: 80, description: '105m spherical cap maintaining 4-11°C with circadian lighting and outdoor feel.'
    },
    {
        id: 'sci_platform', name: 'Scientific Platform', category: 'science', icon: '📡',
        shape: 'box', x: -1, y: -1, w: 2, h: 2, z: 4, h_z: 0.5,
        basePower: 40, description: '16.2m square platform for scientific measuring equipment.'
    },
    {
        id: 'hangar_1', name: 'Industrial Hangar A', category: 'external', icon: '🏭',
        shape: 'box', x: 14, y: -7, w: 5, h: 4, z: 0, h_z: 2,
        basePower: 30, description: 'Helicopter garage and product stock.'
    },
    {
        id: 'hangar_2', name: 'Industrial Hangar B', category: 'external', icon: '🏭',
        shape: 'box', x: 14, y: -2, w: 5, h: 4, z: 0, h_z: 2,
        basePower: 30, description: 'Refuge area and non-daily use storage.'
    },
    {
        id: 'helipad', name: 'Helipad', category: 'external', icon: '🚁',
        shape: 'circle', cx: 16.5, cy: 4, radius: 2.5, z: 0, h_z: 0.1,
        basePower: 10, description: 'Landing zone for helicopters.'
    }
];

const ROADS = [
    { x: 10, y: -2.5, w: 4, h: 1 },
    { x: 13, y: -8, w: 1, h: 14 },
    { x: 15.5, y: 2, w: 2, h: 2 }
];

const POWER_LINES = [
    { x1: 10.5, y1: -2, x2: 13.5, y2: -2 },
    { x1: 13.5, y1: -2, x2: 14, y2: -5 },
    { x1: 13.5, y1: -2, x2: 14, y2: 0 },
    { x1: 14, y1: 0, x2: 16.5, y2: 4 }
];

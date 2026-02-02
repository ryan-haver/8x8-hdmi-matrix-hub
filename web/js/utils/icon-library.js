/**
 * OREI Matrix Control - Device Icon Library
 * Contains SVG icons for input/output device types with multiple style variants
 */

class IconLibrary {
    /**
     * Style variants for each icon:
     * - wireframe: Simple line art, single color (small sizes, status indicators)
     * - detailed: Filled with shading (large cards, featured displays)
     * - glyph: Solid silhouette, minimal detail (very small sizes, badges)
     * 
     * All icons use 24x24 viewBox
     */
    
    /**
     * Base path for external SVG icon files
     */
    static SVG_BASE_PATH = '/assets/icons/svg/';
    
    /**
     * External SVG icons registry
     * These icons are loaded from external files instead of inline paths
     * Key = icon ID, Value = filename (without .svg extension)
     */
    static externalIcons = {
        // Gaming Consoles - Modern
        'playstation-5': 'playstation_5',
        'xbox-series-x': 'xbox_series_x',
        'nintendo-switch-ext': 'nintendo_switch',
        'steam-deck-ext': 'steam_deck',
        'wii-ext': 'wii',
        
        // Gaming Consoles - Retro
        'nes-ext': 'nes_console',
        'snes-ext': 'snes_console',
        'n64-ext': 'n64',
        'gamecube-ext': 'gamecube',
        'sega-genesis': 'sega_genesis',
        'dreamcast-ext': 'dreamcast',
        'atari-2600': 'atari_2600',
        'ps2': 'ps2',
        'ps3': 'ps3',
        'ps4': 'ps4',
        'xbox-360': 'xbox_360',
        'xbox-one': 'xbox_one',
        
        // Streaming Devices
        'apple-tv-ext': 'apple_tv',
        'roku-ext': 'roku_stick',
        'fire-tv-ext': 'fire_tv',
        'chromecast-ext': 'chromecast',
        'nvidia-shield': 'nvidia_shield',
        
        // Computer Devices
        'gaming-pc': 'gaming_pc',
        'laptop-ext': 'laptop',
        'mac-mini-ext': 'mac_mini',
        'htpc': 'htpc',
        
        // Display Devices
        'television-ext': 'television',
        'projector-ext': 'projector',
        'monitor-ext': 'monitor',
        'curved-tv': 'curved_tv',
        
        // Audio Equipment
        'soundbar-ext': 'soundbar',
        'av-receiver-ext': 'av_receiver',
        'speaker': 'speaker',
        'subwoofer': 'subwoofer',
        'headphones': 'headphones',
        'turntable': 'turntable',
        
        // Pro AV Equipment
        'bluray-player': 'bluray_player',
        'cable-box-ext': 'cable_box',
        'hdmi-switch': 'hdmi_switch',
        'server-rack': 'server_rack',
        'security-camera': 'security_camera',
        
        // Scene Icons
        'movie-scene': 'movie_scene',
        'gaming-scene': 'gaming_scene',
        'sports-scene': 'sports_scene',
        'music-scene': 'music_scene',
        
        // Room Icons
        'living-room': 'living_room',
        'bedroom': 'bedroom',
        'home-office': 'office_room',
        'game-room': 'game_room',
        
        // Controllers
        'xbox-controller': 'xbox_controller',
        'ps-controller': 'ps_controller',
        
        // Utility Icons
        'generic-input-ext': 'generic_input',
        'generic-output-ext': 'generic_output',
        'generic-device-ext': 'generic_device',
        'settings-gear': 'settings_gear',
        'tablet': 'tablet'
    };

    static icons = {
        // === GAMING (4) ===
        'playstation': {
            wireframe: `
                <rect x="4" y="3" width="4" height="18" rx="1"/>
                <rect x="16" y="3" width="4" height="18" rx="1"/>
                <rect x="8" y="5" width="8" height="14" rx="0.5"/>
            `,
            detailed: `
                <rect x="4" y="3" width="4" height="18" rx="1" fill="currentColor" opacity="0.3"/>
                <rect x="4" y="3" width="4" height="18" rx="1"/>
                <rect x="16" y="3" width="4" height="18" rx="1" fill="currentColor" opacity="0.3"/>
                <rect x="16" y="3" width="4" height="18" rx="1"/>
                <rect x="8" y="5" width="8" height="14" rx="0.5" fill="currentColor" opacity="0.15"/>
                <rect x="8" y="5" width="8" height="14" rx="0.5"/>
                <circle cx="12" cy="12" r="1.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="4" y="3" width="4" height="18" rx="1" fill="currentColor"/>
                <rect x="16" y="3" width="4" height="18" rx="1" fill="currentColor"/>
                <rect x="8" y="5" width="8" height="14" rx="0.5" fill="currentColor" opacity="0.6"/>
            `
        },
        'xbox': {
            wireframe: `
                <rect x="6" y="2" width="12" height="20" rx="2"/>
                <circle cx="12" cy="8" r="2"/>
                <path d="M9 14h6M12 11v6"/>
            `,
            detailed: `
                <rect x="6" y="2" width="12" height="20" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="6" y="2" width="12" height="20" rx="2"/>
                <circle cx="12" cy="8" r="2.5" fill="currentColor" opacity="0.4"/>
                <circle cx="12" cy="8" r="2"/>
                <path d="M9 14h6M12 11v6"/>
                <rect x="7" y="3" width="2" height="3" rx="0.5" fill="currentColor" opacity="0.3"/>
            `,
            glyph: `
                <rect x="6" y="2" width="12" height="20" rx="2" fill="currentColor"/>
                <circle cx="12" cy="8" r="2" fill="rgba(0,0,0,0.3)"/>
                <path d="M9 14h6M12 11v6" stroke="rgba(0,0,0,0.3)" fill="none"/>
            `
        },
        'nintendo-switch': {
            wireframe: `
                <rect x="2" y="5" width="6" height="14" rx="2"/>
                <rect x="16" y="5" width="6" height="14" rx="2"/>
                <rect x="7" y="6" width="10" height="12" rx="1"/>
                <circle cx="5" cy="9" r="1.5"/>
                <circle cx="19" cy="15" r="1.5"/>
            `,
            detailed: `
                <rect x="2" y="5" width="6" height="14" rx="2" fill="currentColor" opacity="0.3"/>
                <rect x="2" y="5" width="6" height="14" rx="2"/>
                <rect x="16" y="5" width="6" height="14" rx="2" fill="currentColor" opacity="0.3"/>
                <rect x="16" y="5" width="6" height="14" rx="2"/>
                <rect x="7" y="6" width="10" height="12" rx="1" fill="currentColor" opacity="0.15"/>
                <rect x="7" y="6" width="10" height="12" rx="1"/>
                <circle cx="5" cy="9" r="1.5" fill="currentColor" opacity="0.5"/>
                <circle cx="19" cy="15" r="1.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="2" y="5" width="6" height="14" rx="2" fill="currentColor"/>
                <rect x="16" y="5" width="6" height="14" rx="2" fill="currentColor"/>
                <rect x="7" y="6" width="10" height="12" rx="1" fill="currentColor" opacity="0.5"/>
            `
        },
        'steam-deck': {
            wireframe: `
                <rect x="1" y="7" width="22" height="10" rx="3"/>
                <circle cx="5" cy="12" r="2"/>
                <circle cx="19" cy="12" r="2"/>
                <rect x="9" y="9" width="6" height="6" rx="1"/>
            `,
            detailed: `
                <rect x="1" y="7" width="22" height="10" rx="3" fill="currentColor" opacity="0.2"/>
                <rect x="1" y="7" width="22" height="10" rx="3"/>
                <circle cx="5" cy="12" r="2.5" fill="currentColor" opacity="0.3"/>
                <circle cx="5" cy="12" r="2"/>
                <circle cx="19" cy="12" r="2.5" fill="currentColor" opacity="0.3"/>
                <circle cx="19" cy="12" r="2"/>
                <rect x="9" y="9" width="6" height="6" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="9" y="9" width="6" height="6" rx="1"/>
            `,
            glyph: `
                <rect x="1" y="7" width="22" height="10" rx="3" fill="currentColor"/>
                <circle cx="5" cy="12" r="2" fill="rgba(0,0,0,0.3)"/>
                <circle cx="19" cy="12" r="2" fill="rgba(0,0,0,0.3)"/>
                <rect x="9" y="9" width="6" height="6" rx="1" fill="rgba(0,0,0,0.2)"/>
            `
        },

        // === STREAMING (4) ===
        'apple-tv': {
            wireframe: `
                <rect x="4" y="6" width="16" height="12" rx="3"/>
                <path d="M12 10c-.5-.5-1.5 0-1.5.8s.7 1.7 1.5 1.7 1.5-1 1.5-1.7-.5-1.3-1.5-.8z"/>
            `,
            detailed: `
                <rect x="4" y="6" width="16" height="12" rx="3" fill="currentColor" opacity="0.2"/>
                <rect x="4" y="6" width="16" height="12" rx="3"/>
                <path d="M12 9c-1-1-2.5 0-2.5 1.5s1 3 2.5 3 2.5-1.5 2.5-3-1-2.5-2.5-1.5z" fill="currentColor"/>
                <circle cx="12.5" cy="8.5" r="0.8" fill="currentColor"/>
            `,
            glyph: `
                <rect x="4" y="6" width="16" height="12" rx="3" fill="currentColor"/>
                <path d="M12 9.5c-.8-.8-2 0-2 1.2s.8 2.3 2 2.3 2-1.2 2-2.3-.8-2-2-1.2z" fill="rgba(0,0,0,0.4)"/>
            `
        },
        'roku': {
            wireframe: `
                <rect x="6" y="4" width="12" height="16" rx="2"/>
                <circle cx="12" cy="10" r="3"/>
                <rect x="10" y="15" width="4" height="2" rx="1"/>
            `,
            detailed: `
                <rect x="6" y="4" width="12" height="16" rx="2" fill="currentColor" opacity="0.25"/>
                <rect x="6" y="4" width="12" height="16" rx="2"/>
                <circle cx="12" cy="10" r="3.5" fill="currentColor" opacity="0.3"/>
                <circle cx="12" cy="10" r="3"/>
                <text x="12" y="11.5" text-anchor="middle" font-size="5" font-weight="bold" fill="currentColor">R</text>
                <rect x="10" y="15" width="4" height="2" rx="1" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="6" y="4" width="12" height="16" rx="2" fill="currentColor"/>
                <circle cx="12" cy="10" r="3" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'fire-tv': {
            wireframe: `
                <rect x="8" y="3" width="8" height="18" rx="2"/>
                <path d="M12 8c-1.5 0-2.5 1.5-2.5 3s1.5 3 2.5 2.5c1 .5 2.5-1 2.5-2.5s-1-3-2.5-3z"/>
            `,
            detailed: `
                <rect x="8" y="3" width="8" height="18" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="8" y="3" width="8" height="18" rx="2"/>
                <path d="M12 7c-2 0-3 2-3 4s1.5 4 3 3.5c1.5.5 3-1.5 3-3.5s-1-4-3-4z" fill="currentColor" opacity="0.6"/>
                <path d="M12 8c-1 0-1.5 1-1.5 2s1 2 1.5 1.5c.5.5 1.5-.5 1.5-1.5s-.5-2-1.5-2z" fill="currentColor"/>
                <rect x="10" y="17" width="4" height="2" rx="1" fill="currentColor" opacity="0.4"/>
            `,
            glyph: `
                <rect x="8" y="3" width="8" height="18" rx="2" fill="currentColor"/>
                <path d="M12 7c-2 0-3 2-3 4s1.5 4 3 3.5c1.5.5 3-1.5 3-3.5s-1-4-3-4z" fill="rgba(0,0,0,0.4)"/>
            `
        },
        'chromecast': {
            wireframe: `
                <circle cx="12" cy="12" r="8"/>
                <circle cx="12" cy="12" r="4"/>
                <circle cx="12" cy="12" r="1.5"/>
            `,
            detailed: `
                <circle cx="12" cy="12" r="9" fill="currentColor" opacity="0.15"/>
                <circle cx="12" cy="12" r="8"/>
                <circle cx="12" cy="12" r="5" fill="currentColor" opacity="0.25"/>
                <circle cx="12" cy="12" r="4"/>
                <circle cx="12" cy="12" r="2" fill="currentColor"/>
                <path d="M18 7l2.5-2.5M18 17l2.5 2.5" stroke-width="1.5"/>
            `,
            glyph: `
                <circle cx="12" cy="12" r="8" fill="currentColor"/>
                <circle cx="12" cy="12" r="4" fill="rgba(0,0,0,0.3)"/>
                <circle cx="12" cy="12" r="1.5" fill="rgba(0,0,0,0.5)"/>
            `
        },

        // === COMPUTER (3) ===
        'desktop-pc': {
            wireframe: `
                <rect x="5" y="2" width="14" height="18" rx="1"/>
                <rect x="6" y="3" width="12" height="10"/>
                <path d="M8 15h8M8 17h4"/>
                <circle cx="16" cy="17" r="1"/>
            `,
            detailed: `
                <rect x="5" y="2" width="14" height="18" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="5" y="2" width="14" height="18" rx="1"/>
                <rect x="6" y="3" width="12" height="10" fill="currentColor" opacity="0.15"/>
                <rect x="6" y="3" width="12" height="10"/>
                <path d="M8 15h8M8 17h4"/>
                <circle cx="16" cy="17" r="1" fill="currentColor"/>
                <rect x="16" y="3" width="1.5" height="4" rx="0.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="5" y="2" width="14" height="18" rx="1" fill="currentColor"/>
                <rect x="6" y="3" width="12" height="10" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'laptop': {
            wireframe: `
                <path d="M4 6h16v10H4z"/>
                <path d="M2 16h20l-2 4H4l-2-4z"/>
                <rect x="6" y="7" width="12" height="8"/>
            `,
            detailed: `
                <path d="M4 6h16v10H4z" fill="currentColor" opacity="0.2"/>
                <path d="M4 6h16v10H4z"/>
                <path d="M2 16h20l-2 4H4l-2-4z" fill="currentColor" opacity="0.3"/>
                <path d="M2 16h20l-2 4H4l-2-4z"/>
                <rect x="5" y="7" width="14" height="8" fill="currentColor" opacity="0.15"/>
                <rect x="5" y="7" width="14" height="8"/>
                <path d="M9 20h6"/>
            `,
            glyph: `
                <path d="M4 6h16v10H4z" fill="currentColor"/>
                <path d="M2 16h20l-2 4H4l-2-4z" fill="currentColor" opacity="0.7"/>
            `
        },
        'mac-mini': {
            wireframe: `
                <rect x="3" y="8" width="18" height="8" rx="2"/>
                <circle cx="17" cy="12" r="1.5"/>
                <path d="M6 12h6"/>
            `,
            detailed: `
                <rect x="3" y="8" width="18" height="8" rx="2" fill="currentColor" opacity="0.25"/>
                <rect x="3" y="8" width="18" height="8" rx="2"/>
                <rect x="4" y="9" width="16" height="6" rx="1.5" fill="currentColor" opacity="0.1"/>
                <circle cx="17" cy="12" r="2" fill="currentColor" opacity="0.3"/>
                <circle cx="17" cy="12" r="1.5"/>
                <path d="M6 12h6"/>
                <path d="M3 14h18" opacity="0.3"/>
            `,
            glyph: `
                <rect x="3" y="8" width="18" height="8" rx="2" fill="currentColor"/>
                <circle cx="17" cy="12" r="1.5" fill="rgba(0,0,0,0.3)"/>
            `
        },

        // === DISPLAY (3) ===
        'television': {
            wireframe: `
                <rect x="2" y="3" width="20" height="14" rx="1"/>
                <rect x="3" y="4" width="18" height="12"/>
                <path d="M8 20h8"/>
                <path d="M12 17v3"/>
            `,
            detailed: `
                <rect x="2" y="3" width="20" height="14" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="3" width="20" height="14" rx="1"/>
                <rect x="3" y="4" width="18" height="12" fill="currentColor" opacity="0.1"/>
                <rect x="3" y="4" width="18" height="12"/>
                <path d="M8 20h8"/>
                <path d="M12 17v3"/>
                <path d="M5 7l3 3M5 10l3-3" opacity="0.4"/>
            `,
            glyph: `
                <rect x="2" y="3" width="20" height="14" rx="1" fill="currentColor"/>
                <rect x="3" y="4" width="18" height="12" fill="rgba(0,0,0,0.2)"/>
                <path d="M8 20h8M12 17v3" stroke="currentColor"/>
            `
        },
        'projector': {
            wireframe: `
                <rect x="2" y="7" width="20" height="10" rx="2"/>
                <circle cx="7" cy="12" r="3"/>
                <circle cx="7" cy="12" r="1.5"/>
                <rect x="12" y="9" width="8" height="6" rx="1"/>
                <path d="M5 17v2M19 17v2"/>
            `,
            detailed: `
                <rect x="2" y="7" width="20" height="10" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="7" width="20" height="10" rx="2"/>
                <circle cx="7" cy="12" r="3.5" fill="currentColor" opacity="0.3"/>
                <circle cx="7" cy="12" r="3"/>
                <circle cx="7" cy="12" r="1.5" fill="currentColor"/>
                <rect x="12" y="9" width="8" height="6" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="12" y="9" width="8" height="6" rx="1"/>
                <path d="M5 17v2M19 17v2"/>
            `,
            glyph: `
                <rect x="2" y="7" width="20" height="10" rx="2" fill="currentColor"/>
                <circle cx="7" cy="12" r="3" fill="rgba(0,0,0,0.3)"/>
                <circle cx="7" cy="12" r="1.5" fill="rgba(0,0,0,0.5)"/>
            `
        },
        'monitor': {
            wireframe: `
                <rect x="3" y="2" width="18" height="14" rx="1"/>
                <rect x="4" y="3" width="16" height="12"/>
                <path d="M8 19h8"/>
                <path d="M12 16v3"/>
                <rect x="10" y="19" width="4" height="2" rx="0.5"/>
            `,
            detailed: `
                <rect x="3" y="2" width="18" height="14" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="3" y="2" width="18" height="14" rx="1"/>
                <rect x="4" y="3" width="16" height="12" fill="currentColor" opacity="0.1"/>
                <rect x="4" y="3" width="16" height="12"/>
                <path d="M8 19h8"/>
                <path d="M12 16v3"/>
                <rect x="10" y="19" width="4" height="2" rx="0.5" fill="currentColor" opacity="0.4"/>
            `,
            glyph: `
                <rect x="3" y="2" width="18" height="14" rx="1" fill="currentColor"/>
                <rect x="4" y="3" width="16" height="12" fill="rgba(0,0,0,0.2)"/>
                <path d="M12 16v5M8 21h8" stroke="currentColor"/>
            `
        },

        // === MEDIA (3) ===
        'blu-ray': {
            wireframe: `
                <rect x="2" y="8" width="20" height="8" rx="1"/>
                <rect x="3" y="9" width="8" height="6"/>
                <circle cx="7" cy="12" r="2"/>
                <circle cx="7" cy="12" r="0.5"/>
                <path d="M13 10h7M13 12h5"/>
            `,
            detailed: `
                <rect x="2" y="8" width="20" height="8" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="8" width="20" height="8" rx="1"/>
                <rect x="3" y="9" width="8" height="6" fill="currentColor" opacity="0.15"/>
                <rect x="3" y="9" width="8" height="6"/>
                <circle cx="7" cy="12" r="2.5" fill="currentColor" opacity="0.3"/>
                <circle cx="7" cy="12" r="2"/>
                <circle cx="7" cy="12" r="0.8" fill="currentColor"/>
                <path d="M13 10h7M13 12h5M13 14h3" opacity="0.6"/>
            `,
            glyph: `
                <rect x="2" y="8" width="20" height="8" rx="1" fill="currentColor"/>
                <rect x="3" y="9" width="8" height="6" fill="rgba(0,0,0,0.2)"/>
                <circle cx="7" cy="12" r="2" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'cable-box': {
            wireframe: `
                <rect x="2" y="6" width="20" height="12" rx="1"/>
                <rect x="4" y="8" width="6" height="4" rx="0.5"/>
                <path d="M12 9h8M12 11h6M12 13h4"/>
                <circle cx="5" cy="15" r="1"/>
            `,
            detailed: `
                <rect x="2" y="6" width="20" height="12" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="6" width="20" height="12" rx="1"/>
                <rect x="4" y="8" width="6" height="4" rx="0.5" fill="currentColor" opacity="0.4"/>
                <rect x="4" y="8" width="6" height="4" rx="0.5"/>
                <path d="M12 9h8M12 11h6M12 13h4"/>
                <circle cx="5" cy="15" r="1" fill="currentColor"/>
                <circle cx="8" cy="15" r="0.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="2" y="6" width="20" height="12" rx="1" fill="currentColor"/>
                <rect x="4" y="8" width="6" height="4" rx="0.5" fill="rgba(0,0,0,0.4)"/>
            `
        },
        'soundbar': {
            wireframe: `
                <rect x="1" y="9" width="22" height="6" rx="2"/>
                <circle cx="5" cy="12" r="1.5"/>
                <circle cx="9" cy="12" r="1.5"/>
                <circle cx="12" cy="12" r="1.5"/>
                <circle cx="15" cy="12" r="1.5"/>
                <circle cx="19" cy="12" r="1.5"/>
            `,
            detailed: `
                <rect x="1" y="9" width="22" height="6" rx="2" fill="currentColor" opacity="0.25"/>
                <rect x="1" y="9" width="22" height="6" rx="2"/>
                <circle cx="5" cy="12" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="5" cy="12" r="1.5"/>
                <circle cx="9" cy="12" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="9" cy="12" r="1.5"/>
                <circle cx="12" cy="12" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="12" cy="12" r="1.5"/>
                <circle cx="15" cy="12" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="15" cy="12" r="1.5"/>
                <circle cx="19" cy="12" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="19" cy="12" r="1.5"/>
            `,
            glyph: `
                <rect x="1" y="9" width="22" height="6" rx="2" fill="currentColor"/>
                <circle cx="5" cy="12" r="1.5" fill="rgba(0,0,0,0.3)"/>
                <circle cx="9" cy="12" r="1.5" fill="rgba(0,0,0,0.3)"/>
                <circle cx="12" cy="12" r="1.5" fill="rgba(0,0,0,0.3)"/>
                <circle cx="15" cy="12" r="1.5" fill="rgba(0,0,0,0.3)"/>
                <circle cx="19" cy="12" r="1.5" fill="rgba(0,0,0,0.3)"/>
            `
        },

        // === GENERIC (3) ===
        'generic-input': {
            wireframe: `
                <rect x="4" y="4" width="16" height="16" rx="2"/>
                <path d="M8 12h6"/>
                <path d="M11 9l3 3-3 3"/>
            `,
            detailed: `
                <rect x="4" y="4" width="16" height="16" rx="2" fill="currentColor" opacity="0.15"/>
                <rect x="4" y="4" width="16" height="16" rx="2"/>
                <path d="M7 12h7" stroke-width="2"/>
                <path d="M11 8l4 4-4 4" stroke-width="2" fill="none"/>
                <circle cx="17" cy="12" r="1" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="4" y="4" width="16" height="16" rx="2" fill="currentColor"/>
                <path d="M8 12h6M11 9l3 3-3 3" stroke="rgba(0,0,0,0.4)" stroke-width="2" fill="none"/>
            `
        },
        'generic-output': {
            wireframe: `
                <rect x="4" y="4" width="16" height="16" rx="2"/>
                <path d="M10 12h6"/>
                <path d="M13 9l-3 3 3 3"/>
            `,
            detailed: `
                <rect x="4" y="4" width="16" height="16" rx="2" fill="currentColor" opacity="0.15"/>
                <rect x="4" y="4" width="16" height="16" rx="2"/>
                <path d="M10 12h7" stroke-width="2"/>
                <path d="M13 8l-4 4 4 4" stroke-width="2" fill="none"/>
                <circle cx="7" cy="12" r="1" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="4" y="4" width="16" height="16" rx="2" fill="currentColor"/>
                <path d="M10 12h6M13 9l-3 3 3 3" stroke="rgba(0,0,0,0.4)" stroke-width="2" fill="none"/>
            `
        },
        'generic-device': {
            wireframe: `
                <rect x="4" y="4" width="16" height="16" rx="2"/>
                <circle cx="12" cy="12" r="4"/>
                <path d="M12 8v8M8 12h8"/>
            `,
            detailed: `
                <rect x="4" y="4" width="16" height="16" rx="2" fill="currentColor" opacity="0.15"/>
                <rect x="4" y="4" width="16" height="16" rx="2"/>
                <circle cx="12" cy="12" r="5" fill="currentColor" opacity="0.2"/>
                <circle cx="12" cy="12" r="4"/>
                <path d="M12 8v8M8 12h8"/>
            `,
            glyph: `
                <rect x="4" y="4" width="16" height="16" rx="2" fill="currentColor"/>
                <circle cx="12" cy="12" r="4" fill="rgba(0,0,0,0.3)"/>
            `
        },

        // === RETRO GAMING (10) ===
        'nes': {
            wireframe: `
                <rect x="2" y="8" width="20" height="8" rx="1"/>
                <rect x="4" y="10" width="6" height="4"/>
                <path d="M12 10h6M12 12h4M12 14h2"/>
                <rect x="16" y="9" width="4" height="2" rx="0.5"/>
            `,
            detailed: `
                <rect x="2" y="8" width="20" height="8" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="8" width="20" height="8" rx="1"/>
                <rect x="4" y="10" width="6" height="4" fill="currentColor" opacity="0.3"/>
                <rect x="4" y="10" width="6" height="4"/>
                <path d="M12 10h6M12 12h4M12 14h2" opacity="0.6"/>
                <rect x="16" y="9" width="4" height="2" rx="0.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="2" y="8" width="20" height="8" rx="1" fill="currentColor"/>
                <rect x="4" y="10" width="6" height="4" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'snes': {
            wireframe: `
                <rect x="2" y="9" width="20" height="7" rx="1"/>
                <path d="M3 9v-2a1 1 0 0 1 1-1h3v3"/>
                <path d="M21 9v-2a1 1 0 0 0-1-1h-3v3"/>
                <rect x="8" y="11" width="3" height="3" rx="0.5"/>
                <circle cx="16" cy="12" r="1"/>
                <circle cx="18" cy="14" r="1"/>
            `,
            detailed: `
                <rect x="2" y="9" width="20" height="7" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="9" width="20" height="7" rx="1"/>
                <path d="M3 9v-2a1 1 0 0 1 1-1h3v3" fill="currentColor" opacity="0.15"/>
                <path d="M3 9v-2a1 1 0 0 1 1-1h3v3"/>
                <path d="M21 9v-2a1 1 0 0 0-1-1h-3v3" fill="currentColor" opacity="0.15"/>
                <path d="M21 9v-2a1 1 0 0 0-1-1h-3v3"/>
                <rect x="8" y="11" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.4"/>
                <circle cx="16" cy="12" r="1" fill="currentColor" opacity="0.5"/>
                <circle cx="18" cy="14" r="1" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="2" y="9" width="20" height="7" rx="1" fill="currentColor"/>
                <path d="M3 9v-2a1 1 0 0 1 1-1h3v3M21 9v-2a1 1 0 0 0-1-1h-3v3" fill="currentColor"/>
            `
        },
        'n64': {
            wireframe: `
                <path d="M4 14l4-6h8l4 6"/>
                <rect x="6" y="14" width="12" height="4" rx="1"/>
                <circle cx="9" cy="12" r="1.5"/>
                <circle cx="15" cy="12" r="1.5"/>
                <path d="M11 16h2"/>
            `,
            detailed: `
                <path d="M4 14l4-6h8l4 6" fill="currentColor" opacity="0.2"/>
                <path d="M4 14l4-6h8l4 6"/>
                <rect x="6" y="14" width="12" height="4" rx="1" fill="currentColor" opacity="0.25"/>
                <rect x="6" y="14" width="12" height="4" rx="1"/>
                <circle cx="9" cy="12" r="2" fill="currentColor" opacity="0.3"/>
                <circle cx="9" cy="12" r="1.5"/>
                <circle cx="15" cy="12" r="2" fill="currentColor" opacity="0.3"/>
                <circle cx="15" cy="12" r="1.5"/>
                <path d="M11 16h2" stroke-width="2"/>
            `,
            glyph: `
                <path d="M4 14l4-6h8l4 6" fill="currentColor"/>
                <rect x="6" y="14" width="12" height="4" rx="1" fill="currentColor"/>
            `
        },
        'gamecube': {
            wireframe: `
                <rect x="5" y="5" width="14" height="14" rx="2"/>
                <rect x="7" y="7" width="10" height="3" rx="1"/>
                <circle cx="10" cy="14" r="2"/>
                <circle cx="15" cy="13" r="1"/>
            `,
            detailed: `
                <rect x="5" y="5" width="14" height="14" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="5" y="5" width="14" height="14" rx="2"/>
                <rect x="7" y="7" width="10" height="3" rx="1" fill="currentColor" opacity="0.3"/>
                <rect x="7" y="7" width="10" height="3" rx="1"/>
                <circle cx="10" cy="14" r="2.5" fill="currentColor" opacity="0.25"/>
                <circle cx="10" cy="14" r="2"/>
                <circle cx="15" cy="13" r="1.3" fill="currentColor" opacity="0.4"/>
                <rect x="16" y="5" width="2" height="4" rx="0.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="5" y="5" width="14" height="14" rx="2" fill="currentColor"/>
                <rect x="7" y="7" width="10" height="3" rx="1" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'wii': {
            wireframe: `
                <rect x="9" y="2" width="6" height="20" rx="2"/>
                <rect x="10" y="4" width="4" height="2" rx="0.5"/>
                <path d="M10 8h4M10 10h4"/>
                <circle cx="12" cy="14" r="1.5"/>
            `,
            detailed: `
                <rect x="9" y="2" width="6" height="20" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="9" y="2" width="6" height="20" rx="2"/>
                <rect x="10" y="4" width="4" height="2" rx="0.5" fill="currentColor" opacity="0.4"/>
                <path d="M10 8h4M10 10h4" opacity="0.5"/>
                <circle cx="12" cy="14" r="2" fill="currentColor" opacity="0.3"/>
                <circle cx="12" cy="14" r="1.5"/>
                <path d="M9 18h6" opacity="0.3"/>
            `,
            glyph: `
                <rect x="9" y="2" width="6" height="20" rx="2" fill="currentColor"/>
                <rect x="10" y="4" width="4" height="2" rx="0.5" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'genesis': {
            wireframe: `
                <rect x="2" y="10" width="20" height="6" rx="1"/>
                <path d="M4 10v-3a1 1 0 0 1 1-1h6v4"/>
                <rect x="14" y="11" width="6" height="4" rx="0.5"/>
                <circle cx="6" cy="13" r="1"/>
            `,
            detailed: `
                <rect x="2" y="10" width="20" height="6" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="10" width="20" height="6" rx="1"/>
                <path d="M4 10v-3a1 1 0 0 1 1-1h6v4" fill="currentColor" opacity="0.15"/>
                <path d="M4 10v-3a1 1 0 0 1 1-1h6v4"/>
                <rect x="14" y="11" width="6" height="4" rx="0.5" fill="currentColor" opacity="0.3"/>
                <rect x="14" y="11" width="6" height="4" rx="0.5"/>
                <circle cx="6" cy="13" r="1" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="2" y="10" width="20" height="6" rx="1" fill="currentColor"/>
                <path d="M4 10v-3a1 1 0 0 1 1-1h6v4" fill="currentColor"/>
            `
        },
        'saturn': {
            wireframe: `
                <ellipse cx="12" cy="12" rx="10" ry="5"/>
                <ellipse cx="12" cy="12" rx="6" ry="3"/>
                <circle cx="8" cy="12" r="1"/>
                <circle cx="16" cy="12" r="1"/>
            `,
            detailed: `
                <ellipse cx="12" cy="12" rx="10" ry="5" fill="currentColor" opacity="0.15"/>
                <ellipse cx="12" cy="12" rx="10" ry="5"/>
                <ellipse cx="12" cy="12" rx="6" ry="3" fill="currentColor" opacity="0.25"/>
                <ellipse cx="12" cy="12" rx="6" ry="3"/>
                <circle cx="8" cy="12" r="1.2" fill="currentColor" opacity="0.5"/>
                <circle cx="16" cy="12" r="1.2" fill="currentColor" opacity="0.5"/>
                <path d="M12 9v6" opacity="0.3"/>
            `,
            glyph: `
                <ellipse cx="12" cy="12" rx="10" ry="5" fill="currentColor"/>
                <ellipse cx="12" cy="12" rx="6" ry="3" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'dreamcast': {
            wireframe: `
                <rect x="4" y="6" width="16" height="12" rx="2"/>
                <circle cx="12" cy="12" r="4"/>
                <path d="M12 8c2 0 4 2 4 4"/>
                <rect x="8" y="4" width="8" height="2" rx="0.5"/>
            `,
            detailed: `
                <rect x="4" y="6" width="16" height="12" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="4" y="6" width="16" height="12" rx="2"/>
                <circle cx="12" cy="12" r="4.5" fill="currentColor" opacity="0.2"/>
                <circle cx="12" cy="12" r="4"/>
                <path d="M12 8c2.5 0 4.5 2 4.5 4" stroke-width="2" fill="none"/>
                <rect x="8" y="4" width="8" height="2" rx="0.5" fill="currentColor" opacity="0.4"/>
            `,
            glyph: `
                <rect x="4" y="6" width="16" height="12" rx="2" fill="currentColor"/>
                <circle cx="12" cy="12" r="4" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'turbografx': {
            wireframe: `
                <rect x="3" y="9" width="18" height="6" rx="1"/>
                <rect x="5" y="10" width="4" height="4" rx="0.5"/>
                <path d="M11 11h6M11 13h4"/>
                <rect x="17" y="10" width="2" height="4" rx="0.5"/>
            `,
            detailed: `
                <rect x="3" y="9" width="18" height="6" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="3" y="9" width="18" height="6" rx="1"/>
                <rect x="5" y="10" width="4" height="4" rx="0.5" fill="currentColor" opacity="0.35"/>
                <rect x="5" y="10" width="4" height="4" rx="0.5"/>
                <path d="M11 11h6M11 13h4" opacity="0.5"/>
                <rect x="17" y="10" width="2" height="4" rx="0.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="3" y="9" width="18" height="6" rx="1" fill="currentColor"/>
                <rect x="5" y="10" width="4" height="4" rx="0.5" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'atari': {
            wireframe: `
                <rect x="3" y="10" width="18" height="6" rx="1"/>
                <path d="M5 10v-2h14v2"/>
                <rect x="5" y="11" width="5" height="4"/>
                <circle cx="16" cy="13" r="1.5"/>
                <path d="M5 8h3M16 8h3"/>
            `,
            detailed: `
                <rect x="3" y="10" width="18" height="6" rx="1" fill="currentColor" opacity="0.25"/>
                <rect x="3" y="10" width="18" height="6" rx="1"/>
                <path d="M5 10v-2h14v2" fill="currentColor" opacity="0.35"/>
                <path d="M5 10v-2h14v2"/>
                <rect x="5" y="11" width="5" height="4" fill="currentColor" opacity="0.2"/>
                <rect x="5" y="11" width="5" height="4"/>
                <circle cx="16" cy="13" r="2" fill="currentColor" opacity="0.3"/>
                <circle cx="16" cy="13" r="1.5"/>
                <path d="M5 8h3M16 8h3" stroke-width="2" opacity="0.6"/>
            `,
            glyph: `
                <rect x="3" y="10" width="18" height="6" rx="1" fill="currentColor"/>
                <path d="M5 10v-2h14v2" fill="currentColor"/>
            `
        },

        // === PRO AV (5) ===
        'camera': {
            wireframe: `
                <rect x="2" y="6" width="16" height="12" rx="2"/>
                <circle cx="10" cy="12" r="4"/>
                <circle cx="10" cy="12" r="2"/>
                <path d="M18 9l4-2v10l-4-2z"/>
                <rect x="3" y="7" width="3" height="2" rx="0.5"/>
            `,
            detailed: `
                <rect x="2" y="6" width="16" height="12" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="6" width="16" height="12" rx="2"/>
                <circle cx="10" cy="12" r="4.5" fill="currentColor" opacity="0.25"/>
                <circle cx="10" cy="12" r="4"/>
                <circle cx="10" cy="12" r="2.5" fill="currentColor" opacity="0.3"/>
                <circle cx="10" cy="12" r="2"/>
                <path d="M18 9l4-2v10l-4-2z" fill="currentColor" opacity="0.3"/>
                <path d="M18 9l4-2v10l-4-2z"/>
                <rect x="3" y="7" width="3" height="2" rx="0.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="2" y="6" width="16" height="12" rx="2" fill="currentColor"/>
                <circle cx="10" cy="12" r="4" fill="rgba(0,0,0,0.3)"/>
                <path d="M18 9l4-2v10l-4-2z" fill="currentColor"/>
            `
        },
        'capture-card': {
            wireframe: `
                <rect x="3" y="6" width="18" height="12" rx="2"/>
                <rect x="5" y="8" width="6" height="4" rx="1"/>
                <path d="M13 10h5M13 12h3"/>
                <circle cx="17" cy="14" r="1"/>
                <path d="M6 14h4"/>
            `,
            detailed: `
                <rect x="3" y="6" width="18" height="12" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="3" y="6" width="18" height="12" rx="2"/>
                <rect x="5" y="8" width="6" height="4" rx="1" fill="currentColor" opacity="0.35"/>
                <rect x="5" y="8" width="6" height="4" rx="1"/>
                <path d="M13 10h5M13 12h3" opacity="0.5"/>
                <circle cx="17" cy="14" r="1.3" fill="currentColor" opacity="0.6"/>
                <path d="M6 14h4" stroke-width="2"/>
            `,
            glyph: `
                <rect x="3" y="6" width="18" height="12" rx="2" fill="currentColor"/>
                <rect x="5" y="8" width="6" height="4" rx="1" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'video-switcher': {
            wireframe: `
                <rect x="2" y="5" width="20" height="14" rx="1"/>
                <rect x="4" y="7" width="3" height="3" rx="0.5"/>
                <rect x="8" y="7" width="3" height="3" rx="0.5"/>
                <rect x="12" y="7" width="3" height="3" rx="0.5"/>
                <rect x="16" y="7" width="4" height="3" rx="0.5"/>
                <path d="M4 13h16M4 16h16"/>
            `,
            detailed: `
                <rect x="2" y="5" width="20" height="14" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="5" width="20" height="14" rx="1"/>
                <rect x="4" y="7" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.4"/>
                <rect x="8" y="7" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.4"/>
                <rect x="12" y="7" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.4"/>
                <rect x="16" y="7" width="4" height="3" rx="0.5" fill="currentColor" opacity="0.6"/>
                <path d="M4 13h16M4 16h16" opacity="0.4"/>
            `,
            glyph: `
                <rect x="2" y="5" width="20" height="14" rx="1" fill="currentColor"/>
                <rect x="4" y="7" width="3" height="3" rx="0.5" fill="rgba(0,0,0,0.3)"/>
                <rect x="8" y="7" width="3" height="3" rx="0.5" fill="rgba(0,0,0,0.3)"/>
                <rect x="12" y="7" width="3" height="3" rx="0.5" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'hdmi-extender': {
            wireframe: `
                <rect x="2" y="8" width="8" height="8" rx="1"/>
                <rect x="14" y="8" width="8" height="8" rx="1"/>
                <path d="M10 12h4" stroke-dasharray="2 1"/>
                <path d="M4 11h4M4 13h4"/>
                <path d="M16 11h4M16 13h4"/>
            `,
            detailed: `
                <rect x="2" y="8" width="8" height="8" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="8" width="8" height="8" rx="1"/>
                <rect x="14" y="8" width="8" height="8" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="14" y="8" width="8" height="8" rx="1"/>
                <path d="M10 12h4" stroke-dasharray="2 1" stroke-width="2"/>
                <path d="M4 11h4M4 13h4" opacity="0.5"/>
                <path d="M16 11h4M16 13h4" opacity="0.5"/>
                <circle cx="6" cy="12" r="0.8" fill="currentColor"/>
                <circle cx="18" cy="12" r="0.8" fill="currentColor"/>
            `,
            glyph: `
                <rect x="2" y="8" width="8" height="8" rx="1" fill="currentColor"/>
                <rect x="14" y="8" width="8" height="8" rx="1" fill="currentColor"/>
                <path d="M10 12h4" stroke="currentColor" stroke-width="2" stroke-dasharray="2 1"/>
            `
        },
        'ndi-encoder': {
            wireframe: `
                <rect x="3" y="7" width="18" height="10" rx="1"/>
                <circle cx="7" cy="12" r="2"/>
                <path d="M11 10h8M11 12h6M11 14h4"/>
                <rect x="17" y="9" width="2" height="6" rx="0.5"/>
            `,
            detailed: `
                <rect x="3" y="7" width="18" height="10" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="3" y="7" width="18" height="10" rx="1"/>
                <circle cx="7" cy="12" r="2.5" fill="currentColor" opacity="0.3"/>
                <circle cx="7" cy="12" r="2"/>
                <path d="M11 10h8M11 12h6M11 14h4" opacity="0.5"/>
                <rect x="17" y="9" width="2" height="6" rx="0.5" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="3" y="7" width="18" height="10" rx="1" fill="currentColor"/>
                <circle cx="7" cy="12" r="2" fill="rgba(0,0,0,0.3)"/>
            `
        },

        // === STREAMING EXPANSION (2) ===
        'shield-tv': {
            wireframe: `
                <path d="M12 2L4 6v6c0 5.5 3.5 10 8 12 4.5-2 8-6.5 8-12V6l-8-4z"/>
                <path d="M9 10l2 2 4-4"/>
            `,
            detailed: `
                <path d="M12 2L4 6v6c0 5.5 3.5 10 8 12 4.5-2 8-6.5 8-12V6l-8-4z" fill="currentColor" opacity="0.2"/>
                <path d="M12 2L4 6v6c0 5.5 3.5 10 8 12 4.5-2 8-6.5 8-12V6l-8-4z"/>
                <path d="M9 10l2 2 4-4" stroke-width="2"/>
                <path d="M12 4L6 7v5" opacity="0.3"/>
            `,
            glyph: `
                <path d="M12 2L4 6v6c0 5.5 3.5 10 8 12 4.5-2 8-6.5 8-12V6l-8-4z" fill="currentColor"/>
                <path d="M9 10l2 2 4-4" stroke="rgba(0,0,0,0.4)" stroke-width="2" fill="none"/>
            `
        },
        'android-box': {
            wireframe: `
                <rect x="3" y="6" width="18" height="12" rx="2"/>
                <circle cx="8" cy="10" r="1"/>
                <circle cx="16" cy="10" r="1"/>
                <path d="M8 14c0 1 2 2 4 2s4-1 4-2"/>
                <path d="M6 4l2 2M18 4l-2 2"/>
            `,
            detailed: `
                <rect x="3" y="6" width="18" height="12" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="3" y="6" width="18" height="12" rx="2"/>
                <circle cx="8" cy="10" r="1.3" fill="currentColor" opacity="0.5"/>
                <circle cx="16" cy="10" r="1.3" fill="currentColor" opacity="0.5"/>
                <path d="M8 14c0 1 2 2 4 2s4-1 4-2"/>
                <path d="M6 4l2 2M18 4l-2 2" stroke-width="2"/>
            `,
            glyph: `
                <rect x="3" y="6" width="18" height="12" rx="2" fill="currentColor"/>
                <circle cx="8" cy="10" r="1" fill="rgba(0,0,0,0.3)"/>
                <circle cx="16" cy="10" r="1" fill="rgba(0,0,0,0.3)"/>
            `
        },

        // === DISPLAY EXPANSION (3) ===
        'ultrawide-monitor': {
            wireframe: `
                <rect x="1" y="5" width="22" height="10" rx="1"/>
                <rect x="2" y="6" width="20" height="8"/>
                <path d="M8 18h8"/>
                <path d="M12 15v3"/>
                <rect x="10" y="18" width="4" height="1" rx="0.5"/>
            `,
            detailed: `
                <rect x="1" y="5" width="22" height="10" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="1" y="5" width="22" height="10" rx="1"/>
                <rect x="2" y="6" width="20" height="8" fill="currentColor" opacity="0.1"/>
                <rect x="2" y="6" width="20" height="8"/>
                <path d="M8 18h8"/>
                <path d="M12 15v3"/>
                <rect x="10" y="18" width="4" height="1" rx="0.5" fill="currentColor" opacity="0.4"/>
            `,
            glyph: `
                <rect x="1" y="5" width="22" height="10" rx="1" fill="currentColor"/>
                <rect x="2" y="6" width="20" height="8" fill="rgba(0,0,0,0.2)"/>
                <path d="M12 15v4M8 19h8" stroke="currentColor"/>
            `
        },
        'vr-headset': {
            wireframe: `
                <path d="M4 8h16v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8z"/>
                <path d="M4 8c0-2 2-4 8-4s8 2 8 4"/>
                <circle cx="8" cy="12" r="2.5"/>
                <circle cx="16" cy="12" r="2.5"/>
                <path d="M10.5 12h3"/>
            `,
            detailed: `
                <path d="M4 8h16v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8z" fill="currentColor" opacity="0.2"/>
                <path d="M4 8h16v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8z"/>
                <path d="M4 8c0-2 2-4 8-4s8 2 8 4" fill="currentColor" opacity="0.15"/>
                <path d="M4 8c0-2 2-4 8-4s8 2 8 4"/>
                <circle cx="8" cy="12" r="3" fill="currentColor" opacity="0.3"/>
                <circle cx="8" cy="12" r="2.5"/>
                <circle cx="16" cy="12" r="3" fill="currentColor" opacity="0.3"/>
                <circle cx="16" cy="12" r="2.5"/>
                <path d="M10.5 12h3" stroke-width="2"/>
            `,
            glyph: `
                <path d="M4 8c0-2 2-4 8-4s8 2 8 4v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8z" fill="currentColor"/>
                <circle cx="8" cy="12" r="2.5" fill="rgba(0,0,0,0.4)"/>
                <circle cx="16" cy="12" r="2.5" fill="rgba(0,0,0,0.4)"/>
            `
        },
        'video-wall': {
            wireframe: `
                <rect x="2" y="4" width="9" height="7"/>
                <rect x="13" y="4" width="9" height="7"/>
                <rect x="2" y="13" width="9" height="7"/>
                <rect x="13" y="13" width="9" height="7"/>
            `,
            detailed: `
                <rect x="2" y="4" width="9" height="7" fill="currentColor" opacity="0.15"/>
                <rect x="2" y="4" width="9" height="7"/>
                <rect x="13" y="4" width="9" height="7" fill="currentColor" opacity="0.2"/>
                <rect x="13" y="4" width="9" height="7"/>
                <rect x="2" y="13" width="9" height="7" fill="currentColor" opacity="0.25"/>
                <rect x="2" y="13" width="9" height="7"/>
                <rect x="13" y="13" width="9" height="7" fill="currentColor" opacity="0.1"/>
                <rect x="13" y="13" width="9" height="7"/>
            `,
            glyph: `
                <rect x="2" y="4" width="9" height="7" fill="currentColor"/>
                <rect x="13" y="4" width="9" height="7" fill="currentColor" opacity="0.8"/>
                <rect x="2" y="13" width="9" height="7" fill="currentColor" opacity="0.9"/>
                <rect x="13" y="13" width="9" height="7" fill="currentColor" opacity="0.7"/>
            `
        },

        // === AUDIO EXPANSION (2) ===
        'av-receiver': {
            wireframe: `
                <rect x="2" y="6" width="20" height="12" rx="1"/>
                <rect x="4" y="8" width="5" height="3" rx="0.5"/>
                <path d="M11 9h9M11 11h7"/>
                <circle cx="6" cy="14" r="1.5"/>
                <circle cx="10" cy="14" r="1.5"/>
                <circle cx="14" cy="14" r="1.5"/>
                <circle cx="18" cy="14" r="1.5"/>
            `,
            detailed: `
                <rect x="2" y="6" width="20" height="12" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="2" y="6" width="20" height="12" rx="1"/>
                <rect x="4" y="8" width="5" height="3" rx="0.5" fill="currentColor" opacity="0.4"/>
                <rect x="4" y="8" width="5" height="3" rx="0.5"/>
                <path d="M11 9h9M11 11h7" opacity="0.5"/>
                <circle cx="6" cy="14" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="6" cy="14" r="1.5"/>
                <circle cx="10" cy="14" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="10" cy="14" r="1.5"/>
                <circle cx="14" cy="14" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="14" cy="14" r="1.5"/>
                <circle cx="18" cy="14" r="1.8" fill="currentColor" opacity="0.3"/>
                <circle cx="18" cy="14" r="1.5"/>
            `,
            glyph: `
                <rect x="2" y="6" width="20" height="12" rx="1" fill="currentColor"/>
                <rect x="4" y="8" width="5" height="3" rx="0.5" fill="rgba(0,0,0,0.3)"/>
                <circle cx="6" cy="14" r="1.5" fill="rgba(0,0,0,0.3)"/>
                <circle cx="10" cy="14" r="1.5" fill="rgba(0,0,0,0.3)"/>
                <circle cx="14" cy="14" r="1.5" fill="rgba(0,0,0,0.3)"/>
                <circle cx="18" cy="14" r="1.5" fill="rgba(0,0,0,0.3)"/>
            `
        },
        'speaker-system': {
            wireframe: `
                <rect x="6" y="2" width="12" height="20" rx="2"/>
                <circle cx="12" cy="8" r="3"/>
                <circle cx="12" cy="16" r="4"/>
                <circle cx="12" cy="16" r="1.5"/>
            `,
            detailed: `
                <rect x="6" y="2" width="12" height="20" rx="2" fill="currentColor" opacity="0.2"/>
                <rect x="6" y="2" width="12" height="20" rx="2"/>
                <circle cx="12" cy="8" r="3.5" fill="currentColor" opacity="0.25"/>
                <circle cx="12" cy="8" r="3"/>
                <circle cx="12" cy="16" r="4.5" fill="currentColor" opacity="0.2"/>
                <circle cx="12" cy="16" r="4"/>
                <circle cx="12" cy="16" r="2" fill="currentColor" opacity="0.3"/>
                <circle cx="12" cy="16" r="1.5"/>
            `,
            glyph: `
                <rect x="6" y="2" width="12" height="20" rx="2" fill="currentColor"/>
                <circle cx="12" cy="8" r="3" fill="rgba(0,0,0,0.3)"/>
                <circle cx="12" cy="16" r="4" fill="rgba(0,0,0,0.3)"/>
            `
        },

        // === SERVER/NAS (2) ===
        'nas': {
            wireframe: `
                <rect x="4" y="3" width="16" height="18" rx="1"/>
                <rect x="6" y="5" width="12" height="3"/>
                <rect x="6" y="10" width="12" height="3"/>
                <rect x="6" y="15" width="12" height="3"/>
                <circle cx="16" cy="6.5" r="0.8"/>
                <circle cx="16" cy="11.5" r="0.8"/>
                <circle cx="16" cy="16.5" r="0.8"/>
            `,
            detailed: `
                <rect x="4" y="3" width="16" height="18" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="4" y="3" width="16" height="18" rx="1"/>
                <rect x="6" y="5" width="12" height="3" fill="currentColor" opacity="0.15"/>
                <rect x="6" y="5" width="12" height="3"/>
                <rect x="6" y="10" width="12" height="3" fill="currentColor" opacity="0.15"/>
                <rect x="6" y="10" width="12" height="3"/>
                <rect x="6" y="15" width="12" height="3" fill="currentColor" opacity="0.15"/>
                <rect x="6" y="15" width="12" height="3"/>
                <circle cx="16" cy="6.5" r="1" fill="currentColor" opacity="0.6"/>
                <circle cx="16" cy="11.5" r="1" fill="currentColor" opacity="0.6"/>
                <circle cx="16" cy="16.5" r="1" fill="currentColor" opacity="0.6"/>
            `,
            glyph: `
                <rect x="4" y="3" width="16" height="18" rx="1" fill="currentColor"/>
                <rect x="6" y="5" width="12" height="3" fill="rgba(0,0,0,0.2)"/>
                <rect x="6" y="10" width="12" height="3" fill="rgba(0,0,0,0.2)"/>
                <rect x="6" y="15" width="12" height="3" fill="rgba(0,0,0,0.2)"/>
            `
        },
        'media-server': {
            wireframe: `
                <rect x="3" y="4" width="18" height="16" rx="1"/>
                <rect x="5" y="6" width="14" height="8"/>
                <path d="M5 16h14"/>
                <circle cx="8" cy="18" r="1"/>
                <circle cx="16" cy="18" r="1"/>
                <path d="M10 10l4 2-4 2z"/>
            `,
            detailed: `
                <rect x="3" y="4" width="18" height="16" rx="1" fill="currentColor" opacity="0.2"/>
                <rect x="3" y="4" width="18" height="16" rx="1"/>
                <rect x="5" y="6" width="14" height="8" fill="currentColor" opacity="0.15"/>
                <rect x="5" y="6" width="14" height="8"/>
                <path d="M5 16h14" opacity="0.4"/>
                <circle cx="8" cy="18" r="1" fill="currentColor" opacity="0.5"/>
                <circle cx="16" cy="18" r="1" fill="currentColor" opacity="0.5"/>
                <path d="M10 10l4 2-4 2z" fill="currentColor" opacity="0.5"/>
            `,
            glyph: `
                <rect x="3" y="4" width="18" height="16" rx="1" fill="currentColor"/>
                <rect x="5" y="6" width="14" height="8" fill="rgba(0,0,0,0.2)"/>
                <path d="M10 10l4 2-4 2z" fill="rgba(0,0,0,0.4)"/>
            `
        }
    };

    /**
     * Icon metadata for search and categorization
     */
    static metadata = {
        // Gaming
        'playstation': { label: 'PlayStation', category: 'gaming', keywords: ['ps5', 'ps4', 'sony', 'console', 'gaming'] },
        'xbox': { label: 'Xbox', category: 'gaming', keywords: ['microsoft', 'series x', 'series s', 'console', 'gaming'] },
        'nintendo-switch': { label: 'Nintendo Switch', category: 'gaming', keywords: ['nintendo', 'switch', 'handheld', 'console'] },
        'steam-deck': { label: 'Steam Deck', category: 'gaming', keywords: ['valve', 'steam', 'handheld', 'pc gaming'] },
        
        // Retro Gaming
        'nes': { label: 'NES', category: 'retro', keywords: ['nintendo', 'nes', 'famicom', '8-bit', 'classic', 'retro'] },
        'snes': { label: 'Super Nintendo', category: 'retro', keywords: ['snes', 'super nintendo', 'super famicom', '16-bit', 'retro'] },
        'n64': { label: 'Nintendo 64', category: 'retro', keywords: ['n64', 'nintendo 64', '64-bit', 'retro'] },
        'gamecube': { label: 'GameCube', category: 'retro', keywords: ['gamecube', 'nintendo', 'gc', 'retro'] },
        'wii': { label: 'Wii', category: 'retro', keywords: ['wii', 'nintendo', 'motion', 'retro'] },
        'genesis': { label: 'Sega Genesis', category: 'retro', keywords: ['genesis', 'mega drive', 'sega', '16-bit', 'retro'] },
        'saturn': { label: 'Sega Saturn', category: 'retro', keywords: ['saturn', 'sega', 'retro'] },
        'dreamcast': { label: 'Dreamcast', category: 'retro', keywords: ['dreamcast', 'sega', 'dc', 'retro'] },
        'turbografx': { label: 'TurboGrafx-16', category: 'retro', keywords: ['turbografx', 'pc engine', 'nec', 'retro'] },
        'atari': { label: 'Atari 2600', category: 'retro', keywords: ['atari', '2600', 'vcs', 'retro', 'classic'] },
        
        // Streaming
        'apple-tv': { label: 'Apple TV', category: 'streaming', keywords: ['apple', 'streaming', 'airplay', 'tvos'] },
        'roku': { label: 'Roku', category: 'streaming', keywords: ['roku', 'streaming', 'stick'] },
        'fire-tv': { label: 'Fire TV', category: 'streaming', keywords: ['amazon', 'fire', 'alexa', 'streaming'] },
        'chromecast': { label: 'Chromecast', category: 'streaming', keywords: ['google', 'cast', 'streaming'] },
        'shield-tv': { label: 'NVIDIA Shield', category: 'streaming', keywords: ['nvidia', 'shield', 'android', 'streaming', 'gaming'] },
        'android-box': { label: 'Android TV Box', category: 'streaming', keywords: ['android', 'tv box', 'streaming', 'kodi'] },
        
        // Computer
        'desktop-pc': { label: 'Desktop PC', category: 'computer', keywords: ['pc', 'computer', 'tower', 'gaming pc', 'workstation'] },
        'laptop': { label: 'Laptop', category: 'computer', keywords: ['notebook', 'macbook', 'portable', 'computer'] },
        'mac-mini': { label: 'Mac Mini', category: 'computer', keywords: ['apple', 'mac', 'mini', 'computer'] },
        
        // Display
        'television': { label: 'Television', category: 'display', keywords: ['tv', 'screen', 'display', 'smart tv', 'oled', 'qled'] },
        'projector': { label: 'Projector', category: 'display', keywords: ['projector', 'theater', 'cinema', 'screen'] },
        'monitor': { label: 'Monitor', category: 'display', keywords: ['display', 'screen', 'computer monitor'] },
        'ultrawide-monitor': { label: 'Ultrawide Monitor', category: 'display', keywords: ['ultrawide', '21:9', 'curved', 'monitor', 'display'] },
        'vr-headset': { label: 'VR Headset', category: 'display', keywords: ['vr', 'virtual reality', 'headset', 'oculus', 'quest', 'hmd'] },
        'video-wall': { label: 'Video Wall', category: 'display', keywords: ['video wall', 'signage', 'multi-display', 'commercial'] },
        
        // Media
        'blu-ray': { label: 'Blu-ray Player', category: 'media', keywords: ['bluray', 'dvd', 'disc', 'player', '4k'] },
        'cable-box': { label: 'Cable Box', category: 'media', keywords: ['cable', 'satellite', 'dvr', 'set-top', 'receiver'] },
        'soundbar': { label: 'Soundbar', category: 'media', keywords: ['audio', 'speaker', 'sound', 'home theater'] },
        
        // Audio
        'av-receiver': { label: 'AV Receiver', category: 'audio', keywords: ['receiver', 'avr', 'amplifier', 'surround', 'home theater'] },
        'speaker-system': { label: 'Speaker System', category: 'audio', keywords: ['speakers', 'audio', 'stereo', 'floor standing', 'bookshelf'] },
        
        // Pro AV
        'camera': { label: 'Camera', category: 'pro-av', keywords: ['camera', 'dslr', 'camcorder', 'video', 'streaming'] },
        'capture-card': { label: 'Capture Card', category: 'pro-av', keywords: ['capture', 'elgato', 'avermedia', 'recording', 'streaming'] },
        'video-switcher': { label: 'Video Switcher', category: 'pro-av', keywords: ['switcher', 'atem', 'mixer', 'production', 'broadcast'] },
        'hdmi-extender': { label: 'HDMI Extender', category: 'pro-av', keywords: ['extender', 'hdbaset', 'balun', 'over ip', 'cat6'] },
        'ndi-encoder': { label: 'NDI Encoder', category: 'pro-av', keywords: ['ndi', 'encoder', 'streaming', 'ip video', 'broadcast'] },
        
        // Server/NAS
        'nas': { label: 'NAS', category: 'server', keywords: ['nas', 'synology', 'qnap', 'storage', 'network'] },
        'media-server': { label: 'Media Server', category: 'server', keywords: ['server', 'plex', 'jellyfin', 'htpc', 'media'] },
        
        // Generic
        'generic-input': { label: 'Generic Input', category: 'generic', keywords: ['input', 'source', 'device'] },
        'generic-output': { label: 'Generic Output', category: 'generic', keywords: ['output', 'display', 'destination'] },
        'generic-device': { label: 'Generic Device', category: 'generic', keywords: ['device', 'unknown', 'other'] },
        
        // === NEW EXTERNAL ICONS ===
        
        // Gaming Consoles - Modern (External)
        'playstation-5': { label: 'PlayStation 5', category: 'gaming', keywords: ['ps5', 'playstation', 'sony', 'console', 'gaming', 'next gen'] },
        'xbox-series-x': { label: 'Xbox Series X', category: 'gaming', keywords: ['xbox', 'series x', 'microsoft', 'console', 'gaming', 'next gen'] },
        'nintendo-switch-ext': { label: 'Nintendo Switch', category: 'gaming', keywords: ['switch', 'nintendo', 'handheld', 'console', 'gaming'] },
        'steam-deck-ext': { label: 'Steam Deck', category: 'gaming', keywords: ['steam', 'deck', 'valve', 'handheld', 'pc gaming'] },
        'wii-ext': { label: 'Nintendo Wii', category: 'retro', keywords: ['wii', 'nintendo', 'motion', 'console'] },
        
        // Gaming Consoles - Retro (External)
        'nes-ext': { label: 'NES', category: 'retro', keywords: ['nes', 'nintendo', 'famicom', '8-bit', 'classic'] },
        'snes-ext': { label: 'Super Nintendo', category: 'retro', keywords: ['snes', 'super nintendo', '16-bit', 'classic'] },
        'n64-ext': { label: 'Nintendo 64', category: 'retro', keywords: ['n64', 'nintendo 64', '3d', 'retro'] },
        'gamecube-ext': { label: 'GameCube', category: 'retro', keywords: ['gamecube', 'nintendo', 'mini disc'] },
        'sega-genesis': { label: 'Sega Genesis', category: 'retro', keywords: ['genesis', 'sega', 'mega drive', '16-bit'] },
        'dreamcast-ext': { label: 'Dreamcast', category: 'retro', keywords: ['dreamcast', 'sega', 'vmu', 'retro'] },
        'atari-2600': { label: 'Atari 2600', category: 'retro', keywords: ['atari', '2600', 'vcs', 'classic', 'woodgrain'] },
        'ps2': { label: 'PlayStation 2', category: 'retro', keywords: ['ps2', 'playstation 2', 'sony', 'dvd'] },
        'ps3': { label: 'PlayStation 3', category: 'retro', keywords: ['ps3', 'playstation 3', 'sony', 'blu-ray'] },
        'ps4': { label: 'PlayStation 4', category: 'gaming', keywords: ['ps4', 'playstation 4', 'sony', 'console'] },
        'xbox-360': { label: 'Xbox 360', category: 'retro', keywords: ['xbox 360', 'microsoft', 'kinect'] },
        'xbox-one': { label: 'Xbox One', category: 'gaming', keywords: ['xbox one', 'microsoft', 'console'] },
        
        // Streaming Devices (External)
        'apple-tv-ext': { label: 'Apple TV', category: 'streaming', keywords: ['apple tv', 'airplay', 'tvos', 'streaming'] },
        'roku-ext': { label: 'Roku Stick', category: 'streaming', keywords: ['roku', 'stick', 'streaming'] },
        'fire-tv-ext': { label: 'Fire TV', category: 'streaming', keywords: ['fire tv', 'amazon', 'alexa', 'streaming'] },
        'chromecast-ext': { label: 'Chromecast', category: 'streaming', keywords: ['chromecast', 'google', 'cast'] },
        'nvidia-shield': { label: 'NVIDIA Shield', category: 'streaming', keywords: ['shield', 'nvidia', 'android tv', 'gaming'] },
        
        // Computer Devices (External)
        'gaming-pc': { label: 'Gaming PC', category: 'computer', keywords: ['gaming pc', 'desktop', 'tower', 'rgb'] },
        'laptop-ext': { label: 'Laptop', category: 'computer', keywords: ['laptop', 'notebook', 'portable'] },
        'mac-mini-ext': { label: 'Mac Mini', category: 'computer', keywords: ['mac mini', 'apple', 'compact'] },
        'htpc': { label: 'Home Theater PC', category: 'computer', keywords: ['htpc', 'media pc', 'kodi', 'plex'] },
        
        // Display Devices (External)
        'television-ext': { label: 'Television', category: 'display', keywords: ['tv', 'smart tv', 'oled', 'qled'] },
        'projector-ext': { label: 'Projector', category: 'display', keywords: ['projector', 'theater', 'screen'] },
        'monitor-ext': { label: 'Monitor', category: 'display', keywords: ['monitor', 'display', 'screen'] },
        'curved-tv': { label: 'Curved TV', category: 'display', keywords: ['curved', 'tv', 'immersive'] },
        
        // Audio Equipment (External)
        'soundbar-ext': { label: 'Soundbar', category: 'audio', keywords: ['soundbar', 'dolby', 'atmos'] },
        'av-receiver-ext': { label: 'AV Receiver', category: 'audio', keywords: ['receiver', 'avr', 'surround'] },
        'speaker': { label: 'Bookshelf Speaker', category: 'audio', keywords: ['speaker', 'bookshelf', 'stereo'] },
        'subwoofer': { label: 'Subwoofer', category: 'audio', keywords: ['subwoofer', 'bass', 'woofer'] },
        'headphones': { label: 'Headphones', category: 'audio', keywords: ['headphones', 'headset', 'audio'] },
        'turntable': { label: 'Turntable', category: 'audio', keywords: ['turntable', 'vinyl', 'record player'] },
        
        // Pro AV Equipment (External)
        'bluray-player': { label: 'Blu-ray Player', category: 'media', keywords: ['blu-ray', 'bluray', '4k', 'disc'] },
        'cable-box-ext': { label: 'Cable Box', category: 'media', keywords: ['cable', 'satellite', 'dvr'] },
        'hdmi-switch': { label: 'HDMI Switch', category: 'pro-av', keywords: ['hdmi', 'switch', 'selector', 'matrix'] },
        'server-rack': { label: 'Server/NAS', category: 'server', keywords: ['server', 'nas', 'rack', 'storage'] },
        'security-camera': { label: 'Security Camera', category: 'pro-av', keywords: ['camera', 'security', 'surveillance', 'nvr'] },
        
        // Scene Icons (External)
        'movie-scene': { label: 'Movie Night', category: 'scenes', keywords: ['movie', 'cinema', 'film', 'theater'] },
        'gaming-scene': { label: 'Gaming Session', category: 'scenes', keywords: ['gaming', 'play', 'controller'] },
        'sports-scene': { label: 'Sports Viewing', category: 'scenes', keywords: ['sports', 'game', 'stadium', 'live'] },
        'music-scene': { label: 'Music Listening', category: 'scenes', keywords: ['music', 'audio', 'listening', 'hi-fi'] },
        
        // Room Icons (External)
        'living-room': { label: 'Living Room', category: 'rooms', keywords: ['living room', 'family room', 'main'] },
        'bedroom': { label: 'Bedroom', category: 'rooms', keywords: ['bedroom', 'master', 'sleep'] },
        'home-office': { label: 'Home Office', category: 'rooms', keywords: ['office', 'work', 'desk', 'study'] },
        'game-room': { label: 'Game Room', category: 'rooms', keywords: ['game room', 'den', 'entertainment'] },
        
        // Controllers (External)
        'xbox-controller': { label: 'Xbox Controller', category: 'controllers', keywords: ['xbox', 'controller', 'gamepad'] },
        'ps-controller': { label: 'PlayStation Controller', category: 'controllers', keywords: ['playstation', 'dualsense', 'controller', 'gamepad'] },
        
        // Utility Icons (External)
        'generic-input-ext': { label: 'Generic Input', category: 'generic', keywords: ['input', 'source'] },
        'generic-output-ext': { label: 'Generic Output', category: 'generic', keywords: ['output', 'destination'] },
        'generic-device-ext': { label: 'Unknown Device', category: 'generic', keywords: ['unknown', 'device'] },
        'settings-gear': { label: 'Settings', category: 'utility', keywords: ['settings', 'config', 'gear', 'options'] },
        'tablet': { label: 'Tablet', category: 'computer', keywords: ['tablet', 'ipad', 'android tablet', 'mobile'] }
    };

    /**
     * Context-based style recommendations
     */
    static contextStyles = {
        'card': 'detailed',        // Main routing card (48-64px)
        'wizard': 'detailed',      // Wizard input/output selector (32-40px)
        'dropdown': 'wireframe',   // Dropdown menu item (20-24px)
        'status': 'glyph',         // Status tray (16-20px)
        'breadcrumb': 'glyph',     // Breadcrumb/reference (14-16px)
        'picker': 'detailed'       // Icon picker modal
    };

    /**
     * Get SVG markup for an icon
     * @param {string} iconId - Icon identifier
     * @param {number} size - Icon size in pixels (default: 24)
     * @param {string} className - Optional CSS class
     * @param {string} style - Style variant: 'wireframe', 'detailed', or 'glyph' (default: 'detailed')
     * @returns {string} SVG markup
     */
    static getSvg(iconId, size = 24, className = '', style = 'detailed') {
        const icon = this.icons[iconId] || this.icons['generic-device'];
        const paths = typeof icon === 'object' ? (icon[style] || icon.detailed || icon.wireframe) : icon;
        const cls = className ? ` class="${className}"` : '';
        
        return `<svg viewBox="0 0 24 24" width="${size}" height="${size}"${cls} 
                     fill="none" stroke="currentColor" stroke-width="1.5" 
                     stroke-linecap="round" stroke-linejoin="round">
                    ${paths}
                </svg>`;
    }

    /**
     * Get SVG for a specific context (auto-selects appropriate style)
     * @param {string} iconId - Icon identifier
     * @param {string} context - Context: 'card', 'wizard', 'dropdown', 'status', 'breadcrumb', 'picker'
     * @param {number} size - Optional size override
     * @returns {string} SVG markup
     */
    static getSvgForContext(iconId, context, size = null) {
        const style = this.contextStyles[context] || 'detailed';
        const defaultSizes = {
            'card': 48,
            'wizard': 36,
            'dropdown': 22,
            'status': 18,
            'breadcrumb': 14,
            'picker': 28
        };
        const finalSize = size || defaultSizes[context] || 24;
        return this.getSvg(iconId, finalSize, '', style);
    }

    /**
     * Check if an icon is an external SVG file
     * @param {string} iconId - Icon identifier
     * @returns {boolean} True if icon is external
     */
    static isExternalIcon(iconId) {
        return iconId in this.externalIcons;
    }

    /**
     * Get the URL for an external SVG icon
     * @param {string} iconId - Icon identifier
     * @returns {string|null} URL to SVG file or null if not external
     */
    static getExternalSvgUrl(iconId) {
        const filename = this.externalIcons[iconId];
        if (!filename) return null;
        return `${this.SVG_BASE_PATH}${filename}.svg`;
    }

    /**
     * Get an img element for an external SVG icon
     * Falls back to inline SVG if icon is not external
     * @param {string} iconId - Icon identifier
     * @param {number} size - Icon size in pixels (default: 24)
     * @param {string} className - Optional CSS class
     * @returns {HTMLElement} img element for external icons, or span with inline SVG
     */
    static getIconElement(iconId, size = 24, className = '') {
        const url = this.getExternalSvgUrl(iconId);
        
        if (url) {
            // External SVG - return img element
            const img = document.createElement('img');
            img.src = url;
            img.width = size;
            img.height = size;
            img.alt = this.getMeta(iconId)?.label || iconId;
            if (className) img.className = className;
            img.style.cssText = 'display: inline-block; vertical-align: middle;';
            return img;
        } else {
            // Inline icon - return span with SVG
            const span = document.createElement('span');
            span.innerHTML = this.getSvg(iconId, size, className);
            if (className) span.className = className;
            return span.firstChild || span;
        }
    }

    /**
     * Get icon HTML for use in templates (supports both inline and external)
     * For external icons, returns an img tag; for inline, returns SVG markup
     * @param {string} iconId - Icon identifier
     * @param {number} size - Icon size in pixels (default: 24)
     * @param {string} className - Optional CSS class
     * @param {string} style - Style variant for inline icons (default: 'detailed')
     * @returns {string} HTML markup (img tag or SVG)
     */
    static getIconHtml(iconId, size = 24, className = '', style = 'detailed') {
        // Always use inline icons for consistent quality
        // External SVGs are disabled due to quality issues
        return this.getSvg(iconId, size, className, style);
    }

    /**
     * Get all external icon IDs
     * @returns {string[]} Array of external icon IDs
     */
    static getExternalIconIds() {
        return Object.keys(this.externalIcons);
    }

    /**
     * Register a custom external icon (for user uploads or external sync)
     * @param {string} iconId - Unique icon identifier
     * @param {string} filename - Filename without extension (must be in SVG_BASE_PATH)
     * @param {object} meta - Optional metadata {label, category, keywords}
     */
    static registerExternalIcon(iconId, filename, meta = null) {
        this.externalIcons[iconId] = filename;
        if (meta) {
            this.metadata[iconId] = {
                label: meta.label || iconId,
                category: meta.category || 'custom',
                keywords: meta.keywords || []
            };
        }
    }

    /**
     * Get icon metadata
     */
    static getMeta(iconId) {
        return this.metadata[iconId] || { label: 'Unknown', category: 'generic', keywords: [] };
    }

    /**
     * Auto-suggest icon based on device name
     */
    static suggestIcon(deviceName, isOutput = false) {
        const name = deviceName.toLowerCase();
        
        // Gaming consoles (modern)
        if (name.includes('playstation') || name.includes('ps5') || name.includes('ps4') || name.includes('ps3')) return 'playstation';
        if (name.includes('xbox')) return 'xbox';
        if (name.includes('switch')) return 'nintendo-switch';
        if (name.includes('steam') || name.includes('deck')) return 'steam-deck';
        
        // Retro gaming consoles
        if (name.includes('nes') || name.includes('famicom')) return 'nes';
        if (name.includes('snes') || name.includes('super nintendo') || name.includes('super famicom')) return 'snes';
        if (name.includes('n64') || name.includes('nintendo 64')) return 'n64';
        if (name.includes('gamecube') || name.includes('game cube')) return 'gamecube';
        if (name.includes('wii')) return 'wii';
        if (name.includes('genesis') || name.includes('mega drive')) return 'genesis';
        if (name.includes('saturn')) return 'saturn';
        if (name.includes('dreamcast')) return 'dreamcast';
        if (name.includes('turbografx') || name.includes('pc engine')) return 'turbografx';
        if (name.includes('atari')) return 'atari';
        if (name.includes('nintendo')) return 'nintendo-switch'; // fallback for generic nintendo
        
        // Streaming devices
        if (name.includes('apple tv') || name.includes('appletv')) return 'apple-tv';
        if (name.includes('roku')) return 'roku';
        if (name.includes('fire') || name.includes('firestick')) return 'fire-tv';
        if (name.includes('chromecast') || name.includes('google tv')) return 'chromecast';
        if (name.includes('shield') || name.includes('nvidia')) return 'shield-tv';
        if (name.includes('android') && (name.includes('box') || name.includes('tv'))) return 'android-box';
        
        // Computers
        if (name.includes('pc') || name.includes('computer') || name.includes('desktop')) return 'desktop-pc';
        if (name.includes('laptop') || name.includes('macbook') || name.includes('notebook')) return 'laptop';
        if (name.includes('mac mini') || name.includes('mini')) return 'mac-mini';
        
        // Displays
        if (name.includes('ultrawide') || name.includes('21:9')) return 'ultrawide-monitor';
        if (name.includes('vr') || name.includes('headset') || name.includes('oculus') || name.includes('quest')) return 'vr-headset';
        if (name.includes('video wall') || name.includes('signage')) return 'video-wall';
        if (name.includes('tv') || name.includes('television')) return 'television';
        if (name.includes('projector') || name.includes('theater') || name.includes('cinema')) return 'projector';
        if (name.includes('monitor') || name.includes('display')) return 'monitor';
        
        // Audio
        if (name.includes('receiver') || name.includes('avr') || name.includes('amplifier')) return 'av-receiver';
        if (name.includes('speaker') && !name.includes('soundbar')) return 'speaker-system';
        if (name.includes('soundbar')) return 'soundbar';
        
        // Pro AV
        if (name.includes('camera') || name.includes('dslr') || name.includes('camcorder')) return 'camera';
        if (name.includes('capture') || name.includes('elgato') || name.includes('avermedia')) return 'capture-card';
        if (name.includes('switcher') || name.includes('atem') || name.includes('mixer')) return 'video-switcher';
        if (name.includes('extender') || name.includes('hdbaset') || name.includes('balun')) return 'hdmi-extender';
        if (name.includes('ndi') || name.includes('encoder')) return 'ndi-encoder';
        
        // Server/NAS
        if (name.includes('nas') || name.includes('synology') || name.includes('qnap')) return 'nas';
        if (name.includes('server') || name.includes('plex') || name.includes('jellyfin') || name.includes('htpc')) return 'media-server';
        
        // Media
        if (name.includes('blu-ray') || name.includes('bluray') || name.includes('dvd') || name.includes('disc')) return 'blu-ray';
        if (name.includes('cable') || name.includes('satellite') || name.includes('dvr')) return 'cable-box';
        
        // Default based on type
        return isOutput ? 'generic-output' : 'generic-input';
    }

    /**
     * Search icons by query
     */
    static search(query) {
        // Only search inline icons (external icons disabled)
        const inlineIds = Object.keys(this.icons);
        if (!query) return inlineIds;
        
        const q = query.toLowerCase();
        return Object.entries(this.metadata)
            .filter(([id, meta]) => {
                // Only include inline icons
                if (!(id in this.icons)) return false;
                return id.includes(q) || 
                       meta.label.toLowerCase().includes(q) ||
                       meta.keywords.some(k => k.includes(q));
            })
            .map(([id]) => id);
    }

    /**
     * Get icons by category (includes both inline and external icons)
     */
    static getByCategory(category) {
        if (!category || category === 'all') return this.getAllIcons();
        
        // Only return inline icons (external icons disabled)
        return Object.entries(this.metadata)
            .filter(([id, meta]) => {
                // Only include inline icons
                if (!(id in this.icons)) return false;
                return meta.category === category;
            })
            .map(([id]) => id);
    }

    /**
     * Get all available categories
     */
    static getCategories() {
        return ['all', 'gaming', 'retro', 'streaming', 'computer', 'display', 'audio', 'media', 'pro-av', 'server', 'scenes', 'rooms', 'controllers', 'utility', 'generic'];
    }

    /**
     * Get all icon IDs (both inline and external)
     */
    static getAllIcons() {
        // Only return inline icons (external icons disabled for quality reasons)
        return Object.keys(this.icons);
    }

    /**
     * Check if icon exists (inline or external)
     */
    static isValid(iconId) {
        return iconId in this.icons || iconId in this.externalIcons;
    }

    /**
     * Get icon IDs (alias for getAllIcons)
     */
    static getIconIds() {
        return this.getAllIcons();
    }
}

// Export for use
window.IconLibrary = IconLibrary;

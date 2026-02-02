/**
 * OREI Matrix Control - Application Constants
 * Centralized constants to eliminate magic numbers and improve maintainability
 */

const Constants = {
    // Connection settings - SET YOUR MATRIX IP HERE
    CONNECTION: {
        // Default matrix IP address (can be overridden via UI settings)
        MATRIX_HOST: 'http://192.168.0.100',
        STORAGE_KEY: 'orei_matrix_host',  // localStorage key for user override
        WS_RECONNECT_ATTEMPTS: 10,
        WS_RECONNECT_DELAY: 2000
    },
    
    // Matrix hardware limits
    MATRIX: {
        INPUT_COUNT: 8,
        OUTPUT_COUNT: 8,
        PRESET_COUNT: 8,
        MIN_PORT: 1,
        MAX_PORT: 8
    },
    
    // UI timing (milliseconds)
    TIMING: {
        DEBOUNCE_INPUT: 300,       // Input field debounce
        DEBOUNCE_RESIZE: 100,      // Window resize debounce
        TOAST_DURATION: 3000,      // Toast notification duration
        TOAST_DURATION_LONG: 5000, // Long toast duration
        POLLING_INTERVAL: 5000,    // Status polling interval
        RECONNECT_DELAY: 2000,     // WebSocket reconnect delay
        ANIMATION_DURATION: 200,   // CSS animation duration
        LOADING_MIN_DISPLAY: 500   // Minimum loading indicator display
    },
    
    // Breakpoints (match responsive.css)
    BREAKPOINTS: {
        MOBILE: 480,
        TABLET: 768,
        DESKTOP: 1024,
        LARGE_DESKTOP: 1200
    },
    
    // LocalStorage keys
    STORAGE: {
        CACHED_STATE: 'orei_cached_state',
        CACHED_INPUTS: 'orei_cached_inputs',
        CACHED_OUTPUTS: 'orei_cached_outputs',
        CACHED_PRESETS: 'orei_cached_presets',
        CACHED_SCENES: 'orei_cached_scenes',
        CACHED_PROFILES: 'orei_cached_profiles',
        CACHED_MACROS: 'orei_cached_macros',
        DASHBOARD_CONFIG: 'orei_dashboard_config',
        CEC_VOLUME_TARGET: 'cecVolumeTarget',
        CEC_NAV_TARGET: 'cecNavTarget',
        CEC_MUTE_STATE: 'cecMuteState',
        HIDE_CEC_HEADER: 'hideCecHeader',
        HIDE_CEC_WIDGET: 'hideCecWidget'
    },
    
    // EDID modes (from matrix protocol)
    EDID: {
        COPY_OUTPUT_1: 0,
        COPY_OUTPUT_2: 1,
        COPY_OUTPUT_3: 2,
        COPY_OUTPUT_4: 3,
        COPY_OUTPUT_5: 4,
        COPY_OUTPUT_6: 5,
        COPY_OUTPUT_7: 6,
        COPY_OUTPUT_8: 7,
        CUSTOM_4K_HDR: 8,
        CUSTOM_4K_SDR: 9,
        CUSTOM_1080P: 10,
        CUSTOM_720P: 11
    },
    
    // Output scaler modes
    SCALER: {
        AUTO: 0,
        FORCE_4K: 1,
        FORCE_1080P: 2,
        BYPASS: 3,
        AUDIO_ONLY: 4
    },
    
    // API endpoints
    API: {
        BASE: '/api',
        HEALTH: '/api/health',
        STATUS: '/api/status',
        SWITCH: '/api/switch',
        PRESET: '/api/preset',
        SCENE: '/api/scene',
        PROFILE: '/api/profile',
        MACRO: '/api/macro',
        CEC: '/api/cec',
        SETTINGS: '/api/settings',
        WEBSOCKET: '/ws'
    },
    
    // Event types
    EVENTS: {
        STATE_CHANGED: 'stateChanged',
        ROUTING_CHANGED: 'routingChanged',
        CONNECTION_CHANGED: 'connectionChanged',
        SCENE_CHANGED: 'sceneChanged',
        PROFILE_CHANGED: 'profileChanged',
        WS_MESSAGE: 'wsMessage',
        ERROR: 'error'
    }
};

// Freeze to prevent accidental modification
Object.freeze(Constants);
Object.freeze(Constants.CONNECTION);
Object.freeze(Constants.MATRIX);
Object.freeze(Constants.TIMING);
Object.freeze(Constants.BREAKPOINTS);
Object.freeze(Constants.STORAGE);
Object.freeze(Constants.EDID);
Object.freeze(Constants.SCALER);
Object.freeze(Constants.API);
Object.freeze(Constants.EVENTS);

// Export for use in modules
if (typeof window !== 'undefined') {
    window.Constants = Constants;
}

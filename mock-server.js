/**
 * Mock API Server for OREI Matrix UI Development
 * Serves static files AND mock API responses
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const WEB_ROOT = path.join(__dirname, 'web');

// Mock data
const mockData = {
    info: {
        model: 'BK-808',
        firmware: '1.2.3',
        api_version: '1.0',
        inputs: 8,
        outputs: 8
    },
    status: {
        routing: [1, 2, 3, 4, 5, 6, 7, 8],
        power: true
    },
    inputs: Array.from({length: 8}, (_, i) => ({
        id: i + 1,
        name: `Input ${i + 1}`,
        signal: i < 4,
        resolution: i < 4 ? '4K@60Hz' : null,
        hdcp: i < 4 ? '2.2' : null
    })),
    outputs: Array.from({length: 8}, (_, i) => ({
        id: i + 1,
        name: `Output ${i + 1}`,
        connected: i < 6,
        source: i + 1,
        muted: false,
        arc: false
    })),
    profiles: [
        { id: 'movie', name: 'Movie Night', icon: 'movie-scene', outputs: { 1: 1, 2: 1, 3: 1 } },
        { id: 'gaming', name: 'Gaming Session', icon: 'gaming-scene', outputs: { 1: 2, 2: 2 } }
    ],
    edidModes: [
        { id: 0, name: 'Auto' },
        { id: 1, name: '1080p' },
        { id: 2, name: '4K@30Hz' },
        { id: 3, name: '4K@60Hz' }
    ]
};

// MIME types
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

function handleApi(req, res) {
    const url = req.url.split('?')[0];
    
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    // API routes
    if (url === '/api/info') {
        return res.end(JSON.stringify(mockData.info));
    }
    if (url === '/api/status') {
        return res.end(JSON.stringify(mockData.status));
    }
    if (url === '/api/status/inputs') {
        return res.end(JSON.stringify(mockData.inputs));
    }
    if (url === '/api/status/outputs') {
        return res.end(JSON.stringify(mockData.outputs));
    }
    if (url === '/api/profiles') {
        return res.end(JSON.stringify(mockData.profiles));
    }
    if (url === '/api/edid/modes') {
        return res.end(JSON.stringify(mockData.edidModes));
    }
    if (url.startsWith('/api/output/') && url.endsWith('/source')) {
        // Handle routing change
        return res.end(JSON.stringify({ success: true }));
    }
    
    // Default API response
    res.statusCode = 200;
    res.end(JSON.stringify({ status: 'ok' }));
}

function handleStatic(req, res) {
    let filePath = path.join(WEB_ROOT, req.url.split('?')[0]);
    
    // Default to index.html
    if (filePath.endsWith('/') || !path.extname(filePath)) {
        filePath = path.join(WEB_ROOT, 'index.html');
    }
    
    const ext = path.extname(filePath);
    const contentType = mimeTypes[ext] || 'application/octet-stream';
    
    fs.readFile(filePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.statusCode = 404;
                res.end('Not Found');
            } else {
                res.statusCode = 500;
                res.end('Server Error');
            }
        } else {
            res.setHeader('Content-Type', contentType);
            res.end(content);
        }
    });
}

// WebSocket mock (just accept connection)
const server = http.createServer((req, res) => {
    console.log(`${req.method} ${req.url}`);
    
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
        res.statusCode = 204;
        return res.end();
    }
    
    // Route requests
    if (req.url.startsWith('/api/')) {
        handleApi(req, res);
    } else if (req.url === '/ws') {
        // WebSocket upgrade would happen here, just return OK for now
        res.statusCode = 200;
        res.end('WebSocket endpoint');
    } else {
        handleStatic(req, res);
    }
});

server.listen(PORT, () => {
    console.log(`\n🚀 Mock Matrix Server running at http://localhost:${PORT}`);
    console.log(`   Serving files from: ${WEB_ROOT}`);
    console.log(`   API endpoints: /api/info, /api/status, /api/profiles, etc.\n`);
});

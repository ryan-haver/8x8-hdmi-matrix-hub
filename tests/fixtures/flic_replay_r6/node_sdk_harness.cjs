// Node harness to exercise generated Flic Hub SDK snippets
// Stubs CommonJS "buttons" and "http" modules

const fs = require('fs');
const process = require('node:process');

function runHarness(scriptPath, buttonsList, eventsList) {
    const requests = [];
    const eventListeners = {};

    const buttonManager = {
        getButtons: function() {
            return buttonsList.map(b => ({
                name: b.name,
                bdaddr: b.bdaddr,
                serialNumber: b.serial || b.serialNumber || ""
            }));
        },
        getButton: function(bdaddr) {
            const found = buttonsList.find(b => b.bdaddr === bdaddr);
            if (!found) return null;
            return {
                name: found.name,
                bdaddr: found.bdaddr,
                serialNumber: found.serial || found.serialNumber || ""
            };
        },
        on: function(eventName, cb) {
            if (!eventListeners[eventName]) {
                eventListeners[eventName] = [];
            }
            eventListeners[eventName].push(cb);
        }
    };

    const http = {
        makeRequest: function(opts, cb) {
            requests.push({
                url: opts.url,
                method: opts.method,
                headers: opts.headers || {},
                content: opts.content || null
            });
            if (typeof cb === 'function') {
                cb(null, { statusCode: 200, content: '{"success":true}' });
            }
        }
    };

    function customRequire(mod) {
        if (mod === 'buttons') return buttonManager;
        if (mod === 'http') return http;
        throw new Error('Unknown module: ' + mod);
    }

    const scriptCode = fs.readFileSync(scriptPath, 'utf8');

    // Run snippet in an isolated function wrapper with custom require
    const wrapper = new Function('require', 'console', `
        ${scriptCode}
    `);

    // Capture startup
    wrapper(customRequire, { log: () => {}, error: () => {} });
    const startupRequestsCount = requests.length;

    // Dispatch each event
    const eventResults = [];
    for (const evt of eventsList) {
        const preCount = requests.length;
        const listeners = eventListeners[evt.eventName] || [];
        for (const cb of listeners) {
            cb(evt.payload);
        }
        const postCount = requests.length;
        eventResults.push({
            event: evt,
            requestsTriggered: postCount - preCount,
            requests: requests.slice(preCount)
        });
    }

    return {
        allRequests: requests,
        startupRequestsCount,
        eventResults
    };
}

if (require.main === module) {
    const inputJson = fs.readFileSync(0, 'utf8');
    const input = JSON.parse(inputJson);
    const result = runHarness(input.scriptPath, input.buttons || [], input.events || []);
    process.stdout.write(JSON.stringify(result));
}

module.exports = { runHarness };

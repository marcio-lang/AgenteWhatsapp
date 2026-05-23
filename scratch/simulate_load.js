const fs = require('fs');
const path = require('path');

// Basic JSDOM mock
try {
    const { JSDOM } = require('jsdom');
    
    const html = fs.readFileSync(path.join(__dirname, '../frontend/index.html'), 'utf8');
    const dom = new JSDOM(html, {
        runScripts: "dangerously",
        resources: "usable",
        url: "http://localhost:3000/"
    });
    
    const { window } = dom;
    const { document } = window;
    
    // Mock APIs
    window.fetch = async (url) => {
        console.log(`[Fetch Mock] Request to: ${url}`);
        if (url.includes('/api/instance/status')) {
            return { ok: true, json: async () => ({ instance_name: 'Test Instance', instance: { state: 'open', ownerJid: '123@s.whatsapp.net' } }) };
        }
        if (url.includes('/api/config')) {
            return { ok: true, json: async () => ({ url: 'http://localhost:3000', token: 'test', instance: 'test' }) };
        }
        if (url.includes('/api/chats')) {
            return { ok: true, json: async () => [] };
        }
        if (url.includes('/api/contact-groups')) {
            return { ok: true, json: async () => [] };
        }
        if (url.includes('/api/flows')) {
            return { ok: true, json: async () => [] };
        }
        return { ok: true, json: async () => ({}) };
    };
    
    // Audio mock
    window.Audio = class {
        constructor() {}
        play() { return Promise.resolve(); }
    };
    
    // Notification mock
    window.Notification = {
        permission: 'granted',
        requestPermission: () => Promise.resolve('granted')
    };
    
    // Capture console errors
    window.console.error = (...args) => {
        console.log('[Console Error]', ...args);
    };
    window.console.warn = (...args) => {
        console.log('[Console Warn]', ...args);
    };
    window.console.log = (...args) => {
        console.log('[Console Log]', ...args);
    };
    
    // Load app.js
    const jsCode = fs.readFileSync(path.join(__dirname, '../frontend/app.js'), 'utf8');
    const scriptEl = document.createElement("script");
    scriptEl.textContent = jsCode;
    document.body.appendChild(scriptEl);
    
    // Trigger DOMContentLoaded
    const event = document.createEvent("Event");
    event.initEvent("DOMContentLoaded", true, true);
    window.document.dispatchEvent(event);
    
    console.log('\n--- AFTER LOAD ---');
    console.log('Active sections:');
    document.querySelectorAll('.content-section').forEach(s => {
        console.log(`  #${s.id}: classes=${s.className}`);
    });
    
    console.log('\nClicking "Agente (Fluxos)" tab...');
    const agenteTab = Array.from(document.querySelectorAll('.nav-item')).find(item => item.getAttribute('data-section') === 'agente');
    if (agenteTab) {
        agenteTab.click();
        
        console.log('\n--- AFTER CLICK ---');
        console.log('Active sections:');
        document.querySelectorAll('.content-section').forEach(s => {
            console.log(`  #${s.id}: classes=${s.className}`);
        });
    } else {
        console.log('Agente tab not found!');
    }
    
} catch (err) {
    console.log('Error setting up JSDOM mock:', err);
}

/**
 * Hedge Intelligence Frontend
 * Created: 2025-06-14
 */

class HedgeAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.ws = null;
    }
    
    async getIPOCalendar(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${this.baseURL}/calendar?${params}`);
        return response.json();
    }
    
    connectChat(docId) {
        this.ws = new WebSocket(`ws://localhost:8000/ws/chat/${docId}`);
        return this.ws;
    }
}

class HedgeIntelligence {
    constructor() {
        this.api = new HedgeAPI();
        this.currentView = 'calendar';
    }
    
    async init() {
        console.log('Hedge Intelligence initialized');
        // TODO: Implement initialization
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.app = new HedgeIntelligence();
    app.init();
});

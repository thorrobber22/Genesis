// Hedge Intelligence Frontend
// Real data only - no mocks

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Hedge Intelligence Loading...');
    loadIPOCalendar();
    
    // Safe filter setup
    const periodFilter = document.getElementById('period-filter');
    const statusFilter = document.getElementById('status-filter');
    
    if (periodFilter) {
        periodFilter.addEventListener('change', loadIPOCalendar);
    }
    if (statusFilter) {
        statusFilter.addEventListener('change', loadIPOCalendar);
    }
});

async function loadIPOCalendar() {
    console.log("Loading IPO calendar from scraped data...");
    const tableBody = document.getElementById('ipo-table-body');
    
    if (!tableBody) {
        console.error("Table body element not found!");
        return;
    }
    
    try {
        // Fetch REAL data from API (reads ipo_calendar.json)
        const response = await fetch('/api/calendar');
        console.log("API Response status:", response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const ipos = await response.json();
        console.log(`Loaded ${ipos.length} REAL IPOs from scraper`);
        
        // Clear table - NO MOCK DATA
        tableBody.innerHTML = '';
        
        // Display each REAL IPO
        ipos.forEach((ipo, index) => {
            const row = document.createElement('tr');
            
            // Format lead managers on multiple lines
            const leadManagers = ipo.lead_managers ? 
                ipo.lead_managers.split('/').map(m => m.trim()).join('<br>') : '-';
            
            // Create row with REAL scraped data - ALL 11 COLUMNS
            row.innerHTML = `
                <td>${formatDate(ipo.expected_date)}</td>
                <td><button class="ticker-button" onclick="openContextPanel('${ipo.ticker}')">${ipo.ticker}</button></td>
                <td>${ipo.company}</td>
                <td>${ipo.price_range || '-'}</td>
                <td>${ipo.shares || '-'}</td>
                <td>${ipo.volume || '-'}</td>
                <td><span class="status-${ipo.status.toLowerCase()}">${ipo.status}</span></td>
                <td>${ipo.documents || 0}</td>
                <td>${ipo.lockup || '-'}</td>
                <td style="font-size: 11px; line-height: 1.4;">${leadManagers}</td>
                <td>${ipo.scoop_rating || '-'}</td>
            `;
            
            tableBody.appendChild(row);
        });
        
        console.log("✅ Real IPO data displayed successfully");
        
    } catch (error) {
        console.error('Error loading real IPO data:', error);
        tableBody.innerHTML = '<tr><td colspan="11">Error loading scraped data. Check console.</td></tr>';
    }
}

// Format dates intelligently
function formatDate(dateStr) {
    if (!dateStr) return '-';
    
    // Handle special cases from scraper
    if (dateStr === 'Priced') return 'Priced';
    if (dateStr.includes('Week of')) return dateStr;
    if (dateStr.includes('Wednesday')) return dateStr;
    if (dateStr.includes('Thursday')) return dateStr;
    if (dateStr.includes('Tuesday')) return dateStr;
    
    // Format regular dates
    try {
        const date = new Date(dateStr);
        const today = new Date();
        const diffDays = Math.floor((date - today) / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Tomorrow';
        if (diffDays === -1) return 'Yesterday';
        if (diffDays > 1 && diffDays <= 7) return `In ${diffDays} days`;
        
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch (e) {
        return dateStr; // Return original if can't parse
    }
}

// View switching functionality
function showView(viewName) {
    console.log('Switching to view:', viewName);
    
    // Hide all views
    document.querySelectorAll('.view').forEach(v => {
        v.classList.remove('active');
    });
    
    // Show selected view
    const targetView = document.getElementById(viewName + '-view');
    if (targetView) {
        targetView.classList.add('active');
    }
    
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Set active nav item based on view name
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Special handling for companies view
    if (viewName === 'companies') {
        loadCompaniesTree();
    } else if (viewName === 'watchlist') {
        loadWatchlist();
    }
}

// Show company details in context panel
function showCompanyDetails(ipo) {
    const ticker = document.getElementById('contextTicker');
    const contextPanel = document.getElementById('contextPanel');
    
    if (ticker) {
        ticker.textContent = ipo.ticker || '';
    }
    
    // Show the panel
    if (contextPanel) {
        contextPanel.classList.remove('compressed');
    }
}

// Open context panel for ticker
function openContextPanel(ticker) {
    console.log(`Opening context for ${ticker}`);
    const contextPanel = document.getElementById('contextPanel');
    const contextTicker = document.getElementById('contextTicker');
    
    if (contextTicker) {
        contextTicker.textContent = ticker;
    }
    
    if (contextPanel) {
        contextPanel.classList.remove('compressed');
    }
}

// Load companies tree from actual data
async function loadCompaniesTree() {
    try {
        const response = await fetch('/api/companies/tree');
        const tree = await response.json();
        renderCompaniesTree(tree);
    } catch (error) {
        console.error('Error loading companies:', error);
    }
}

// Render companies tree
function renderCompaniesTree(tree) {
    const container = document.querySelector('#companies-view .folder-content');
    if (!container) return;
    
    // Clear existing content
    container.innerHTML = '';
    
    // Add companies from tree
    Object.entries(tree).forEach(([sector, companies]) => {
        companies.forEach(company => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.onclick = () => selectCompany(company.ticker);
            item.innerHTML = `
                <span>[D] <span class="file-name">${company.company} (${company.ticker})</span></span>
                <span class="doc-count">${company.filing_count || 0} docs</span>
            `;
            container.appendChild(item);
        });
    });
}

// Placeholder for watchlist
async function loadWatchlist() {
    console.log('Loading watchlist...');
}

// Update company selection
function selectCompany(ticker) {
    console.log('Selected company:', ticker);
    // Update active state
    document.querySelectorAll('.file-item').forEach(item => {
        item.classList.remove('active');
    });
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}

// Missing functions
function toggleFolder(element) {
    const content = element.nextElementSibling;
    if (content) {
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
    }
}

function openChat() {
    console.log('Opening chat panel');
    const chatPanel = document.getElementById('chatPanel');
    if (chatPanel) {
        chatPanel.classList.add('open');
    }
}

function toggleChat() {
    const chatPanel = document.getElementById('chatPanel');
    if (chatPanel) {
        chatPanel.classList.toggle('open');
    }
}

function toggleDocChat() {
    const docChat = document.querySelector('.chat-panel.document-mode');
    if (docChat) {
        docChat.classList.toggle('open');
    }
}

function askQuestion(type) {
    console.log('Question:', type);
}

function jumpToCitation(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
        element.classList.add('highlight');
        setTimeout(() => element.classList.remove('highlight'), 2000);
    }
}
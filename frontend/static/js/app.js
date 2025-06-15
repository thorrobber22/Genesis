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
    try {
        // Handle missing filters gracefully
        const periodFilter = document.getElementById('period-filter');
        const statusFilter = document.getElementById('status-filter');
        
        const period = periodFilter ? periodFilter.value : 'all';
        const status = statusFilter ? statusFilter.value : 'all';
        
        const response = await fetch(`/api/calendar?period=${period}&status=${status}`);
        const ipos = await response.json();
        
        console.log(`✅ Loaded ${ipos.length} IPOs`);
        renderIPOTable(ipos);
        
    } catch (error) {
        console.error('❌ Error loading IPOs:', error);
        // Try loading without filters
        try {
            const response = await fetch('/api/calendar');
            const ipos = await response.json();
            renderIPOTable(ipos);
        } catch (e) {
            console.error('Failed to load IPOs:', e);
        }
    }
}&status=${status}`);
        const ipos = await response.json();
        
        console.log(`✅ Loaded ${ipos.length} IPOs`);
        renderIPOTable(ipos);
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

function renderIPOTable(ipos) {
    const tbody = document.querySelector('#ipo-calendar tbody');
    tbody.innerHTML = '';
    
    ipos.forEach(ipo => {
        const row = document.createElement('tr');
        row.onclick = () => showCompanyDetails(ipo);
        
        row.innerHTML = `
            <td class="date">${ipo.expected_date || 'TBD'}</td>
            <td><span class="ticker">${ipo.ticker || ''}</span></td>
            <td class="company">${ipo.company || ''}</td>
            <td class="price-range">${ipo.price_range || 'TBD'}</td>
            <td class="shares">${ipo.shares || '-'}</td>
            <td class="volume">${ipo.volume || '-'}</td>
            <td><span class="status ${(ipo.status || '').toLowerCase()}">${ipo.status || 'Expected'}</span></td>
            <td class="documents">${ipo.documents || 0}</td>
            <td class="lockup">${ipo.lockup || '180 days'}</td>
            <td class="lead-managers">${ipo.lead_managers || '-'}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function showCompanyDetails(ipo) {
    const ticker = document.getElementById('contextTicker');
    const content = document.getElementById('contextContent');
    
    ticker.textContent = ipo.ticker;
    content.innerHTML = `
        <div style="margin-bottom: 20px;">
            <p style="font-weight: 600; margin-bottom: 8px;">OVERVIEW</p>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #A3A3A3; font-size: 11px;">Company</span>
                <span style="font-size: 13px;">${ipo.company}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #A3A3A3; font-size: 11px;">Price Range</span>
                <span style="font-size: 13px;">${ipo.price_range}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #A3A3A3; font-size: 11px;">Status</span>
                <span style="font-size: 13px;">${ipo.status}</span>
            </div>
        </div>
        <div>
            <p style="font-weight: 600; margin-bottom: 8px;">DETAILS</p>
            <div style="font-size: 13px; line-height: 1.6;">
                • Volume: ${ipo.volume}<br>
                • Lead Managers: ${ipo.lead_managers}<br>
                • Exchange: ${ipo.exchange || 'NASDAQ'}
            </div>
        </div>
    `;
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
        if (item.textContent.toLowerCase().includes(viewName)) {
            item.classList.add('active');
        }
    });
    
    // Special handling for companies view
    if (viewName === 'companies') {
        loadCompaniesTree();
    } else if (viewName === 'watchlist') {
        loadWatchlist();
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
    event.currentTarget.classList.add('active');
}

// Missing functions
function toggleFolder(element) {
    const content = element.nextElementSibling;
    if (content) {
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
    }
}

function openChat() {
    console.log('Chat functionality coming soon');
}

function askQuestion(type) {
    console.log('Question:', type);
}

function openContextPanel(ticker) {
    showCompanyDetails({ ticker: ticker });
}
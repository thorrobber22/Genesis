// fix_frontend_display.js
"""Fix the frontend to display all IPO fields correctly"""

const frontendFix = `
// Update frontend/static/js/app.js or wherever the IPO table is rendered

function renderIPOTable(ipos) {
    const tbody = document.querySelector('#ipo-table tbody');
    tbody.innerHTML = '';
    
    ipos.forEach(ipo => {
        const row = document.createElement('tr');
        row.innerHTML = \`
            <td>\${ipo.expected_date || 'TBD'}</td>
            <td class="ticker">\${ipo.ticker}</td>
            <td>\${ipo.company}</td>
            <td>\${ipo.price_range || 'TBD'}</td>
            <td>\${ipo.shares || '-'}</td>
            <td>\${ipo.volume || '-'}</td>
            <td class="status \${ipo.status.toLowerCase()}">\${ipo.status}</td>
            <td>\${ipo.documents || 0}</td>
            <td>\${ipo.lockup || '180 days'}</td>
            <td>\${ipo.lead_managers || '-'}</td>
            <td>\${ipo.scoop_rating || '-'}</td>
        \`;
        tbody.appendChild(row);
    });
}

// Update the table headers too
const tableHeaders = \`
    <thead>
        <tr>
            <th>Expected Date</th>
            <th>Ticker</th>
            <th>Company</th>
            <th>Price Range</th>
            <th>Shares (M)</th>
            <th>Volume</th>
            <th>Status</th>
            <th>Docs</th>
            <th>Lockup</th>
            <th>Lead Managers</th>
            <th>Rating</th>
        </tr>
    </thead>
\`;
`;

console.log("Add this to your frontend JavaScript!");
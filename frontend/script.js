// Function to toggle dropdown menus in sidebar
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    const icon = document.getElementById(dropdownId + '-icon');
    
    // Close all other dropdowns first
    const allDropdowns = document.querySelectorAll('[id$="Dropdown"]');
    const allIcons = document.querySelectorAll('[id$="-icon"]');
    
    allDropdowns.forEach(d => {
        if (d.id !== dropdownId && !d.classList.contains('hidden')) {
            d.classList.add('hidden');
        }
    });
    
    allIcons.forEach(i => {
        if (i.id !== dropdownId + '-icon' && i.classList.contains('rotate-180')) {
            i.classList.remove('rotate-180');
        }
    });
    
    // Toggle current dropdown
    dropdown.classList.toggle('hidden');
    icon.classList.toggle('rotate-180');
}

// Function to refresh dashboard data
function refreshDashboard() {
    loadDashboard();
    loadKPIs();
    loadOrders();
}

// Function to display username on index.html (if needed)
function displayUsername() {
    const token = localStorage.getItem('token');
    if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        document.getElementById('username').textContent = payload.username || 'User';
    } else {
        window.location.href = '/login';
    }
}

// Function to load dashboard based on role
// Add this at the top after any imports or before functions
const pageRoles = {
    '/index': ['administrator', 'manufacturing manager'],
    '/users': ['administrator'],
    '/mo_list': ['administrator', 'manufacturing manager'],
    '/mo_create': ['administrator', 'manufacturing manager'],
    '/mo_detail': ['administrator', 'manufacturing manager'],
    '/wo_list': ['administrator', 'manufacturing manager', 'operator'],
    '/wo-task': ['administrator', 'manufacturing manager','operator'],
    '/bom_list': ['administrator', 'manufacturing manager'],
    '/bom_create': ['administrator'],
    '/inventory': ['administrator', 'manufacturing manager', 'inventory manager'],
    '/product_master': ['inventory manager'],
    '/reports': ['administrator', 'manufacturing manager', 'inventory manager'],
    '/settings': ['administrator'],
    '/profile': ['manufacturing manager', 'inventory manager', 'operator']
};

// Global page protection
const currentPath = window.location.pathname;
if (pageRoles[currentPath]) {
    protectPage(pageRoles[currentPath]);
}

// Logout handling
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = '/login';
    });
}

// Register form handling
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData);
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                alert('Registered successfully');
                window.location.href = '/login';  // Redirect to login.html on success
            } else {
                alert(result.error || 'Registration failed');
            }
        } catch (err) {
            alert('Error during registration');
        }
    });
}

// Login form handling
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        const data = Object.fromEntries(formData);
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                localStorage.setItem('token', result.token);
                localStorage.setItem('username', result.username);

                const lowerRole = result.role.toLowerCase();

                if (lowerRole === 'administrator' || lowerRole === 'manufacturing manager' || lowerRole === 'inventory manager') {
                    window.location.href = '/index';
                } else if (lowerRole === 'operator') {
                    window.location.href = '/wo_list';
                } else {
                    window.location.href = '/login';
                }

            } else {
                alert(result.error || 'Login failed');
            }

        } catch (err) {
            alert('Error during login');
        }
    });
}


// Call displayUsername if on index.html
if (document.getElementById('username')) {
    displayUsername();
}

// Function to decode JWT (assuming it's already there from previous implementations)
function decodeJWT(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}

// Protect page based on required roles
function protectPage(requiredRoles) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    try {
        const decoded = decodeJWT(token);
        const userRole = decoded.role.toLowerCase();
        if (!requiredRoles.some(role => role.toLowerCase() === userRole)) {
            alert('Access denied. Redirecting to dashboard.');
            window.location.href = '/index';
        }
    } catch (error) {
        console.error('Invalid token', error);
        localStorage.removeItem('token');
        window.location.href = '/login';
    }
}

// BOM related functions
async function loadBOMs() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/boms', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const boms = await response.json();
        const list = document.getElementById('bomList');
        list.innerHTML = boms.map(bom => `<div>BOM ID: ${bom.id} - Product: ${bom.product_id}</div>`).join('');
    } catch (error) {
        console.error('Error loading BOMs:', error);
    }
}

async function createBOM(event) {
    event.preventDefault();
    const token = localStorage.getItem('token');
    const productId = document.getElementById('productId').value;
    const components = document.getElementById('components').value;
    try {
        const response = await fetch('/api/boms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId, components: JSON.parse(components) })
        });
        if (response.ok) {
            alert('BOM created successfully');
            loadBOMs();
        } else {
            alert('Error creating BOM');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// MO related functions
// Load MO List
async function loadMOList() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/mos', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const mos = await response.json();
        const tableBody = document.getElementById('moListTable');
        tableBody.innerHTML = mos.map(mo => `
            <tr>
                <td class="p-2 border-b">${mo.id}</td>
                <td class="p-2 border-b">${mo.product_name || mo.product_id}</td>
                <td class="p-2 border-b">${mo.quantity}</td>
                <td class="p-2 border-b">${mo.status}</td>
                <td class="p-2 border-b">${mo.assignee_name || mo.assignee_id}</td>
                <td class="p-2 border-b">${mo.start_date}</td>
                <td class="p-2 border-b">${mo.deadline}</td>
                <td class="p-2 border-b">
                    <a href="mo_detail.html?id=${mo.id}" class="text-blue-500">View</a>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading MO list:', error);
    }
}

// Load MO Detail
async function loadMODetail(moId) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`/api/mos/${moId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const mo = await response.json();
        document.getElementById('moHeader').innerHTML = `
            <p><strong>ID:</strong> ${mo.id}</p>
            <p><strong>Product:</strong> ${mo.product_name || mo.product_id}</p>
            <p><strong>Quantity:</strong> ${mo.quantity}</p>
            <p><strong>Status:</strong> ${mo.status}</p>
            <p><strong>Assignee:</strong> ${mo.assignee_name || mo.assignee_id}</p>
            <p><strong>Start Date:</strong> ${mo.start_date}</p>
            <p><strong>Deadline:</strong> ${mo.deadline}</p>
        `;
        
        // Load BOM Tab
        const bomResponse = await fetch(`/api/boms/${mo.product_id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const bomItems = await bomResponse.json();
        document.getElementById('bomItems').innerHTML = bomItems.map(item => `
            <p>${item.raw_material_name} - Quantity: ${item.quantity}</p>
        `).join('');
        
        // Load Work Orders Tab
        const woResponse = await fetch(`/api/wos?mo_id=${moId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const wos = await woResponse.json();
        document.getElementById('workOrdersList').innerHTML = wos.map(wo => `
            <p>WO ID: ${wo.id} - Operation: ${wo.operation_name} - Status: ${wo.status}</p>
        `).join('');
        
        showTab('bom'); // Show BOM tab by default
    } catch (error) {
        console.error('Error loading MO detail:', error);
    }
}

// Show Tab
function showTab(tabName) {
    document.getElementById('bomTab').classList.add('hidden');
    document.getElementById('workOrdersTab').classList.add('hidden');
    document.getElementById(`${tabName}Tab`).classList.remove('hidden');
}

// Action functions (placeholders; implement API calls as needed)
function editMO() {
    // Redirect to edit form or handle inline edit
    alert('Edit functionality to be implemented');
}

async function confirmMO() {
    const moId = new URLSearchParams(window.location.search).get('id');
    const token = localStorage.getItem('token');
    try {
        await fetch(`/api/mos/${moId}/confirm`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        alert('MO confirmed');
        loadMODetail(moId);
    } catch (error) {
        console.error('Error confirming MO:', error);
    }
}

async function cancelMO() {
    const moId = new URLSearchParams(window.location.search).get('id');
    const token = localStorage.getItem('token');
    try {
        await fetch(`/api/mos/${moId}/cancel`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        alert('MO canceled');
        loadMODetail(moId);
    } catch (error) {
        console.error('Error canceling MO:', error);
    }
}

// Load Products for dropdown
async function loadProducts() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/products', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const products = await response.json();
        const select = document.getElementById('productId');
        select.innerHTML = products.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Load Users for assignee dropdown
async function loadUsers() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/users', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const users = await response.json();
        const select = document.getElementById('assigneeId');
        select.innerHTML = users.map(u => `<option value="${u.id}">${u.username}</option>`).join('');
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Load BOM for selected product
async function loadBOMForProduct(productId) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`/api/boms/${productId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const bomItems = await response.json();
        const materialsDiv = document.getElementById('requiredMaterials');
        materialsDiv.innerHTML = bomItems.map(item => `
            <p>${item.raw_material_name} - Required: ${item.quantity * document.getElementById('quantity').value || item.quantity}</p>
        `).join('');
    } catch (error) {
        console.error('Error loading BOM:', error);
    }
}

// Create MO
async function createMO(event) {
    event.preventDefault();
    const token = localStorage.getItem('token');
    const formData = {
        product_id: document.getElementById('productId').value,
        quantity: document.getElementById('quantity').value,
        start_date: document.getElementById('startDate').value,
        deadline: document.getElementById('deadline').value,
        assignee_id: document.getElementById('assigneeId').value
    };
    try {
        const response = await fetch('/api/mos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });
        if (response.ok) {
            alert('MO created successfully');
            window.location.href = 'mo_list.html';
        } else {
            alert('Error creating MO');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// WO related functions
async function loadWorkOrders() {
    const token = localStorage.getItem('token');
    const payload = JSON.parse(atob(token.split('.')[1]));
    const role = payload.role.toLowerCase();
    let endpoint = '/api/wos';
    if (role === 'operator') {
        endpoint = '/api/wos/assigned';
    }
    try {
        const response = await fetch(endpoint, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            throw new Error('Failed to fetch work orders');
        }
        const wos = await response.json();
        const list = document.getElementById('woList');
        list.innerHTML = wos.map(wo => `
            <div class="mb-4">
                WO ID: ${wo.id} - Status: ${wo.status} - MO ID: ${wo.mo_id}
                ${role === 'operator' ? `
                <button onclick="updateWOStatus(${wo.id}, 'start')" class="bg-green-500 text-white px-2 py-1">Start</button>
                <button onclick="updateWOStatus(${wo.id}, 'pause')" class="bg-yellow-500 text-white px-2 py-1">Pause</button>
                <button onclick="updateWOStatus(${wo.id}, 'complete')" class="bg-blue-500 text-white px-2 py-1">Complete</button>
                ` : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading WOs:', error);
        document.getElementById('woList').innerHTML = '<p class="text-red-500">Error loading work orders.</p>';
    }
}

async function updateWOStatus(woId, status) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`/api/wos/${woId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status })
        });
        if (response.ok) {
            alert('WO status updated');
            loadAssignedWOs();
        } else {
            alert('Error updating WO');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Inventory related functions
async function loadInventory() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/inventory', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const items = await response.json();
        const list = document.getElementById('inventoryList');
        list.innerHTML = items.map(item => `<div>Item ID: ${item.id} - Quantity: ${item.quantity}</div>`).join('');
    } catch (error) {
        console.error('Error loading inventory:', error);
    }
}

async function updateInventory(event) {
    event.preventDefault();
    const token = localStorage.getItem('token');
    const itemId = document.getElementById('itemId').value;
    const quantity = document.getElementById('quantity').value;
    try {
        const response = await fetch(`/api/inventory/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ quantity })
        });
        if (response.ok) {
            alert('Inventory updated');
            loadInventory();
        } else {
            alert('Error updating inventory');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Reports related functions
async function loadReports() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/reports', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        // Assuming data has progress and delays arrays
        renderChart('progressChart', data.progress);
        renderChart('delaysChart', data.delays);
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

function renderChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Values',
                data: data.values,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        }
    });
}

// Assuming decodeJWT is already defined as in previous implementations

async function loadDashboard() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    let decoded;
    try {
        decoded = decodeJWT(token);
    } catch (error) {
        console.error('Invalid token', error);
        localStorage.removeItem('token');
        window.location.href = '/login';
        return;
    }
    
    const allowedRoles = ['Administrator', 'Manufacturing Manager'];
    if (!allowedRoles.includes(decoded.role)) {
        if (decoded.role === 'Operator') {
            window.location.href = '/wo_list';
        } else {
            alert('Access denied. Redirecting to login.');
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return;
    }
    
    // Show create button for admin and managers
    document.getElementById('createOrderBtn').classList.remove('hidden');
    
    // Show admin users management section for admin only
    if (decoded.role === 'Administrator') {
        document.getElementById('adminUsersSection').classList.remove('hidden');
    }
    
    // Load KPIs and Orders
    await loadKPIs();
    await loadOrders();
}

// Function to load KPIs
async function loadKPIs() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/mos/kpis', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Failed to load KPIs');
        const kpis = await response.json();
        document.getElementById('totalOrders').textContent = kpis.total_orders || 0;
        document.getElementById('inProgress').textContent = kpis.in_progress || 0;
        document.getElementById('completedToday').textContent = kpis.completed_today || 0;
        document.getElementById('delayedOrders').textContent = kpis.delayed_orders || 0;
    } catch (error) {
        console.error('Error loading KPIs:', error);
    }
}

// Variable to store all orders for filtering
let allOrders = [];

// Function to load all orders
async function loadOrders() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/mos', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Failed to load orders');
        allOrders = await response.json();
        renderOrders(allOrders);
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

// Function to render orders in the table
function renderOrders(orders) {
    const tableBody = document.getElementById('ordersTable');
    tableBody.innerHTML = '';
    orders.forEach(order => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-2 border-b">${order.id}</td>
            <td class="p-2 border-b">${order.product_name || order.product_id}</td>
            <td class="p-2 border-b">${order.quantity}</td>
            <td class="p-2 border-b">${order.status}</td>
            <td class="p-2 border-b">${order.deadline}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Function to filter orders
function filterOrders(status) {
    if (status === 'all') {
        renderOrders(allOrders);
    } else {
        const filtered = allOrders.filter(order => order.status.toLowerCase() === status);
        renderOrders(filtered);
    }
}

// Load Work Centers List
async function loadWorkCenters() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/workcenters', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const wcs = await response.json();
        const tableBody = document.getElementById('wcListTable');
        tableBody.innerHTML = wcs.map(wc => `
            <tr>
                <td class="p-2 border-b">${wc.name}</td>
                <td class="p-2 border-b">${wc.description}</td>
                <td class="p-2 border-b">$${wc.hourly_cost_rate}</td>
                <td class="p-2 border-b">${wc.status}</td>
                <td class="p-2 border-b">
                    <a href="wc_detail.html?id=${wc.id}" class="text-blue-500">View</a>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading work centers:', error);
    }
}

// Load Work Center Detail
async function loadWCDetail(wcId) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`/api/workcenters/${wcId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const wc = await response.json();
        document.getElementById('wcProperties').innerHTML = `
            <p><strong>Name:</strong> <span id="name">${wc.name}</span></p>
            <p><strong>Description:</strong> <span id="description">${wc.description}</span></p>
            <p><strong>Hourly Cost Rate:</strong> <span id="hourly_cost_rate">$${wc.hourly_cost_rate}</span></p>
            <p><strong>Status:</strong> ${wc.status}</p>
        `;
    } catch (error) {
        console.error('Error loading WC detail:', error);
    }
}

// Load Utilization
async function loadUtilization(wcId) {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`/api/workcenters/${wcId}/utilization`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const utilization = await response.json();
        document.getElementById('utilizationData').innerHTML = `
            <p>Utilization Rate: ${utilization.rate}%</p>
            <p>Downtime Hours: ${utilization.downtime_hours}</p>
            <!-- Add more utilization metrics as needed -->
        `;
    } catch (error) {
        console.error('Error loading utilization:', error);
    }
}

// Enable Edit
function enableEdit() {
    const name = document.getElementById('name');
    const description = document.getElementById('description');
    const hourlyCost = document.getElementById('hourly_cost_rate');
    name.innerHTML = `<input type="text" id="editName" value="${name.textContent}">`;
    description.innerHTML = `<input type="text" id="editDescription" value="${description.textContent}">`;
    hourlyCost.innerHTML = `<input type="number" id="editHourlyCost" value="${hourlyCost.textContent.replace('$', '')}">`;
    document.getElementById('saveButton').classList.remove('hidden');
}

// Save WC Changes
async function saveWC() {
    const wcId = new URLSearchParams(window.location.search).get('id');
    const token = localStorage.getItem('token');
    const formData = {
        name: document.getElementById('editName').value,
        description: document.getElementById('editDescription').value,
        hourly_cost_rate: document.getElementById('editHourlyCost').value
    };
    try {
        const response = await fetch(`/api/workcenters/${wcId}/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });
        if (response.ok) {
            alert('Changes saved');
            loadWCDetail(wcId);
            document.getElementById('saveButton').classList.add('hidden');
        } else {
            alert('Error saving changes');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Update WC Status
async function updateWCStatus() {
    const wcId = new URLSearchParams(window.location.search).get('id');
    const token = localStorage.getItem('token');
    const status = document.getElementById('status').value;
    try {
        const response = await fetch(`/api/workcenters/${wcId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status })
        });
        if (response.ok) {
            alert('Status updated');
            loadWCDetail(wcId);
        } else {
            alert('Error updating status');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    
    loadDashboard();
    
    document.getElementById('create-snapshot-btn').addEventListener('click', createSnapshot);
    document.getElementById('snapshot-search-btn').addEventListener('click', searchSnapshots);
    document.getElementById('snapshot-search').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchSnapshots();
        }
    });
    
    setupAutoRefresh();
});

/**
 * Setup auto-refresh for dashboard and snapshots
 */
function setupAutoRefresh() {
    setInterval(() => {
        const activeSection = document.querySelector('section:not(.d-none)');
        if (activeSection) {
            const sectionId = activeSection.id;
            
            if (sectionId === 'dashboard') {
                loadDashboard();
            } else if (sectionId === 'instances') {
                loadInstances();
            } else if (sectionId === 'snapshots') {
                loadSnapshots();
            }
        }
    }, 60000); 
}

/**
 * Initialize the navigation
 */
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            navLinks.forEach(l => l.classList.remove('active'));
            
            this.classList.add('active');
            
            const targetId = this.getAttribute('href').substring(1);
            
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('d-none');
            });
            
            document.getElementById(targetId).classList.remove('d-none');
            
            if (targetId === 'dashboard') {
                loadDashboard();
            } else if (targetId === 'instances') {
                loadInstances();
            } else if (targetId === 'snapshots') {
                loadSnapshots();
            }
            
            window.location.hash = targetId;
        });
    });
    
    if (window.location.hash) {
        const targetId = window.location.hash.substring(1);
        const targetLink = document.querySelector(`.nav-link[href="#${targetId}"]`);
        if (targetLink) {
            targetLink.click();
        }
    }
}

/**
 * Load dashboard data
 */
async function loadDashboard() {
    try {
        document.getElementById('protected-instances-count').innerHTML = '<small>Loading...</small>';
        document.getElementById('total-snapshots-count').innerHTML = '<small>Loading...</small>';
        document.getElementById('total-storage').innerHTML = '<small>Loading...</small>';
        
        const metrics = await api.getMetrics();
        
        document.getElementById('protected-instances-count').textContent = metrics.protected_instances;
        document.getElementById('total-snapshots-count').textContent = metrics.total_snapshots;
        document.getElementById('total-storage').textContent = metrics.total_size_gb.toFixed(1);
        
        const lastBackupEl = document.getElementById('last-backup-time');
        if (metrics.total_snapshots > 0) {
            const snapshots = await api.getSnapshots();
            if (snapshots && snapshots.length > 0) {
                snapshots.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
                const latestSnapshot = snapshots[0];
                const startTime = new Date(latestSnapshot.start_time);
                lastBackupEl.textContent = startTime.toLocaleString();
            }
        } else {
            lastBackupEl.textContent = 'Never';
        }
        
        loadInstancesForDropdown();
        
    } catch (error) {
        showAlert('danger', `Failed to load dashboard data: ${error.message}`);
    }
}

/**
 * Load instances
 */
async function loadInstances() {
    try {
        const tableBody = document.getElementById('instances-table-body');
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Loading instances...</td></tr>';
        
        const instances = await api.getInstances();
        
        tableBody.innerHTML = '';
        
        if (instances.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="6" class="text-center">No instances found</td>';
            tableBody.appendChild(row);
            return;
        }
        
        instances.forEach(instance => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${instance.name}</td>
                <td>${instance.id}</td>
                <td>${instance.type}</td>
                <td>
                    <span class="badge bg-${instance.state === 'running' ? 'success' : 'secondary'}">
                        ${instance.state}
                    </span>
                </td>
                <td>
                    <span class="badge ${instance.backup_enabled ? 'bg-success' : 'bg-danger'}">
                        ${instance.backup_enabled ? 'Enabled' : 'Disabled'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-${instance.backup_enabled ? 'danger' : 'success'} toggle-backup-btn" 
                            data-instance-id="${instance.id}">
                        ${instance.backup_enabled ? 'Disable Backup' : 'Enable Backup'}
                    </button>
                    <button class="btn btn-sm btn-primary create-snapshot-btn"
                            data-instance-id="${instance.id}"
                            data-bs-toggle="modal" 
                            data-bs-target="#createSnapshotModal">
                        Create Snapshot
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        document.querySelectorAll('.toggle-backup-btn').forEach(button => {
            button.addEventListener('click', toggleBackup);
        });
        
        document.querySelectorAll('.create-snapshot-btn').forEach(button => {
            button.addEventListener('click', function() {
                const instanceId = this.getAttribute('data-instance-id');
                document.getElementById('instance-select').value = instanceId;
            });
        });
        
    } catch (error) {
        showAlert('danger', `Failed to load instances: ${error.message}`);
        
        const tableBody = document.getElementById('instances-table-body');
        tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error: ${error.message}</td></tr>`;
    }
}

/**
 * Load instances for the dropdown in the create snapshot modal
 */
async function loadInstancesForDropdown() {
    try {
        const instances = await api.getInstances();
        const select = document.getElementById('instance-select');
        
        select.innerHTML = '<option value="">Choose an instance...</option>';
        
        instances.forEach(instance => {
            if (instance.state === 'running') {
                const option = document.createElement('option');
                option.value = instance.id;
                option.textContent = `${instance.name} (${instance.id})`;
                select.appendChild(option);
            }
        });
        
    } catch (error) {
        console.error(`Failed to load instances for dropdown: ${error.message}`);
    }
}

/**
 * Load snapshots
 */
async function loadSnapshots() {
    try {
        const tableBody = document.getElementById('snapshots-table-body');
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Loading snapshots...</td></tr>';
        
        const snapshots = await api.getSnapshots();
        
        tableBody.innerHTML = '';
        
        if (snapshots.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="6" class="text-center">No snapshots found</td>';
            tableBody.appendChild(row);
            return;
        }
        
        snapshots.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
        
        snapshots.forEach(snapshot => {
            const row = document.createElement('tr');
            
            const startTime = new Date(snapshot.start_time);
            
            row.innerHTML = `
                <td>${snapshot.id}</td>
                <td>${snapshot.volume_id}</td>
                <td>${snapshot.instance_id}</td>
                <td>
                    <span class="badge bg-${snapshot.state === 'completed' ? 'success' : 'warning'}">
                        ${snapshot.state}
                    </span>
                    ${snapshot.progress !== '100%' ? `(${snapshot.progress})` : ''}
                </td>
                <td>${startTime.toLocaleString()}</td>
                <td>${snapshot.delete_after || 'N/A'}</td>
            `;
            
            tableBody.appendChild(row);
        });
        
        const searchTerm = document.getElementById('snapshot-search').value;
        if (searchTerm) {
            searchSnapshots();
        }
        
    } catch (error) {
        showAlert('danger', `Failed to load snapshots: ${error.message}`);
        
        const tableBody = document.getElementById('snapshots-table-body');
        tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error: ${error.message}</td></tr>`;
    }
}

/**
 * Toggle backup for an instance
 */
async function toggleBackup(event) {
    const button = event.target;
    const instanceId = button.getAttribute('data-instance-id');
    
    button.disabled = true;
    const originalText = button.textContent;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Updating...';
    
    try {
        const result = await api.toggleBackup(instanceId);
        
        loadInstances();
        
        loadDashboard();
        
        showAlert('success', `Backup ${result.backup_enabled ? 'enabled' : 'disabled'} for instance ${instanceId}`);
        
    } catch (error) {
        showAlert('danger', `Failed to toggle backup: ${error.message}`);
        
        button.disabled = false;
        button.textContent = originalText;
    }
}

/**
 * Create a new snapshot
 */
async function createSnapshot() {
    const instanceId = document.getElementById('instance-select').value;
    const retentionDays = parseInt(document.getElementById('retention-days').value);
    
    if (!instanceId) {
        showAlert('danger', 'Please select an instance', 'snapshot-creation-alert');
        return;
    }
    
    if (isNaN(retentionDays) || retentionDays < 1 || retentionDays > 365) {
        showAlert('danger', 'Retention days must be between 1 and 365', 'snapshot-creation-alert');
        return;
    }
    
    
    const button = document.getElementById('create-snapshot-btn');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Creating...';
    
    try {
        const result = await api.createSnapshot(instanceId, retentionDays);
        
        showAlert('success', result.message, 'snapshot-creation-alert');
        
        if (!document.getElementById('snapshots').classList.contains('d-none')) {
            loadSnapshots();
        }
        
        loadDashboard();
        
        document.getElementById('instance-select').value = '';
        document.getElementById('retention-days').value = '7';
        
        setTimeout(() => {
            button.disabled = false;
            button.textContent = 'Create Snapshot';
        }, 1500);
        
    } catch (error) {
        showAlert('danger', `Failed to create snapshot: ${error.message}`, 'snapshot-creation-alert');
        
        button.disabled = false;
        button.textContent = 'Create Snapshot';
    }
}

/**
 * Search snapshots
 */
function searchSnapshots() {
    const searchTerm = document.getElementById('snapshot-search').value.toLowerCase();
    const rows = document.querySelectorAll('#snapshots-table-body tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Show an alert message
 */
function showAlert(type, message, elementId = null) {
    const alertElement = elementId ? 
        document.getElementById(elementId) : 
        document.createElement('div');
    
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    if (!elementId) {
        alertElement.style.position = 'fixed';
        alertElement.style.top = '20px';
        alertElement.style.left = '50%';
        alertElement.style.transform = 'translateX(-50%)';
        alertElement.style.zIndex = '9999';
        alertElement.style.minWidth = '300px';
        
        document.body.appendChild(alertElement);
        
        setTimeout(() => {
            alertElement.remove();
        }, 5000);
    } else {
        document.getElementById(elementId).classList.remove('d-none');
    }
}
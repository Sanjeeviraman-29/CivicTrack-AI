const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

let map = null;
let refreshInterval = null;
let currentAssignmentData = null;
let resolvers = [];
let allIssues = []; // Store all issues for filtering

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

function switchTab(tabName) {
    // Hide all tabs
    document.getElementById('assignmentTab').classList.add('hidden');
    document.getElementById('resolutionsTab').classList.add('hidden');
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    if (tabName === 'assignment') {
        document.getElementById('assignmentTab').classList.remove('hidden');
        document.querySelectorAll('.tab-button')[0].classList.add('active');
        setTimeout(() => {
            if (map) map.invalidateSize();
        }, 100);
        loadIssueTable();
    } else if (tabName === 'resolutions') {
        document.getElementById('resolutionsTab').classList.remove('hidden');
        document.querySelectorAll('.tab-button')[1].classList.add('active');
        loadResolutions();
    }
}

async function loadResolvers() {
    try {
        const response = await fetch("http://127.0.0.1:5000/resolvers", {
            headers: { "Authorization": "Bearer " + token }
        });

        if (response.ok) {
            resolvers = await response.json();
            
            // Populate resolver dropdown
            const select = document.getElementById('resolverSelect');
            select.innerHTML = '<option value="">-- Choose a Resolver --</option>';
            
            resolvers.forEach(resolver => {
                const option = document.createElement('option');
                option.value = resolver.id;
                option.text = resolver.name + ' (' + resolver.email + ')';
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error("Error loading resolvers:", error);
    }
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await fetch("http://127.0.0.1:5000/dashboard-stats", {
            headers: { "Authorization": "Bearer " + token }
        });

        if (response.ok) {
            const stats = await response.json();
            
            // Update stat cards with safe property access
            document.getElementById('statTotal').innerText = stats.total_issues || 0;
            document.getElementById('statPending').innerText = stats.by_status?.['Pending'] || 0;
            document.getElementById('statInProgress').innerText = stats.by_status?.['In Progress'] || 0;
            document.getElementById('statResolved').innerText = stats.by_status?.['Resolved'] || 0;
            if (stats.avg_resolution_hours !== undefined) {
                document.getElementById('statAvgTime').innerText = Math.round(stats.avg_resolution_hours) || 0;
            }
            document.getElementById('statVerify').innerText = (stats.verification_success_rate || 0).toFixed(1) + '%';
            document.getElementById('statResolvers').innerText = stats.total_resolvers || 0;
            document.getElementById('statCitizens').innerText = stats.total_citizens || 0;
            
            // Update the timestamp
            document.getElementById('updateTime').innerText = 'just now';
        } else {
            console.error('Dashboard stats response error:', response.status);
        }
    } catch (error) {
        console.error("Error loading stats:", error);
    }
}

// Apply search and filters
async function applyFilters() {
    const searchText = document.getElementById('searchBox').value;
    const status = document.getElementById('statusFilter').value;
    const severity = document.getElementById('severityFilter').value;
    const category = document.getElementById('categoryFilter').value;

    try {
        const response = await fetch("http://127.0.0.1:5000/search-issues", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                search: searchText,
                status: status,
                severity: severity,
                category: category
            })
        });

        if (response.ok) {
            const issues = await response.json();
            displayFilteredIssues(issues);
        }
    } catch (error) {
        console.error("Error applying filters:", error);
    }
}

// Display filtered issues in table
function displayFilteredIssues(issues) {
    const table = document.getElementById('issueTable');
    table.innerHTML = '';

    if (!issues || issues.length === 0) {
        table.innerHTML = '<tr><td colspan="6" class="p-3 text-center text-gray-500">No issues found</td></tr>';
        return;
    }

    issues.forEach(issue => {
        const statusColor = issue.status === 'Resolved' ? 'bg-green-200 text-green-800' :
                           issue.status === 'In Progress' ? 'bg-blue-200 text-blue-800' :
                           issue.status === 'Awaiting Verification' ? 'bg-purple-200 text-purple-800' :
                           'bg-yellow-200 text-yellow-800';

        const severityColor = issue.severity === 'High' ? 'bg-red-200 text-red-800' :
                             issue.severity === 'Medium' ? 'bg-yellow-200 text-yellow-800' :
                             'bg-green-200 text-green-800';

        const createdDate = new Date(issue.created_at).toLocaleDateString();

        table.innerHTML += `
            <tr class="border-b hover:bg-gray-50">
                <td class="p-3 font-semibold">${issue.title}</td>
                <td class="p-3">${issue.category}</td>
                <td class="p-3">
                    <span class="px-3 py-1 rounded-full text-sm font-semibold ${severityColor}">
                        ${issue.severity}
                    </span>
                </td>
                <td class="p-3">
                    <span class="px-3 py-1 rounded-full text-sm font-semibold ${statusColor}">
                        ${issue.status}
                    </span>
                </td>
                <td class="p-3 text-sm text-gray-500">${createdDate}</td>
                <td class="p-3">
                    <button onclick="openAssignModal(${issue.id}, '${issue.title}', ${issue.latitude}, ${issue.longitude})" 
                        class="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700 mr-2">
                        Assign / View
                    </button>
                    <button onclick="viewIssueTimeline(${issue.id})"
                        class="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700">
                        Timeline
                    </button>
                </td>
            </tr>
        `;
    });
}

// View issue timeline
async function viewIssueTimeline(issueId) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/issue-timeline/${issueId}`, {
            headers: { "Authorization": "Bearer " + token }
        });

        if (response.ok) {
            const timeline = await response.json();
            showTimelineModal(timeline);
        }
    } catch (error) {
        console.error("Error loading timeline:", error);
        alert("Error loading issue timeline");
    }
}

// Show timeline modal
function showTimelineModal(timeline) {
    let timelineHTML = '<div class="max-h-96 overflow-y-auto">';
    
    timeline.forEach((event, index) => {
        timelineHTML += `
            <div class="flex mb-4">
                <div class="flex flex-col items-center mr-4">
                    <div class="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-semibold">
                        ${index + 1}
                    </div>
                    ${index < timeline.length - 1 ? '<div class="w-1 h-12 bg-indigo-300"></div>' : ''}
                </div>
                <div class="flex-1 pt-1">
                    <p class="font-semibold text-lg">${event.event}</p>
                    <p class="text-sm text-gray-600">By: ${event.by}</p>
                    <p class="text-sm text-gray-500">${new Date(event.timestamp).toLocaleString()}</p>
                    <p class="text-sm text-gray-700 mt-1">${event.details}</p>
                </div>
            </div>
        `;
    });
    
    timelineHTML += '</div>';
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white p-8 rounded-xl shadow-lg max-w-2xl w-full">
            <h2 class="text-2xl font-semibold mb-6">📅 Issue Timeline</h2>
            ${timelineHTML}
            <button onclick="this.closest('.fixed').remove()" class="mt-6 w-full bg-gray-300 text-gray-800 py-2 rounded-lg font-semibold hover:bg-gray-400">
                Close
            </button>
        </div>
    `;
    document.body.appendChild(modal);
}

async function loadKPI() {
    try {
        // Load dashboard stats - same as loadDashboardStats
        const response = await fetch("http://127.0.0.1:5000/dashboard-stats", {
            headers: { "Authorization": "Bearer " + token }
        });

        if (response.ok) {
            const stats = await response.json();
            
            // Update stat cards
            document.getElementById('statTotal').innerText = stats.total_issues || 0;
            document.getElementById('statPending').innerText = stats.by_status?.['Pending'] || 0;
            document.getElementById('statInProgress').innerText = stats.by_status?.['In Progress'] || 0;
            document.getElementById('statResolved').innerText = stats.by_status?.['Resolved'] || 0;
            if (stats.avg_resolution_hours !== undefined) {
                document.getElementById('statAvgTime').innerText = Math.round(stats.avg_resolution_hours) || 0;
            }
            document.getElementById('statVerify').innerText = (stats.verification_success_rate || 0).toFixed(1) + '%';
            document.getElementById('statResolvers').innerText = stats.total_resolvers || 0;
            document.getElementById('statCitizens').innerText = stats.total_citizens || 0;
        }
    } catch (error) {
        console.error("Error loading KPI:", error);
    }
}

async function loadMap() {
    try {
        const response = await fetch("http://127.0.0.1:5000/map-issues", {
            headers: { "Authorization": "Bearer " + token }
        });

        const data = await response.json();

        const mapContainer = document.getElementById('map');
        
        // Destroy existing map if it exists
        if (map) {
            map.remove();
            map = null;
        }

        // Ensure the map container is visible and properly sized
        mapContainer.style.height = '400px';
        mapContainer.style.width = '100%';

        // Initialize new map - set to Chennai coordinates
        map = L.map('map').setView([13.0827, 80.2707], 12);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        // Add markers for each issue
        if (data && data.length > 0) {
            data.forEach(issue => {
                let color;
                let radius = 8;

                if (issue.severity === "High") {
                    color = "red";
                    radius = 10;
                } else if (issue.severity === "Medium") {
                    color = "orange";
                    radius = 9;
                } else {
                    color = "green";
                    radius = 8;
                }

                const marker = L.circleMarker([issue.latitude, issue.longitude], {
                    color: color,
                    radius: radius,
                    fillOpacity: 0.8,
                    weight: 2
                }).addTo(map);

                marker.bindPopup(`
                    <b>${issue.title}</b><br>
                    Severity: ${issue.severity}<br>
                    Status: ${issue.status}
                `);
            });
        } else {
            console.log("No issues to display on map");
        }

        // Invalidate map size after initialization
        setTimeout(() => {
            if (map) {
                map.invalidateSize();
            }
        }, 100);

    } catch (error) {
        console.error("Error loading map:", error);
    }
}

async function loadIssueTable() {
    try {
        const response = await fetch("http://127.0.0.1:5000/all-issues", {
            headers: { "Authorization": "Bearer " + token }
        });

        const data = await response.json();

        const table = document.getElementById("issueTable");
        table.innerHTML = "";

        if (data && data.length > 0) {
            data.forEach(issue => {
                // Column structure: [0]id, [1]title, [2]description, [3]category, [4]severity, 
                // [5]latitude, [6]longitude, [7]created_by, [8]status, [9]created_at, 
                // [10]updated_at, [11]assigned_to, [12]resolved_at
                
                // Check if issue is unassigned (assigned_to at index [11] is null)
                if (!issue[11] || issue[11] === null) {
                    table.innerHTML += `
                        <tr class="border-b hover:bg-gray-50">
                            <td class="p-3">${issue[1]}</td>
                            <td class="p-3">${issue[3]}</td>
                            <td class="p-3">
                                <span class="px-3 py-1 rounded-full text-sm 
                                    ${issue[4] === 'High' ? 'bg-red-200 text-red-800' :
                                      issue[4] === 'Medium' ? 'bg-yellow-200 text-yellow-800' :
                                      'bg-green-200 text-green-800'}">
                                    ${issue[4]}
                                </span>
                            </td>
                            <td class="p-3">${issue[8]}</td>
                            <td class="p-3">
                                <button onclick="openAssignModal(${issue[0]}, '${issue[1]}', ${issue[5]}, ${issue[6]})"
                                    class="bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700">
                                    Assign
                                </button>
                            </td>
                        </tr>
                    `;
                }
            });
        }
        
        if (table.innerHTML === "") {
            table.innerHTML = '<tr><td colspan="5" class="p-3 text-center text-gray-500">No unassigned issues</td></tr>';
        }
    } catch (error) {
        console.error("Error loading issue table:", error);
    }
}

async function loadResolutions() {
    try {
        const response = await fetch("http://127.0.0.1:5000/resolved-issues", {
            headers: { "Authorization": "Bearer " + token }
        });

        const data = await response.json();

        const table = document.getElementById("resolutionTable");
        table.innerHTML = "";

        if (data && data.length > 0) {
            data.forEach(resolution => {
                // Determine verification status color
                let verificationColor = 'bg-blue-200 text-blue-800';
                if (resolution.verification_status === 'Verified') {
                    verificationColor = 'bg-green-200 text-green-800';
                } else if (resolution.verification_status === 'Rejected') {
                    verificationColor = 'bg-red-200 text-red-800';
                }

                table.innerHTML += `
                    <tr class="border-b hover:bg-gray-50">
                        <td class="p-3">${resolution.title}</td>
                        <td class="p-3">${resolution.category}</td>
                        <td class="p-3">
                            <span class="px-3 py-1 rounded-full text-sm 
                                ${resolution.severity === 'High' ? 'bg-red-200 text-red-800' :
                                  resolution.severity === 'Medium' ? 'bg-yellow-200 text-yellow-800' :
                                  'bg-green-200 text-green-800'}">
                                ${resolution.severity}
                            </span>
                        </td>
                        <td class="p-3">${resolution.resolved_by || 'N/A'}</td>
                        <td class="p-3">${new Date(resolution.resolution_date).toLocaleDateString()}</td>
                        <td class="p-3">
                            <span class="px-3 py-1 rounded-full text-sm font-semibold ${verificationColor}">
                                ${resolution.verification_status}
                            </span>
                        </td>
                        <td class="p-3">
                            ${resolution.image_path ? `
                                <button onclick="viewImage('${resolution.image_path}')" class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">
                                    View
                                </button>
                            ` : '<span class="text-gray-500">-</span>'}
                        </td>
                    </tr>
                `;
            });
        } else {
            table.innerHTML = '<tr><td colspan="7" class="p-3 text-center text-gray-500">No resolved issues</td></tr>';
        }
    } catch (error) {
        console.error("Error loading resolutions:", error);
    }
}

function viewImage(imagePath) {
    window.open(imagePath, '_blank');
}

function openAssignModal(issueId, issueTitle, lat, lng) {
    document.getElementById('modalIssueId').innerText = issueId;
    document.getElementById('modalIssueTitle').innerText = issueTitle;
    document.getElementById('modalLat').innerText = lat.toFixed(4);
    document.getElementById('modalLng').innerText = lng.toFixed(4);
    document.getElementById('resolverSelect').value = '';
    document.getElementById('navLink').checked = false;
    
    currentAssignmentData = { issueId, lat, lng, issueTitle };
    document.getElementById('assignModal').classList.remove('hidden');
}

function closeAssignModal() {
    document.getElementById('assignModal').classList.add('hidden');
    currentAssignmentData = null;
}

async function confirmAssign() {
    const resolverId = document.getElementById('resolverSelect').value;
    const generateNav = document.getElementById('navLink').checked;
    
    if (!resolverId) {
        alert("Please select a resolver");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/assign-issue", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                issue_id: currentAssignmentData.issueId,
                resolver_id: resolverId
            })
        });

        if (response.ok) {
            alert("Issue assigned successfully!");
            
            // Generate navigation link if requested
            if (generateNav) {
                const navUrl = `https://www.google.com/maps/dir/?api=1&destination=${currentAssignmentData.lat},${currentAssignmentData.lng}`;
                
                // Store navigation link for resolver reference
                const selectedResolver = document.getElementById('resolverSelect').options[document.getElementById('resolverSelect').selectedIndex];
                
                // Copy to clipboard and show to admin
                navigator.clipboard.writeText(navUrl).then(() => {
                    alert(`Navigation link copied to clipboard:\n${navUrl}\n\nShare this with the resolver.`);
                });
            }
            
            closeAssignModal();
            loadIssueTable();
            loadMap();
            loadKPI();
        } else {
            alert("Error assigning issue");
        }
    } catch (error) {
        alert("Error: " + error.message);
        console.error("Assignment error:", error);
    }
}

// Function to refresh all dashboard data
async function refreshDashboard() {
    console.log("Refreshing dashboard...");
    await loadKPI();
    await loadMap();
    await loadIssueTable();
}

// Initial load
loadResolvers();
loadKPI();
loadDashboardStats();
loadMap();
loadIssueTable();

// Auto-refresh every 30 seconds to show new issues in real-time
refreshInterval = setInterval(() => {
    console.log("Auto-refreshing dashboard...");
    refreshDashboard();
    loadDashboardStats();
}, 30000);

// Close modal when clicking outside
document.getElementById('assignModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeAssignModal();
    }
});

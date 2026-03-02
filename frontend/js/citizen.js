const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

let currentVerificationData = null;
let locationMap = null;
let locationMarker = null;
let allMyIssues = []; // Store all issues for filtering

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

function switchTab(tabName) {
    // Hide all tabs
    document.getElementById("reportTab").classList.add("hidden");
    document.getElementById("verifyTab").classList.add("hidden");
    document.getElementById("myIssuesTab").classList.add("hidden");

    // Remove active class from all buttons
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));

    // Show selected tab
    if (tabName === 'report') {
        document.getElementById("reportTab").classList.remove("hidden");
        document.querySelectorAll(".tab-btn")[0].classList.add("active");
        // Initialize map when report tab is opened
        setTimeout(() => {
            initializeLocationMap();
        }, 100);
    } else if (tabName === 'verify') {
        document.getElementById("verifyTab").classList.remove("hidden");
        document.querySelectorAll(".tab-btn")[1].classList.add("active");
        loadPendingVerifications();
    } else if (tabName === 'myissues') {
        document.getElementById("myIssuesTab").classList.remove("hidden");
        document.querySelectorAll(".tab-btn")[2].classList.add("active");
    }
}

function initializeLocationMap() {
    if (locationMap) return; // Already initialized
    
    // Default center: Chennai, India
    const defaultLat = 13.0827;
    const defaultLng = 80.2707;

    locationMap = L.map('locationMap').setView([defaultLat, defaultLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(locationMap);

    // Handle map click to select location
    locationMap.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        setLocation(lat, lng);
    });

    // Get user's current location if available
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;
                
                // Center map on user location
                locationMap.setView([userLat, userLng], 15);
                
                // Add user location marker
                L.circleMarker([userLat, userLng], {
                    color: "blue",
                    radius: 8,
                    fillOpacity: 0.8,
                    weight: 2,
                    popup: "Your Location"
                }).addTo(locationMap);
            },
            function() {
                console.log("Geolocation not available, using default location");
            }
        );
    }

    // Add instructions text
    const info = L.control();
    info.onAdd = function() {
        const div = L.DomUtil.create('div', 'bg-white p-3 rounded shadow text-sm');
        div.innerHTML = '<strong>📍 Click on map to set location</strong>';
        div.style.backgroundColor = 'white';
        div.style.padding = '10px';
        div.style.borderRadius = '5px';
        div.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';
        return div;
    };
    info.addTo(locationMap);
}

function setLocation(lat, lng) {
    lat = parseFloat(lat);
    lng = parseFloat(lng);

    // Update hidden input fields
    document.getElementById("latitude").value = lat;
    document.getElementById("longitude").value = lng;

    // Update displayed coordinates
    document.getElementById("selectedLatitude").innerText = lat.toFixed(6);
    document.getElementById("selectedLongitude").innerText = lng.toFixed(6);

    // Remove previous marker
    if (locationMarker) {
        locationMap.removeLayer(locationMarker);
    }

    // Add new marker at selected location
    locationMarker = L.circleMarker([lat, lng], {
        color: "red",
        radius: 10,
        fillOpacity: 0.8,
        weight: 2,
        popup: `Selected Location<br>Lat: ${lat.toFixed(6)}<br>Lng: ${lng.toFixed(6)}`
    }).addTo(locationMap).openPopup();

    // Center map on selected location
    locationMap.setView([lat, lng], 15);
}

async function createIssue() {

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const latitude = document.getElementById("latitude").value;
    const longitude = document.getElementById("longitude").value;

    if (!title || !description || !latitude || !longitude) {
        alert("Please fill in all fields:\n- Title\n- Description\n- Location (click on map)");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/create-issue", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                title,
                description,
                latitude: parseFloat(latitude),
                longitude: parseFloat(longitude)
            })
        });

        if (response.ok) {
            alert("Complaint Submitted Successfully!");
            // Clear form fields
            document.getElementById("title").value = "";
            document.getElementById("description").value = "";
            document.getElementById("latitude").value = "";
            document.getElementById("longitude").value = "";
            document.getElementById("selectedLatitude").innerText = "Click on map";
            document.getElementById("selectedLongitude").innerText = "Click on map";
            
            // Clear map marker
            if (locationMarker) {
                locationMap.removeLayer(locationMarker);
                locationMarker = null;
            }
            
            loadMyIssues();
        } else {
            const data = await response.json();
            alert("Error submitting complaint: " + (data.message || "Unknown error"));
        }
    } catch (error) {
        alert("Error submitting complaint: " + error.message);
        console.error("Create issue error:", error);
    }
}

async function loadMyIssues() {
    try {
        const response = await fetch("http://127.0.0.1:5000/my-issues", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();
        allMyIssues = data; // Store for filtering

        const container = document.getElementById("issuesContainer");
        container.innerHTML = "";

        if (data && data.length > 0) {
            displayMyIssues(data);
        } else {
            container.innerHTML = '<div class="col-span-full text-center py-12"><p class="text-gray-500 text-lg">No issues submitted yet</p></div>';
        }
    } catch (error) {
        console.error("Error loading issues:", error);
    }
}

function displayMyIssues(issues) {
    const container = document.getElementById("issuesContainer");
    container.innerHTML = "";

    if (!issues || issues.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center py-12"><p class="text-gray-500">No issues match filters</p></div>';
        return;
    }

    issues.forEach(issue => {
        // Handle array-based response
        const id = issue[0];
        const title = issue[1];
        const description = issue[2];
        const category = issue[3];
        const severity = issue[4];
        const status = issue[7];

        const severityColor = severity === 'High' ? 'bg-red-200 text-red-800' : 
                             severity === 'Medium' ? 'bg-yellow-200 text-yellow-800' : 
                             'bg-green-200 text-green-800';

        const statusColor = status === 'Resolved' ? 'bg-green-100 text-green-800' :
                           status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                           status === 'Awaiting Verification' ? 'bg-purple-100 text-purple-800' :
                           'bg-yellow-100 text-yellow-800';

        container.innerHTML += `
            <div class="bg-white p-5 rounded-xl shadow-md border-l-4 border-indigo-600 hover:shadow-lg transition">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="text-lg font-semibold">${title}</h3>
                    <span class="px-3 py-1 text-sm rounded-full font-semibold ${severityColor}">
                        ${severity}
                    </span>
                </div>
                <p class="text-gray-600 mb-3 text-sm">${description}</p>
                <div class="flex justify-between items-center">
                    <div class="flex gap-2">
                        <span class="px-2 py-1 text-xs bg-gray-200 text-gray-800 rounded">
                            ${category}
                        </span>
                        <span class="px-2 py-1 text-xs font-semibold ${statusColor} rounded">
                            ${status}
                        </span>
                    </div>
                    <button onclick="viewIssueTimeline(${id})" class="text-indigo-600 hover:text-indigo-800 text-sm font-semibold">
                        📅 Timeline
                    </button>
                </div>
            </div>
        `;
    });
}

function filterMyIssues() {
    const statusFilter = document.getElementById('myStatusFilter').value;
    const severityFilter = document.getElementById('mySeverityFilter').value;

    const filtered = allMyIssues.filter(issue => {
        const status = issue[7];
        const severity = issue[4];

        const statusMatch = statusFilter === 'All' || status === statusFilter;
        const severityMatch = severityFilter === 'All' || severity === severityFilter;

        return statusMatch && severityMatch;
    });

    displayMyIssues(filtered);
}

function viewIssueTimeline(issueId) {
    fetch(`http://127.0.0.1:5000/issue-timeline/${issueId}`, {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(r => r.json())
    .then(timeline => {
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
    })
    .catch(err => alert('Error loading timeline: ' + err.message));
}

async function loadMyIssues() {
    try {
        const response = await fetch("http://127.0.0.1:5000/my-issues", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();
        allMyIssues = data; // Store for filtering

        const container = document.getElementById("issuesContainer");
        container.innerHTML = "";

        if (data && data.length > 0) {
            displayMyIssues(data);
        } else {
            container.innerHTML = '<div class="col-span-full text-center py-12"><p class="text-gray-500 text-lg">No issues submitted yet</p></div>';
        }
    } catch (error) {
        console.error("Error loading issues:", error);
    }
}

async function loadPendingVerifications() {
    try {
        const response = await fetch("http://127.0.0.1:5000/pending-verifications", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();
        const container = document.getElementById("verificationContainer");
        container.innerHTML = "";

        if (data && data.length > 0) {
            data.forEach(verification => {
                const severityColor = verification.severity === 'High' ? 'bg-red-100 text-red-800' :
                    verification.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800';

                container.innerHTML += `
                    <div class="bg-white p-6 rounded-xl shadow-md border-l-4 border-blue-600">
                        <div class="flex justify-between items-start mb-3">
                            <div>
                                <h3 class="text-lg font-semibold">${verification.title}</h3>
                                <p class="text-sm text-gray-500">Completed by: ${verification.resolver_name || 'Unknown'}</p>
                            </div>
                            <span class="px-3 py-1 rounded-full text-sm font-semibold ${severityColor}">
                                ${verification.severity}
                            </span>
                        </div>
                        
                        <p class="text-gray-600 mb-3 text-sm">${verification.description}</p>
                        
                        ${verification.image_path ? `
                            <div class="mb-4">
                                <p class="font-semibold text-sm mb-2">Work Completion Photo:</p>
                                <img src="${verification.image_path}" alt="Work completed" class="w-full rounded-lg max-h-48 object-contain border border-gray-200">
                            </div>
                        ` : ''}
                        
                        ${verification.comments ? `
                            <div class="bg-gray-100 p-3 rounded-lg mb-4">
                                <p class="font-semibold text-sm mb-1">Resolver's Notes:</p>
                                <p class="text-sm text-gray-700">${verification.comments}</p>
                            </div>
                        ` : ''}

                        <button onclick="openVerificationModal(${verification.id}, '${verification.title}', '${verification.description}', '${verification.image_path || ''}', '${verification.comments || ''}')"
                            class="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700">
                            Review & Verify
                        </button>
                    </div>
                `;
            });
        } else {
            container.innerHTML = '<div class="col-span-full text-center py-12"><p class="text-gray-500 text-lg">No pending verifications</p></div>';
        }
    } catch (error) {
        console.error("Error loading verifications:", error);
        document.getElementById("verificationContainer").innerHTML = '<p class="text-red-500">Error loading verifications</p>';
    }
}

function openVerificationModal(issueId, title, description, imagePath, comments) {
    document.getElementById("verifyIssueTitle").innerText = title;
    document.getElementById("verifyDescription").innerText = description;
    document.getElementById("verifyComments").innerText = comments || "(No additional comments)";
    document.getElementById("verifyImage").src = imagePath || "";
    document.getElementById("rejectionReason").value = "";
    
    currentVerificationData = { issueId, title };
    document.getElementById("verificationModal").classList.remove("hidden");
}

function closeVerificationModal() {
    document.getElementById("verificationModal").classList.add("hidden");
    currentVerificationData = null;
}

async function approveVerification() {
    if (!currentVerificationData) return;

    try {
        const response = await fetch("http://127.0.0.1:5000/verify-issue", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                issue_id: currentVerificationData.issueId
            })
        });

        if (response.ok) {
            alert("✓ Work approved! Issue marked as Resolved.");
            closeVerificationModal();
            loadPendingVerifications();
            loadMyIssues();
        } else {
            const data = await response.json();
            alert("Error: " + (data.message || data.error));
        }
    } catch (error) {
        alert("Error: " + error.message);
        console.error("Verification error:", error);
    }
}

async function rejectVerification() {
    if (!currentVerificationData) return;

    const reason = document.getElementById("rejectionReason").value.trim();
    if (!reason) {
        alert("Please provide a reason for rejection");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/reject-issue", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                issue_id: currentVerificationData.issueId,
                reason: reason
            })
        });

        if (response.ok) {
            alert("✗ Work rejected. The resolver has been notified to redo the work.");
            closeVerificationModal();
            loadPendingVerifications();
            loadMyIssues();
        } else {
            const data = await response.json();
            alert("Error: " + (data.message || data.error));
        }
    } catch (error) {
        alert("Error: " + error.message);
        console.error("Rejection error:", error);
    }
}

loadMyIssues();

// Initialize map on page load
setTimeout(() => {
    initializeLocationMap();
}, 500);
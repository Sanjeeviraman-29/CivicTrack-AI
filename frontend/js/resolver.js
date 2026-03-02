const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

let miniMap = null;
let currentNavigationData = null;
let currentCompletionData = null;
let refreshInterval = null;
let allAssignments = []; // Store all assignments for filtering

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

async function loadAssignments() {
    try {
        const response = await fetch("http://127.0.0.1:5000/my-assignments", {
            headers: { "Authorization": "Bearer " + token }
        });

        if (!response.ok) {
            console.error("Error loading assignments:", response.status);
            return;
        }

        const data = await response.json();
        allAssignments = data || []; // Store all assignments for filtering
        displayResolverAssignments(allAssignments);
        
        // Update counts
        let assignedCount = 0;
        if (data && data.length > 0) {
            assignedCount = data.filter(a => a.status !== 'Resolved').length;
        }
        document.getElementById("assignedCount").innerText = assignedCount;
        
        // Count completed
        const completedCount = data && data.length > 0 ? data.filter(a => a.status === 'Resolved').length : 0;
        document.getElementById("completedCount").innerText = completedCount;

    } catch (error) {
        console.error("Error loading assignments:", error);
    }
}

function displayResolverAssignments(assignments) {
    const table = document.getElementById("assignmentTable");
    table.innerHTML = "";

    if (assignments && assignments.length > 0) {
        assignments.forEach(assignment => {
            // Determine status color
            let statusClass = 'status-assigned';
            if (assignment.status === 'In Progress') {
                statusClass = 'status-in-progress';
            }

            table.innerHTML += `
                <tr class="border-b hover:bg-gray-50">
                    <td class="p-3 font-semibold">${assignment.title}</td>
                    <td class="p-3">${assignment.category}</td>
                    <td class="p-3">
                        <span class="px-3 py-1 rounded-full text-sm 
                            ${assignment.severity === 'High' ? 'bg-red-200 text-red-800' :
                              assignment.severity === 'Medium' ? 'bg-yellow-200 text-yellow-800' :
                              'bg-green-200 text-green-800'}">
                            ${assignment.severity}
                        </span>
                    </td>
                    <td class="p-3">
                        <span class="status-badge ${statusClass}">
                            ${assignment.status}
                        </span>
                    </td>
                    <td class="p-3">
                        <button onclick="openNavigation(${assignment.id}, '${assignment.title}', ${assignment.latitude}, ${assignment.longitude})"
                            class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                            View Map
                        </button>
                    </td>
                    <td class="p-3">
                        ${assignment.status !== 'Resolved' ? `
                            <button onclick="openCompleteModal(${assignment.id}, '${assignment.title}')"
                                class="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                                Mark Done
                            </button>
                        ` : `
                            <span class="text-green-600 font-semibold">✓ Completed</span>
                        `}
                    </td>
                </tr>
            `;
        });
    } else {
        table.innerHTML = '<tr><td colspan="6" class="p-3 text-center text-gray-500">No assignments matching filters</td></tr>';
    }
}

function filterResolverAssignments() {
    const filterValue = document.getElementById("resolverStatusFilter").value;
    
    if (filterValue === "") {
        // Show all assignments
        displayResolverAssignments(allAssignments);
    } else {
        // Filter by selected status
        const filtered = allAssignments.filter(assignment => assignment.status === filterValue);
        displayResolverAssignments(filtered);
    }
}

function openNavigation(issueId, issueTitle, latitude, longitude) {
    document.getElementById("navIssueTitle").innerText = issueTitle;
    document.getElementById("navCoordinates").innerText = `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
    
    currentNavigationData = { issueId, issueTitle, latitude, longitude };
    
    // Initialize mini map
    setTimeout(() => {
        initializeMiniMap(latitude, longitude);
    }, 100);
    
    document.getElementById("navModal").classList.remove("hidden");
}

function closeNavModal() {
    document.getElementById("navModal").classList.add("hidden");
    if (miniMap) {
        miniMap.remove();
        miniMap = null;
    }
}

function initializeMiniMap(latitude, longitude) {
    const mapContainer = document.getElementById('miniMap');
    
    // Destroy existing map if it exists
    if (miniMap) {
        miniMap.remove();
        miniMap = null;
    }

    // Initialize new map
    miniMap = L.map('miniMap').setView([latitude, longitude], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(miniMap);

    // Add marker for destination
    L.circleMarker([latitude, longitude], {
        color: "red",
        radius: 10,
        fillOpacity: 0.8,
        weight: 2
    }).addTo(miniMap);

    // Add marker for current location if geolocation is available
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            L.circleMarker([userLat, userLng], {
                color: "blue",
                radius: 8,
                fillOpacity: 0.8,
                weight: 2
            }).bindPopup("Your Location").addTo(miniMap);
            
            // Fit map to show both locations
            miniMap.fitBounds([
                [Math.min(userLat, latitude), Math.min(userLng, longitude)],
                [Math.max(userLat, latitude), Math.max(userLng, longitude)]
            ]);
        });
    }

    // Invalidate map size
    setTimeout(() => {
        if (miniMap) {
            miniMap.invalidateSize();
        }
    }, 100);
}

function openGoogleMaps() {
    if (currentNavigationData) {
        const { latitude, longitude } = currentNavigationData;
        const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
        window.open(mapsUrl, '_blank');
    }
}

function openCompleteModal(issueId, issueTitle) {
    document.getElementById("completeIssueId").innerText = issueId;
    document.getElementById("completeIssueTitle").innerText = issueTitle;
    document.getElementById("completionComments").value = "";
    
    currentCompletionData = { issueId, issueTitle };
    document.getElementById("completeModal").classList.remove("hidden");
}

function closeCompleteModal() {
    document.getElementById("completeModal").classList.add("hidden");
    currentCompletionData = null;
}

function previewImage() {
    const fileInput = document.getElementById("completionImage");
    const preview = document.getElementById("imagePreview");
    const previewText = document.getElementById("imagePreviewText");
    
    if (fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        
        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert("File size exceeds 5MB limit");
            fileInput.value = "";
            previewText.innerText = "No image selected";
            preview.classList.add("hidden");
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove("hidden");
            previewText.innerText = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`;
        };
        reader.readAsDataURL(file);
    } else {
        previewText.innerText = "No image selected";
        preview.classList.add("hidden");
    }
}

async function confirmCompletion() {
    const imageInput = document.getElementById("completionImage");
    const comments = document.getElementById("completionComments").value;

    if (!currentCompletionData) return;

    // Check if image is selected
    if (!imageInput.files || imageInput.files.length === 0) {
        alert("Please select a completion photo");
        return;
    }

    try {
        const formData = new FormData();
        formData.append("issue_id", currentCompletionData.issueId);
        formData.append("image", imageInput.files[0]);
        formData.append("comments", comments);

        const response = await fetch("http://127.0.0.1:5000/complete-issue-with-image", {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token
            },
            body: formData
        });

        if (response.ok) {
            alert("Work completion uploaded successfully!\nAwating citizen verification...");
            closeCompleteModal();
            loadAssignments();
        } else {
            const data = await response.json();
            alert("Error: " + (data.message || data.error || "Unknown error"));
        }
    } catch (error) {
        alert("Error: " + error.message);
        console.error("Completion error:", error);
    }
}

// Initial load
loadAssignments();

// Auto-refresh every 30 seconds
refreshInterval = setInterval(() => {
    loadAssignments();
}, 30000);

// Close modals when clicking outside
document.getElementById('navModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeNavModal();
    }
});

document.getElementById('completeModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeCompleteModal();
    }
});

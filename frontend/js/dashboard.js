const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

async function loadCategoryStats() {

    const response = await fetch("http://127.0.0.1:5000/category-stats", {
        headers: { "Authorization": "Bearer " + token }
    });

    const data = await response.json();

    const labels = data.map(item => item.category);
    const counts = data.map(item => item.count);

    new Chart(document.getElementById("categoryChart"), {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Issues",
                data: counts
            }]
        }
    });
}

async function loadSeverityStats() {

    const response = await fetch("http://127.0.0.1:5000/severity-stats", {
        headers: { "Authorization": "Bearer " + token }
    });

    const data = await response.json();

    const labels = data.map(item => item.severity);
    const counts = data.map(item => item.count);

    new Chart(document.getElementById("severityChart"), {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                data: counts
            }]
        }
    });
}

async function loadKPI() {

    const response = await fetch("http://127.0.0.1:5000/status-stats", {
        headers: { "Authorization": "Bearer " + token }
    });

    const data = await response.json();

    let total = 0;
    let pending = 0;
    let resolved = 0;

    data.forEach(item => {
        total += item.count;

        if (item.status === "Pending") pending = item.count;
        if (item.status === "Resolved") resolved = item.count;
    });

    document.getElementById("totalIssues").innerText = total;
    document.getElementById("pendingIssues").innerText = pending;
    document.getElementById("resolvedIssues").innerText = resolved;
}

async function loadMap() {

    const response = await fetch("http://127.0.0.1:5000/map-issues", {
        headers: { "Authorization": "Bearer " + token }
    });

    const data = await response.json();

    const map = L.map('map').setView([13.0827, 80.2707], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    data.forEach(issue => {

        let color;

        if (issue.severity === "High") color = "red";
        else if (issue.severity === "Medium") color = "orange";
        else color = "green";

        const marker = L.circleMarker([issue.latitude, issue.longitude], {
            color: color,
            radius: 8,
            fillOpacity: 0.8
        }).addTo(map);

        marker.bindPopup(`
            <b>${issue.title}</b><br>
            Severity: ${issue.severity}<br>
            Status: ${issue.status}
        `);
    });
}

async function loadIssueTable() {

    const response = await fetch("http://127.0.0.1:5000/all-issues", {
        headers: { "Authorization": "Bearer " + token }
    });

    const data = await response.json();

    const table = document.getElementById("issueTable");
    table.innerHTML = "";

    data.forEach(issue => {

        table.innerHTML += `
            <tr class="border-b">
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
                <td class="p-3">${issue[7]}</td>
                <td class="p-3">
                    <select onchange="updateStatus(${issue[0]}, this.value)"
                        class="border p-2 rounded">
                        <option value="">Change</option>
                        <option value="Pending">Pending</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Resolved">Resolved</option>
                    </select>
                </td>
            </tr>
        `;
    });
}

async function updateStatus(issueId, newStatus) {

    if (!newStatus) return;

    await fetch(`http://127.0.0.1:5000/update-status/${issueId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ status: newStatus })
    });

    loadIssueTable();
    loadKPI();
}

loadCategoryStats();
loadSeverityStats();
loadKPI();
loadMap();
loadIssueTable();
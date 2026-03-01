const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

async function createIssue() {

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const latitude = document.getElementById("latitude").value;
    const longitude = document.getElementById("longitude").value;

    const response = await fetch("http://127.0.0.1:5000/create-issue", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            title,
            description,
            latitude,
            longitude
        })
    });

    if (response.ok) {
        alert("Complaint Submitted Successfully!");
        loadMyIssues();
    } else {
        alert("Error submitting complaint");
    }
}

async function loadMyIssues() {

    const response = await fetch("http://127.0.0.1:5000/my-issues", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const data = await response.json();

    const container = document.getElementById("issuesContainer");
    container.innerHTML = "";

    data.forEach(issue => {

        container.innerHTML += `
            <div class="bg-white p-5 rounded-xl shadow-md">
                <h3 class="text-lg font-semibold mb-2">${issue[1]}</h3>
                <p class="text-gray-600 mb-2">${issue[2]}</p>
                <span class="inline-block px-3 py-1 text-sm rounded-full 
                    ${issue[4] === 'High' ? 'bg-red-200 text-red-800' : 
                      issue[4] === 'Medium' ? 'bg-yellow-200 text-yellow-800' : 
                      'bg-green-200 text-green-800'}">
                    ${issue[4]}
                </span>
                <p class="mt-2 text-sm text-gray-500">Status: ${issue[7]}</p>
            </div>
        `;
    });
}

loadMyIssues();
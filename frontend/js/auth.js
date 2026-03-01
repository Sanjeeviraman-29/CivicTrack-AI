async function login() {

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email,
            password
        })
    });

    const data = await response.json();

    if (response.ok) {

        localStorage.setItem("token", data.token);

        // Decode token to check role
        const payload = JSON.parse(atob(data.token.split('.')[1]));

        if (payload.role === "admin") {
            window.location.href = "dashboard.html";
        } else {
            window.location.href = "citizen.html";
        }

    } else {
        alert("Invalid credentials");
    }
}
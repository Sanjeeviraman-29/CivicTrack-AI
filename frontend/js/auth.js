async function login() {

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please fill in all fields");
        return;
    }

    try {
        console.log("Attempting login for email:", email);
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

        console.log("Response status:", response.status);
        const data = await response.json();

        if (response.ok) {

            localStorage.setItem("token", data.token);

            // Decode token to check role
            const payload = JSON.parse(atob(data.token.split('.')[1]));

            // Redirect based on role
            if (payload.role === "admin") {
                window.location.href = "dashboard.html";
            } else if (payload.role === "resolver") {
                window.location.href = "resolver.html";
            } else {
                window.location.href = "citizen.html";
            }

        } else {
            alert("Login failed: " + (data.message || "Invalid credentials"));
            console.error("Login error:", data);
        }
    } catch (error) {
        console.error("Fetch error:", error);
        alert("Error during login: " + error.message + ". Make sure the backend server is running on http://127.0.0.1:5000");
    }
}
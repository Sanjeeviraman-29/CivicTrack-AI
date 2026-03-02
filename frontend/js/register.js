async function register() {

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    if (!name || !email || !password) {
        alert("Please fill in all fields");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name,
                email,
                password,
                role: role
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Registration successful! Please login.");
            window.location.href = "login.html";
        } else {
            alert("Registration failed: " + (data.message || "Unknown error"));
            console.error("Registration error:", data);
        }
    } catch (error) {
        alert("Error during registration: " + error.message);
        console.error("Registration error:", error);
    }
}
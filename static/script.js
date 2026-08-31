let mode = "login";

function showLogin() {
    mode = "login";

    document.getElementById("submitBtn").innerText = "Login";

    document.getElementById("loginTab").classList.add("active");
    document.getElementById("signupTab").classList.remove("active");

    document.getElementById("message").innerText = "";
}


function showSignup() {
    mode = "signup";

    document.getElementById("submitBtn").innerText = "Sign Up";

    document.getElementById("signupTab").classList.add("active");
    document.getElementById("loginTab").classList.remove("active");

    document.getElementById("message").innerText = "";
}


document
    .getElementById("authForm")
    .addEventListener("submit", async function (event) {

        event.preventDefault();

        const email =
            document.getElementById("email").value.trim();

        const password =
            document.getElementById("password").value.trim();

        const message =
            document.getElementById("message");

        const endpoint =
            mode === "login"
                ? "/auth/login"
                : "/auth/signup";

        message.innerText = "Please wait...";

        try {

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                message.innerText =
                    data.detail || "Something went wrong";
                return;
            }

            if (mode === "login") {

                localStorage.setItem(
                    "access_token",
                    data.access_token
                );

                message.innerText =
                    "Login successful! Token saved.";

            } else {

                message.innerText =
                    "Account created successfully. You can now login.";
            }

        } catch (error) {

            message.innerText =
                "Server connection failed.";
        }
    });
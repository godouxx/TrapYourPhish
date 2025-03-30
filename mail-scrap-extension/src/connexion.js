document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("login").addEventListener("click", async () => {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("http://localhost:5000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });
            const data = await response.json();

            if (data.token) {
                localStorage.setItem("token", data.token);
                alert("Connexion réussie !");
            } else {
                alert("Erreur de connexion");
            }
        } catch (error) {
            console.error("Erreur d'authentification:", error);
        }
    });
});

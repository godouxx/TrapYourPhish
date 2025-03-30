document.querySelector("form").addEventListener("submit", async (event) => {
    event.preventDefault();
  
    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;
  
    try {
      const response = await fetch("http://localhost:8080/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
  
      if (response.ok) {
        const data = await response.json();
        // Stocke le token dans le stockage local
        localStorage.setItem("authToken", data.user_cookie);
        alert("Connexion réussie !");
        // Redirige vers la page d'accueil
        window.location.href = "/src/dashboard.html";
      } else {
        const error = await response.json();
        alert(`Erreur : ${error.message}`);
      }
    } catch (err) {
      console.error("Erreur lors de la connexion :", err);
      alert("Une erreur est survenue. Veuillez réessayer.");
    }
  });
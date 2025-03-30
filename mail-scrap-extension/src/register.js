document.querySelector("form").addEventListener("submit", async (event) => {
  event.preventDefault(); // Empêche le rechargement de la page

  const email = document.querySelector("#email").value;
  const password = document.querySelector("#password").value;

  try {
    const response = await fetch("http://localhost:8080/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

    if (response.ok) {
      const data = await response.json();
      alert("Inscription réussie !");
      // Redirige vers la page de connexion
      window.location.href = "/src/connexion.html";
    } else {
      const error = await response.json();
      alert(`Erreur : ${error.message}`);
    }
  } catch (err) {
    console.error("Erreur lors de l'inscription :", err);
    alert("Une erreur est survenue. Veuillez réessayer.");
  }
});
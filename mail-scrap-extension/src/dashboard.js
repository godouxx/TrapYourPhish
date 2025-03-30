// Vérifie si un token est présent dans le stockage local
const token = localStorage.getItem("authToken");

if (!token) {
  // Si aucun token, redirige vers la page de connexion
  window.location.href = "connexion.html";
} else {
  console.log("Utilisateur connecté avec le token :", token);
}

// Ajoutez un gestionnaire d'événements pour le bouton central
document.getElementById("central-button").addEventListener("click", () => {
  alert("Action centrale déclenchée !");
});

document.getElementById("logout-button").addEventListener("click", () => {
    // Supprime le token du stockage local
    localStorage.removeItem("authToken");
    // Redirige vers la page de connexion
    window.location.href = "/src/connexion.html";
  });
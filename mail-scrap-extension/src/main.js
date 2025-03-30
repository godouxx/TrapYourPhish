function loadPage(page) {
  console.log("Chargement de la page:", page);

  const app = document.getElementById("app");

  // Add fade-out effect
  app.classList.add("fade-out");

  setTimeout(() => {
    // Utilisez un chemin relatif correct pour charger les fichiers HTML
    fetch(`src/${page}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            `Erreur lors du chargement de la page: ${response.statusText}`
          );
        }
        return response.text();
      })
      .then((html) => {
        app.innerHTML = html;

        // Charger dynamiquement le script JS associé
        const scriptName = page.replace(".html", ".js");
        const existingScript = document.getElementById("dynamic-script");

        if (existingScript) {
          existingScript.remove(); // Supprime l'ancien script pour éviter les doublons
        }

        const script = document.createElement("script");
        script.id = "dynamic-script";
        script.src = `src/${scriptName}`;
        script.type = "module";
        document.body.appendChild(script);

        // Charger dynamiquement le CSS associé
        const cssLink = document.getElementById("dynamic-css");
        if (cssLink) {
          cssLink.href = `src/${page.replace(".html", ".css")}`;
        } else {
          const link = document.createElement("link");
          link.id = "dynamic-css";
          link.rel = "stylesheet";
          link.href = `src/${page.replace(".html", ".css")}`;
          document.head.appendChild(link);
        }

        // Ajouter les gestionnaires d'événements pour la navigation
        if (page === "connexion.html") {
          const registerLink = document.getElementById("register-link");
          if (registerLink) {
            registerLink.addEventListener("click", () => loadPage("register.html"));
          }
        } else if (page === "register.html") {
          const backToLoginLink = document.getElementById("back-to-login");
          if (backToLoginLink) {
            backToLoginLink.addEventListener("click", () => loadPage("connexion.html"));
          }
        }

        // Add fade-in effect
        app.classList.remove("fade-out");
        app.classList.add("fade-in");

        // Remove the fade-in class after the animation completes
        setTimeout(() => {
          app.classList.remove("fade-in");
        }, 300); // Durée de l'animation
      })
      .catch((error) => {
        console.error("Erreur lors du chargement de la page :", error);
      });
  }, 300); // Durée de l'animation de fade-out
}

// Vérifie si un token est présent pour la persistance de la connexion
const token = localStorage.getItem("authToken");
if (token) {
  // Si un token est présent, redirige vers le tableau de bord
  loadPage("dashboard.html");
} else {
  // Sinon, charge la page de connexion
  loadPage("connexion.html");
}
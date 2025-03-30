function loadPage(page) {
  console.log("Chargement de la page:", page);

  const app = document.getElementById("app");

  // Add fade-out effect
  app.classList.add("fade-out");

  setTimeout(() => {
    fetch(`/src/${page}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Erreur lors du chargement de la page: ${response.statusText}`);
        }
        return response.text();
      })
      .then((html) => {
        app.innerHTML = html;

        // Update the CSS dynamically
        const cssLink = document.getElementById("dynamic-css");
        if (cssLink) {
          cssLink.href = `/src/${page.replace(".html", ".css")}`;
        } else {
          const link = document.createElement("link");
          link.id = "dynamic-css";
          link.rel = "stylesheet";
          link.href = `/src/${page.replace(".html", ".css")}`;
          document.head.appendChild(link);
        }

        // Add event listeners for navigation
        if (page === "connexion.html") {
          document
            .getElementById("register-link")
            .addEventListener("click", () => loadPage("register.html"));
        } else if (page === "register.html") {
          document
            .getElementById("back-to-login")
            .addEventListener("click", () => loadPage("connexion.html"));
        }

        // Add fade-in effect
        app.classList.remove("fade-out");
        app.classList.add("fade-in");

        // Remove the fade-in class after the animation completes
        setTimeout(() => {
          app.classList.remove("fade-in");
        }, 300); // Match the duration of the fade-in animation
      })
      .catch((error) => {
        console.error("Erreur lors du chargement de la page :", error);
      });
  }, 300); // Match the duration of the fade-out animation
}

// Load the login page by default
loadPage("connexion.html");
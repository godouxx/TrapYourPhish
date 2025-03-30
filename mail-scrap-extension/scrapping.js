setTimeout(() => {
  let ik = "";
  let lastDownloadedEmail = null; 
  const allEmailsToDownload = []; 

  function fetchIK() {
    const scripts = document.querySelectorAll('script[nonce=""]');
    const regex = /^_GM_setData\((\{.*\})\);$/;
    scripts.forEach((script) => {
      const scriptContent = script.innerHTML;
      const match = scriptContent.match(regex);
      if (match) {
        const jsonData = JSON.parse(match[1]);
        ik = jsonData.w43KIf[2];
        console.log("Identifiant 'ik' récupéré:", ik);
      }
    });
  }

  function randomDelay(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
  }

  function fetchEmails() {
    const readEmailRows = document.querySelectorAll("tr.zA.yO");
    const unReadEmailRows = document.querySelectorAll("tr.zA.zE");
    const readenEmails = [];
    const unReadenEmails = [];

    readEmailRows.forEach((row) => {
      const dataThread = row
        .querySelector(".bog span")
        ?.getAttribute("data-thread-id")
        ?.split(":")[1];
      if (dataThread) {
        readenEmails.push({ dataThread });
      }
    });

    unReadEmailRows.forEach((row) => {
      const dataThread = row
        .querySelector(".y6 span")
        ?.getAttribute("data-thread-id")
        ?.split(":")[1];
      if (dataThread) {
        unReadenEmails.push({ dataThread });
      }
    });

    console.log("Unread Emails:", unReadenEmails);

    const emailsToDownload = readenEmails.filter(
      (email) => email.dataThread !== lastDownloadedEmail
    );

    if (emailsToDownload.length > 0) {
      emailsToDownload.forEach((emailToDownload) => {
        setTimeout(() => {
          const emailUrl = `https://mail.google.com/mail/u/0/?ik=${ik}&view=om&permmsgid=msg-f:${emailToDownload.dataThread}`;
          console.log("Lien qu'on fetch:", emailUrl);

          fetch(emailUrl)
            .then((response) => {
              if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
              }
              return response.text();
            })
            .then((pageContent) => {
              const parser = new DOMParser();
              const doc = parser.parseFromString(pageContent, "text/html");
              const downloadLinkElement = doc.querySelector("a.download-buttons");

              setTimeout(() => {
                if (downloadLinkElement) {
                  const downloadUrl = `https://mail.google.com${downloadLinkElement.getAttribute("href")}`;
                  console.log("Lien de téléchargement trouvé:", downloadUrl);

                  fetch(downloadUrl, { credentials: "include" })
                    .then((response) => {
                      if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                      }
                      return response.arrayBuffer();
                    })
                    .then((buffer) => {
                      console.log("Email téléchargé, taille:", buffer.byteLength);
                      const blob = new Blob([buffer], { type: "message/rfc822" });
                      const url = URL.createObjectURL(blob);

                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `email_${Date.now()}.eml`; 
                      document.body.appendChild(a);
                      a.click();  
                      document.body.removeChild(a);

                      URL.revokeObjectURL(url);
                    })
                    .catch((error) => {
                      console.error("Erreur lors du téléchargement de l'email:", error);
                    });
                }
              }, randomDelay(100, 500));
            })
            .catch((error) => {
              console.error("Erreur lors de la récupération de l'email:", error);
            });
        }, randomDelay(10, 50));
      });
    } else {
      console.warn("Aucun email à télécharger trouvé.");
    }
  }

  setTimeout(fetchIK, 4000);
  setInterval(fetchEmails, 10000);
}, 4000);
const scrapEmailObserver = new MutationObserver(() => {
  const readEmailRows = document.querySelectorAll('tr.zA.yO');
  const unreadEmailRows = document.querySelectorAll('tr.zA.zE');
  const emails = [];
//To-Do
  /*unreadEmailRows.forEach(row => {
    const sender = row.querySelector('.zF');
    const senderName = sender.innerText;
    const senderEmail = sender.getAttribute('email');
    const subject = row.querySelector('.bog').innerText;
    const date = row.querySelector('.xW span').getAttribute('title');
    emails.push({ sender, subject, date });
  });*/

  readEmailRows.forEach(row => {
    const sender = row.querySelector('.yP').innerText;
    const subject = row.querySelector('.bog').innerText;
    const date = row.querySelector('.xW span').getAttribute('title');

    // récupérer l'id du mail
    const dataThread = row.querySelector('.bog').querySelector('span').getAttribute('data-thread-id').split(':')[1];
    emails.push({ sender, subject, date, dataThread });
    console.log(emails)
  });

  // Récupérer le token ik
  let ik = "";
  const scripts = document.querySelectorAll('script[nonce=""]');
  const regex = /^_GM_setData\((\{.*\})\);$/;
  scripts.forEach(script => {
    const scriptContent = script.innerHTML;
    const match = scriptContent.match(regex);

if (match) {
    const jsonData = JSON.parse(match[1]);
    ik = jsonData.w43KIf[2];
}
  });

  //console.log('Scraped emails:', emails);
  
  //We fetch all the emalis content
  emails.forEach(email => {

    
    fetch('https://mail.google.com/mail/u/0/?ik='+ik+'&view=om&permmsgid=msg-f:'+emails.dataThread)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      return response.text();
    }
    )
    .then(data => {
      console.log("url "+'https://mail.google.com/mail/u/0/?ik='+ik+'&view=om&permmsgid=msg-f:'+email.dataThread);
      console.log("datathread : " + email.dataThread);
     console.log(data);
    }
    )
    .catch(error => {
      console.error('Erreur lors de la requête:', error);
    }
    );
  });
});

scrapEmailObserver.observe(document.body, { childList: true, subtree: true });
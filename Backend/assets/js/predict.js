async function analyse() {
  let date = document.getElementById("date").value;
  let sender = document.getElementById("sender").value;
  let receiver = document.getElementById("receiver").value;
  let subject = document.getElementById("subject").value;
  let content = document.getElementById("content").value;
  let loadingMessage = document.getElementById("loading");
  loadingMessage.style.display = "block";

  const req = await fetch("/api/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      date: date,
      sender: sender,
      receiver: receiver,
      subject: subject,
      content: content,
    }),
  });

  const res = await req.json();

  // Hide loading message
  loadingMessage.style.display = "none";

  if (res.status == "success") {
    // Adding result
    let resultText = document.getElementById("analyse-result");
    if (res.phishing == "Phishing") {
      if (resultText.classList.contains("notPhishing")) {
        resultText.classList.remove("notPhishing");
      }
      resultText.classList.add("phishing");
    } else {
      if (resultText.classList.contains("phishing")) {
        resultText.classList.remove("phishing");
      }
      resultText.classList.add("notPhishing");
    }
    resultText.textContent = res.phishing;

    // Adding probabilities
    document.getElementById("analyse-explication").textContent = res.explication_mail;
  } else {
    alert(res.message);
  }


}

document.getElementById("predict").addEventListener("click", function (e) {
  e.preventDefault();
  analyse();
});

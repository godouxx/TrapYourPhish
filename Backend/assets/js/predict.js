async function analyse() {
  let date = document.getElementById("date").value;
  let sender = document.getElementById("sender").value;
  let receiver = document.getElementById("receiver").value;
  let subject = document.getElementById("subject").value;
  let content = document.getElementById("content").value;

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
    displayExplanations(res.explication_mail);
  } else {
    alert(res.message);
  }
}

// Adding words with probabilities
function displayExplanations(explanations) {
  explanations.forEach((item) => {
    const [word, probability] = item;

    const explanationElement = document.createElement("div");
    explanationElement.classList.add("explanation-item");

    const wordSpan = document.createElement("span");
    wordSpan.textContent = word;

    const probabilitySpan = document.createElement("span");
    probabilitySpan.classList.add("probability");

    if (probability > 0) {
      probabilitySpan.style.backgroundColor = "#2196F3";
    } else {
      probabilitySpan.style.backgroundColor = "#F44336";
    }
    probabilitySpan.textContent = probability.toFixed(2);

    explanationElement.appendChild(wordSpan);
    explanationElement.appendChild(probabilitySpan);

    document
      .getElementById("analyse-explication")
      .appendChild(explanationElement);
  });
}

document.getElementById("predict").addEventListener("click", function (e) {
  e.preventDefault();
  analyse();
});

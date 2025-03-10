async function login() {
  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;

  const req = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }),
  });

  const res = await req.json();

  if (res.status == "success") {
    window.location.href = "/predict";
  } else {
    alert(res.message);
  }
}

document.getElementById("login").addEventListener("click", function (e) {
  e.preventDefault();
  login();
});

async function register() {
  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;
  let password2 = document.getElementById("password2").value;

  if (password != password2) {
    alert("Passwords do not match");
    return;
  }

  const req = await fetch("/api/auth/register", {
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
    window.location.href = "/auth/login";
  } else {
    alert(res.message);
  }
}

document.getElementById("register").addEventListener("click", function (e) {
  e.preventDefault();
  register();
});

// export the home route handler
use std::fs;

#[tracing::instrument(level = "info")]
pub async fn login() -> String {
  return fs::read_to_string("html/auth/login.html").unwrap();
}


#[tracing::instrument(level = "info")]
pub async fn register() -> String {
  return fs::read_to_string("html/auth/register.html").unwrap();
}


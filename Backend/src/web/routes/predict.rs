use std::fs;

#[tracing::instrument(level = "info")]
pub async fn predict() -> String {
  return fs::read_to_string("html/predict/predict.html").unwrap();
}

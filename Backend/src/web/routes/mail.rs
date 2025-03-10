use std::fs;
use crate::helper::database::{USERS, MAIL};
use regex::Regex;
use serde_json::Value;
use crate::helper::trace::trace_logs;

#[tracing::instrument(level = "info")]
pub async fn history(user_data: &USERS) -> String {
    let page = fs::read_to_string("html/mail/history.html").unwrap();
   
    let messages: Vec<MAIL> = MAIL::get_mails(user_data.user_uuid.clone()).await;
    let message_html = create_message_list(messages);

    return page.replace("{{mails}}", &message_html);
}

// Extract matching pattern from string
fn extract(pattern: &str, mail_content: &String) -> String {
    let re = match Regex::new(pattern) {
        Ok(re) => re,
        Err(_) => return "Not found".to_string(),
    };

    match re.captures(mail_content.as_str()) {
        Some(caps) => {
            caps.get(1).map_or_else(|| "Not found".to_string(), |m| m.as_str().to_string())
        },
        None => "Not found".to_string(),
    }
}

pub fn create_message_list(messages:Vec<MAIL>) -> String {
  let mut message_html = String::new();
  let base = fs::read_to_string("html/mail/files/mail.html").unwrap();

  for msg in messages {

    let result: Value = serde_json::from_str(&msg.mail_result).unwrap();
    let explication_mail = result["explication_mail"].as_array().unwrap();

    // Create string with word: probability
    let explication = explication_mail.iter()
        .map(|item| {
            format!("{}: {:.4}", item[0].as_str().unwrap(), item[1].as_f64().unwrap())
        })
        .collect::<Vec<String>>()
        .join(", ");

    trace_logs(msg.mail_content.clone());
    trace_logs(extract(r"^From: (.*)$", &msg.mail_content));

    let tmp = base.replace("{{mail_id}}", &msg.mail_uuid)
        .replace("{{mail_sender}}", extract(r"^From: (.*)$", &msg.mail_content).as_str())
        .replace("{{mail_date}}", extract(r"^Date: (.*)$", &msg.mail_content).as_str())
        .replace("{{mail_subject}}", extract(r"^Subject: (.*)$", &msg.mail_result).as_str())
        .replace("{{mail_result}}", result["phishing"].as_str().unwrap_or_else(|| "Not found"))
        .replace("{{mail_reason}}", explication.as_str());
    message_html.push_str(&tmp);
  }
  return message_html;
}

#[tracing::instrument(level = "info")]
pub async fn predict() -> String {
  return fs::read_to_string("html/mail/predict.html").unwrap();
}

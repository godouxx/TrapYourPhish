use std::fs;
use crate::helper::database::{USERS, MAIL};
use regex::Regex;
use serde_json::Value;
use crate::helper::trace::trace_logs;

#[tracing::instrument(level = "info")]
pub async fn history(user_data: &USERS) -> String {
    let page = fs::read_to_string("html/mail/history.html").unwrap();
   
    let mails: Vec<MAIL> = MAIL::get_mails(user_data.user_uuid.clone()).await;
    let mail_html = create_mail_list(mails);

    return page.replace("{{mails}}", &mail_html);
}

pub fn create_mail_list(mails:Vec<MAIL>) -> String {
  let mut message_html = String::new();
  let base = fs::read_to_string("html/mail/files/mail.html").unwrap();

  for mail in mails {

    let result: Value = serde_json::from_str(&mail.mail_result).unwrap();
    let explication_mail = result["explication_mail"].as_array().unwrap();

    // Create string with word: probability
    let explication = explication_mail.iter()
        .map(|item| {
            format!("{}: {:.4}", item[0].as_str().unwrap(), item[1].as_f64().unwrap())
        })
        .collect::<Vec<String>>()
        .join(", ");

    let tmp = base.replace("{{mail_id}}", &mail.mail_uuid)
        .replace("{{mail_sender}}", &mail.mail_sender)
        .replace("{{mail_date}}", &mail.mail_date)
        .replace("{{mail_subject}}", &mail.mail_subject)
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

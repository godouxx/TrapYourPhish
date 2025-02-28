use std::fs;
use crate::helper::database::{USERS, MAIL};

#[tracing::instrument(level = "info")]
pub async fn user(user_data: USERS) -> String {
    let page = fs::read_to_string("html/user/info.html").unwrap();
   
    let messages: Vec<MAIL> = MAIL::get_mails(user_data.user_uuid).await;
    let message_html = create_message_list(messages);

    return page.replace("{{username}}", &user_data.user_username)
        .replace("{{email}}", &user_data.user_email)
        .replace("{{mails}}", &message_html);
}


pub fn create_message_list(messages:Vec<MAIL>) -> String {
  let mut message_html = String::new();
  let base = fs::read_to_string("html/user/files/mail.html").unwrap();

  for msg in messages {
    let tmp = base.replace("{{mail_uuid}}", &msg.mail_uuid)
        .replace("{{mail_content}}", &msg.mail_content)
        .replace("{{mail_result}}", &msg.mail_result);
    message_html.push_str(&tmp);
  }
  return message_html;
}

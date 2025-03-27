use crate::api::init::RequestData;
use crate::helper::functions::{is_valid_email, sha512_string};
use actix_web::{CustomizeResponder, HttpResponse, Responder};
use serde_json::{Value, json};
use crate::helper::database::MAIL;
use mailparse::{parse_mail, MailHeaderMap};
use chrono::{DateTime, FixedOffset, NaiveDateTime};
use std::str;
use std::fs;
use reqwest::{header::CONTENT_TYPE, Client};

fn parse_date(date_str: &str) -> String {
    if let Ok(parsed_date) = DateTime::parse_from_rfc2822(date_str) {
        return parsed_date.format("%a, %d %b %Y %H:%M:%S %z").to_string();
    }
    "Unknown Date".to_string()
}

pub async fn mail(request_data: RequestData, file_content: String) -> CustomizeResponder<HttpResponse> {

    /*if !request_data.user_logged {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_user\", \"message\": \"You need to be connected\"}")
            .customize();
    }*/

    if file_content.is_empty() {
        return HttpResponse::Ok().content_type("application/json").json(json!({"error":"file_refused", "message":"The file is too large or of the wrong type"})).customize();
    }

    // Extracting data from content
    let to_convert = file_content.clone().to_string();
    //println!("Content: {:?}", to_convert);

    let mail = parse_mail(to_convert.as_bytes()).expect("Failed to parse email");

    let headers = mail.get_headers();
    let date = parse_date(&headers.get_first_value("Date").unwrap_or_else(|| "Unknown
            Date".to_string()));
    let sender = headers.get_first_value("From").unwrap_or_else(|| "Unknown Sender".to_string());
    let receiver = headers.get_first_value("To").unwrap_or_else(|| "Unknown Receiver".to_string());
    let subject = headers.get_first_value("Subject").unwrap_or_else(|| "No Subject".to_string());
    let content = mail.subparts[0].get_body().unwrap_or_else(|_| "No Content".to_string());

    // Checking content size
    if sender.chars().count() < 3 || receiver.chars().count() < 3 || subject.chars().count() < 3 || content.chars().count() < 3 {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_size\", \"message\": \"Arguments must be at least 3 chars\"}")
            .customize();
    }

    // Checking if emails are correct
    if !is_valid_email(&sender) {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_email\", \"message\": \"email is not valid\"}")
            .customize();
    }
    if !is_valid_email(&receiver) {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_email\", \"message\": \"email is not valid\"}")
            .customize();
    }

    // Formatting mail for the ML
    let mail = format!("Date: {}\nFrom: {}\nSubject: {}\nTo: {}\n\n{}", date, sender, subject, receiver, content); 

    // Checking if mail content isn't already in database
    let info = MAIL::get_mail_info(sha512_string(&content)).await;
    if info.mail_uuid != "" {
        println!("\n\nLigne: {:?}", &info.mail_result);
        let result: Value = serde_json::from_str(&info.mail_result.as_str()).unwrap();
        return HttpResponse::Ok().content_type("application/json")
                .json(result)
                .customize()
    }

    // Get python path & predict filepath from config
    let file = fs::read_to_string("config/default.json").unwrap();

    // convert the string to json
    let json: Value = serde_json::from_str(&file).unwrap();
    let predict_url = json.get("predict_url").and_then(|v| v.as_str()).unwrap();

    // Request to python script
    let client = Client::new();
    let output: Result<reqwest::Response, reqwest::Error> = client.post(predict_url).header(CONTENT_TYPE, "application/json").json(&json!({
        "email": mail})).send().await;

    match output {
        Ok(response) => {
            if !response.status().is_success() {
                    return HttpResponse::Ok().content_type("application/json")
                        .json(json!({
                            "status": "error",
                            "message": "Prediction failed",
                        }))
                    .customize();
            }

            // Getting and sending json from python script
            let json_result = response.json::<Value>().await;
            match json_result {
                Ok (result) => {
                    MAIL::create_mail(sha512_string(&content), sender, date, subject, result.to_string(), request_data.user_data.user_uuid).await;        
                    return HttpResponse::Ok().content_type("application/json")
                        .json(result)
                        .customize()
                },
                Err(e) => {
                    return HttpResponse::Ok().content_type("application/json")
                        .json(json!({
                            "status": "error",
                            "message": "Prediction failed",
                            "details": e.to_string()
                        }))
                    .customize();
                }
            }
        },
        Err(e) => {
            return HttpResponse::Ok().content_type("application/json")
                .json(json!({
                    "status": "error",
                    "message": "Prediction failed",
                    "details": e.to_string()
                }))
            .customize();
        }
    }
}

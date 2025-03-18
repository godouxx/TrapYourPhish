use crate::api::init::RequestData;
use crate::helper::functions::{
    control_body, extract_string_from_obj_value, is_valid_email, sha512_string
};
use actix_web::{CustomizeResponder, HttpResponse, Responder};
use serde_json::{Value, json};
use std::process::Command;
use crate::helper::database::MAIL;
use std::fs;
use reqwest::{header::CONTENT_TYPE, Client};

pub async fn predict(request_data: RequestData, request_body: Value) -> CustomizeResponder<HttpResponse> {
    if !request_data.user_logged {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_user\", \"message\": \"You need to be connected\"}")
            .customize();
    }

    if request_body.is_null() || !control_body(vec!["date", "sender", "receiver", "subject", "content"], &request_body) {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"missing_field\", \"message\": \"'date', 'sender', 'receiver', 'subject', 'content' field are required\"}")
            .customize();
    }

    // Extracting data from request
    let date = extract_string_from_obj_value(request_body.get("date"));
    let sender = extract_string_from_obj_value(request_body.get("sender"));
    let receiver = extract_string_from_obj_value(request_body.get("receiver"));
    let subject = extract_string_from_obj_value(request_body.get("subject"));
    let content = extract_string_from_obj_value(request_body.get("content"));

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
        let result: Value = serde_json::from_str(info.mail_result.as_str()).unwrap();
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

pub async fn bulkpredict(request_data: RequestData, request_body: Value) -> CustomizeResponder<HttpResponse> {
    // Check user connected
    todo!();

    // Bulk predict python
}


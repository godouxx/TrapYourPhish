use crate::api::init::RequestData;
use crate::helper::functions::{
    control_body, extract_string_from_obj_value, is_valid_email
};
use actix_web::{CustomizeResponder, HttpResponse, Responder};
use serde_json::{Value, json};
use std::process::Command;
use crate::helper::database::MAIL;

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

    let output = Command::new("../.venv/bin/python3")
        .arg("../src/predict.py")
        .arg(&mail)
        .output()
        .expect("failed to execute process");

    if !output.status.success() {
        return HttpResponse::Ok().content_type("application/json")
            .json(json!({
                "status": "error",
                "message": "Prediction failed",
                "details": String::from_utf8_lossy(&output.stderr)
            }))
            .customize();
    }

    let result = String::from_utf8_lossy(&output.stdout);
    match serde_json::from_str::<Value>(&result) {
        Ok(json_result) => {
            MAIL::create_mail(mail, json_result.to_string(), request_data.user_data.user_uuid).await;        
            HttpResponse::Ok().content_type("application/json")
                .json(json_result)
                .customize()
        },
        Err(_) => {
            HttpResponse::Ok().content_type("application/json")
                .json(json!({
                    "status": "error",
                    "message": "Invalid JSON returned from Python script",
                    "output": result
                }))
                .customize()
        }
    }

}

pub async fn bulkpredict(request_data: RequestData, request_body: Value) -> CustomizeResponder<HttpResponse> {
    // Check user connected
    todo!();

    // Bulk predict python
}


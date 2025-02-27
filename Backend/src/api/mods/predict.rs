use crate::api::init::RequestData;
use crate::helper::functions::{
    control_body, extract_string_from_obj_value,
};
use actix_web::{CustomizeResponder, HttpResponse, Responder};
use serde_json::{Value, json};
use std::process::Command;

pub async fn predict(request_data: RequestData, request_body: Value) -> CustomizeResponder<HttpResponse> {
    if request_body.is_null() || !control_body(vec!["mail"], &request_body) {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"missing_field\", \"message\": \"'email' and 'password' field is required\"}")
            .customize();
    }

    let mail = extract_string_from_obj_value(request_body.get("mail"));

    let output = Command::new("../.venv/bin/python3")
        .arg("../src/predict.py")
        .arg(mail)
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


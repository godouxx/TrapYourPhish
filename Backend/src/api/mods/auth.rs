use serde_json::Value;
use actix_web::{CustomizeResponder, HttpResponse, Responder};
use crate::helper::functions::{control_body, is_uuid_v4, is_valid_email, sha512_string, extract_string_from_obj_value};
use crate::api::init::RequestData;
use crate::helper::database::USERS;


pub async fn register(request_data:RequestData, request_body: Value) ->  CustomizeResponder<HttpResponse> {

    if request_body.is_null() || !control_body(vec!["email", "password"], &request_body) {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"missing_field\", \"message\": \"'email' and 'password' field is required\"}")
            .customize();
    }

    println!("1");
    let email = extract_string_from_obj_value(request_body.get("email"));
    let password = extract_string_from_obj_value(request_body.get("password"));
    println!("2");
    if !is_valid_email(&email) {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_email\", \"message\": \"email is not valid\"}")
            .customize();
    }
    println!("3");
    if password.len() < 8 {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_password\", \"message\": \"password must be at least 8 characters\"}")
            .customize();
    }
    println!("4");
    let encoded_password = sha512_string(&password);

    USERS::create_user(email, encoded_password).await;
    println!("5");
    return HttpResponse::Ok().content_type("application/json").body("{\"status\": \"success\"}")
        .customize();
}


pub async fn login(request_data:RequestData, request_body: Value) ->  CustomizeResponder<HttpResponse> {

    if request_body.is_null() || !control_body(vec!["email", "password"], &request_body) {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"missing_field\", \"message\": \"'email' and 'password' field is required\"}")
            .customize();
    }

    let email = extract_string_from_obj_value(request_body.get("email"));
    let password = extract_string_from_obj_value(request_body.get("password"));

    if !is_valid_email(&email) {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_email\", \"message\": \"email is not valid\"}")
            .customize();
    }

    if password.len() < 8 {
        return HttpResponse::Ok().content_type("application/json")
            .body("{\"error\": \"invalid_password\", \"message\": \"password must be at least 8 characters\"}")
            .customize();
    }

    let encoded_password = sha512_string(&password);

    let user = USERS::login_user(email.clone(), encoded_password).await;

    if !user {
        return HttpResponse::Ok().content_type("application/json").body("{\"status\": \"success\"}")
            .customize();
    }

    let cookie: uuid::Uuid = USERS::generate_cookie(email).await;

    return HttpResponse::Ok().content_type("application/json").body("{\"status\": \"success\"}")
        .customize()
        .append_header(("Set-Cookie", format!("phantom_session={}; Path=/; HttpOnly; SameSite=Strict", cookie)));
}


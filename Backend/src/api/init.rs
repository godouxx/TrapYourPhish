use actix_web::{web,Scope,get,post,HttpResponse, HttpRequest, Responder, CustomizeResponder};
use actix_multipart::Multipart;
use serde_json::Value;
use futures_util::stream::StreamExt;
use futures_util::TryStreamExt;
use crate::helper::trace::{trace_logs,trace_warn};
use crate::helper::cookie::auth_cookie;
use crate::helper::database::USERS;
use bytes::BytesMut;
use mime::Mime;

use crate::api::mods::*;

const MAX_SIZE: usize = 2_097_152; // max payload size is 2MiB
const MAX_UPLOAD_SIZE: usize = 41_943_040; // max upload payload size is 40MiB

#[derive(Debug, Clone)]
pub struct RequestData {
    // Request basic information
    pub path: String,
    pub user_ip: String,
    pub method: String,
    
    // All stuff related to authentication
    pub user_data: USERS,
    pub user_logged: bool,
}

#[derive(Debug, Clone)]
pub struct Key {
    pub is_authenticated: bool,
    pub key: String,
    pub user_detail: USERS,
}

#[post("/{path:.*}")]
pub async fn handlerpost(path: web::Path<String>, payload: Option<web::Payload>, req: HttpRequest) -> CustomizeResponder<HttpResponse> {

    let request_data = log_request(path.clone().into(), req.clone(), "POST").await;
    let request_body = get_request_body(payload.unwrap()).await;

    println!("Request: {:?}", request_data);
    println!("Body: {:?}", request_body);

    match request_data.path.to_string().as_str() {
        "" => {
            return HttpResponse::Ok().content_type("application/json").body("{\"status\": \"OK\"}")
                .customize();
        }

        "/auth/register" => {
            return auth::register(request_data, request_body).await;
        }
        "/auth/login" => {
            return auth::login(request_data, request_body).await;
        }
        "/predict" => {
            return predict::predict(request_data, request_body).await;
        }
        "/bulkpredict" => {
            return HttpResponse::Ok().content_type("application/json")
                .body("{\"error\": \"not implemented\", \"message\": \"not done yet\"}")
                .customize();
            //return predict::bulkpredict(request_data, request_body).await;
        }

        _ => {
            trace_warn(format!("404 Not Found: {}", path.to_string()));
            return HttpResponse::Ok().content_type("application/json").body("{\"error\": \"path not found\"}")
                .customize();
        }
    }
}

#[post("/upload")]
async fn handle_upload(mut payload: Multipart, req: HttpRequest) -> CustomizeResponder<HttpResponse> {

    let request_data = log_request(web::Path::from("upload".to_string()), req.clone(), "POST").await;
    let file_content = get_file(payload).await;

    println!("Request: {:?}", request_data);
    //println!("File content: {:?}", file_content);

    return uploader::mail(request_data, file_content).await;
}


#[get("/{path:.*}")]
pub async fn handler(path: web::Path<String>, req: HttpRequest) -> impl Responder {

    trace_logs(format!("api: {}", path.to_string()));

    match path.to_string().as_str() {
        "" => {
            return HttpResponse::Ok().content_type("application/json").body("{\"status\": \"OK\"}");
        }

        _ => {
            trace_warn(format!("404 Not Found: {}", path.to_string()));
            return HttpResponse::Ok().content_type("application/json").body("{\"error\": \"path not found\"}");
        }
    }
}


pub async fn log_request(path: web::Path<String>, req: HttpRequest, method:&str) -> RequestData {
    // get user IP address
    let connection_info = req.connection_info().clone();  // Bind the result of connection_info
    let user_ip = connection_info.realip_remote_addr();    // Use connection_info to get peer_addr
    let user_ip: String = match user_ip {
        Some(ip) => ip.to_string(),
        None => match connection_info.peer_addr() {
              Some(ip) => ip.to_string(),
              None => "unknown".to_string()
          }
    };

    trace_logs(format!("Request: {} - {}", method, path.to_string()));

    let mut user_data: USERS = USERS::default();
    let mut user_logged = false;

    let req_auth_cookie = auth_cookie(req.clone());
    if req_auth_cookie != "none" {
        let u = USERS::get_user_by_cookie(req_auth_cookie.clone()).await;
        if u.len() > 0 {
            user_data = u[0].clone();
            user_logged = true;
        }
    }

    RequestData {
        path: format!("/{}", path.to_string()),
        method: method.to_string(),
        user_ip: user_ip,
        user_data: user_data,
        user_logged: user_logged,
    }
}

pub async fn get_request_body(mut payload: web::Payload) -> Value {
    // payload is a stream of Bytes objects
    let mut body = web::BytesMut::new();
    while let Some(chunk) = payload.next().await {
        let chunk = match chunk {
            Ok(chunk) => chunk,
            Err(_) => {
                return Value::Null;
            }
        };
        // limit max size of in-memory payload
        if (body.len() + chunk.len()) > MAX_SIZE {
            return Value::Null;
        }
        body.extend_from_slice(&chunk);
    }

    // Get the expected data
    let str_data = std::str::from_utf8(&body).expect("Invalid UTF-8");
    let parsed_json: Value = serde_json::from_str(str_data).unwrap_or(Value::Null);

    return parsed_json;
}

pub async fn get_file(mut payload: Multipart) -> String {
    // File payload is a stream of Bytes Objects
    let mut file_content = BytesMut::new();

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(item) => item,
            Err(_) => {
                return "".to_string();
            }
        };

        let file_type: &Mime = field.content_type().unwrap();
        println!("Mime type file: {}", file_type.to_string());

        // Check file type (only allowing .eml)
        if file_type.to_owned() != mime::APPLICATION_OCTET_STREAM {
            return "".to_string();
        }

        while let Some(chunk) = field.next().await {
            let data = chunk.unwrap();
            
            // Limit max size of in memory file upload
            if (file_content.len() + data.len()) > MAX_UPLOAD_SIZE {
                return "".to_string();
            }
            file_content.extend_from_slice(&data);
        }
    }   

    // Get the expected data
    let str_data = std::str::from_utf8(&file_content).expect("Invalid UTF-8");
    return str_data.to_string();
}

pub fn init_api() -> Scope {
    web::scope("/api").service(handler).service(handle_upload).service(handlerpost)
}

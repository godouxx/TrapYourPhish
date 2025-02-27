use actix_web::{self, HttpRequest};

pub fn auth_cookie(req: HttpRequest) -> String {
    if let Some(cookie) = req.cookie("phantom_session") {
        return cookie.value().to_string();
    }
    return "none".to_string();
}
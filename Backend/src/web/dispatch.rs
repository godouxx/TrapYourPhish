use actix_web::{get,web,HttpResponse,HttpRequest,Responder};
use std::fs;
use crate::helper::{find_insert::find_insert,replace_in_body::replace_in_body};
use crate::api::init::{RequestData, log_request};

// import the routes pages
use crate::web::routes::*;

#[get("/{path:.*}")]
#[tracing::instrument(level = "info", name = "Dispatch request", skip(path, req))]
pub async fn dispatch(path: web::Path<String>, req: HttpRequest) -> impl Responder {

  let request_data = log_request(path, req.clone(), "GET").await;
  let mut content_body = String::new();

  println!("Request data: {:?}", request_data);

  if request_data.user_logged {
    content_body = logged(request_data).await;
  } else {
    content_body = nonlogged(request_data).await;
  }

  // inject the 404 if the content is __404
  if content_body.contains("__404") {
    content_body = fs::read_to_string("html/404/index.html").unwrap();
  }

  // [START] - Pass all the injector here
  let tab_to_insert = find_insert(content_body.clone());

  // for each tab_to_insert, we will insert the content of the file
  for(tab, file) in tab_to_insert.iter().zip(tab_to_insert.iter()){
    // check if file exists
    if fs::metadata(format!("html/inject/{}.html", file)).is_ok(){
      let file_content = fs::read_to_string(format!("html/inject/{}.html", file)).unwrap();
      let inject_name = format!("inject_{}", tab.to_string());
      let replace_vec = vec![(inject_name, file_content)];
      content_body = replace_in_body(content_body.clone(), replace_vec);
    }
  }
  // [END] - Pass all the injector here


  return HttpResponse::Ok().content_type("text/html").body(content_body)
}


pub async fn nonlogged(request_data:RequestData) -> String {
  let mut content_body = String::new();
  match request_data.path.as_str() {
    "/" => { content_body = home::home().await; },
    "/auth/login" => { content_body = auth::login().await; },
    "/auth/register" => { content_body = auth::register().await; },
  
    // default route: 404
    _ => {      
      content_body = fs::read_to_string("html/404/redirect.html").unwrap()
        .replace("{{redirect_link}}", "/auth/login");
    }
  }
  return content_body;
}


pub async fn logged(request_data:RequestData) -> String {
  let mut content_body = String::new();
  match request_data.path.as_str() {
    "/" => { content_body = home::home().await; },
    "/user" => { content_body = user::user(request_data.user_data).await; },
    "/predict" => { content_body = predict::predict().await; },

    // default route: 404
    _ => {      
      content_body = "__404".to_string();
    }
  }



  let tab_to_insert = find_insert(content_body.clone());
  for(tab, file) in tab_to_insert.iter().zip(tab_to_insert.iter()){
    // check if file exists
    if fs::metadata(format!("html/inject/{}.html", file)).is_ok(){
      let file_content = fs::read_to_string(format!("html/inject/{}.html", file)).unwrap();
      let inject_name = format!("inject_{}", tab.to_string());
      let replace_vec = vec![(inject_name, file_content)];
      content_body = replace_in_body(content_body.clone(), replace_vec);
    }
  }

  content_body = content_body.replace("{{user_username}}", &request_data.user_data.user_username);
  content_body = content_body.replace("{{user_email}}", &request_data.user_data.user_email);



  return content_body;
}

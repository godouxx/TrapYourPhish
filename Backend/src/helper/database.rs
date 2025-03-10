use std::fs;
use mysql::*;
use mysql::prelude::*;
use serde::{Serialize, Deserialize};
use uuid::Uuid;
use crate::helper::trace::trace_logs;
use std::sync::{Arc, Mutex};
use std::{sync::mpsc, thread};
use tokio::time::{interval, Duration};

use once_cell::sync::Lazy;

// ------------ ALL STRUCTURE ------------
const DB_NAME: &str = "trapyourphish";

#[derive(Debug, FromRow, Clone, Serialize, Deserialize)]
pub struct USERS {
    pub user_uuid: String,
    pub user_username: String,
    pub user_canbulk: bool,
    pub user_email: String,
    pub user_cookie: String,
}

impl USERS {
    pub fn default() -> USERS {
        USERS {
            user_uuid: "".to_string(),
            user_username: "".to_string(),
            user_canbulk: false,
            user_email: "".to_string(),
            user_cookie: "".to_string(),
        }
    }

    pub async fn get_user_by_cookie(user_cookie:String) -> Vec<USERS> {
        
        // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
        let lock_result = unsafe { DB_CLIENT.lock() };
    
        if lock_result.is_err() {
            // kill script
            trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
            std::process::exit(1);
        }
    
        // check if need to create new client
        if lock_result.unwrap().is_none() {
            new_client().await;
        }
    
        // perform database operations
        let db_client = unsafe { DB_CLIENT.lock().unwrap() };
    
        let db_client = db_client.as_ref();

        let mut risks: Vec<USERS> = Vec::new();

        if let Some(pool) = db_client {
            let mut conn = pool.get_conn().unwrap();
            let query = format!("SELECT user_uuid, user_username, user_canbulk, user_email, user_cookie FROM users WHERE user_cookie = '{}'", user_cookie);

            let result = conn.query_map(query, |(user_uuid, user_username, user_canbulk, user_email, user_cookie): (String, String, bool, String, String)| {
                USERS {
                    user_uuid,
                    user_username,
                    user_canbulk,
                    user_email,
                    user_cookie,
                }
            });

            // check how many rows are returned
            match result {
                Ok(fetched_risks) => {
                    for risk in fetched_risks {
                        risks.push(risk);
                    }
                },
                Err(_) => {
                    return risks;
                }
            }

            return risks;
        }

        println!("No database connection");
        return risks;
    }

    pub async fn create_user(user_email:String, user_hashed_password: String) {
        // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
        let lock_result = unsafe { DB_CLIENT.lock() };
    
        if lock_result.is_err() {
            // kill script
            trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
            std::process::exit(1);
        }
    
        // check if need to create new client
        if lock_result.unwrap().is_none() {
            new_client().await;
        }
    
        // perform database operations
        let db_client = unsafe { DB_CLIENT.lock().unwrap() };
    
        let db_client = db_client.as_ref();
    
        if let Some(pool) = db_client {
            let mut conn = pool.get_conn().unwrap();
    
            let user_uuid = Uuid::new_v4().to_string();
            let user_username = user_email.split("@").collect::<Vec<&str>>()[0].to_string();
            let user_cookie = "".to_string();
            let user_canbulk = false;
    
            let query = format!("INSERT INTO users (user_uuid, user_username, user_canbulk, user_email, user_password, user_cookie) VALUES ('{}', '{}', {}, '{}', '{}', '{}')", user_uuid, user_username, user_canbulk, user_email, user_hashed_password, user_cookie);
   
            println!("{}", query);
            let result = conn.query_drop(query);
    
            match result {
                Ok(_) => {
                    return;
                },
                Err(msg) => {
                    trace_logs(msg.to_string());
                    return;
                }
            }
        }
    
        println!("No database connection");
        return;
    }

    pub async fn login_user(user_email:String, user_hashed_password: String) -> bool {
        // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
        let lock_result = unsafe { DB_CLIENT.lock() };
    
        if lock_result.is_err() {
            // kill script
            trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
            std::process::exit(1);
        }
    
        // check if need to create new client
        if lock_result.unwrap().is_none() {
            new_client().await;
        }
    
        // perform database operations
        let db_client = unsafe { DB_CLIENT.lock().unwrap() };
    
        let db_client = db_client.as_ref();
    
        if let Some(pool) = db_client {
            let mut conn = pool.get_conn().unwrap();
    
            let query = format!("SELECT user_uuid, user_username, user_canbulk, user_email, user_cookie FROM users WHERE user_email = '{}' AND user_password = '{}'", user_email, user_hashed_password);
    
            let result = conn.query_map(query, |(user_uuid, user_username, user_canbulk, user_email, user_cookie): (String, String, bool, String, String)| {
                USERS {
                    user_uuid,
                    user_username,
                    user_canbulk,
                    user_email,
                    user_cookie,
                }
            });
    
            // check how many rows are returned
            match result {
                Ok(fetched_risks) => {
                    if fetched_risks.len() > 0 {
                        return true;
                    }
                },
                Err(_) => {
                    return false;
                }
            }
    
            return false;
        }
    
        println!("No database connection");
        return false;
    }

    pub async fn generate_cookie(user_email:String) -> Uuid {
        // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
        let lock_result = unsafe { DB_CLIENT.lock() };
    
        if lock_result.is_err() {
            // kill script
            trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
            std::process::exit(1);
        }
    
        // check if need to create new client
        if lock_result.unwrap().is_none() {
            new_client().await;
        }
    
        // perform database operations
        let db_client = unsafe { DB_CLIENT.lock().unwrap() };
    
        let db_client = db_client.as_ref();
    
        if let Some(pool) = db_client {
            let mut conn = pool.get_conn().unwrap();
    
            let user_cookie = Uuid::new_v4();
    
            let query = format!("UPDATE users SET user_cookie = '{}' WHERE user_email = '{}'", user_cookie.to_string(), user_email);
    
            let result = conn.query_drop(query);
    
            match result {
                Ok(_) => {
                    return user_cookie;
                },
                Err(_) => {
                    return Uuid::nil();
                }
            }
        }
    
        println!("No database connection");
        return Uuid::nil();
    }
}

pub struct MAIL {
    pub mail_uuid: String,
    pub mail_content: String,
    pub mail_result: String,
    pub mail_user_uuid: String,
}

impl MAIL {
    pub fn default() -> MAIL {
        MAIL {
            mail_uuid: "".to_string(),
            mail_content: "".to_string(),
            mail_result: "".to_string(),
            mail_user_uuid: "".to_string(),
        }
    }

    // Retourne la liste des mails liées à un utilisateur
    pub async fn get_mails(user_uuid: String) -> Vec<MAIL> {
        // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
        let lock_result = unsafe { DB_CLIENT.lock() };
    
        if lock_result.is_err() {
            // kill script
            trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
            std::process::exit(1);
        }
    
        // check if need to create new client
        if lock_result.unwrap().is_none() {
            new_client().await;
        }
    
        // perform database operations
        let db_client = unsafe { DB_CLIENT.lock().unwrap() };
    
        let db_client = db_client.as_ref();

        let mut msgs: Vec<MAIL> = Vec::new();

        if let Some(pool) = db_client {
            let mut conn = pool.get_conn().unwrap();
            let query = format!("SELECT mail_uuid, mail_content, mail_result FROM mails WHERE mail_user_uuid = '{}'", user_uuid);

            let result = conn.query_map(query, |(mail_uuid, mail_content, mail_result): (String, String, String)| {
                MAIL {
                    mail_uuid,
                    mail_content,
                    mail_result,
                    mail_user_uuid: user_uuid.clone(),
                }
            });

            // check how many rows are returned
            match result {
                Ok(fetched_msgs) => {
                    for msg in fetched_msgs {
                        msgs.push(msg);
                    }
                },
                Err(_) => {
                    return msgs;
                }
            }

            return msgs;
        }

        println!("No database connection");
        return msgs;
    }

    // Retourne les informations d'un mail
    pub async fn get_mail_info(mail_uuid: String) -> MAIL{
        // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
        let lock_result = unsafe { DB_CLIENT.lock() };
    
        if lock_result.is_err() {
            // kill script
            trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
            std::process::exit(1);
        }
    
        // check if need to create new client
        if lock_result.unwrap().is_none() {
            new_client().await;
        }
    
        // perform database operations
        let db_client = unsafe { DB_CLIENT.lock().unwrap() };
    
        let db_client = db_client.as_ref();
    
        if let Some(pool) = db_client {
            let mut conn = pool.get_conn().unwrap();
    
            let query = format!("SELECT mail_uuid, mail_content, mail_result, mail_user_uuid FROM mails WHERE mail_uuid = '{}'", mail_uuid);
    
            let result = conn.query_first::<(String, String, String, String), _>(query);

            // check how many rows are returned
            match result {
                Ok(Some(fetched_msg)) => {
                    // Assuming MAIL has fields like mail_uuid, mail_content, mail_result, and mail_user_uuid
                    return MAIL {
                        mail_uuid: fetched_msg.0,
                        mail_content: fetched_msg.1,
                        mail_result: fetched_msg.2,
                        mail_user_uuid: fetched_msg.3,
                    };
                }
                Ok(None) => {
                    // If no result is found, return a default MAIL
                    return MAIL::default();
                }
                Err(_) => {
                    // Handle query execution error
                    return MAIL::default();
                }
            }
        }
    
        println!("No database connection");
        return MAIL::default();
    }



    pub async fn create_mail(mail_content: String, mail_result: String, mail_user_uuid: String) {
        // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
        let lock_result = unsafe { DB_CLIENT.lock() };
    
        if lock_result.is_err() {
            // kill script
            trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
            std::process::exit(1);
        }
    
        // check if need to create new client
        if lock_result.unwrap().is_none() {
            new_client().await;
        }
    
        // perform database operations
        let db_client = unsafe { DB_CLIENT.lock().unwrap() };
    
        let db_client = db_client.as_ref();
    
        if let Some(pool) = db_client {
            let mut conn = pool.get_conn().unwrap();
    
            let mail_uuid = Uuid::new_v4().to_string();
            let clean_content = mail_content.replace("\"", "\\\"").replace("'", "\\'");
            let clean_result = mail_result.replace("\"", "\\\"").replace("'", "\\'");
    
            let query = format!("INSERT INTO mails (mail_uuid, mail_content, mail_result, mail_user_uuid) VALUES ('{}', '{}', '{}', '{}')", mail_uuid, clean_content, clean_result, mail_user_uuid);
   
            println!("{}", query);
            let result = conn.query_drop(query);
    
            match result {
                Ok(_) => {
                    return;
                },
                Err(msg) => {
                    trace_logs(msg.to_string());
                    return;
                }
            }
        }
    
        println!("No database connection");
        return;
    }
}

// ------------ DATABASE SYSTEM ------------

static mut DB_CLIENT: Lazy<Arc<Mutex<Option<mysql::Pool>>>> = Lazy::new(|| {
    Arc::new(Mutex::new(None))
});

async fn new_client() {

    let (tx, _rx) = mpsc::channel();

    thread::spawn(move || {
        tokio::runtime::Runtime::new().unwrap().block_on(async {
            periodic_database().await;
            tx.send(()).unwrap(); // Signal that work is done
        });
    });

    reset_database().await
}

async fn periodic_database() {
    let mut interval = interval(Duration::from_secs(300));
    loop {
        interval.tick().await;
        reset_database().await;
    }
}

async fn reset_database() {

    let mut h = "127.0.0.1";

    let config = fs::read_to_string("config/default.json").unwrap();
    let config: serde_json::Value = serde_json::from_str(config.as_str()).unwrap();

    let port: u16 = config.get("db_port").unwrap().as_u64().unwrap() as u16;
    let host:String = config.get("db_host").unwrap().as_str().unwrap().to_owned();
    let db_username:String = config.get("db_username").unwrap().as_str().unwrap().to_owned();
    let db_password:String = config.get("db_password").unwrap().as_str().unwrap().to_owned();

    // check if process arg --prod is used
    if std::env::args().any(|arg| arg == "--prod") {
        h = host.as_str();
    }

    // Define MySQL connection options
    let opts = mysql::OptsBuilder::new()
        .ip_or_hostname(Some(h))
        .tcp_port(port)
        .db_name(Some(DB_NAME))
        .user(Some(db_username))
        .pass(Some(db_password));

    // hcekc if DB_CLIENT.lock().unwrap().is_none() return any poison error
    if mysql::Pool::new(opts.clone()).is_err() {
        return ;
    }

    // Create a new MySQL connection pool
    let pool = mysql::Pool::new(opts).unwrap();

    unsafe {
        let mut db_client = DB_CLIENT.lock().unwrap();
        *db_client = Some(pool);
    }

}

pub async fn check_db_is_up() -> bool {

    reset_database().await;

    let db_client = unsafe { DB_CLIENT.lock().unwrap() };

    if db_client.is_none() {
        return false;
    }

    let db_client = db_client.as_ref().unwrap();

    let mut conn = db_client.get_conn().unwrap();

    let query = "SELECT 1";

    let result = conn.query_map(query, |_: i32| {
        ()
    });

    match result {
        Ok(_) => {
            return true;
        },
        Err(_) => {
            return false;
        }
    }
}

/***
 *     ____    __   ____   __    ____    __    ___  ____ 
 *    (  _ \  /__\ (_  _) /__\  (  _ \  /__\  / __)( ___)
 *     )(_) )/(__)\  )(  /(__)\  ) _ < /(__)\ \__ \ )__) 
 *    (____/(__)(__)(__)(__)(__)(____/(__)(__)(___/(____)
 */

// ------------ DATABASE UTILS ------------
pub async fn check_if_table_exist(table_name:String) -> bool {
    // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
    let lock_result = unsafe { DB_CLIENT.lock() };

    if lock_result.is_err() {
        // kill script
        trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
        std::process::exit(1);
    }

    // check if need to create new client
    if lock_result.unwrap().is_none() {
        new_client().await;
    }

    // perform database operations
    let db_client = unsafe { DB_CLIENT.lock().unwrap() };

    let db_client = db_client.as_ref();

    if let Some(pool) = db_client {
        let mut conn = pool.get_conn().unwrap();

        let query = format!("SELECT table_name FROM information_schema.tables WHERE table_name = '{}' AND table_schema = '{}' LIMIT 1", table_name, DB_NAME);

        let result = conn.query_map(query, |table_name: String| {
            table_name
        });

        // check how many rows are returned
        match result {
            Ok(fetched_table) => {
                if fetched_table.len() > 0 {
                    return true;
                }
            },
            Err(_) => {
                return false;
            }
        }

        return false;
    }

    println!("No database connection");
    return false;
}

pub async fn create_table(table_name:String, column:Vec<serde_json::Value>) {
    // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
    let lock_result = unsafe { DB_CLIENT.lock() };

    if lock_result.is_err() {
        // kill script
        trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
        std::process::exit(1);
    }

    // check if need to create new client
    if lock_result.unwrap().is_none() {
        new_client().await;
    }

    // perform database operations
    let db_client = unsafe { DB_CLIENT.lock().unwrap() };

    let db_client = db_client.as_ref();

    if let Some(pool) = db_client {
        let mut conn = pool.get_conn().unwrap();

        let mut query = format!("CREATE TABLE {} (", table_name);

        for (i, col) in column.iter().enumerate() {
            if i == column.len() - 1 {
                query.push_str(&format!("{} {})", col["name"], col["type"]));
            } else {
                query.push_str(&format!("{} {}, ", col["name"], col["type"]));
            }
        }

        query = query.replace("\"", "");
        println!("{}", query);

        let result = conn.query_drop(query);

        match result {
            Ok(_) => {
                return;
            },
            Err(msg) => {
                trace_logs(msg.to_string());
                return;
            }
        }
    }

    println!("No database connection");
    return;
}

pub async fn check_column_exist(table_name:String, column_name:String) -> bool {
    // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
    let lock_result = unsafe { DB_CLIENT.lock() };

    if lock_result.is_err() {
        // kill script
        trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
        std::process::exit(1);
    }

    // check if need to create new client
    if lock_result.unwrap().is_none() {
        new_client().await;
    }

    // perform database operations
    let db_client = unsafe { DB_CLIENT.lock().unwrap() };

    let db_client = db_client.as_ref();

    if let Some(pool) = db_client {
        let mut conn = pool.get_conn().unwrap();

        let query = format!("SELECT column_name FROM information_schema.columns WHERE table_name = '{}' AND column_name = '{}'  AND database = '{}' LIMIT 1", table_name, column_name, DB_NAME);

        let result = conn.query_map(query, |(column_name): (String)| {
            column_name
        });

        // check how many rows are returned
        match result {
            Ok(fetched_column) => {
                if fetched_column.len() > 0 {
                    return true;
                }
            },
            Err(_) => {
                return false;
            }
        }

        return false;
    }

    println!("No database connection");
    return false;
}

pub async fn add_column(table_name:String, column_name:String, column_type:String) {
    // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
    let lock_result = unsafe { DB_CLIENT.lock() };

    if lock_result.is_err() {
        // kill script
        trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
        std::process::exit(1);
    }

    // check if need to create new client
    if lock_result.unwrap().is_none() {
        new_client().await;
    }

    // perform database operations
    let db_client = unsafe { DB_CLIENT.lock().unwrap() };

    let db_client = db_client.as_ref();

    if let Some(pool) = db_client {
        let mut conn = pool.get_conn().unwrap();

        let query = format!("ALTER TABLE {} ADD COLUMN {} {}", table_name, column_name, column_type);

        let result = conn.query_drop(query);

        match result {
            Ok(_) => {
                return;
            },
            Err(_) => {
                return;
            }
        }
    }

    println!("No database connection");
    return;
}

pub async fn get_all_col(table_name:String) -> Vec<String> {
    // check if DB_CLIENT.lock().unwrap().is_none() return any poison error
    let lock_result = unsafe { DB_CLIENT.lock() };

    if lock_result.is_err() {
        // kill script
        trace_logs("Error: DB_CLIENT.lock().unwrap() is_none() return any poison".to_owned());
        std::process::exit(1);
    }

    // check if need to create new client
    if lock_result.unwrap().is_none() {
        new_client().await;
    }

    // perform database operations
    let db_client = unsafe { DB_CLIENT.lock().unwrap() };

    let db_client = db_client.as_ref();

    let mut columns: Vec<String> = Vec::new();

    if let Some(pool) = db_client {
        let mut conn = pool.get_conn().unwrap();

        let query = format!("SHOW COLUMNS FROM {}", table_name);

        let result = conn.query_map(query, |col: String| {
            col
        });

        // check how many rows are returned
        match result {
            Ok(fetched_columns) => {
                for col in fetched_columns {
                    columns.push(col);
                }
            },
            Err(_) => {
                return columns;
            }
        }

        return columns;
    }

    println!("No database connection");
    return columns;
}

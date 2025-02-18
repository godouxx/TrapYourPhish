import imaplib
import email
from email.header import decode_header
import time


EMAIL_USER = "ton.email@gmail.com"
EMAIL_PASS = "mot-de-passe-application"  # Utiliser un mot de passe d'application IMAP
IMAP_SERVER = "imap.gmail.com"

def connect_to_gmail():

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        print("Connexion réussie à Gmail")
        return mail
    except imaplib.IMAP4.error:
        print("Erreur : Connexion IMAP refusée. Vérifiez vos identifiants Gmail ou les paramètres IMAP.")
        return None
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return None


def extract_subject(msg):
    """Extrait le sujet de l'email"""
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        try:
            return subject.decode(encoding if encoding else "utf-8")
        except:
            return "Sujet non décodable"
    return subject if subject else "Aucun sujet"


def fetch_unread_emails(folder="INBOX"):

    mail = connect_to_gmail()
    if mail is None:
        return
    try:
        mail.select(folder)
        status, messages = mail.search(None, 'UNSEEN')  # Filtrer les emails non lus
        email_ids = messages[0].split()
        folder_name = "Boîte de réception" if folder == "INBOX" else "Spams"
        print(f" Nombre d'emails non lus dans {folder_name} : {len(email_ids)}")
        for email_id in email_ids:
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    # Extraction du sujet
                    subject = extract_subject(msg)
                    print(f"📧 Email non lu : {subject}")

    except Exception as e:
        print(f"[Erreur lors de la récupération des emails de {folder_name} : {e}")

    finally:
        mail.logout()


# Boucle d'exécution pour vérifier les emails toutes les 30 secondes
while True:
    print("\nVérification des nouveaux emails dans la boîte de réception...")
    fetch_unread_emails("INBOX")  # Vérifier la boîte de réception

    print("\n Vérification des nouveaux emails dans les spams...")
    fetch_unread_emails("[Gmail]/Spam")  # Vérifier les spams

    print("\n Attente de 30 secondes avant la prochaine vérification...\n")
    time.sleep(30)

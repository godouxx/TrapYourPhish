from simplegmail import Gmail
import json

gmail = Gmail()

# Unread messages in your inbox
messages = gmail.get_unread_inbox()

# Convert messages to dictionaries with specific labels
messages_dict = []
for message in messages:
    message_info = {
        "from": message.sender,
        "to": message.recipient,
        "id": message.id,
        "subject": message.subject,
        "date": message.date,
        "snippet": message.snippet,
        "body": message.plain
    }
    messages_dict.append(message_info)

# Save all the messages in a JSON file
with open("emails.json", "w") as f:
    json.dump(messages_dict, f, indent=4)

print("Messages saved to emails.json")
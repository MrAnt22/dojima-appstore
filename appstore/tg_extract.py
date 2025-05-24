from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument
from decouple import config
import json 
import asyncio
import json
import os

api_id = config('TELEGRAM_API_ID')
api_hash = config('TELEGRAM_API_HASH')

session_name = config('SESSION_NAME')
chat_input = config('CHAT_NAME')
save_dir = config('SAVE_DIR')

# --- functions ---

async def main(chat_name, limit):
    async with TelegramClient(session_name, api_id, api_hash) as client:
        
        chat_info = await client.get_entity(chat_name)
        
        messages = await client.get_messages(entity=chat_info, limit=limit)
        
        return ({"messages": messages, "channel": chat_info})

async def download_files(messages, client):
    os.makedirs(save_dir, exist_ok=True)
    downloaded_files = {}

    for msg in messages:
        if hasattr(msg, 'media') and isinstance(msg.media, MessageMediaDocument):
            try:
                filename = None
                doc = msg.media.document
                if doc and doc.attributes:
                    for attr in doc.attributes:
                        if type(attr).__name__ == "DocumentAttributeFilename":
                            filename = attr.file_name
                            break
                
                if not filename:
                    filename = f"{msg.id}_file"

                full_path = os.path.join(save_dir, filename)

                file_path = await client.download_media(msg, file=full_path)
                downloaded_files[msg.id] = file_path
                print(f"[+] Downloaded message {msg.id} to {file_path}")
            except Exception as e:
                print(f"[!] Failed to download media from message {msg.id}: {e}")
    
    return downloaded_files

async def clean_telegram_json(data, msg_list):
    clean_data = []

    async with TelegramClient(session_name, api_id, api_hash) as client:
        files_downloaded =  await download_files(msg_list, client)

    for msg in data:
        text = msg.get("message", "")
        lines = text.strip().splitlines()
        title = lines[0] if lines else ""
        description = "\n".join(lines[1:]) if len(lines) > 1 else ""

        reactions = msg.get("reactions")
        reaction_data = reactions.get("results", []) if reactions else []
        reaction_count = sum(item.get("count", 0) for item in reaction_data)

        file_path = files_downloaded.get(msg["id"])
        files = [file_path] if file_path else []

        clean_data.append({
            "title": title,
            "description": description,
            "files": files,
            "created": msg.get("date"),
            "updated": msg.get("edit_date"),
            "views": msg.get("views", 0),
            "likes": reaction_count
        })

    return clean_data

# --------------------------
    
results = asyncio.run(main(chat_name=chat_input, limit=10))
msg_list = [msg.to_dict() for msg in results["messages"]]

out_path = os.path.join(config("TELEGRAM_DIR"), f"{chat_input}.json")
with open(out_path, "w") as f:
        json.dump(msg_list, f, default=str, ensure_ascii=False, indent=2)

with open(out_path, "r") as f:
    raw_data = json.load(f)

cleaned =  asyncio.run(clean_telegram_json(raw_data, results["messages"]))

clean_path = os.path.join(config("TELEGRAM_DIR"), f"cleaned.json")
with open(clean_path, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)
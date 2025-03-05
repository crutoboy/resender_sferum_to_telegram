import time
import pprint
import json
import os
from datetime import datetime

import telebot
from telebot import types

import SferumAPI
from config import TG_TOKEN, REMIXDSID_TOKEN_TO_SFERUM, SFERUM_TARGET_PEER_ID, TG_TARGET_CHAT_ID, DIR_FOR_LOG_UNKNOWN_TYPE_ATTACHMENTS, UPDATE_AUTH_INTERVAL


bot = telebot.TeleBot(TG_TOKEN)
api = SferumAPI.SferumAPI(remixdsid=REMIXDSID_TOKEN_TO_SFERUM)
last_update_vk_auth = datetime.now()

with open('./vk_scripts/get_unread_msg_from_peer.js', 'r') as file:
    script_from_get_unread_message = f"var peer_id = {SFERUM_TARGET_PEER_ID};\n" + file.read()

def mark_as_read(messages: dict):
    if len(messages) > 0:
        mark_as_read_resp = api.messages.mark_as_read(SFERUM_TARGET_PEER_ID)

def main(resp_from_vk: dict):
    messages = resp_from_vk.get('messages')[::-1]
    profiles = resp_from_vk.get('profiles')
    iter_messages(messages, profiles)
    mark_as_read(messages)

def iter_messages(messages: dict, profiles: dict, forward: bool = False):
    for message in messages:
        message_handler(message, profiles, forward)
    
def message_handler(message: dict, profiles: dict, forward: bool = False):
    fwd_messages = message.get('fwd_messages', [])
    if len(fwd_messages) > 0:
        iter_messages(fwd_messages, profiles, forward=True)

    if message.get('attachments'):
        send_attachments(message)

    send_text(message, profiles, forward)

def send_text(message: dict, profiles: dict, forward: bool):
    text = message.get('text', '')
    user_id = message.get('from_id')
    profile = get_profile_from_id(profiles, user_id)
    what_do = 'пишет'
    if forward:
        what_do = 'переслал(а)'
    answer = generate_text_message(message, profile, what_do)
    bot.send_message(TG_TARGET_CHAT_ID, answer)

def get_profile_from_id(profiles: tuple, id: int) -> dict:
    for i in profiles:
        cur_id = i.get('id')
        if cur_id == id:
            return i

def generate_text_message(message, profile, what_doing='пишет'):
    first_name = profile.get('first_name')
    last_name = profile.get('last_name')
    text = message.get('text')
    
    msg = f'{first_name} {last_name} {what_doing}: \n\n{text}'
    return msg

def group_attachments(message: dict):
    attachments = message.get('attachments')
    result = {'photo': [], 'doc': [], 'unknown': []}
    for attachment in attachments:
        type_attachment = attachment.get('type', 'unknown')
        result[type_attachment].append(attachment.get(type_attachment))
    result['count'] = len(attachments)
    return result

def send_attachments(message: dict):
    attachments = group_attachments(message)
    send_photo(attachments)
    send_doc(attachments)
    send_log_about_unknown(attachments)

def send_photo(attachments: dict):
    photos = attachments.get('photo', [])
    if len(photos) > 1:
        photo_objects = [types.InputMediaPhoto(i['orig_photo']['url']) for i in photos]
        bot.send_media_group(TG_TARGET_CHAT_ID, photo_objects)
    elif len(photos) == 1:
        url = photos[0]['orig_photo']['url']
        bot.send_photo(TG_TARGET_CHAT_ID, url)

def send_doc(attachments: dict):
    docs = attachments.get('doc', [])
    if len(docs) > 1:
        document_objects = [types.InputMediaDocument(i['url']) for i in docs]
        bot.send_media_group(TG_TARGET_CHAT_ID, document_objects)
    elif len(docs) == 1:
        url = docs[0]['url']
        bot.send_document(TG_TARGET_CHAT_ID, url)

def send_log_about_unknown(attachments: dict):
    unknowns = attachments.get('unknown', [])
    if len(unknowns) == 0:
        return None
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    filename = f"unknown_type_{timestamp}.log"
    path_to_file = os.path.join(DIR_FOR_LOG_UNKNOWN_TYPE_ATTACHMENTS, filename)
    with open(path_to_file, 'w') as file:
        json.dump(unknowns, file)
    with open(path_to_file, 'r') as file:
        bot.send_document(TG_TARGET_CHAT_ID, file, caption='отправлено не поддерживание вложение. сырой объект в этом файле и на сервере')

def update_auth(api_object: SferumAPI.SferumAPI):
    global last_update_vk_auth
    if (datetime.now() - last_update_vk_auth).total_seconds() > UPDATE_AUTH_INTERVAL:
        api_object.users.authorize()
        last_update_vk_auth = datetime.now()

# resp = api.messages.execution_vkscript(script_from_get_unread_message).get('response')
# print(resp)

if __name__ == '__main__':
    while True:
        try:
            update_auth(api)
            resp = api.messages.execution_vkscript(script_from_get_unread_message).get('response')
            main(resp)
            time.sleep(0.5)
        except Exception as error:
            timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            print(timestamp)
            print(error)
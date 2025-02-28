import time
import pprint
import telebot

import SferumAPI
from config import TG_TOKEN, REMIXDSID_TOKEN_TO_SFERUM, SFERUM_TARGET_PEER_ID, TG_TARGET_CHAT_ID


# bot = pyrogram.Client("sferum_resender_bot", bot_token=TG_TOKEN)
bot = telebot.TeleBot(TG_TOKEN)
api = SferumAPI.SferumAPI(remixdsid=REMIXDSID_TOKEN_TO_SFERUM)

with open('./vk_scripts/get_unread_msg_from_peer.js', 'r') as file:
    script_from_get_unread_message = f"var peer_id = {SFERUM_TARGET_PEER_ID};\n" + file.read()
# print(script_from_get_unread_message)


def get_profile_from_id(profiles: tuple, id: int) -> dict:
    for i in profiles:
        cur_id = i.get('id')
        if cur_id == id:
            return i

# bot.start()
while True:
    resp = api.messages.execution_vkscript(script_from_get_unread_message).get('response')
    messages = resp.get('messages')[::-1]

    for i in messages:
        user = get_profile_from_id(resp.get('profiles'), i.get('from_id'))
        first_name = user.get('first_name')
        last_name = user.get('last_name')
        text = i.get('text')
        pprint.pprint(i)
        msg = f'{first_name} {last_name} пишет: \n\n{text}'

        bot.send_message(TG_TARGET_CHAT_ID, msg)
        print(msg)

    if len(messages) > 0:
        mark_as_read_resp = api.messages.mark_as_read(SFERUM_TARGET_PEER_ID)
        print(mark_as_read_resp)

    time.sleep(0.5)

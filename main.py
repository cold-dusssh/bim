import telebot
from telebot import types
import requests
from io import BytesIO
import html
import g4f
import json
from config import *
from bS import log


prompt = ""
with open("prompt.txt") as f:
    prompt = f.readlines()[0].strip()

whiteListUsers = []
whiteList = False
GPTModel = "deepseek-r1"
ADMIN_ID = [5737305913, 1816346878]
MODELS = ["gpt-4o", "gpt-3.5-turbo", "gemini-1.5-flash", "gemini-1.5-pro", "deepseek-r1"]

bot = telebot.TeleBot(BOT_TOKEN)

def savehistory(chatid, history):
    with open(f"history/{chatid}.json", "w", encoding="utf-16") as f:
        json.dump(history, f)

def gethistory(chatid):
    with open(f"history/{chatid}.json", "r", encoding="utf-16") as f:
        chat_context = json.load(f)
    return chat_context

def isUserInWhiteList(id):
    global whiteListUsers, whiteList
    if not whiteList:
        return True
    return id in whiteListUsers

def gpt(message):
    global GPTModel

    userInput = message.text.strip()
    chat_id = message.chat.id
    log(f"@{message.from_user.username} : {userInput}")
    
    chat_context = gethistory(chat_id)

    chat_context.append({"role": "user", "content": userInput})
    bot.send_chat_action(chat_id, "typing")

    prompt = f'Пользователь по имени {message.from_user.first_name} спросил: "{userInput}". Ответь четко и ясно на его вопрос.'
    prompt += "\nИстория беседы:\n" + "\n".join([item["content"] for item in chat_context])

    try:
        response = g4f.ChatCompletion.create(
            model = GPTModel,
            messages = [{"role": "user", "content": prompt}],
        )
        if isinstance(response, dict) and "choices" in response:
            assistant_message = response["choices"][0]["message"]["content"]
        else:
            assistant_message = str(response)
    except Exception as e:
        assistant_message = f"Произошла ошибка при генерации ответа: {str(e)}"
        log(assistant_message)

    chat_context.append({"role": "assistant", "content": assistant_message})
    
    def delete_think(assistant_message):
        assistant_message = assistant_message[assistant_message.rfind("<ans>") + 5: assistant_message.rfind("</ans>")]
        return assistant_message
        
    log(assistant_message)
    assistant_message = delete_think(assistant_message)
    # decoded_response = html.unescape(assistant_message)
    savehistory(chat_id, chat_context)
    split_messages = split_long_message(assistant_message)
    for msg in split_messages:
        bot.reply_to(message, msg, parse_mode = "Markdown")

def split_long_message(message, chunkSize=4096):
    return [message[i:i + chunkSize] for i in range(0, len(message), chunkSize)]



@bot.message_handler(commands=["start"], func = lambda message: message.chat.type == "private" and isUserInWhiteList(message.chat.id))
def start(message):
    global prompt
    try:
        chat_id = message.chat.id
        chat_context = [{"role": "system", "content": prompt}]
        savehistory(chat_id, chat_context)
    except Exception as e:
        log(e)
    text = gpt(message)
    bot.reply_to(message, text, parse_mode = "Markdown")

@bot.message_handler(commands=["menu"], func = lambda message: message.chat.type == "private" and isUserInWhiteList(message.chat.id))
def menu(message):
    bot.reply_to(message, "MENU", parse_mode = "Markdown")

@bot.message_handler(commands=["gdz"], func = lambda message: message.chat.type == "private" and isUserInWhiteList(message.chat.id))
def gdz(message):
    try:
        subject, taskNum = [_.lower() for _ in message.text.split()[1:3]]
    except Exception as e:
        bot.reply_to(message, "НЕВЕРНЫЙ ФОРМАТ", parse_mode = "Markdown")
        return

    if subject in ["rus", "ru", "r", "русский", "рус"]:
        try:
            photo_url = f"https://reshak.ru/reshebniki/russkijazik/10-11/goltsova/images1/part1/{taskNum}.png"
            response = requests.get(photo_url)
            response.raise_for_status()
            photo = BytesIO(response.content)
            photo.name = f"rus{taskNum}.png"
            bot.send_photo(message.chat.id, photo, reply_to_message_id = message.message_id)

        except requests.RequestException as e:
            bot.reply_to(message, f"Я не смогла загрузить для Вас гдз 😭: {e}")

        except Exception as e:
            bot.reply_to(message, f"Произошел какой-то ужас: {e}")

    elif subject in ["physics", "phys", "phy", "физика", "физ"]:
        try:
            photo_url = f"https://reshak.ru/reshebniki/fizika/10/rimkevich10-11/images1/{taskNum}.png"
            response = requests.get(photo_url)
            response.raise_for_status()
            photo = BytesIO(response.content)
            photo.name = f"rus{taskNum}.png"
            bot.send_photo(message.chat.id, photo, reply_to_message_id = message.message_id)

        except requests.RequestException as e:
            bot.reply_to(message, f"Я не смогла загрузить для Вас гдз 😭: {e}")

        except Exception as e:
            bot.reply_to(message, f"Произошел какой-то ужас: {e}")

    elif subject in ["algebra", "alg", "al", "алгебра", "алг"]:
        try:
            url = f"https://gdz.fm/algebra/10-klass/merzlyak-nomirovskij-uglublennij?ysclid=m5v4pyw2zy982385215#taskContainer?t={taskNum.split('/')[0]}-par-{taskNum.split('/')[1]}"
            response = requests.get(url)
            response.raise_for_status()
            bot.reply_to(message, url)

        except requests.RequestException as e:
            bot.reply_to(message, f"Я не смогла загрузить для Вас гдз 😭: {e}")

        except IndexError:
            bot.reply_to(message, f"Неверный формат!")

        except Exception as e:
            bot.reply_to(message, f"Произошел какой-то ужас: {e}")

    else:
        bot.reply_to(message, "НЕВЕРНЫЙ ПРЕДМЕТ")


@bot.message_handler(commands=["reset", "delcontext"], func = lambda message: message.chat.type == "private" and isUserInWhiteList(message.chat.id))
def reset(message):
    try:
        chat_id = message.chat.id
        # if chat_id in chat_contexts:
        #     chat_contexts.pop(chat_id)
        with open("end-message.txt") as f:
            text = f.readlines()[0].strip()
        chat_context = [{"role": "system", "content": prompt}]
        savehistory(chat_id, chat_context)
        bot.send_message(chat_id, text)
    except Exception as e:
        print(e)

@bot.message_handler(commands=["model"], func = lambda message: message.chat.type == "private" and isUserInWhiteList(message.chat.id))
def model(message):
    global GPTModel

    if message.from_user.id in ADMIN_ID:
        try:
            model = message.text.split()[1]
            if model in MODELS:
                GPTModel = model
                bot.reply_to(message, f"success : {GPTModel}")
            else:
                bot.reply_to(message, f"models : {MODELS}")
        except Exception:
            bot.reply_to(message, f"models : {'; '.join(MODELS)}\ncurrent model: {GPTModel}")

@bot.message_handler(content_types = ["text"], func = lambda message: message.chat.type == "private" and isUserInWhiteList(message.chat.id))
def textGPT(message):
    gpt(message)

bot.polling(none_stop = True)

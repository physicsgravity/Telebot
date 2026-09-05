from config import API_TOKEN
import telebot
import json
import os
import re
import random

bot = telebot.TeleBot(token=API_TOKEN)

telebot.apihelper.proxy = {"https": 'socks5h://127.0.0.1:1080'}

WARNINGS_FILE = "warnings.json"

# بارگذاری اخطارها از فایل (اگه وجود داشته باشه)
def load_warnings():
    if os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_warnings():
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warnings, f, ensure_ascii=False, indent=2)

warnings = load_warnings()

def is_admin(message):
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    return status in ("administrator", "creator")


@bot.message_handler(func=lambda message: message.reply_to_message is not None and message.text in ["بن", "سکوت", "رفع سکوت", "اخطار"])
def moderation(message):
    if not is_admin(message):
        return

    target = message.reply_to_message.from_user
    chat_id = str(message.chat.id)   # کلیدهای JSON باید رشته باشن
    target_id = str(target.id)
    text = message.text.strip()

    if text == "بن":
        bot.ban_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"{target.first_name} بن شد. 🚫")

    elif text == "سکوت":
        bot.restrict_chat_member(message.chat.id, target.id, can_send_messages=False)
        bot.reply_to(message, f"{target.first_name} سکوت شد. 🔇")

    elif text == "رفع سکوت":
        bot.restrict_chat_member(
            message.chat.id, target.id,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        bot.reply_to(message, f"سکوت {target.first_name} برداشته شد. 🔊")

    elif text == "اخطار":
        chat_warnings = warnings.setdefault(chat_id, {})
        count = chat_warnings.get(target_id, 0) + 1
        chat_warnings[target_id] = count

        if count >= 3:
            bot.restrict_chat_member(message.chat.id, target.id, can_send_messages=False)
            bot.reply_to(message, f"⚠️ {target.first_name} سه اخطار گرفت و سکوت شد. 🔇")
            chat_warnings[target_id] = 0
        else:
            bot.reply_to(message, f"⚠️ {target.first_name} اخطار گرفت. ({count}/3)")

        save_warnings()   # بعد از هر تغییر، ذخیره کن


@bot.message_handler(commands=["start"])
def welcome(message):
    welcome_text = f"user {message.from_user.first_name} welcome to Hiro Bot"
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(func=lambda message: "سلام" in message.text)
def جواب_سلام(message):
    bot.reply_to(message, "سلام عزیزم حالت چطوره؟")

@bot.message_handler(func=lambda message: "شاه" in message.text or "پهلوی" in message.text)
def جاوید_شاه(message):
    bot.reply_to(message, "جاوید شاه❤️👑")

@bot.message_handler(regexp="امید دانا|امیددانا|رودست")
def امید(message):
    bot.reply_to(message, "درود بر امید دانا❤️")

responses = [
    {"patterns": ["سلام", "درود", "علیک السلام", "سلامتی", "hi", "hello"],
        "replies": ["درود بر شما ❤️","سلام سلام! چطوری؟ 😊","به‌به سلام! خوش اومدی 🌹"]},

    {"patterns": ["خوبی", "چطوری", "حالت چطوره"],
        "replies": ["تریاک میکشم و تو اسمونام","عالیم! تو چه چطوری؟",]},

    {"patterns": ["خداحافظ", "بای", "فعلا", "می‌رم"],
        "replies": ["بدرود، مراقب خودت باش 🌷","به امید دیدار! 👋"]},

    {"patterns": ["ممنون", "مرسی", "تشکر"],
        "replies": ["خواهش می‌کنم 🌸","قابلی نداشت 😊"]},

    {"patterns": ["اسمت چیه", "تو کی هستی", "خودتو معرفی کن"],
        "replies": ["من هیرو ربات هستم و هیچ کمکی ازم ساخته نیستwe are cooked bro"]},

    {"patterns": ["ببخشید", "sorry", "معذرت"],
        "replies":["نمیبخشم", "seriously? after all the things you've done to ME?"],},
     {"patterns":["خمینی","امام"],
      "replies":["خمینی ای امام", "روح منی خمینی بت شکنی خمینی❤️"]},
]

def find_reply(text: str):
    """متن پیام رو با همه الگوها چک می‌کنه و اگه تطابق پیدا شد، یه جواب رندوم برمی‌گردونه"""
    text = text.lower()
    for group in responses:
        for pattern in group["patterns"]:
            if re.search(pattern, text):
                return random.choice(group["replies"])
    return None


@bot.message_handler(func=lambda m: True, content_types=["text"])
def smart_reply(message):
    reply = find_reply(message.text)
    if reply:
        bot.reply_to(message, reply)
    #else:
        # وقتی هیچ الگویی مچ نشد — می‌تونی اینجا به یه AI واقعی وصل بشی
        # (نمونه در پایین فایل توضیح داده شده)
        #bot.reply_to(message, "متوجه نشدم 🤔 می‌تونی واضح‌تر بگی؟")



bot.infinity_polling()
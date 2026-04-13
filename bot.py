import os
import certifi
import asyncio
import threading
from pyrogram import Client, errors
import telebot
from telebot import types
from backend import app
from db import database

DB = database()
App = app()
os.environ['SSL_CERT_FILE'] = certifi.where() 

api_id = '20663523'
api_hash = 'f75fe6157dd68bdf0df5198adbc590fd'
TELEGRAM_TOKEN = "8603925028:AAETfGb0r3ud-wFRzJPatAn67gN4wF4o5KI" 

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False, num_threads=55, skip_pending=True)

@bot.message_handler(commands=['start'])
def Admin(message):
    AddAccount = types.InlineKeyboardButton("اضافه حساب 🛎", callback_data="AddAccount")
    Accounts = types.InlineKeyboardButton("اكواد حساباتك 🖲", callback_data="Accounts")
    a1 = types.InlineKeyboardButton("نقل اعضاء 👤😇", callback_data="a1")
    inline = types.InlineKeyboardMarkup(keyboard=[[a1], [AddAccount], [Accounts]])
    bot.send_message(message.chat.id, """*مرحبا بك  👋اختار ما تريد من الازار اسفل 🔥يمكنك نقل اعضاء لجروبك 🛎من اي جروب اخر عام  ☄Creator : @amrakl *""", reply_markup=inline, parse_mode="markdown")

@bot.callback_query_handler(lambda call: True)
def handle_query(call):
    if call.data == "Accounts":
        num = len(DB.accounts())
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"حساباتك المسجلة بالكامل : {num}", parse_mode="markdown")
    
    if call.data == "AddAccount":
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*قوم بارسال الرقم الذي تريد تسليمه مع رمز الدولة الان*📞🎩", parse_mode="markdown")
        bot.register_next_step_handler(msg, AddAccount)
    
    if call.data == "a1":
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*قوم بارسال رابط الجروب المراد النقل منه *🖲", parse_mode="markdown")
        bot.register_next_step_handler(msg, statement)

def statement(message):
    Fromgrob = message.text
    msg = bot.send_message(chat_id=message.chat.id, text="*قوم بارسال رابط الجروب المراد النقل له*🛎", parse_mode="markdown")
    bot.register_next_step_handler(msg, statement2, Fromgrob)

def statement2(message, Fromgrob):
    Ingrob = message.text
    bot.send_message(chat_id=message.chat.id, text="*انتظر قليلا ⏱*", parse_mode="markdown")
    
    # Run async function in a thread
    def run_get_user():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        users = loop.run_until_complete(App.GETuser(Fromgrob, Ingrob))
        loop.close()
        return users

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_get_user)
        user_list = future.result()

    if not user_list:
        bot.send_message(message.chat.id, "*عذراً، لم يتم العثور على أعضاء أو حدث خطأ.*")
        return

    numUser = len(user_list)
    bot.send_message(message.chat.id, f"""*تم حفظ جميع الاعضاء المتاحه بنجاح *✅
*معلومات عملية النقل 🥸😇*
الاعضاء المتاحه : {numUser} عضو 😋
النقل من : {Fromgrob} 🎒
النقل الي : {Ingrob} 🧳
مده الفحص : 1 ثانية ⏱
انتظر الي ان تتم العملية 🎩* """, parse_mode="markdown")
    
    # Start adding users in background
    def run_add_user():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(App.ADDuser(user_list, Ingrob, message.chat.id, bot))
        loop.close()

    threading.Thread(target=run_add_user).start()

def AddAccount(message):
    try:
        if "+" in message.text:
            bot.send_message(message.chat.id, "*انتظر جاري الفحص* ⏱", parse_mode="markdown")
            _client = Client("::memory::", in_memory=True, api_id=api_id, api_hash=api_hash, lang_code="ar")
            _client.connect()
            SendCode = _client.send_code(message.text)
            Mas = bot.send_message(message.chat.id, "*أدخل الرمز المرسل إليك 🔏*", parse_mode="markdown")
            bot.register_next_step_handler(Mas, sigin_up, _client, message.text, SendCode.phone_code_hash, message.text)
        else:
            bot.send_message(message.chat.id, "*يرجى إدخال الرقم مع رمز الدولة بشكل صحيح (مثال: +20123456789)*")
    except Exception as e:
        bot.send_message(message.chat.id, f"ERROR: {str(e)}")

def sigin_up(message, _client, phone, hash, name):
    try:
        bot.send_message(message.chat.id, "*انتظر قليلا ⏱*", parse_mode="markdown")
        _client.sign_in(phone, hash, message.text)
        bot.send_message(message.chat.id, "*تم تاكيد الحساب بنجاح ✅ *", parse_mode="markdown")
        ses = _client.export_session_string()
        DB.AddAcount(ses, name, message.chat.id)
    except errors.SessionPasswordNeeded:
        Mas = bot.send_message(message.chat.id, "*أدخل كلمة المرور الخاصة بحسابك 🔐*", parse_mode="markdown")
        bot.register_next_step_handler(Mas, AddPassword, _client, name)
    except Exception as e:
        bot.send_message(message.chat.id, f"ERROR: {str(e)}")

def AddPassword(message, _client, name):
    try:
        _client.check_password(message.text) 
        ses = _client.export_session_string()
        DB.AddAcount(ses, name, message.chat.id)
        try:
            _client.stop()
        except:
            pass
        bot.send_message(message.chat.id, "*تم تاكيد الحساب بنجاح ✅ *", parse_mode="markdown")
    except Exception as e:
        print(e)
        try:
            _client.stop()
        except:
            pass
        bot.send_message(message.chat.id, f"ERROR: {str(e)}")

bot.infinity_polling(none_stop=True, timeout=15, long_polling_timeout=15)

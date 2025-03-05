from flask import Flask, request
import telebot
import json
import os

TOKEN = "7784209299:AAHeVTjwHMNglQV6wOTosvolltOhUcpqCos"  # توکن رباتتون رو اینجا بذارید
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

cart = {}
products = {
    "1": {"name": "محصول 1", "price": 100000},
    "2": {"name": "محصول 2", "price": 200000},
    "3": {"name": "محصول 3", "price": 300000}
}

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📋 محصولات", "🛒 سبد خرید", "📦 ثبت سفارش")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "به فروشگاه من خوش اومدی! چی می‌خوای؟", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📋 محصولات")
def show_products(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for pid, product in products.items():
        markup.add(telebot.types.InlineKeyboardButton(
            f"{product['name']} - {product['price']} تومن", 
            callback_data=f"add_{pid}"
        ))
    bot.reply_to(message, "محصولات ما:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_to_cart(call):
    user_id = call.from_user.id
    product_id = call.data.split("_")[1]
    if user_id not in cart:
        cart[user_id] = []
    cart[user_id].append(products[product_id])
    bot.answer_callback_query(call.id, f"{products[product_id]['name']} به سبد اضافه شد!")
    bot.send_message(call.message.chat.id, "محصول دیگه‌ای می‌خوای؟", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "🛒 سبد خرید")
def show_cart(message):
    user_id = message.from_user.id
    if user_id not in cart or not cart[user_id]:
        bot.reply_to(message, "سبد خریدت خالیه!", reply_markup=main_menu())
        return
    total = sum(item['price'] for item in cart[user_id])
    cart_text = "سبد خریدت:\n" + "\n".join([f"- {item['name']} ({item['price']} تومن)" for item in cart[user_id]])
    cart_text += f"\n\nجمع کل: {total} تومن"
    bot.reply_to(message, cart_text, reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📦 ثبت سفارش")
def checkout(message):
    user_id = message.from_user.id
    if user_id not in cart or not cart[user_id]:
        bot.reply_to(message, "سبد خریدت خالیه!", reply_markup=main_menu())
        return
    total = sum(item['price'] for item in cart[user_id])
    bot.reply_to(message, f"سفارشت ثبت شد! جمع کل: {total} تومن\nبه زودی باهات تماس می‌گیریم.", reply_markup=main_menu())
    del cart[user_id]

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return "ربات فروشگاهی فعال است!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

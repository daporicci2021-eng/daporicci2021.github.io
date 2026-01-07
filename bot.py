import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F

# Твой токен от @BotFather
API_TOKEN = '8366303303:AAE51tGCunmiQjyKLD9J_GJ18IZAxy4l18w'  # Замени на реальный токен!

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранение данных пользователя (в реальности используй БД, например SQLite)
user_data = {}  # user_id: {'rp': 148, 'online_hours': 3, 'vip': 'Gold/Plat', 'multiplier': 'X2', 'toggles': {...}}

TOGGLES = ['Лотерея', 'Тир', 'Киностудия', 'Кинотеатр', 'Сайт', 'Brawl', 'Лайк в Match']

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'rp': 148,
            'online_hours': 3,
            'online_minutes': 0,
            'vip': 'Gold/Plat',
            'multiplier': 'X2',
            'toggles': {name: True for name in TOGGLES}  # Все включены по умолчанию
        }
    return user_data[user_id]

# Главное меню (нижняя клавиатура)
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [
        KeyboardButton('⚔️ Фарм'),
        KeyboardButton('⏰ Таймеры'),
        KeyboardButton('🍳 Кулинария'),
        KeyboardButton('📅 Календари'),
        KeyboardButton('📖 Гайды'),
        KeyboardButton('💎 Донат')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню фарма с переключателями
def farm_menu(user_id):
    data = get_user_data(user_id)
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(InlineKeyboardButton('🏠 Лотерея', callback_data='toggle_Лотерея'))
    keyboard.add(InlineKeyboardButton('🎯 Тир', callback_data='toggle_Тир'))
    keyboard.add(InlineKeyboardButton('🎥 Киностудия', callback_data='toggle_Киностудия'))
    
    # Кинотеатр с счётом (пример 5/5)
    cinema_text = f'🎬 Кинотеатр 5 🔽 5 🔼'
    keyboard.add(InlineKeyboardButton(cinema_text, callback_data='cinema_adjust'))
    
    keyboard.add(InlineKeyboardButton('🌐 Сайт', callback_data='toggle_Сайт'))
    keyboard.add(InlineKeyboardButton('🤜 Brawl', callback_data='toggle_Brawl'))
    keyboard.add(InlineKeyboardButton('❤️ Лайк в Match', callback_data='toggle_Лайк в Match'))
    
    # Кнопка назад
    keyboard.add(InlineKeyboardButton('🔙 Назад', callback_data='back_to_main'))
    
    # Текст сообщения
    text = (
        f"🪙 Получено: {data['rp']} 🪙\n"
        f"{data['multiplier']} {data['vip']}\n\n"
        f"🕒 {data['online_hours']} часа онлайн\n\n"
        "Выберите активности для фарма:"
    )
    
    # Добавляем статус переключателей
    for name in TOGGLES:
        status = '🔴' if not data['toggles'][name] else '🟢'
        text += f"\n{status} {name}"
    
    return text, keyboard

@dp.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    get_user_data(user_id)  # Инициализация
    await message.answer(
        "Добро пожаловать в 5RP Assistant! 🚀\n"
        "Бот-помощник для фарма RP на серверах GTA 5 RP.",
        reply_markup=main_menu()
    )

@dp.message(F.text == '⚔️ Фарм')
async def farm_handler(message: types.Message):
    user_id = message.from_user.id
    text, keyboard = farm_menu(user_id)
    await message.answer(text, reply_markup=keyboard)

# Обработка переключателей
@dp.callback_query(F.data.startswith('toggle_'))
async def toggle_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = get_user_data(user_id)
    toggle_name = callback.data.split('_')[1]
    if toggle_name in data['toggles']:
        data['toggles'][toggle_name] = not data['toggles'][toggle_name]
    text, keyboard = farm_menu(user_id)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == 'back_to_main')
async def back_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu())
    await callback.answer()

# Здесь можно добавить другие кнопки (Таймеры, Календари и т.д.) аналогично

# Симуляция онлайн-таймера (увеличивает каждые 60 сек, для теста)
async def online_timer():
    while True:
        await asyncio.sleep(60)  # Каждую минуту
        for user_id in user_data:
            data = user_data[user_id]
            data['online_minutes'] += 1
            if data['online_minutes'] >= 60:
                data['online_minutes'] = 0
                data['online_hours'] += 1
                data['rp'] += 10  # Пример фарма RP за час

async def main():
    asyncio.create_task(online_timer())  # Запуск таймера
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
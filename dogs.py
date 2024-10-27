from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import asyncio

from config import TOKEN

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния для регистрации
class RegistrationStates(StatesGroup):
    selecting_role = State()
    entering_name = State()
    entering_phone = State()
    uploading_passport = State()
    completed = State()

# Основное меню для владельцев собак
def owner_menu():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Создать задачу")],
            [types.KeyboardButton(text="Проверить мои задачи")]
        ],
        resize_keyboard=True
    )
    return markup

# Основное меню для выгульщиков собак
def walker_menu():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Проверить доступные задачи")],
            [types.KeyboardButton(text="Мой рейтинг и отзывы")],
            [types.KeyboardButton(text="Биография")]
        ],
        resize_keyboard=True
    )
    return markup

# Кнопки для выбора роли
def role_selection_buttons():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Владелец собаки")],
            [KeyboardButton(text="Выгульщик собак")]
        ],
        resize_keyboard=True
    )
    return markup

# Кнопка "Назад"
def back_button_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    return markup

# Запуск бота и выбор роли
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("Вы владелец собаки или выгульщик собак?", reply_markup=role_selection_buttons())
    await state.set_state(RegistrationStates.selecting_role)

# Обработка выбора роли
@dp.message(lambda message: message.text in ["Владелец собаки", "Выгульщик собак"], StateFilter(RegistrationStates.selecting_role))
async def process_role_selection(message: types.Message, state: FSMContext):
    role = "owner" if message.text == "Владелец собаки" else "walker"
    await state.update_data(role=role)
    await message.answer("Введите ваше имя:", reply_markup=back_button_keyboard())
    await state.set_state(RegistrationStates.entering_name)

# Обработка кнопки "Назад" на этапе ввода имени
@dp.message(lambda message: message.text == "Назад", StateFilter(RegistrationStates.entering_name))
async def back_to_role_selection(message: types.Message, state: FSMContext):
    await message.answer("Вы вернулись назад. Выберите роль: владелец собаки или выгульщик собак.", reply_markup=role_selection_buttons())
    await state.set_state(RegistrationStates.selecting_role)

# Обработка ввода имени
@dp.message(StateFilter(RegistrationStates.entering_name))
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона:", reply_markup=back_button_keyboard())
    await state.set_state(RegistrationStates.entering_phone)

# Обработка кнопки "Назад" на этапе ввода телефона
@dp.message(lambda message: message.text == "Назад", StateFilter(RegistrationStates.entering_phone))
async def back_to_entering_name(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:", reply_markup=back_button_keyboard())
    await state.set_state(RegistrationStates.entering_name)

# Обработка ввода телефона
@dp.message(StateFilter(RegistrationStates.entering_phone))
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Загрузите фотографию паспорта:", reply_markup=back_button_keyboard())
    await state.set_state(RegistrationStates.uploading_passport)

# Обработка кнопки "Назад" на этапе загрузки паспорта
@dp.message(lambda message: message.text == "Назад", StateFilter(RegistrationStates.uploading_passport))
async def back_to_entering_phone(message: types.Message, state: FSMContext):
    await message.answer("Введите номер телефона:", reply_markup=back_button_keyboard())
    await state.set_state(RegistrationStates.entering_phone)

# Обработка загрузки паспорта
@dp.message(lambda message: message.photo, StateFilter(RegistrationStates.uploading_passport))
async def process_passport_photo(message: types.Message, state: FSMContext):
    await state.update_data(passport_photo=message.photo[-1].file_id)
    user_data = await state.get_data()

    # Завершение регистрации
    role = user_data['role']
    if role == "owner":
        await message.answer("Регистрация завершена! Добро пожаловать, владелец собаки.", reply_markup=owner_menu())
    else:
        await message.answer("Регистрация завершена! Добро пожаловать, выгульщик собак.", reply_markup=walker_menu())
    
    await state.set_state(RegistrationStates.completed)

# Обработка действий владельца собаки
@dp.message(lambda message: message.text == "Создать задачу", StateFilter(RegistrationStates.completed))
async def create_task(message: types.Message, state: FSMContext):
    await message.answer("Функция создания задачи пока в разработке.")

@dp.message(lambda message: message.text == "Проверить мои задачи", StateFilter(RegistrationStates.completed))
async def view_tasks(message: types.Message, state: FSMContext):
    await message.answer("Функция проверки задач пока в разработке.")

# Обработка действий выгульщика собак
@dp.message(lambda message: message.text == "Проверить доступные задачи", StateFilter(RegistrationStates.completed))
async def check_available_tasks(message: types.Message, state: FSMContext):
    await message.answer("Функция проверки доступных задач пока в разработке.")

@dp.message(lambda message: message.text == "Мой рейтинг и отзывы", StateFilter(RegistrationStates.completed))
async def view_ratings_and_reviews(message: types.Message, state: FSMContext):
    await message.answer("Функция просмотра рейтинга и отзывов пока в разработке.")

@dp.message(lambda message: message.text == "Биография", StateFilter(RegistrationStates.completed))
async def view_biography(message: types.Message, state: FSMContext):
    await message.answer("Функция биографии пока в разработке.")

# Асинхронный запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

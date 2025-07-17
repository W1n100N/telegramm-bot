from aiogram import F, Router, types
from aiogram.filters import Command
from database import *
from keyboards import generate_options_keyboard
from quiz_data import quiz_data
import datetime

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = types.ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer(
        "Добро пожаловать в квиз!",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0)
    await update_correct_count(user_id, 0)
    await message.answer("Давайте начнем квиз!")
    await get_question(message, user_id)

async def get_question(message: types.Message, user_id: int):
    current_index = await get_quiz_index(user_id)
    
    if current_index >= len(quiz_data):
        await message.answer("Квиз завершен! Начните новый с помощью /quiz")
        return
    
    question = quiz_data[current_index]
    kb = generate_options_keyboard(
        question['options'],
        question['options'][question['correct_option']]
    )
    await message.answer(question['question'], reply_markup=kb)



@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    user = callback.from_user
    current_index = await get_quiz_index(user.id)
    correct_count = await get_correct_count(user.id)
    
    # Обновляем оба значения сразу
    new_correct = correct_count + 1
    new_index = current_index + 1
    await update_quiz_state(user.id, new_index, new_correct)
    
    await callback.bot.edit_message_reply_markup(
        chat_id=user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    await callback.message.answer("✅ Верно!")
    
    if new_index < len(quiz_data):
        await get_question(callback.message, user.id)
    else:
        await save_quiz_result(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            correct=new_correct,
            total=len(quiz_data)
        )
        await callback.message.answer(
            f"🏆 Квиз завершен! Ваш результат: {new_correct}/{len(quiz_data)}"
        )

@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    user = callback.from_user
    current_index = await get_quiz_index(user.id)
    correct_count = await get_correct_count(user.id)
    
    # Обновляем только индекс
    new_index = current_index + 1
    await update_quiz_state(user.id, new_index, correct_count)
    
    await callback.bot.edit_message_reply_markup(
        chat_id=user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    correct_option = quiz_data[current_index]['correct_option']
    await callback.message.answer(
        f"❌ Неверно! Правильный ответ: {quiz_data[current_index]['options'][correct_option]}"
    )
    
    if new_index < len(quiz_data):
        await get_question(callback.message, user.id)
    else:
        await save_quiz_result(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            correct=correct_count,
            total=len(quiz_data)
        )
        await callback.message.answer(
            f"🏆 Квиз завершен! Ваш результат: {correct_count}/{len(quiz_data)}"
        )

async def handle_next_question(user_id: int, message: types.Message, correct_count: int):
    current_index = await get_quiz_index(user_id)
    current_index += 1
    await update_quiz_index(user_id, current_index)
    
    if current_index < len(quiz_data):
        await get_question(message, user_id)
    else:
        await save_quiz_result(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            correct=correct_count,
            total=len(quiz_data)
        )
        await message.answer(
            f"🏆 Квиз завершен! Ваш результат: {correct_count}/{len(quiz_data)}"
        )

@router.message(Command("stats"))
async def show_stats(message: types.Message):
    leaderboard = await get_leaderboard()
    
    if not leaderboard:
        await message.answer("Статистика пока недоступна")
        return
    
    stats_text = "🏆 Топ игроков:\n\n"
    for i, (name, correct, total) in enumerate(leaderboard, 1):
        percentage = (correct / total) * 100
        stats_text += f"{i}. {name}: {correct}/{total} ({percentage:.1f}%)\n"
    
    await message.answer(stats_text)

@router.message(Command("my_stats"))
async def show_my_stats(message: types.Message):
    user = message.from_user
    stats = await get_user_stats(user.id)
    
    if not stats:
        await message.answer("Вы еще не завершили ни одного квиза")
        return
    
    stats_text = f"📊 Ваша статистика ({user.first_name}):\n\n"
    for i, (correct, total, date) in enumerate(stats, 1):
        date_str = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")
        percentage = (correct / total) * 100
        stats_text += f"Попытка {i} ({date_str}): {correct}/{total} ({percentage:.1f}%)\n"
    
    await message.answer(stats_text)
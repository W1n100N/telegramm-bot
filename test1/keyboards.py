from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def generate_options_keyboard(answer_options: list[str], right_answer: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer"
        ))
    builder.adjust(1)
    return builder.as_markup()
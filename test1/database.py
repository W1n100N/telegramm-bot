import aiosqlite
from datetime import datetime

DB_NAME = 'quiz_bot.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Удаляем старые таблицы если есть
        await db.execute("DROP TABLE IF EXISTS quiz_state")
        await db.execute("DROP TABLE IF EXISTS quiz_results")
        
        # Создаём новые таблицы
        await db.execute('''CREATE TABLE quiz_state (
            user_id INTEGER PRIMARY KEY,
            question_index INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0
        )''')
        
        await db.execute('''CREATE TABLE quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            correct_answers INTEGER,
            total_questions INTEGER,
            completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        await db.commit()

async def update_correct_count(user_id: int, count: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            '''INSERT OR REPLACE INTO quiz_state 
               (user_id, correct_count) 
               VALUES (?, ?)''',
            (user_id, count)
        )
        await db.commit()

async def update_quiz_state(user_id: int, index: int, count: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            '''INSERT OR REPLACE INTO quiz_state 
               (user_id, question_index, correct_count) 
               VALUES (?, ?, ?)''',
            (user_id, index, count)
        )
        await db.commit()

async def get_quiz_index(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT question_index FROM quiz_state WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0

async def update_quiz_index(user_id: int, index: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)',
            (user_id, index)
        )
        await db.commit()

async def get_correct_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT correct_count FROM quiz_state WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0

async def save_quiz_result(user_id: int, username: str, first_name: str, correct: int, total: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO quiz_results 
            (user_id, username, first_name, correct_answers, total_questions)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, correct, total))
        await db.commit()

async def get_leaderboard(limit: int = 10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT first_name, correct_answers, total_questions 
            FROM quiz_results 
            ORDER BY correct_answers DESC, completion_date DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()

async def get_user_stats(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT correct_answers, total_questions, completion_date
            FROM quiz_results 
            WHERE user_id = ?
            ORDER BY completion_date DESC
            LIMIT 5
        ''', (user_id,))
        return await cursor.fetchall()
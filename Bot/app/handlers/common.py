from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from Model_1.model_1 import *

from app.db.functions import get_passenger_flow_from_db


class Diologue(StatesGroup):
    waiting_for_question = State()
    answer_for_question = State()

async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
'''Привет, я Метробот! Могу ответить, какой пассажиропоток на станциях московского метрополитена.
        
Пример вопроса, которые я поддерживаю
Вопрос: 
Какой пассажиропоток был 25 марта на станции Охотный ряд?
Ответ:
Дата: 2024-03-25 
Cтанция: Охотный ряд 
Линия: Сокольническая линия
Пассажиропоток: 111

Задавай вопросы про пассажиропоток, готов на все ответить!
''',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Diologue.waiting_for_question.state)

# async def cmd_cancel(message: types.Message, state: FSMContext):
#     await state.finish()
#     await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())

# Просто функция, которая доступна только администратору,
# чей ID указан в файле конфигурации.

import datetime
import json

prompt_fromat = '''{"дата": <дата>, "cтанция метро": <станция метро>, "линия метро": <линия метро>}'''
prompt = f'''
Твоя задача получить из текстововго запроса следующие данные: дату в формате год, месяц и дени через дефис, станцию метро и линию метро. В формате {'{}'}.
Если что то не удалось найти в запросе, то пиши None. Если указано сегодня, завтра или неделю назад, то считай относительно текущей даты.
Сегодняшняя дата: 03.04.2024
Запрос: {'{}'}
'''

answer_prompt = '''
Дата: {}
Cтанция: {}
Пассажиропоток: {}
'''
# TODO Линия: {}
async def answer_question(message: types.Message, state: FSMContext):
    # if len(message.text) > max_name_length:
    #     await message.answer('Пожалуйста, напишите имя короче 255 символов')
    #     return

    print(f'Test мы получили сообщение переходим в состояние answer_for_question: {message.text}')
    await message.answer('Запрос обрабатывается')
    full_prompt = prompt.format(prompt_fromat, message.text)
    print(full_prompt)
    answer = get_chat_completion(giga_token, full_prompt)
    text_answer = answer.json()['choices'][0]['message']['content']
    print(text_answer)
    res_dict = json.loads(text_answer)
    # запрос SQL
    dt = res_dict['дата']
    station = res_dict['cтанция метро']
    line_name = res_dict['линия метро']
    passenger_flow = await get_passenger_flow_from_db(station, line_name, dt) # res_dict

    # line_name,
    await message.answer(answer_prompt.format(dt, station, str(passenger_flow)))
    await state.set_state(Diologue.waiting_for_question.state)



async def secret_command(message: types.Message):
    await message.answer("Поздравляю! Эта команда доступна только администратору бота.")

def register_hendlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(answer_question, state=Diologue.waiting_for_question)
    # dp.register_message_handler(model_answer, state=Diologue.answer_for_question)
    # dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
    # dp.register_message_handler(cmd_cancel, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(secret_command, IDFilter(user_id=admin_id), commands='abracadabra')

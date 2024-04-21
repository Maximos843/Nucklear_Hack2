from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from model.model import *

from app.db.functions import get_passenger_flow_from_db


class Diologue(StatesGroup):
    waiting_for_question = State()
    answer_for_question = State()


async def cmd_start(message: types.Message, state: FSMContext):

    await message.answer(
        '''Привет, я Метробот! Могу ответить, какой пассажиропоток на станциях московского метрополитена.
        
Пример вопроса, которые я поддерживаю
Вопрос: 
Какой пассажиропоток был 25 марта на станции Охотный ряд?
Ответ:
Сегодня: 2024-04-03
Дата просмотра: 2024-03-25
На сколько дней сдвиг: -9
Cтанция: Охотный ряд
Пассажиропоток: 
На линии "Сокольническая" пассажиропоток равен 12161

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

answer_prompt = '''
Сегодня: {}
Дата просмотра: {}
На сколько дней сдвиг: {}
Cтанция: {}
Пассажиропоток: {}
'''
# TODO Линия: {}

stations = ["Яхромская", "Ясенево", "Южная", "Юго-Западная", "Юго-Восточная",
            "Электрозаводская", "Щукинская", "Щёлковская", "Шоссе Энтузиастов", "Шипиловская", "Шелепиха",
            "Шаболовская", "Чкаловская", "Чистые пруды",
            "Чеховская", "Чертановская", "Черкизовская", "ЦСКА", "Цветной Бульвар", "Царицыно", "Хорошёвская",
            "Хорошевская", "Хорошёво", "Ховрино",
            "Фрунзенская", "Фонвизинская", "Фили", "Филёвский парк", "Филатов луг", "Физтех", "Университет",
            "Улица Скобелевская", "Улица Дмитриевского",
            "Улица Горчакова", "Улица Академика Янгеля", "Улица 1905 года", "Угрешская", "Тушинская", "Тургеневская",
            "Тульская", "Трубная",
            "Тропарёво", "Третьяковская", "ТПУ Рязанская", "Тимирязевская", "Технопарк", "Терехово", "Тёплый стан",
            "Текстильщики", "Театральная",
            "Тверская", "Таганская", "Сходненская", "Сухаревская", "Студенческая", "Строгино", "Стрешнево", "Стенд",
            "Станционная", "Старокачаловская",
            "Сретенский Бульвар", "Спортивная", "Спартак", "Солнцево", "Сокольники", "Соколиная Гора", "Сокол",
            "Смоленская", "Славянский бульвар",
            "Серпуховская", "Семёновская", "Селигерская", "Севастопольская", "Свиблово", "Саларьево", "Савёловская",
            "Рязанский Проспект",
            "Румянцево", "Ростокино", "Римская", "Рижская", "Речной вокзал", "Рассказовка", "Раменки",
            "Пятницкое шоссе", "Пыхтино", "Пушкинская",
            "Профсоюзная", "Проспект Мира", "Проспект Вернадского", "Пролетарская", "Прокшино",
            "Преображенская площадь", "Пражская", "Полянка",
            "Полежаевская", "Площадь Революции", "Площадь Ильича", "Площадь Гагарина", "Планерная", "Пионерская",
            "Печатники", "Петровско-Разумовская",
            "Петровский парк", "Перово", "Первомайская", "Партизанская", "Парк Победы", "Парк культуры", "Панфиловская",
            "Павелецкая", "Охотный ряд", "Отрадное",
            "Орехово", "Ольховая", "Октябрьское поле", "Октябрьская", "Окская", "Окружная", "Озёрная",
            "Новые Черёмушки", "Новоясеневская", "Новохохловская",
            "Новослободская", "Новопеределкино", "Новокузнецкая", "Новокосино", "Новогиреево", "Новаторская",
            "Нижегородская", "Некрасовка",
            "Нахимовский Проспект", "Народное Ополчение", "Нагорная", "Нагатинский затон", "Нагатинская", "Мякинино",
            "Москва-Сити", "Молодёжная", "Мнёвники",
            "Мичуринский проспект", "Митино", "Минская", "Менделеевская", "Медведково", "Маяковская", "Марьино",
            "Марьина Роща", "Марксистская", "Люблино",
            "Лухмановская", "Лужники", "Лубянка", "Ломоносовский проспект", "Ломоносовский проспект", "Локомотив",
            "Лихоборы", "Лианозово", "Лефортово",
            "Лесопарковая", "Лермонтовский проспект", "Ленинский Проспект", "Кутузовская", "Курская", "Кунцевская",
            "Кузьминки", "Кузнецкий мост",
            "Крымская", "Крылатское", "Кропоткинская", "Крестьянская застава", "Красные ворота", "Красносельская",
            "Краснопресненская", "Красногвардейская",
            "Котельники", "Косино", "Коптево", "Коньково", "Комсомольская", "Коммунарка", "Коломенская", "Кожуховская",
            "Кленовый бульвар", "Китай-город", "Киевская",
            "Каширская", "Каховская", "Кантемировская", "Калужская", "Измайловская", "Измайлово", "Зябликово", "Зюзино",
            "Зорге", "ЗИЛ", "Жулебино", "Дубровка",
            "Достоевская", "Домодедовская", "Добрынинская", "Дмитровская", "Динамо", "Деловой центр", "Давыдково",
            "Говорово", "Выхино", "Воронцовская",
            "Воробьёвы горы", "Волоколамская", "Волжская", "Волгоградский проспект", "Войковская", "Водный Стадион",
            "Владыкино", "Верхние Лихоборы",
            "Верхние Котлы", "ВДНХ", "Варшавская", "Бутырская", "Бунинская аллея", "Бульвар Рокоссовского",
            "Бульвар Дмитрия Донского", "Бульвар Адмирала Ушакова",
            "Братиславская", "Ботанический сад", "Боровское шоссе", "Боровицкая", "Борисово", "Битцевский парк",
            "Библиотека имени Ленина", "Бибирево",
            "Беляево", "Белорусская", "Беломорская", "Белокаменная", "Беговая", "Бауманская", "Баррикадная",
            "Балтийская", "Багратионовская", "Бабушкинская",
            "Аэропорт Внуково", "Аэропорт", "Арбатская", "Аннино", "Андроновка", "Аминьевская", "Алтуфьево",
            "Алма-Атинская", "Алексеевская",
            "Александровский сад", "Академическая",
            "Административная", "Автозаводская", "Авиамоторная"]

get_station_fromat = '''Получи из текста название станций московского метро>. Если это невозможно то верни None. 
Слово ответ в свой ответ не включай.
Примеры:
Текст: Сколько была пассажиров на станции Царицыно вчера. Ответ: Царицыно
Текст: {}'''


async def get_station(question):
    full_prompt = get_station_fromat.format(question)
    answer = get_chat_completion(giga_token, full_prompt)
    station = answer.json()['choices'][0]['message']['content']
    return station


get_date_prompt = '''
Получи из текста дату в формате год-месяц-день, если это невозможно, то верни None.
Сегодняшняя дата: {}
Текст: {}
'''


async def get_date(question, today):
    full_prompt = get_date_prompt.format(today, question)
    answer = get_chat_completion(giga_token, full_prompt)
    date = answer.json()['choices'][0]['message']['content']
    return date


get_date_gap_prompt = '''
Из текста ниже тебе необходимо понять на сколько дней идёт сдвиг относительно текущего врмени в днях
Если речь идёт о будущем, то число положительное
Если речь идёт о прошлом, то число отрицательное
Сегодняшняя дата: {}
Сегодняшний день недели: {}
Примеры
1. Текст: две недели назад. Ответ: -14
2. Текст: через месяц. Ответ: 30
3. Текст: зватра. Ответ: 1
5. Текст: вчера. Ответ: -1
6. Текст: 21.04.2024 вторник прошлой недели. Ответ: -12
7. Сегодняшний день недели: вторник Текст: прошлый понедельник. Ответ: -8

Текст: {}
'''


async def get_date_gap(question, today):
    today_date = datetime.datetime.fromisoformat(today)
    weekday = today_date.weekday()
    full_prompt = get_date_gap_prompt.format(today, weekday, question)
    answer = get_chat_completion(giga_token, full_prompt)
    text_answer_day = answer.json()['choices'][0]['message']['content']
    text_answer_day = text_answer_day.replace('.', '')
    text_answer_day = text_answer_day.replace('"', '')
    print(f'text_answer_day: {text_answer_day}')
    return text_answer_day


async def answer_question(message: types.Message, state: FSMContext):
    question = message.text
    print(f'Test мы получили сообщение переходим в состояние answer_for_question: {question}')
    await message.answer('Запрос обрабатывается...')

    station = await get_station(question)
    print(station, station not in stations)
    if station not in stations:
        await message.answer('Проверьте корректность вашего запроса')
        return
    today = '2024-04-03'
    date_today = datetime.datetime.fromisoformat(today)
    text_day = await get_date(question, today)
    text_day_gap = await get_date_gap(question, today)

    try:
        int_day = int(text_day_gap.split()[-1])
    except Exception:
        int_day = None

    try:
        # запрос SQL
        res_text_date = None
        line_name = None  # TODO убрать
        if 'None' in text_day and int_day is None:
            Exception('"None" in text_day and int_day is None')
        elif 'None' not in text_day:
            res_text_date = text_day
        elif int_day is not None:
            dt_full = date_today + datetime.timedelta(days=int_day)
            res_text_date = str(dt_full)[0:10]

        passenger_flow = await get_passenger_flow_from_db(station, line_name, res_text_date)  # res_dict
        str_passenger_flow = '\n'
        if passenger_flow:
            for val1, val2 in passenger_flow:
                val1 = str(val1).lower().capitalize()
                str_passenger_flow += f'На линии "{val1}" пассажиропоток равен {val2}\n'
        if str_passenger_flow == '\n':
            str_passenger_flow += 'На эту дату информации нет'
        # line_name,
        final_int_day = datetime.datetime.fromisoformat(res_text_date) - date_today
        final_int_day = final_int_day.days
        await message.answer(answer_prompt.format(today, res_text_date, final_int_day, station, str(str_passenger_flow)))
    except Exception:
        await message.answer('Проверьте корректность вашего запроса')
    await state.set_state(Diologue.waiting_for_question.state)


async def secret_command(message: types.Message):
    await message.answer("Поздравляю! Эта команда доступна только администратору бота.")


def register_hendlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(answer_question, state='*')
    # dp.register_message_handler(model_answer, state=Diologue.answer_for_question)
    # dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
    # dp.register_message_handler(cmd_cancel, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(secret_command, IDFilter(user_id=admin_id), commands='abracadabra')

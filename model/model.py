import dateparser
from transformers import pipeline
import datetime
import nltk
from config import Variables
import re
from utils import (normalize_station_name,
                   lemmatize_sentence,
                   translate_date,
                   change_weird_words_to_normal,
                   words_to_numbers,
                   split_hyphenated_words)


model_pipeline = pipeline(
    task='question-answering',
    model='timpal0l/mdeberta-v3-base-squad2'
)


class MetroDataExtractor:
    def __init__(self):
        pass

    def process_list_to_strings(self, tokens: list) -> str:
        return ' '.join(tokens)

    def extract_station(self, text: str) -> str:
        answer = model_pipeline(question=Variables.QUESTION_STATION, context=text)['answer']
        result = normalize_station_name(answer.strip(), Variables.STATIONS)
        return result

    def extract_date(self, text) -> str:
        #tokens = nltk.word_tokenize(text)
        time_delta = datetime.timedelta(days=17)
        for k, v in Variables.HALF.items():
            text = text.replace(k, str(v))
        text = lemmatize_sentence(text)
        if 'следующий' in text:
            text = text.replace('следующий', 'через 1')
        if 'прошлый' in text:
            text = text.replace('прошлый', '1')
        matches = re.findall(Variables.PATTERN, text)
        try:
            res = str(dateparser.parse(matches[0], settings={'DATE_ORDER': 'YMD'})).split(' ')[0]
            if res != 'None':
                res2 = datetime.datetime.strptime(res, '%Y-%m-%d')
                res2 -= time_delta
                return res2.strftime("%Y-%m-%d")
        except IndexError:
            pass
        answer = model_pipeline(question=Variables.QUESTION_DATE, context=text)['answer']
        answer = translate_date(words_to_numbers(change_weird_words_to_normal(split_hyphenated_words(answer))))
        res = str(dateparser.parse(answer, settings={'DATE_ORDER': 'YMD'})).split(' ')[0]
        if res != 'None':
            res2 = datetime.datetime.strptime(res, '%Y-%m-%d')
            res2 -= time_delta
            return res2.strftime("%Y-%m-%d")
        return 'Incorrect request'


if __name__ == '__main__':
    print('Извлечение даты и времени из текста')
    text = 'Скажи данные о пассажиропотоке вчера на станции метро Сокольник'
    extractor = MetroDataExtractor()
    print(extractor.extract_station(text), extractor.extract_date(text))

import dateparser
from transformers import pipeline
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
    def __init__(self, text: str):
        self.text = text
        self.tokens = nltk.word_tokenize(text)

    def process_list_to_strings(self, tokens: list) -> str:
        return ' '.join(tokens)

    def extract_station(self) -> str:
        answer = model_pipeline(question=Variables.QUESTION_STATION, context=self.text)['answer']
        result = normalize_station_name(answer.strip(), Variables.STATIONS)
        return result

    def extract_date(self) -> str:
        for k, v in Variables.HALF.items():
            self.text = self.text.replace(k, str(v))
        self.text = lemmatize_sentence(self.text)
        if 'следующий' in self.text:
            self.text = self.text.replace('следующий', 'через 1')
        if 'прошлый' in self.text:
            self.text = self.text.replace('прошлый', '1')
        matches = re.findall(Variables.PATTERN, self.text)
        try:
            res = str(dateparser.parse(matches[0], settings={'DATE_ORDER': 'YMD'})).split(' ')[0]
            if res != 'None':
                return res
        except IndexError:
            pass
        answer = model_pipeline(question=Variables.QUESTION_DATE, context=self.text)['answer']
        answer = translate_date(words_to_numbers(change_weird_words_to_normal(split_hyphenated_words(answer))))
        res = str(dateparser.parse(answer, settings={'DATE_ORDER': 'YMD'})).split(' ')[0]
        if res != 'None':
            return res
        return 'Incorrect request'


if __name__ == '__main__':
    print('Извлечение даты и времени из текста')
    text = 'Скажи данные о пассажиропотоке вчера на станции метро Сокольник'
    extractor = MetroDataExtractor(text)
    print(extractor.extract_station(), extractor.extract_date())

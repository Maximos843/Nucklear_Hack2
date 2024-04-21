import re
import nltk
from pymystem3 import Mystem
import pymorphy3
from nltk.stem.snowball import SnowballStemmer
from config import Variables
nltk.download('punkt')


stemmer = SnowballStemmer("russian")
morph = pymorphy3.MorphAnalyzer()
mystem = Mystem()


def lemmatize_sentence(text: str) -> str:
    lemmas = mystem.lemmatize(text)
    return ' '.join(lemmas).strip()


def normalize_station_name(station_name: str, stations: list[str]) -> str:
    station_name_stemmed = [stemmer.stem(word) for word in station_name.split()]
    station_name_splitted = station_name.lower().split()
    for station in stations:
        counter = 0
        for i in range(len(station_name_splitted)):
            for station_el in station.lower().split():
                if morph.parse(station_name_splitted[i])[0].normal_form == morph.parse(station_el)[0].normal_form:
                    counter += 1
        if counter == len(station_name_stemmed):
            return station
        else:
            continue
    return 'Incorrect request'


def translate_date(text: str) -> str:
    words = [morph.parse(word)[0].normal_form for word in text.split()]
    result = []
    for i in range(len(words)):
        if words[i] in Variables.MONTHS_DICT:
            if words[i-1].isdigit():
                day = words[i-1].zfill(2)
                month = Variables.MONTHS_DICT[words[i]]
                year = '2024'
                result = words[:i-1] + [f"{day}.{month}.{year}"]
        else:
            result += [words[i]]
    return ' '.join(result)


def sum_numbers_in_text(text: str) -> str:
    pattern = r'\b(\d+)\s(\d+)\b'

    def add_nums(match) -> str:
        num1, num2 = match.groups()
        result = int(num1) + int(num2)
        return str(result)

    result = re.sub(pattern, add_nums, text)
    return result


def words_to_numbers(text: str) -> str:
    words = text.split()
    for i, word in enumerate(words):
        parsed_word = morph.parse(word)[0]
        if 'NUMR' in parsed_word.tag:
            words[i] = str(Variables.NUMBERS_DICT[parsed_word.normal_form])
        elif parsed_word.normal_form in Variables.DCT_NUMBERS_ADJ.keys():
            words[i] = str(Variables.DCT_NUMBERS_ADJ[parsed_word.normal_form])
    return sum_numbers_in_text(' '.join(words))


def change_weird_words_to_normal(text: str) -> str:
    words = text.split()
    for key in Variables.DCT_OF_WEIRDS.keys():
        for i in range(len(words)):
            if key == words[i]:
                words[i] = Variables.DCT_OF_WEIRDS[key]
    return ' '.join(words)


def split_hyphenated_words(text: str) -> str:
    words = text.split('-')
    new_text = ' - '.join(words)
    return new_text

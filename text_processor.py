import os
import re
from pymorphy2 import MorphAnalyzer
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

morph = MorphAnalyzer()
russian_stopwords = stopwords.words('russian')

extra_stopwords = {
    'это', 'весь', 'который', 'свой', 'наш', 'ваш', 'их', 'мой', 'твой', 'свой',
    'какой', 'который', 'такой', 'такой', 'такой', 'какой-то', 'который-то',
    'сей', 'оный', 'другой', 'иной', 'некий', 'никакой', 'ничей', 'чей-то',
    'кто', 'что', 'как', 'где', 'когда', 'почему', 'зачем', 'сколько', 'кто-то',
    'что-то', 'какой-то', 'где-то', 'когда-то', 'почему-то', 'зачем-то', 'сколько-то'
}
russian_stopwords = set(russian_stopwords).union(extra_stopwords)


def preprocess_text(text):
    text = re.sub(r'[^а-яА-ЯёЁa-zA-Z\- ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text


def tokenize(text):
    words = text.split()
    return words


def lemmatize(word):
    parsed = morph.parse(word)[0]
    return parsed.normal_form


def process_document(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    processed_text = preprocess_text(text)

    tokens = tokenize(processed_text)

    lemmas = []
    for token in tokens:
        if len(token) < 2:
            continue

        lemma = lemmatize(token)

        if (lemma not in russian_stopwords and
                re.fullmatch(r'[а-яё\-]+', lemma) and
                len(lemma) > 1):
            lemmas.append(lemma)

    return ' '.join(lemmas)


def process_all_documents(input_dir='files', output_dir='processed_files'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.startswith('doc_') and filename.endswith('.txt'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f'processed_{filename}')

            try:
                processed_text = process_document(input_path)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(processed_text)

                print(f'Обработан: {filename}')
            except Exception as e:
                print(f'Ошибка при обработке {filename}: {e}')


if __name__ == "__main__":
    process_all_documents()
import os
import re
from pymorphy2 import MorphAnalyzer
from nltk.corpus import stopwords
import nltk

# Загрузка стоп-слов
nltk.download('stopwords')
nltk_stopwords = stopwords.words('russian')


def load_custom_stopwords(filepath='stopwords-ru.txt'):
    custom_stopwords = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word and not word.startswith('#'):
                    custom_stopwords.append(word)
    return custom_stopwords


custom_stopwords = load_custom_stopwords()
russian_stopwords = list(set(nltk_stopwords + custom_stopwords))

morph = MorphAnalyzer()


def preprocess_text(text):
    # Сохраняем только буквы, дефисы и пробелы
    text = re.sub(r'(?<!\w)-(?!\w)', ' ', text)  # Удаляем одиночные дефисы
    text = re.sub(r'[^а-яА-ЯёЁa-zA-Z\- ]', ' ', text)
    # Заменяем множественные пробелы на одинарные
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text


def tokenize(text):
    return text.split()


def process_compound_word(word):
    """Обработка составных слов с дефисами"""
    parts = [p for p in word.split('-') if p]  # Разбиваем и удаляем пустые части
    processed_parts = []

    for part in parts:
        if len(part) < 2:
            continue

        lemma = morph.parse(part)[0].normal_form
        if (lemma not in russian_stopwords and
                re.fullmatch(r'[а-яё]+', lemma)):
            processed_parts.append(lemma)

    return processed_parts


def process_document(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    processed_text = preprocess_text(text)
    tokens = tokenize(processed_text)
    lemmas = []

    for token in tokens:
        if len(token) < 2:
            continue

        # Обрабатываем слова с дефисами
        if '-' in token:
            parts = process_compound_word(token)
            lemmas.extend(parts)
        else:
            lemma = morph.parse(token)[0].normal_form
            if (lemma not in russian_stopwords and
                    re.fullmatch(r'[а-яё]+', lemma)):
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
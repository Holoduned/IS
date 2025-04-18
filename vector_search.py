import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
from pymorphy2 import MorphAnalyzer
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')
morph = MorphAnalyzer()
russian_stopwords = stopwords.words('russian')

tfidf_df = pd.read_csv('tfidf.csv', index_col=0).fillna(0)
idf_df = pd.read_csv('idf.csv', index_col=0).fillna(0)

inverted_index = {}
with open('inverted_list.txt', 'r', encoding='utf-8') as f:
    for line in f:
        word, docs = line.strip().split(':')
        inverted_index[word.strip()] = list(map(int, docs.split(',')))

def preprocess_text(text):
    words = re.findall(r'\w+', text.lower())
    return [morph.parse(word)[0].normal_form for word in words
            if word not in russian_stopwords and len(word) > 2]

def get_word_weights(doc_id, words):
    return {word: tfidf_df.loc[word, f'doc_{doc_id}']
            for word in words if word in tfidf_df.index}

def vector_search(query):
    query_words = preprocess_text(query)
    if not query_words:
        print("Запрос не содержит значимых слов.")
        return []

    # Фильтр слов из индекса
    valid_words = [word for word in query_words if word in inverted_index]
    if not valid_words:
        print("Ни одно слово не найдено в индексе.")
        return []

    relevant_docs = set()
    for word in valid_words:
        relevant_docs.update(inverted_index[word])
    relevant_docs = sorted(relevant_docs)

    vocabulary = tfidf_df.index.tolist()
    query_vector = np.zeros(len(vocabulary))
    for i, word in enumerate(vocabulary):
        if word in valid_words:
            query_vector[i] = 1

    doc_vectors = tfidf_df[[f'doc_{doc}' for doc in relevant_docs]].values.T
    similarities = cosine_similarity(query_vector.reshape(1, -1), doc_vectors).flatten()

    results = []
    for doc, score in zip(relevant_docs, similarities):
        word_weights = get_word_weights(doc, valid_words)
        results.append((doc, score, word_weights))

    return sorted(results, key=lambda x: -x[1])

if __name__ == "__main__":
    while True:
        query = input("> ").strip()
        if query.lower() == 'exit':
            break

        results = vector_search(query)
        if not results:
            continue

        print(f"\nРезультаты для запроса '{query}':")
        for doc_id, score, word_weights in results[:10]:  # Топ-10
            print(f"\nДокумент {doc_id}: общий вес = {score:.4f}")
            for word, weight in word_weights.items():
                print(f"  {word}: {weight:.5f}")
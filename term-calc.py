import os
import re
import math
from collections import defaultdict
import pandas as pd

def load_inverted_list(file_path):
    term_docs = defaultdict(list)
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                term, docs = line.strip().split(':')
                docs = [int(doc.strip()) for doc in docs.split(',') if doc.strip().isdigit()]
                term_docs[term] = docs
    return term_docs


def calculate_tf(processed_dir, term_docs):
    tf_data = defaultdict(dict)
    doc_files = [f for f in os.listdir(processed_dir) if f.startswith("processed_doc_")]

    for doc_file in doc_files:
        doc_id = int(re.search(r"processed_doc_(\d+).txt", doc_file).group(1))
        doc_path = os.path.join(processed_dir, doc_file)

        with open(doc_path, 'r', encoding='utf-8') as f:
            text = f.read()
            words = text.split()
            total_words = len(words)

            if total_words == 0:
                continue

            word_counts = defaultdict(int)
            for word in words:
                word_counts[word] += 1

            for term, docs in term_docs.items():
                if doc_id in docs:
                    count = word_counts.get(term, 0)
                    tf = count / total_words
                    tf_data[term][f"doc_{doc_id}"] = tf

    tf_df = pd.DataFrame.from_dict(tf_data, orient='index')
    tf_df = tf_df.sort_index()
    return tf_df


def calculate_idf(term_docs, total_docs):
    idf_data = {}
    for term, docs in term_docs.items():
        docs_with_term = len(docs)
        idf = math.log(total_docs / docs_with_term) if docs_with_term > 0 else 0
        idf_data[term] = idf

    idf_df = pd.DataFrame.from_dict(idf_data, orient='index', columns=['IDF'])
    idf_df = idf_df.sort_index()
    return idf_df


def calculate_tfidf(tf_df, idf_df):
    tfidf_data = defaultdict(dict)
    for term in tf_df.index:
        idf = idf_df.loc[term, 'IDF']
        for doc in tf_df.columns:
            tf = tf_df.loc[term, doc]
            tfidf_data[term][doc] = tf * idf

    tfidf_df = pd.DataFrame.from_dict(tfidf_data, orient='index')
    tfidf_df = tfidf_df.sort_index()
    return tfidf_df

def sort_columns(df):
    doc_numbers = [int(col.split('_')[-1]) for col in df.columns]
    sorted_columns = [f"doc_{num}" for num in sorted(doc_numbers)]
    return df[sorted_columns]

def clean_data(df):
    return df.loc[(df != 0).any(axis=1)]


def main():
    inverted_list_path = "inverted_list.txt"
    processed_dir = "processed_files"

    term_docs = load_inverted_list(inverted_list_path)
    total_docs = len([f for f in os.listdir(processed_dir) if f.startswith("processed_doc_")])

    tf_df = calculate_tf(processed_dir, term_docs)
    idf_df = calculate_idf(term_docs, total_docs)
    tfidf_df = calculate_tfidf(tf_df, idf_df)

    tf_df = sort_columns(tf_df)
    tfidf_df = sort_columns(tfidf_df)

    tf_df = clean_data(tf_df)
    tfidf_df = clean_data(tfidf_df)

    tf_df.to_csv("tf.csv", float_format="%.6f", na_rep='')
    idf_df.to_csv("idf.csv", float_format="%.6f")
    tfidf_df.to_csv("tfidf.csv", float_format="%.6f", na_rep='')

    print("Результаты сохранены в tf.csv, idf.csv и tfidf.csv")


if __name__ == "__main__":
    main()
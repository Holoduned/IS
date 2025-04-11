import os
from collections import defaultdict


def build_inverted_index(processed_files_dir):
    inverted_index = defaultdict(list)
    doc_ids = []

    for filename in os.listdir(processed_files_dir):
        if filename.startswith("processed_doc_") and filename.endswith(".txt"):
            doc_id = filename.split("_")[-1].split(".")[0]
            doc_ids.append(doc_id)
            filepath = os.path.join(processed_files_dir, filename)

            with open(filepath, "r", encoding="utf-8") as file:
                words = set(file.read().split())

                for word in words:
                    inverted_index[word].append(doc_id)

    sorted_index = {word: sorted(list(set(docs))) for word, docs in sorted(inverted_index.items())}

    return sorted_index, doc_ids


inverted_index, all_docs = build_inverted_index("processed_files")

with open("inverted_list.txt", "w", encoding="utf-8") as f:
    for word, docs in inverted_index.items():
        f.write(f"{word}: {', '.join(docs)}\n")
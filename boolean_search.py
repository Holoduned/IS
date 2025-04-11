import os


def load_inverted_index_and_docs(file_path):
    inverted_index = {}
    all_docs = set()

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                word, docs_str = line.strip().split(':', 1)
                docs = [doc.strip() for doc in docs_str.split(',')]
                inverted_index[word.strip()] = docs
                all_docs.update(docs)

    all_docs = sorted(all_docs, key=lambda x: int(x))
    return inverted_index, all_docs


def apply_operator(op, set1, set2):
    if op == "И":
        return set1 & set2
    elif op == "ИЛИ":
        return set1 | set2
    return set()


def boolean_search(query, inverted_index, all_docs):
    # Нормализация запроса
    query = query.replace("&", " & ").replace("|", " | ").replace("!", " ! ")
    query = " ".join(query.split())  # Удаляем лишние пробелы

    # Замена операторов
    query = (
        query.replace(" & ", " И ")
        .replace(" | ", " ИЛИ ")
        .replace(" ! ", " НЕ ")
    )


    # Разбиваем на токены
    tokens = query.split()

    # Обработка токенов
    processed_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "НЕ":
            # Обработка НЕ с отдельным словом
            if i + 1 < len(tokens):
                next_word = tokens[i + 1]
                docs = set(all_docs) - set(inverted_index.get(next_word, []))
                processed_tokens.append(docs)
                i += 2
            else:
                i += 1
        elif token.startswith("НЕ"):
            # Обработка слитного написания НЕслово
            word = token[2:]
            docs = set(all_docs) - set(inverted_index.get(word, []))
            processed_tokens.append(docs)
            i += 1
        elif token in ["И", "ИЛИ"]:
            processed_tokens.append(token)
            i += 1
        else:
            docs = set(inverted_index.get(token, []))
            processed_tokens.append(docs)
            i += 1

    # Обработка операторов И (имеют приоритет)
    i = 0
    while i < len(processed_tokens):
        token = processed_tokens[i]
        if token == "И":
            left = processed_tokens[i - 1]
            right = processed_tokens[i + 1]
            result = apply_operator("И", left, right)
            processed_tokens[i - 1:i + 2] = [result]
            i -= 1
        else:
            i += 1

    # Обработка операторов ИЛИ
    result = set()
    if processed_tokens:
        result = processed_tokens[0]
        i = 1
        while i < len(processed_tokens):
            token = processed_tokens[i]
            if token == "ИЛИ":
                right = processed_tokens[i + 1]
                result = apply_operator("ИЛИ", result, right)
                i += 2
            else:
                i += 1

    return sorted(result, key=lambda x: int(x))


if __name__ == "__main__":
    # Загрузка данных
    inverted_index, all_docs = load_inverted_index_and_docs("inverted_list.txt")

    # Ввод запроса
    print("Введите ваш запрос:")
    user_query = input().strip()

    # Выполнение поиска
    results = boolean_search(user_query, inverted_index, all_docs)
    print("Результат поиска:", results)
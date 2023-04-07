from importer import *

if __name__ == "__main__":
    print("\nget_data_tsvs()")
    tsvs = get_data_tsvs()
    print(tsvs)
    print("\nget_language_pairs(tsvs)")
    pairs = get_language_pairs(tsvs)
    print(pairs)
    print("\nload_database()")
    data = load_database()
    print(data)
    print("\nsave_database(data)")
    save_database(data)
    print("\nimport_databases(tsvs, data)")
    result = import_databases(tsvs, data)
    sentences = data["sentences"]
    print(sentences[list(sentences)[0]])
    print(result)
    print("\nsave_database(data)")
    save_database(data)

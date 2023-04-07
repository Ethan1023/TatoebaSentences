from importer import *
import random
import math

def load():
    data = load_database()
    return data

def update(data):
    tsvs = get_data_tsvs()
    tsvs = get_data_tsvs()
    import_databases(tsvs, data)
    save_database(data)

def get_language_choice(languages):
    print(f"Languages: {', '.join(languages)}")
    choice_from = -1
    while not choice_from in range(len(languages)):
        user = input(f"Select from language {list(range(len(languages)))}: ")
        if user.isdigit():
            choice_from = int(user)
    choice_to = -1
    while not choice_to in range(len(languages)) or choice_from == choice_to:
        user = input(f"Select to language: ")
        if user.isdigit():
            choice_to = int(user)
    return choice_from, choice_to

# Find sentences in lang_from that have a translation in lang_to
def get_matching_id_pairs(sentences, lang_from, lang_to):
    pairs = {}
    for id1 in sentences:
        sentence = sentences[id1]
        if sentence["lang"] == lang_from:
            for id2 in sentence["ids"]:
                if sentences[id2]["lang"] == lang_to:
                    if id1 in pairs:
                        pairs[id1].add(id2)
                    else:
                        pairs[id1] = {id2}
    return pairs

def get_practice_pair(id_pairs, confidences, max_conf, max_see):
    # Randomly select int less than max_practice
    selection = random.randrange(max_see)
    # Go through seen sentences
    id_from = -1
    level = -1
    for cur_level, level_ids in enumerate(confidences[:max_conf+1]):
        if selection < len(level_ids):
            level = cur_level
            id_from = random.choice(list(level_ids))
            break
        else:
            selection -= len(level_ids)
    if id_from == -1:
        id_from = random.choice(list(id_pairs))
        confidences[0].add(id_from)
        level = 0
    id_to = random.choice(list(id_pairs[id_from]))

    return id_from, id_to, level

def do_activity(sentences, confidences, id_pairs, activity_func, max_conf=2, max_see=5, reverse=False, args=None):
    # Get random matching pair
    id_from, id_to, level = get_practice_pair(id_pairs, confidences, max_conf, max_see)
    # Do practice
    if reverse:
        new_level = max(0, level + activity_func(sentences, id_to, id_from, args=args))
    else:
        new_level = max(0, level + activity_func(sentences, id_from, id_to, args=args))
    # Update confidence 
    print(f"Confidence {level} -> {new_level}")
    confidences[level].remove(id_from)
    # Extend list if higher score has been reached
    while len(confidences) <= new_level:
        confidences.append(set())
    confidences[new_level].add(id_from)

def do_reading_practice(sentences, id_from, id_to, args=None):
    print("Original sentence:")
    print(sentences[id_from]["sen"])
    input("Press enter to see translated sentence:")
    print(sentences[id_to]["sen"])
    while True:
        user = input("Confidence? (yes/no/maybe) ").lower().strip()
        if user.isdigit():
            return int(user)
        if re.match("y(es)?", user):
            return 1
        if re.match("no?", user):
            return -1
        if re.match("m(aybe)?", user):
            return 0

def do_sorting_practice(sentences, id_from, id_to, extra_words=5, args=None):
    # args must be list of ids of sentences in same language as id_from if extra_words > 0
    assert(extra_words == 0 or args is not None)
    print("Original sentence:")
    print(sentences[id_from]["sen"])
    # Add some random words and scramble
    words = sentences[id_to]["sen"].split()
    scrambled_words = words[:]
    while len(scrambled_words) < len(words) + extra_words:
        random_id = random.choice(args)
        scrambled_words.append(re.sub('[^a-z0-9]', '', random.choice(sentences[random_id]["sen"].split()).lower()))
    random.shuffle(scrambled_words)
    
    score = 0
    added = []
    for i in range(len(words)):
        if i > 0:
            print(sentences[id_from]["sen"])
            print(" ".join(words[:i]))
        # Print words that haven't been added yet
        [print(f"{j}: {re.sub('[^a-z0-9]', '', word.lower())}") for j, word in enumerate(scrambled_words) if j not in added]
        answer = -1
        # Repeat until answer is correct
        while answer < 0 or not scrambled_words[answer] == words[i]:
            user = "NaN"
            # Repeat until answer is valid
            while not user.isdigit() or int(user) < 0 or int(user) >= len(scrambled_words) or int(user) in added:
                user = input("i = ")
            answer = int(user)
            if not scrambled_words[answer] == words[i]:
                print("Wrong!")
                score -= 1
            else:
                added.append(answer)
                score += 1
        print()
    print("Translated sentence:")
    print(sentences[id_to]["sen"])
    # over 90% = +1, 1 mistake less than 90% = 0, else -1
    return min(1, max(-1, score + 1 - math.ceil(0.9*len(words)))) 

# Get parameters for practice from user
def get_practice_params(user):
    obj = re.match("[a-z]* ?([0-9]+),? ([0-9]+),? ([0-9]+),? ?(re?v?e?r?s?e?)?", user)
    num = 0
    max_conf = 0
    max_see = 0
    reverse = False
    if not obj:
        user = input("Number, Max confidence, Max see, [reverse]").lower().strip()
        obj = re.match("([0-9]+),? ([0-9]+),? ([0-9]+),? ?(re?v?e?r?s?e?)?", user)
    if obj:
        num = int(obj[1])
        max_conf = int(obj[2])
        max_see = int(obj[3])
        if obj[4] is not None:
            reverse = re.match("r", obj[4]) is not None
    return num, max_conf, max_see, reverse


def main():
    data = load()
    languages = list(data["languages"])
    sentences = data["sentences"]
    print(f"{len(sentences)} phrases loaded")

    user = "lang"
    while not re.match("exit|quit", user):
        # Change language
        if re.match("lang", user):
            choice_from, choice_to = get_language_choice(languages)
            confidences = data["languages"][languages[choice_from]]["confidences"]
            id_pairs = get_matching_id_pairs(sentences, languages[choice_from], languages[choice_to])
            from_sentences = list(id_pairs.keys())
            to_sentences = [key for key in sentences.keys() if sentences[key]["lang"] == languages[choice_to]]
            print(f"{len(id_pairs)} pairs found, {sum([len(conf) for conf in confidences])} seen")
        # Reading practice
        elif re.match("read", user):
            num, max_conf, max_see, reverse = get_practice_params(user)
            for i in range(num):
                do_activity(sentences, confidences, id_pairs, do_reading_practice, max_conf, max_see, reverse)
                save_database(data)
        # Sorting practice
        elif re.match("sort", user):
            num, max_conf, max_see, reverse = get_practice_params(user)
            for i in range(num):
                do_activity(sentences, confidences, id_pairs, do_sorting_practice, max_conf, max_see, reverse, args=from_sentences if reverse else to_sentences)
                save_database(data)
        # Get statistics for current language
        elif re.match("stat", user):
            print(f"Language: {languages[choice_from]}")
            for level, confidence in enumerate(confidences):
                print(f"{level}: {len(confidence)}")
        elif re.match("help", user):
            print("lang, read, sort, stat, exit")
        user = input("> ").lower().strip()

if __name__ == "__main__":
    main()

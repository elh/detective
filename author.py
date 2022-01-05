import sys
import os
import argparse
import pprint

from story import get_story

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--story_file', type=str, default="story_1.yaml", help='story yaml to run author on')
    parser.add_argument('--mode', type=str, default="words_to_entries", help='mode must be one of: words_to_entries, entries_to_words')
    args = parser.parse_args()

    pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)

    story = get_story(args.story_file)

    if args.mode == 'words_to_entries':
        pp.pprint(words_to_entries(story))
    elif args.mode == 'entries_to_words':
        pp.pprint(entries_to_words(story))
    else:
        print('mode must be one of: words')
        sys.exit(0)

# number of entries words appear in
def words_to_entries(story):
    word_counts = {} # word -> dictionary of count:int and entries:list of entry ids
    for entry in story['entries']:
        for word in set([remove_punc(word.lower()) for word in entry['text'].split()]):
            if word in word_counts:
                word_counts[word]['count'] += 1
                word_counts[word]['entry_ids'].append(entry['id'])
            else:
                word_counts[word] = {
                    'count': 1,
                    'entry_ids': [entry['id']]
                }
    return dict(sorted(word_counts.items(), key=lambda item: item[1]['count'], reverse=True))

def entries_to_words(story):
    words = {} # entry id -> set of words in it
    for entry in story['entries']:
        words[entry['id']] = set()
        for word in set([remove_punc(word.lower()) for word in entry['text'].split()]):
            words[entry['id']].add(word)
    return words

def remove_punc(str):
    # not including apostrophe because can be meaningful in contractions
    common_punc = '''!()-[]{};:"\,<>./?@#$%^&*_~'''
    for char in common_punc:
        str = str.replace(char, "")
    return str

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nSession ended. Goodbye')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

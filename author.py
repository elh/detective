import sys
import os
import argparse
import pprint

from story import get_story

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--story_file', type=str, default="story_1.yaml", help='story yaml to run author on')
    parser.add_argument('--mode', type=str, default="words_to_entries", help='mode must be one of: words_to_entries')
    args = parser.parse_args()

    story = get_story(args.story_file)

    if args.mode == 'words_to_entries':
        words_to_entries(story)
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
    word_counts = dict(sorted(word_counts.items(), key=lambda item: item[1]['count'], reverse=True))

    pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)
    pp.pprint(word_counts)

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

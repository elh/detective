import sys
import os
import argparse
import pprint
import graphviz

from story import get_story

ignore_words = {
    'i',
    'you',
    'he',
    'she',
    'we',
    'us',
    'they',
    'them',
    'theirs',
    'my',
    'mine',
    'her',
    'him',
    'to',
    'the',
    'of',
    'is',
    'was',
    'this',
    'be',
    'and',
    'have',
    'has',
    'had',
    'got',
    'a',
    'an',
    'on',
    'our',
    'that',
    'are',
    'it',
    'how',
    'why',
    'who',
    'when',
    'what',
    'where',
    "in",
    "out",
    "go",
    "some",
    "will",
    "up",
    "down",
    'as',
    'with',
    'at'
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--story_file', type=str, default="stories/story_2.yaml", help='story yaml to run author on')
    parser.add_argument('--mode', type=str, default="words_to_entries", help='mode must be one of: words_to_entries, entries_to_words, searches_to_entries, entries_graph, searches_graph')
    args = parser.parse_args()

    pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)

    story = get_story(args.story_file)

    if args.mode == 'words_to_entries':
        pp.pprint(words_to_entries(story))
    elif args.mode == 'entries_to_words':
        pp.pprint(entries_to_words(story))
    elif args.mode == 'searches_to_entries':
        pp.pprint(searches_to_entries(story))
    elif args.mode == 'entries_graph':
        print(entries_graph(story)) # just normal print
    elif args.mode == 'searches_graph':
        print(searches_graph(story)) # just normal print
    else:
        print('mode must be one of: words_to_entries, entries_to_words, searches_to_entries, entries_graph, searches_graph')
        sys.exit(0)

# number of entries words appear in
def words_to_entries(story):
    word_counts = {} # word -> dictionary of count:int and entry_ids:list of entry ids
    for entry in story['entries']:
        for word in set([remove_punc(word.lower()) for word in entry['text'].split()]):
            if word in ignore_words:
                continue
            if word in word_counts:
                word_counts[word]['count'] += 1
                word_counts[word]['entry_ids'].append(entry['id'])
            else:
                word_counts[word] = {
                    'count': 1,
                    'entry_ids': [entry['id']]
                }
    return dict(sorted(word_counts.items(), key=lambda item: item[1]['count'], reverse=True))

# show what entries searches would return. this respects the story-configured match limit
def searches_to_entries(story):
    # word -> dictionary of count:int and entry_ids:list of entry ids
    w_to_e = words_to_entries(story)
    for word in w_to_e:
        w_to_e[word]['entry_ids'] = w_to_e[word]['entry_ids'][:story['match_count_limit']]
    return w_to_e

# this builds a graph where nodes are entries and edges are the searches that connect them
# this is excessively detailed and not capturing the right context. you actually just need a graph of how terms relate to each other
# also prescribing directions in any of these graphs is pretty tricky. there are very specific topological conditions needed to
# say an edge is unidirectional.
# this is only practical at all with a manually specified white list of key terms
# Deprecated in favor of `searches_graph`. There are some other UI things like directions of arrows that could be improved but do not care to do so now.
# TODO: update so that edges respect the match limit
def entries_graph(story):
    if 'initial_search' not in story:
        print("start required. not sure how I want to visualize this right now")
        sys.exit(0)

    start = '*START*'
    dot = graphviz.Digraph()
    dot.node(start)
    for entry in story['entries']:
        dot.node(entry['id'])

    s_to_e = searches_to_entries(story)
    e_to_w = entries_to_words(story)
    # set up start
    e_to_w[start] = {story['initial_search'].lower().strip()}

    # traversal
    seen = {start}
    fringe = [start]
    while fringe:
        cur_entry = fringe.pop(0)
        cur_words = e_to_w[cur_entry]
        for w in cur_words:
            if w in ignore_words:
                continue

            search_to_entries = s_to_e[w]['entry_ids']
            for e in search_to_entries:
                if cur_entry == e:
                    continue
                dot.edge(cur_entry, e, label=w)

                if e not in seen:
                    seen.add(e)
                    fringe.append(e)

    return dot.source

# TODO: update so that edges respect the match limit
# these should be gone in story 2
# eve -> song [dir=none]
# eve -> hannah [dir=none]
def searches_graph(story):
    dot = graphviz.Digraph()

    s_to_e = searches_to_entries(story)
    e_to_w = entries_to_words(story)

    searches = set()
    for s in s_to_e:
        if s in ignore_words:
            continue
        search_entry_ids = s_to_e[s]['entry_ids']
        # this is really simplistic...
        if len(search_entry_ids) <= 1:
            continue
        searches.add(s)

    for s in searches:
        search_entry_ids = s_to_e[s]['entry_ids']
        if 'initial_search' in story and story['initial_search'].lower().strip() == s:
            dot.node(s, s + ": " + ', '.join(search_entry_ids), color='green')
        else:
            dot.node(s, s + ": " + ', '.join(search_entry_ids))

        neighbors = set()
        for search_entry_id in search_entry_ids:
            for n in e_to_w[search_entry_id]:
                if n not in searches:
                    continue
                # only create 1 edge across the pair of search terms. also prevent edges back to self
                if s >= n:
                    continue
                neighbors.add(n)

        for n in neighbors:
            dot.edge(s, n, dir="none")

    return dot.source

def entries_to_words(story):
    words = {} # entry id -> set of words in it
    for entry in story['entries']:
        words[entry['id']] = set()
        for word in set([remove_punc(word.lower()) for word in entry['text'].split()]):
            if word in ignore_words:
                continue
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

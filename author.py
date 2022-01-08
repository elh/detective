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
    parser.add_argument('--mode', type=str, default="searches_to_entries", help='mode must be one of: searches_to_entries, entries_to_words, entries_graph, searches_graph')
    args = parser.parse_args()

    pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)

    story = get_story(args.story_file)

    if args.mode == 'searches_to_entries':
        pp.pprint(searches_to_entries(story))
    elif args.mode == 'entries_to_words':
        pp.pprint(entries_to_words(story))
    elif args.mode == 'entries_graph':
        print(entries_graph(story)) # just normal print
    elif args.mode == 'searches_graph':
        print(searches_graph_to_graphviz(searches_graph(story))) # just normal print
    else:
        print('mode must be one of: searches_to_entries, entries_to_words, entries_graph, searches_graph')
        sys.exit(0)

# returns a dict where keys are search terms and values are a dict w/ fields
#   all_entry_ids: list of strings. list of entry ids
#   match_entry_ids: list of strings. list of matching entry ids based on configured n-match limit
#   all_entry_count: int. len of all_entry_ids
#   match_entry_count: int. len of match_entry_ids
#   initial_search: bool. true if is the intial search of story
# sorted by all_entry_count desc
def searches_to_entries(story):
    ret = {}
    for entry in story['entries']: # requires entries in order
        for word in set([remove_punc(word.lower()) for word in entry['text'].split()]):
            if word in ignore_words:
                continue
            if word in ret:
                if entry['id'] not in ret[word]['all_entry_ids']:
                    ret[word]['all_entry_ids'].append(entry['id'])
                    ret[word]['all_entry_count'] = len(ret[word]['all_entry_ids'])
                    ret[word]['match_entry_ids'] = ret[word]['all_entry_ids'][:story['match_count_limit']]
                    ret[word]['match_entry_count'] = len(ret[word]['match_entry_ids'])
            else:
                ret[word] = {
                    'all_entry_ids': [entry['id']],
                    'match_entry_ids': [entry['id']],
                    'all_entry_count': 1,
                    'match_entry_count': 1,
                    'initial_search': 'initial_search' in story and story['initial_search'].lower().strip() == word,
                }
    return dict(sorted(ret.items(), key=lambda item: item[1]['all_entry_count'], reverse=True))

# this builds a graph where nodes are entries and edges are the searches that connect them
# Deprecated in favor of `searches_graph`.
def entries_graph(story):
    if 'initial_search' not in story:
        print("start required. not sure how I want to visualize this right now")
        sys.exit(0)

    start = '*START*'
    dot = graphviz.Digraph()
    dot.node(start, color='green')
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

            search_to_entries = s_to_e[w]['match_entry_ids']
            for e in search_to_entries:
                if cur_entry == e:
                    continue
                if cur_entry in s_to_e[w]['match_entry_ids']:
                    if cur_entry >= e:
                        continue
                    dot.edge(cur_entry, e, label=w, dir="both")
                else:
                    dot.edge(cur_entry, e, label=w)

                if e not in seen:
                    seen.add(e)
                    fringe.append(e)

    return dot.source

# returns a dict where keys are search terms and values are a dict w/ fields. (re-using searches_to_entries)
#   ... the searches_to_entries fields ...
#   edges_to: list of strings. list of target search terms that are reachable from this source term. this captures the directional edges in the graph. if term A
#             and term B both have each other in their edges_to lists, that is a bidirectional edge
def searches_graph(story):
    s_to_e = searches_to_entries(story)
    e_to_w = entries_to_words(story)

    # TODO: revisit this...
    # Hmm.. This is tricky to reason about. I think this is too restrictive because what if "Alice" only shows in 1 entry but that entry also contains "Bob"
    # but after Bob's n-match limit. However, that does seem like a degenerate case because why would the "Alice" search be interesting? How did you get 
    # to it? Probably from another term so search_entry_ids would be >1 or this term is redundant to the other one. Supporting this will also make pruning out
    # random words that just appear in 1 entry difficult.
    ret = {k: v for k, v in s_to_e.items() if len(v['match_entry_ids']) > 1}

    for term in ret:
        ret[term]['edges_to'] = []
        for match_entry_id in ret[term]['match_entry_ids']:
            for w in e_to_w[match_entry_id]:
                if w not in ret:
                    continue
                if w == term:
                    continue
                if w not in ret[term]['edges_to']:
                    ret[term]['edges_to'].append(w)

    return ret

def searches_graph_to_graphviz(g):
    dot = graphviz.Digraph()

    for term in g:
        label = term + "\\n" + ', '.join(g[term]['match_entry_ids'])
        if len(g[term]['all_entry_ids']) > len(g[term]['match_entry_ids']):
            label += ", (" + ', '.join(g[term]['all_entry_ids'][len(g[term]['match_entry_ids']):]) + ")"
        if g[term]['initial_search']:
            dot.node(term, label, color='green')
        else:
            dot.node(term, label)
        
        for neighbor in g[term]['edges_to']:
            if term in g[neighbor]['edges_to']:
                # don't create duplicate edges
                if term >= neighbor:
                    continue
                dot.edge(term, neighbor, dir="both")
            else:
                dot.edge(term, neighbor)
        
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

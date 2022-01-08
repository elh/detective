import sys
import os
import argparse
from bullet import Bullet

from story import get_story, search_entries, get_short_date_and_text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--story_file', type=str, default="stories/story_2.yaml", help='story yaml to run detective on')
    args = parser.parse_args()

    story = get_story(args.story_file)

    # display intro
    if 'intro_text' in story:
        print(">>> " + story['intro_text'])
    if 'intro_stats' in story and story['intro_stats']:
        print(">>> " + str(len(story['entries'])) + " searchable entries...")

    # prompt types:
    state = {
        'next_prompt': {
            'prompt': 'new_search',
            'args': {
                'term': story['initial_search'] if 'initial_search' in story else None
            }
        },
        'search_history': [] # a ordered list of unique tuples (search term, all match count)
    }

    # start game loop: display prompt, take input, update game
    while True:
        if state['next_prompt']['prompt'] == 'new_search':
            search_term = search_prompt(state['next_prompt'].get('args',{}))

            # update game, next prompt
            matches = search_entries(story['entries'], search_term)
            if len(matches) == 0:
                print("no matches")
                continue

            if (search_term.lower(), len(matches)) not in state['search_history']:
                state['search_history'].append((search_term.lower(), len(matches)))
            state['next_prompt'] = {
                'prompt': 'search_results',
                'args': {
                    'match_entries': matches[:story['match_count_limit']],
                    'all_entry_count': len(matches),
                    'match_count_limit': story['match_count_limit'],
                }
            }
        elif state['next_prompt']['prompt'] == 'search_results':
            res = search_results_prompt(state['next_prompt'].get('args',{}))

            # update game, next prompt
            search_results_prompt_args = state['next_prompt']['args']
            state['next_prompt'] = {
                'prompt': res['selection_type']
            }
            if res['selection_type'] == "read_entry":
                state['next_prompt']['args'] = {
                    'entry': res['entry'],
                    'search_results_prompt_args': search_results_prompt_args
                }
        elif state['next_prompt']['prompt'] == 'read_entry':
            entry = state['next_prompt']['args']['entry']
            print("\n" + str(entry['date']) + "\n" + entry['text'])

            # update game, next prompt
            state['next_prompt'] = {
                'prompt': 'search_results',
                'args': state['next_prompt']['args']['search_results_prompt_args']
            }
        elif state['next_prompt']['prompt'] == 'search_history':
            # TODO: fix all of this.
            res = search_history_prompt(state['search_history'])

            # update game, next prompt
            state['next_prompt'] = {
                'prompt': 'new_search',
            }
        else:
            print('ERROR: unknown next prompt!')
            break

# prompts display context, wait for input, and return that input as a result

# returns search term
def search_prompt(args):
    term = args.get('term', "")
    if term != "" and term is not None:
        print("\nSearch: " + term)
        return term
    else:
        # do not use bullet.Input. cannot handle up and down arrow keys smh
        search_term = input("\nSearch: ").strip()
        if len(search_term) == 0:
            return search_prompt()
        return search_term

# returns a dict w/ selection type and selection
def search_results_prompt(args):
    match_entries = args.get('match_entries', [])
    all_entry_count = args.get('all_entry_count', 0)
    match_count_limit = args.get('match_count_limit', 0)

    prompt = f'\n{len(match_entries)} matches. Read entry:' if all_entry_count <= match_count_limit else f'\nFirst {len(match_entries)} of {all_entry_count} matches. Read entry:'
    cli_choices = format_entry_selections(match_entries)
    cli_choices.append("> run a new search <") # second to last
    cli_choices.append("> search history <") # last

    cli = Bullet(
        prompt = prompt,
        choices = cli_choices,
        bullet = "",
        margin = 2,
        pad_right = 4,
        return_index = True
    )
    result = cli.launch()

    ret = {}
    if result[1] == len(cli_choices)-2: # exit. new search
        ret['selection_type'] = "new_search"
    elif result[1] == len(cli_choices)-1: # show search history
        ret['selection_type'] = "search_history"
    else:
        ret['selection_type'] = "read_entry"
        ret['entry'] = match_entries[result[1]]
    return ret

# returns a dict w/ selection type and selection
def search_history_prompt(search_history):
    print(search_history)
    return None

def format_entry_selections(entries):
    # just use get_short_date_and_text impl as is for now
    return [get_short_date_and_text(entry) for entry in entries]

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nSession ended. Goodbye')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

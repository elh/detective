import sys
import os
import argparse
from bullet import Bullet, ScrollBar

from story import get_story, search_entries, get_short_date_and_text

new_search_option_text = "> run a new search <"
search_history_option_text = "> search history <"
read_progress_option_text = "> show read entry progress <"

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

    # prompt types: new_search, search_results, read_entry, search_history
    state = {
        'next_prompt': {
            'prompt': 'new_search',
            'args': {
                'term': story['initial_search'] if 'initial_search' in story else None
            }
        },
        'search_history': [],           # a ordered list of unique tuples (search term, all match count)
        'read_entry_history': set()     # a set of entry_ids that have been read
    }

    # start game loop: display prompt, take input, update game
    while True:
        if state['next_prompt']['prompt'] == 'new_search':
            search_term = search_prompt(state['next_prompt'].get('args',{}))
            if len(search_term) == 0:
                state['next_prompt'] = {
                    'prompt': 'main_menu'
                }
                continue

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
            res = search_results_prompt(state['next_prompt'].get('args',{}), state['read_entry_history'])

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
            state['read_entry_history'].add(entry['id'])
            state['next_prompt'] = {
                'prompt': 'search_results',
                'args': state['next_prompt']['args']['search_results_prompt_args']
            }
        elif state['next_prompt']['prompt'] == 'search_history':
            term = search_history_prompt(state['search_history'])

            # update game, next prompt
            state['next_prompt'] = {
                'prompt': 'new_search',
                'args': {
                    'term': term
                }
            }
        elif state['next_prompt']['prompt'] == 'read_entry_history':
            display_read_entry_history(story, state['read_entry_history'])

            # update game, next prompt
            state['next_prompt'] = {
                'prompt': 'new_search'
            }
        elif state['next_prompt']['prompt'] == 'main_menu':
            res = display_main_menu()

            # update game, next prompt
            state['next_prompt'] = {
                'prompt': res
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
        return search_term

# returns next prompt
def display_main_menu():
    cli_choices = [
        new_search_option_text,
        search_history_option_text,
        read_progress_option_text
    ]

    cli = Bullet(
        prompt = "\nSelect:",
        choices = cli_choices,
        bullet = "",
        margin = 2,
        pad_right = 4,
        return_index = True
    )
    result = cli.launch()

    if result[1] == 0:
        return 'new_search'
    elif result[1] == 1:
        return 'search_history'
    else:
        return 'read_entry_history'

# returns a dict w/ selection type and selection
def search_results_prompt(args, read_entry_history):
    match_entries = args.get('match_entries', [])
    all_entry_count = args.get('all_entry_count', 0)
    match_count_limit = args.get('match_count_limit', 0)

    prompt = f'\n{len(match_entries)} matches. Read entry:' if all_entry_count <= match_count_limit else f'\nFirst {len(match_entries)} of {all_entry_count} matches. Read entry:'
    cli_choices = format_entry_selections(match_entries, read_entry_history)
    cli_choices.append(new_search_option_text) # third to last
    cli_choices.append(search_history_option_text) # second to last
    cli_choices.append(read_progress_option_text) # last

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
    if result[1] == len(cli_choices)-3: # exit. new search
        ret['selection_type'] = "new_search"
    elif result[1] == len(cli_choices)-2: # show search history
        ret['selection_type'] = "search_history"
    elif result[1] == len(cli_choices)-1: # show read progress
        ret['selection_type'] = "read_entry_history"
    else:
        ret['selection_type'] = "read_entry"
        ret['entry'] = match_entries[result[1]]
    return ret

# returns string. term to start next search
def search_history_prompt(search_history):
    cli_choices = format_search_history_selections(search_history)
    cli_choices.append(new_search_option_text) # last

    cli = ScrollBar(
        "\nSearch History:",
        cli_choices,
        height = 16,
        margin = 1,
        pointer = "👉",
        return_index = True
    )
    result = cli.launch()

    if result[1] == len(cli_choices)-1: # exit. new search
        return ""
    else:
        return search_history[result[1]][0]

# no return
def display_read_entry_history(story, read_entry_history):
    progress_str = ""
    read_count = 0
    for idx, e in enumerate(story['entries']):
        if idx != 0 and idx % 10 == 0:
            progress_str += "\n"

        if e['id'] in read_entry_history:
            progress_str += "x"
            read_count += 1
        else:
            progress_str += "o"

    progress_pct = str(round((read_count / len(story['entries'])) * 100, 2)) + "%"
    print("\n" + progress_pct + " Progress ('o' is unread, 'x' is read):\n" + progress_str)

def format_search_history_selections(search_history):
    return [v[0] + " (" + str(v[1]) + ")" for v in search_history]

def format_entry_selections(entries, read_entry_history):
    # just use get_short_date_and_text impl as is for now
    return [ ("  " if entry['id'] in read_entry_history else "* ") + get_short_date_and_text(entry) for entry in entries]

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nSession ended. Goodbye')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

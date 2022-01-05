import sys
import os
import argparse
from bullet import Bullet

from story import get_story, search_entries, get_short_date_and_text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--story_file', type=str, default="story_1.yaml", help='story yaml to run detective on')
    args = parser.parse_args()

    story = get_story(args.story_file)
    if 'intro_text' in story:
        print(">>> " + story['intro_text'])
    if 'intro_stats' in story and story['intro_stats']:
        print(">>> " + str(len(story['entries'])) + " searchable entries...")

    first_run = True

    while True:
        # ----- Prompt for search term -----
        # special handling for initial run. automatically seed and run with default first search term
        if first_run and 'initial_search' in story:
            print("\nSearch: " + story['initial_search'])
            search_term = story['initial_search']
        else:
            # do not use bullet.Input. cannot handle up and down arrow keys smh
            search_term = input("\nSearch: ").strip()
            if len(search_term) == 0:
                continue
        first_run = False

        # ----- Search -----
        matches = search_entries(story['entries'], search_term)
        if len(matches) == 0:
            print("no matches")
            continue
        visible_matches = matches[:story['match_count_limit']]

        prompt = f'\n{len(visible_matches)} matches. Read entry:' if len(matches) <= story['match_count_limit'] else f'\nFirst {len(visible_matches)} of {len(matches)} matches. Read entry:'

        # ----- Show results -----
        while True:
            cli_choices = format_entry_selections(visible_matches)
            cli_choices.append("> run a new search <")

            cli = Bullet(
                prompt = prompt,
                choices = cli_choices,
                bullet = "",
                margin = 2,
                pad_right = 4,
                return_index = True
            )

            result = cli.launch()
            if result[1] == len(cli_choices)-1: # exit
                break
            print("\n" + str(matches[result[1]]['date']) + "\n" + matches[result[1]]['text'])
            # TODO: bold matching text selection

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

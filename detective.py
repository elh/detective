from bullet import Bullet
import yaml
import argparse

default_match_count_limit = int(1e6)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--story_file', type=str, default="story_1.yaml", help='story yaml to run detective on')
    args = parser.parse_args()

    story = get_story(args.story_file)
    if 'intro_text' in story:
        print(">>> " + story['intro_text'])
    if 'intro_stats' in story and story['intro_stats']:
        print(">>> " + str(len(story['entries'])) + " searchable entries...")
    if 'match_count_limit' not in story or story['match_count_limit'] == 0:
        story['match_count_limit'] = default_match_count_limit

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
    results = []
    for entry in entries:
        truncated_text = entry['text'][:75] + '..' if len(entry['text']) > 75 else entry['text']
        results.append(entry['date'].strftime("%m/%d/%Y") + ": " + truncated_text)
    return results

# for local usage from db (single yaml file)
# * intro_text: string. if set, text to display at start of session (optional)
# * intro_stats: bool. if set, display some stats about the story at start of session (optional)
# * match_count_limit: int. if set, maximum number of entries that can be returned by a search (optional)
# * initial_search: string. if set, start the session with an already executed serach for this term (optional)
# * entries: sequence of mappings w/ keys. this is the meat of the data
#     * date: date. date for the entry. matches will be returned in order of date ascending
#     * text: string. the content of the entry to be displayed
def get_story(file_name):
    with open(file_name, 'r') as file:
        return yaml.safe_load(file)

def search_entries(entries, search_term):
    results = [entry for entry in entries if search_term.lower() in entry['text'].lower()]
    return sorted(results, key=lambda x: x['date'])

if __name__ == "__main__":
    main()

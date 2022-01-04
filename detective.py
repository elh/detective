from bullet import Bullet
import yaml
import argparse

match_limit = 2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--story_file', type=str, default="story_1.yaml", help='story yaml to run detective on')
    args = parser.parse_args()

    entries = get_entries(args.story_file)
    print(">>> Welcome to the document archive.")
    print(">>> " + str(len(entries)) + " searchable entries...")

    first_run = True

    while True:
        # ----- Prompt for search term -----
        # special handling for initial run. automatically seed and run with default first search term
        if first_run:
            print("\nSearch: COVID")
            search_term = "COVID"
        else:
            # do not use bullet.Input. cannot handle up and down arrow keys smh
            search_term = input("\nSearch: ").strip()
            if len(search_term) == 0:
                continue
        first_run = False

        # ----- Search -----
        matches = search_entries(entries, search_term)
        if len(matches) == 0:
            print("no matches")
            continue
        visible_matches = matches[:match_limit]

        prompt = f'\n{len(visible_matches)} matches. Read entry:' if len(matches) <= match_limit else f'\nFirst {len(visible_matches)} of {len(matches)} matches. Read entry:'

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
            print()
            print(matches[result[1]]['date'])
            print(matches[result[1]]['text'])
            # TODO: bold matching text selection

def format_entry_selections(entries):
    results = []
    for entry in entries:
        truncated_text = entry['text'][:75] + '..' if len(entry['text']) > 75 else entry['text']
        results.append(entry['date'].strftime("%m/%d/%Y") + ": " + truncated_text)
    return results

# for local usage from db (single yaml file)
def get_entries(file_name):
    with open(file_name, 'r') as file:
        db = yaml.safe_load(file)
        return db['entries']

def search_entries(entries, search_term):
    results = []
    for entry in entries:
        if search_term.lower() in entry['text'].lower():
            results.append(entry)
    return sorted(results, key=lambda x: x['date'])

if __name__ == "__main__":
    main()

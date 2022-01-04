from bullet import Bullet
from bullet import Input
import yaml

match_limit = 2

def main():
    entries = get_entries()
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
        results.append(entry['date'].strftime("%m/%d/%Y") + ": " + (entry['text'][:75] + '..') if len(entry['text']) > 75 else entry['text'])
    return results

# for local usage from db (single yaml file)
def get_entries():
    with open('db.yaml', 'r') as file:
        db = yaml.safe_load(file)
        return db['entries']

# TODO: ensure sort by entry date
def search_entries(entries, search_term):
    results = []
    for entry in entries:
        if search_term.lower() in entry['text'].lower():
            results.append(entry)
    return results

if __name__ == "__main__":
    main()

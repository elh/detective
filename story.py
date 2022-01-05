import yaml

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

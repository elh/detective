import yaml

default_match_count_limit = int(1e6)

# for local usage from db (single yaml file)
# * intro_text: string. if set, text to display at start of session (optional)
# * intro_stats: bool. if set, display some stats about the story at start of session (optional)
# * match_count_limit: int. if set, maximum number of entries that can be returned by a search (optional)
# * initial_search: string. if set, start the session with an already executed serach for this term (optional)
# * entries: sequence of mappings w/ keys. this is the meat of the data
#     * id: string. if not set, id will be set to entry's position index in list of entries (optional)
#     * date: date. date for the entry. matches will be returned in order of date ascending
#     * text: string. the content of the entry to be displayed
def get_story(file_name):
    with open(file_name, 'r') as file:
        story = yaml.safe_load(file)

        # defaults
        if 'match_count_limit' not in story or story['match_count_limit'] == 0:
            story['match_count_limit'] = default_match_count_limit

        # populate entry ids if not set
        for idx, entry in enumerate(story['entries']):
            if 'id' not in entry:
                entry['id'] = str(idx)

        # ensure entries sorted for downstream users
        story['entries'] = sorted(story['entries'], key=lambda x: x['date'])
        return story

def search_entries(entries, search_term):
    results = [entry for entry in entries if search_term.lower() in entry['text'].lower()]
    return sorted(results, key=lambda x: x['date'])

def get_short_date_and_text(entry):
    return entry['date'].strftime("%m/%d/%Y") + ": " + (entry['text'][:75] + '..' if len(entry['text']) > 75 else entry['text'])

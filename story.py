import yaml
import datetime
import re

default_match_count_limit = int(1e6)

# for local usage from db (single yaml file)
# * intro_text: string. if set, text to display at start of session (optional)
# * intro_stats: bool. if set, display some stats about the story at start of session (optional)
# * match_count_limit: int. if set, maximum number of entries that can be returned by a search (optional)
# * initial_search: string. if set, start the session with an already executed serach for this term (optional)
# * entries: sequence of mappings w/ keys. this is the meat of the data
#     * id: string. if not set, id will be set to entry's position index in list of entries (optional)
#     * date: date|datetime. date for the entry. matches will be returned in order of date ascending
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

# follow "her story" logic
def search_entries(entries, search_term):
    # an entry matches search if all tokenized alphanumeric parts exist in entry
    # no substring matches of parts are allowed
    # examples:
    # search "one one" matches "one"                (each part of term is searched indpendently)
    # search "one two" matches "three two one"      (order does not mater)
    # search "haven't" matches "haven couldn't"     (punctuation splits tokens)
    # search "a" does not match "apple"             (no partial matches)
    # search "cars" matches "car"                   (unpluralization)
    # search "car" matches "cars"                   (unpluralization)
    # search "s" matches "hello"                    ("s" gets unpluralized into empty list)
    def matches_entry(entry, search_term):
        entry_parts = tokenize_text(entry['text'])
        search_term_parts = tokenize_text(search_term)
        for p in search_term_parts:
            if p not in entry_parts:
                return False
        return True

    results = [entry for entry in entries if matches_entry(entry, search_term)]
    return sorted(results, key=lambda x: x['date'])

# follow "her story" logic
# naive convesion of string into non-plural, alphanumeric parts
def tokenize_text(txt):
    ts = [unpluralize(t) for t in re.split('[^a-zA-Z]', txt.lower())]
    return [t for t in ts if t != '']

# follow "her story" logic
# naive convesion of string into non-plural parts
def unpluralize(w):
    if w.endswith("ss"):
        return w
    elif w.endswith("es"):
        return w[:len(w)-2]
    if w.endswith("s"):
        return w[:len(w)-1]
    return w

def get_short_date_and_text(entry):
    date = entry['date'].strftime("%m/%d/%Y")
    if type(entry['date']) is datetime.datetime:
        date = entry['date'].strftime("%m/%d/%Y, %H:%M:%S")

    return date + ": " + (entry['text'][:75] + '..' if len(entry['text']) > 75 else entry['text'])

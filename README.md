# detective 🕵️

create and play text-based games in the style of "Her Story"

![detective](https://user-images.githubusercontent.com/1035393/148714247-828010e4-a024-407a-86d8-118049f96c7e.gif)

### Setup
`pip install -r requirements.txt`

### Usage
1. be the detective. `python detective.py` (`python detective.py -h` for more info)
2. be the author. `python author.py` (`python author.py -h` for more info)
    * `--mode` options
        * `searches_to_entries`
        * `entries_to_words`
        * `entries_graph`
        * `searches_graph`

### Story data
stories are defined by yaml files. see example `stories/story_2.yaml`

* intro_text: string. if set, text to display at start of session (optional)
* intro_stats: bool. if set, display some stats about the story at start of session (optional)
* match_count_limit: int. if set, maximum number of entries that can be returned by a search (optional)
* initial_search: string. if set, start the session with an already executed serach for this term (optional)
* entries: sequence of mappings w/ keys. this is the meat of the data
    * id: string. if not set, id will be set to entry's position index in list of entries (optional)
    * date: date|datetime. date for the entry. matches will be returned in order of date ascending
    * text: string. the content of the entry to be displayed

### Under construction 🚧
see [notes](https://github.com/elh/detective/blob/main/notes.md)

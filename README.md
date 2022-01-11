# detective 🕵️

Create and play text-based games in the style of "Her Story". See [Context](#Context) for more info.

![detective](https://user-images.githubusercontent.com/1035393/148714247-828010e4-a024-407a-86d8-118049f96c7e.gif)

### Setup
`pip install -r requirements.txt`

### Play a story
run `python detective.py` (`python detective.py -h` for more info)

Starts an interactive session for a story. Play the detective searching and reading story entries. Prompts and menus are navigated with arrow keys + Return key⏎

### Write a story
Create a story of your own by writing the segmented entries a detective player can search through. A story is basically just a set of timestamped entries that are strategically linked by search terms. A story can also associated with some configuration like the max number of entries to make returnable on searches.

#### Story data
Stories are defined by yaml files. see example `stories/story_2.yaml`

* `intro_text`: string. if set, text to display at start of session (optional)
* `intro_stats`: bool. if set, display some stats about the story at start of session (optional)
* `match_count_limit`: int. if set, maximum number of entries that can be returned by a search (optional)
* `initial_search`: string. if set, start the session with an already executed search for this term (optional)
* `entries`: sequence of mappings w/ keys. this is the meat of the data
    * `id`: string. if not set, id will be set to entry's position index in list of entries (optional)
    * `date`: date|datetime. date for the entry. matches will be returned in order of date ascending
    * `text`: string. the content of the entry to be displayed

#### "author" tools
Tools to help review structure of stories and plan ahead. The open-ended nature of this game design may make it hard to keep track of connections between entries and also keep track of which entries are returnable as you iterate on stories.

run `python author.py` w/ the desired `--mode` (`python author.py -h` for more info)
* `searches_graph` mode. Creates a graphviz visualization. Vertices are search terms (that appear more than once) annotated with the entries they appear in. A directional edge from A to B represents that returnable entries for A contain the term B. A bidirectional edge means that both terms appear in the returnable entries for the other. You can interpret this like "if you know A, you can learn B"
<img src="https://user-images.githubusercontent.com/1035393/148715952-6452bb64-3a68-4dd6-876b-6782adf3c634.png" height="500">

* `entries_graph` mode. Creates a graphviz visualization. Vertices are entries. Directional edges connect source entries to target entries that can be reached by searching a word that is contained in the source entry. This is implemented as a traversal starting from the initial search. This is likely not as useful as `searches_graph`.
<img src="https://user-images.githubusercontent.com/1035393/148715948-4e53b9c4-2699-46f6-8bf8-dfdc92c19613.png" height="600">

* `searches_to_entries` mode. Reports on entries that match search terms. The `match_` entries are the subset of entries that are returnable based on the stories configured `match_count_limit`
* `entries_to_words` mode. Reports on words contained by entries

FYI At the moment, there is a crude, hardcoded list of `ignore_words` in order to limit uninteresting search term matches

Disclaimer: These have not been refined for large graphs of 50+ vertices like the original "Her Story" game. See [TODOs and notes](https://github.com/elh/detective/blob/main/notes.md) for WIP ideas.

### Context

"Her Story" is a narrative puzzle game where the player assumes the role of a detective combing through police interview videos and coming up with their own searches to run. The only interface is a search bar which lets the player ask their own questions by running searches on the transcripts of those video segments. A search will tell you how many total videos match your term, but only the first 5 matches in chronological order can be watched. This forces the player to continually find more specific and less obvious terms in order to surface later videos.

This creates an interactive, open-ended game with nonlinear narratives. At any point, players can search whatever they want and it is up to the designer to ensure the story unfolds in an interesting way.

Shout out Sam Barlow and Game Maker's Toolkit for introducing me to the game.

### Under construction 🚧
see [TODOs and notes](https://github.com/elh/detective/blob/main/notes.md)

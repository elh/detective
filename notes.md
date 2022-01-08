### `searches_graph`

Scheme = Nodes are search terms (that appear more than once) annotated with the entries they appear in. A directional edge from A to B represents that matching entries for A contain the term B. a bidirectional edge means that both terms appear in the matching entries for the other. You can interpret this like "if you know A, you can learn B"

#### Thoughts
- [x] ~1. Update to work off an intermediate graph representation instead of writing straight to graphviz.~
- [x] ~2. BUG: I realized that my original scheme for edges is incomplete. It matters whether or not "A" is in "B"'s first-n-matches or just some later entry. Both `entries_graph` and `searches_graph` have this imprecision~
- [ ] 3. There are interesting things we can do around implied order of search terms. This requires thinking about the topological order of the graph. There are specific conditions where you could say that it possible to see term "B" before seeing term "A". This cannot be done locally/greedily. This might just be best expressed as pair-wise "happens before" relationships.
- [ ] 4. There are also additional features to represent "leaps" where a entry (and the search term that found it) can be connected to another search w/o an exact string match. For example, this could be used to model a puzzle or just a pattern match like a puzzle referencing "Alpha" and "Gamma" and then having the player guess "Beta" as a search term. This would need to be declared in the story config. Maybe try using dashed lined.
- [ ] 5. Consider more scalable approach to either `ignore_words` or just allowing story config to whitelist meaningful search terms. Having the full traversal is still useful for author to realize if they have accidental connections they want to remove.

### `entries_graph` [deprecated]

Scheme = Nodes are entries. Edges connect entries that share words

This was the first "author" visualization idea when working bottoms-up from a test story I created. This is likely way too detailed and noisy to be useful. I later realized that the likely higher leverage abstraction is just thinking about the traversal in terms of "searches" or search terms. This consolidates nodes and edges greatly and is also probably much more natural for design.

Deprecated in favor of `searches_graph`. There are some other UI things like directions of arrows that could be improved but do not care to do so now.

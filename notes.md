### `searches_graph`

Scheme = Nodes are search terms (that appear more than once) annotated with the entries they appear in. A directional edge from A to B represents that matching entries for A contain the term B. a bidirectional edge means that both terms appear in the matching entries for the other. You can interpret this like "if you know A, you can learn B"

#### Thoughts
- [x] ~1. Update to work off an intermediate graph representation instead of writing straight to graphviz.~
- [x] ~2. BUG: I realized that my original scheme for edges is incomplete. It matters whether or not "A" is in "B"'s first-n-matches or just some later entry. Both `entries_graph` and `searches_graph` have this imprecision~
- [ ] 3. There are interesting things we can do around implied order of search terms. This requires thinking about all possible paths in the graph. There are specific conditions where you could say that it possible to see term "B" before seeing term "A". This might just be best expressed as pair-wise "happens before" relationships.
    * Given a graph of directed edges and a starting vertex in the graph, is there a name for the concept that all paths from the start vertex to some vertex B “must pass” through vertex A? If (A->B, A->C, B->), C must pass A and B must pass A but you cannot say that C must pass B (you could reach C by the path A->C). B is an “ancestor” of C but this is more specific than that.
    * this will be useful for reasoning through “happens before” like relationships in the text adventure. each of these vertices are search terms you can discover based on previous search terms
    * (if i expand “her story” semantics so that it is path dependent or transitions depend on multiple terms, this will get much more complicated…)
    * also because the graph inherently has lots of cycles and i want to use this to delete edges that are uninteresting because they connect back to nodes we “must pass”. while the total graph will have cycles, you can delete edges if no non-cyclical path from the start to any node needs that edge. so like in this graph if there was an edge from C back to A, you could delete it because it’s sort of uninteresting. interpretation in this game: technically you can learn about A from C but you already know about A so who cares
- [ ] 4. There are also additional features to represent "leaps" where a entry (and the search term that found it) can be connected to another search w/o an exact string match. For example, this could be used to model a puzzle or just a pattern match like a puzzle referencing "Alpha" and "Gamma" and then having the player guess "Beta" as a search term. This would need to be declared in the story config. Maybe try using dashed lined.
- [ ] 5. Consider more scalable approach to either `ignore_words` or just allowing story config to whitelist meaningful search terms. Having the full traversal is still useful for author to realize if they have accidental connections they want to remove.
- [ ] 6. "Tarjan's strongly connected components algorithm" could also be interesting for reasoning about "must pass" subgraphs

#### original graph of story_2
![graphviz (1)](https://user-images.githubusercontent.com/1035393/148710999-4da68698-86dd-4ea6-b213-b15af31291b6.png)
```
digraph {
	elle [label="elle\nA, B, D, (I)" color=green]
	elle -> purchases [dir=both]
	museum [label="museum\nC, G, H, (I)"]
	museum -> purchases [dir=both]
	museum -> otto [dir=both]
	purchases [label="purchases\nD, F, G, (I)"]
	purchases -> x7000 [dir=both]
	catering [label="catering\nB, C"]
	catering -> elle [dir=both]
	catering -> museum [dir=both]
	x7000 [label="x7000\nE, F"]
	otto [label="otto\nH, I"]
	otto -> elle
	otto -> purchases
}
```

#### story_2 without "must pass" cycle edges
graph with all "must pass" cycle edges removed. this makes the overall structure much more meaningful. removing all of those edges does not make the graph as a whole acyclical nor does it remove bidirectional edges.

![graphviz (2)](https://user-images.githubusercontent.com/1035393/148711002-c6a968f2-72c9-42af-a4b3-cc6e47811f56.png)
```
digraph {
	elle [label="elle\nA, B, D, (I)" color=green]
	elle -> purchases # [dir=both]
	elle -> catering # new
	museum [label="museum\nC, G, H, (I)"]
	museum -> purchases [dir=both]
	museum -> otto # [dir=both]
	purchases [label="purchases\nD, F, G, (I)"]
	purchases -> x7000 # [dir=both]
	catering [label="catering\nB, C"]
    // catering -> elle [dir=both]
	catering -> museum [dir=both]
	x7000 [label="x7000\nE, F"]
	otto [label="otto\nH, I"]
    // otto -> elle
	otto -> purchases
}
```

### `entries_graph`

Scheme = Nodes are entries. Edges connect entries that share words

This was the first "author" visualization idea when working bottoms-up from a test story I created. This is likely way too detailed and noisy to be useful. I later realized that the likely higher leverage abstraction is just thinking about the traversal in terms of "searches" or search terms. This consolidates nodes and edges greatly and is also probably much more natural for design.

Probably deprecated in favor of `searches_graph`. ~There are some other UI things like directions of arrows that could be improved but do not care to do so now.~

#!/usr/bin/python
# coding=utf8

# Checks whether list1 is a prefix of list 2
is_prefix = lambda list1, list2 : list2[:len(list1)] == list1

def is_node_visited(node, identifier):
	global visited
	for vis in visited[node]:
		if is_prefix(vis, identifier):
			return True

	return False

def cycle_search_rec_node(node, identifier):
	if is_node_visited(node, identifier):
		return True

	visited[node].append(identifier)

	# AND-Verknüpfung der Fahrweg-Alternativen
	for idx, alt in enumerate(zuege[node]):
		if not cycle_search_rec_alt(alt, identifier + [idx]):
			return False

	return True

def cycle_search_rec_alt(alt, identifier):
	# OR-Verknüpfung der Elemente in der Fahrwegalternative
	for node in alt:
		if cycle_search_rec_node(node, identifier):
			return True

	return False

def cycle_search(graph):
	global visited
	
	for start_node in graph.keys():
		visited = dict((key, []) for key in graph.keys())
		if cycle_search_rec_node(start_node, []):
			return True

	return False

# Data import
import dataset3 as dataset
zuege = dataset.zuege
register = dataset.register
# End of data import

# Wait-for-Graphen aufbauen: Ersetze Registernummern durch Züge, die dieses Register belegen. Unbelegte Register werden sogleich herausgefiltert.
zuege = dict((zug,
		[filter(lambda x:x, [register[reg] for reg in fs])
			for fs in zuege[zug]
		]
	) for zug in zuege.keys())

# Erstelle eine Liste von Zügen, auf die gewartet wird
blockierend = set()
for alternativen in zuege.values():
	for fs in alternativen:
		blockierend.update(fs)

# Filtere die Züge, auf die nicht gewartet wird, aus dem Wait-For-Graphen
zuege = dict((zug, zuege[zug]) for zug in zuege.keys() if zug in blockierend)

# Finde Zyklen im Wait-for-Graphen
print(cycle_search(zuege))

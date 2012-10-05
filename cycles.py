#!/usr/bin/python
import networkx as nx

graphs =[
{
	"A" : [["B"], ["C"]],
	"B" : [["A"]],
	"C" : [["A"]],
},

{ "A" : [["B"]], "B" : [["A"]] },

{
	"A" : [["B","C"],["B"]],
	"B" : [["D"]],
	"C" : [["A", "B"]],
	"D" : [["B"], ["C"]],
},

{
	"A" : [["B", "C"], ["B"]],
	"B" : [["D"]],
	"C" : [["A", "B"]],
	"D" : [["E"]],
	"E" : [["B"]],
}
]

# map of node numbers to characters and vice versa. only for convenience
alpha = ["A", "B", "C", "D", "E"]

# Filters out invalid cycles from the list of cycles given
def filter_cycles(cycles, graph):
	for node in graph.keys():
		# rule:
		# - of each route alternative of node A, at least one node has to appear in at least one of the cycles
		#   containing node A.
		cycles_containing_node = [cycle for cycle in cycles if alpha.index(node) in cycle]

		routealts_appeared = set()

		# no optimization here yet
		for cycle in cycles_containing_node:
			for idx, routealt in enumerate(graph[node]):
				for n in routealt:
					if alpha.index(n) in cycle:
						routealts_appeared.add(idx)

		if len(routealts_appeared) != len(graph[node]):
			cycles = [c for c in cycles if c not in cycles_containing_node]

	print(cycles)

for graph in graphs:
	print("===")
	edges = []
	for node, routes in graph.items():
		for route in routes:
			# build one big graph ignoring routes
			edges.extend([(alpha.index(node), alpha.index(neighbor)) for neighbor in route])
	G = nx.DiGraph(edges)

	filter_cycles(nx.simple_cycles(G), graph)
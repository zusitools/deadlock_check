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
},

{
	"A" : [["B", "C"], ["B"]],
	"B" : [[]],
	"C" : [["A"]]
},

{
	"A" : [["B"]],
	"B" : [["C"]],
	"C" : [["A"]],
	
	"D" : [["E"]],
	"E" : [["F"]],
	"F" : [["D"]],
},

]

# map of node numbers to characters and vice versa. only for convenience
alpha = ["A", "B", "C", "D", "E", "F"]

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

	return cycles

# Filters out cycles that are proper supersets of other cycles
# Fixme: This filters out too much!
def find_minimum_cycles(cycles):
	return [c for c in cycles if not any([set(c) > set(c2) for c2 in cycles])]

# Very!! naive implementation of the Set Cover problem that runs in exponential time.
# There is probably no exact algorithm that is more efficient since MSC is NP-hard.
def set_cover(cycles, num_nodes):
	lst = range(0, num_nodes)
	potlst = [[lst[i] for i in range(0, len(lst)) if ((1 << i) & m) != 0] for m in range(0,2**len(lst))]
	return [p for p in potlst if all([not set(p).isdisjoint(set(c)) for c in cycles])]

for graph in graphs:
	print("===")
	edges = []
	for node, routes in graph.items():
		for route in routes:
			# build one big graph ignoring routes
			edges.extend([(alpha.index(node), alpha.index(neighbor)) for neighbor in route])
	G = nx.DiGraph(edges)

	cycles = nx.simple_cycles(G)
	print(cycles)
	cycles = filter_cycles(cycles, graph)
	print(cycles)
	#cycles = find_minimum_cycles(cycles)
	#print(cycles)
	if len(cycles) > 0:
		setcover = set_cover(cycles, len(graph.keys()))
		min_set_cover_count = min([len(sc) for sc in setcover])
		min_set_cover = [sc for sc in setcover if len(sc) == min_set_cover_count]
		print(min_set_cover)

		# TODO: Minimum Weighted Set Cover
		# parameters: own train yes/no, running time, etc.
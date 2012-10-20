#!/usr/bin/python
# coding=utf8

import networkx as nx
from copy import deepcopy

import dataset2 as dataset
zuege = dataset.zuege
register = dataset.register

# Hilfsfunktion "nachfolger": Bestimmt den Nachfolger des Elements x in der zyklischen Liste l = [l1 l2 … ln l1]
nachfolger = lambda x, l : l[l.index(x) + 1]

def altnrs(zug):
	global zuege
	return range(0, len(zuege[zug]))

def zykelnrs():
	global zyklen
	return range(0, len(zyklen))

# Schritt 1: Dataset parsen

# Dazu Registernummern in "zuege"-Dictionary umwandeln in von diesen Zügen belegte Register
# sowie Wait-For-Graph und Blockiert-Graph erstellen.
# Letzterer entsteht aus dem Wait-For-Graphen durch Umdrehen der Kanten und Vernachlässigen der Fahrstraßen.
#
# Zug A blockiert Zug B, wenn Zug A ein Register einer Fahrstraße belegt hält, die Zug B als nächstes benutzen könnte.

# waitfor = { blockierterZug : { FahrstraßenalternativeNr : [Blockierende Züge]  }}
waitfor = dict((key, dict((altnr, set()) for altnr in altnrs(key))) for key in zuege.keys())
# blockiert = { blockierender Zug : [blockierte Züge] }
blockiert = dict((key, set()) for key in zuege.keys())

for zug, alts in zuege.items():
	for alt, regs in enumerate(alts):
		waitfor[zug][alt] = set(register[reg] for reg in regs)
		waitfor[zug][alt].discard(None)

		for blockierender_zug in waitfor[zug][alt]:
			blockiert[blockierender_zug].add(zug)

print("WaitFor:", waitfor)
print("Blockiert-Graph:", blockiert)

# Schritt 2: Nicht blockierte Züge entfernen
# Laufzeit: O(n²)
frei = [key for key in waitfor.keys() if any(map(lambda x : len(x) == 0, waitfor[key].values()))]

while len(frei) > 0:
	frei_neu = []

	print("---")
	print("Nicht blockierte Züge: ", frei)
	for zugnr in frei:
		# Lösche den Zug
		del waitfor[zugnr]

		# Prüfe alle Züge, die dieser Zug blockiert hat, darauf, ob sie jetzt noch blockiert sind
		for blockierter_zug in blockiert[zugnr]:
			if blockierter_zug in waitfor:
				for alt in waitfor[blockierter_zug].values():
					# Entferne aktuell betrachteten Zug aus der Liste blockierender Züge
					alt.remove(zugnr)
					# Wenn ein Zug auf mindestens einer Fahrwegalternative nicht mehr blockiert ist,
					# gilt er als nicht blockiert und kann im nächsten Schleifendurchlauf entfernt werden.
					if len(alt) == 0:
						frei_neu.append(blockierter_zug)

	print("Wait-For-Graph: ", waitfor)

	frei = list(frei_neu)

# Alle Züge, die jetzt noch im Wait-for-Graphen sind, sind blockiert; somit existiert ein Deadlock, wenn der Graph nicht leer ist.
if len(waitfor) == 0:
	print("Kein Deadlock")
	exit

# Schritt 3: Aus restlichen Zügen Wait-for-Graphen W erstellen und darin Kreise finden
W = nx.DiGraph()
for zug, alts in waitfor.items():
	for altnr, waitsfor in alts.items():
		for blockierender_zug in waitsfor:
			if zug in W and blockierender_zug in W[zug]:
				W[zug][blockierender_zug]['fsnrs'].append(altnr)
			else:
				W.add_edge(zug, blockierender_zug, fsnrs = [altnr])

zyklen = nx.simple_cycles(W)
print(zyklen)

# Für Debug-Zwecke Graph zeichnen
if False:
	import matplotlib.pyplot as plt
	import matplotlib as mpl

	edge_labels = dict((edge, nx.get_edge_attributes(W, 'fsnrs')[edge]) for edge in W.edges())
	layout = nx.shell_layout(W)
	nx.draw_networkx(W, layout, node_shape = 's', node_size = 1000)
	nx.draw_networkx_edge_labels(W, layout, edge_labels = edge_labels, label_pos = 0.3)

	plt.show()


# Schritt 3a: Graph aufteilen in Knoten, die in Kreisen enthalten sind, und solche, die dies nicht sind (letztere sind dann "blockiert", aber nicht an Deadlocks beteiligt)
# Schritt 4: Abhängigkeiten unter Kreisen finden
#
# Kreis A hängt ab von Kreis B, wenn B eine Kante enthält, deren Beschriftung eine Fahrwegalternative ist, die
# in Kreis A nicht enthalten ist.
#
# Dazu wird ein Abhängigkeitsgraph ganz ähnlich dem Wait-For-Graph erstellt.

# zyklen_abh = { Zug : { FahrstraßenalternativeNr : [Kreise, die diese Fahrstraßenalternative benutzen]  }}
zyklen_abh = dict((key, dict((altnr, set()) for altnr in altnrs(key))) for key in zuege.keys())
# zyklen_block = { Kreis : [ (Zug, Fahrstraßenalternative) ] }
zyklen_block = dict((key, set()) for key in zykelnrs())

for zug in waitfor.keys():
	# Prüfe, in welchen Kreisen dieser Zug enthalten ist und mit welchen Fahrwegalternativen
	zyklen_zug = filter(lambda x : zug in zyklen[x], zykelnrs())

	if len(zyklen_zug) == 0:
		print('Zug ' + str(zug) + ' ist nicht in einem Kreis enthalten')
		del zyklen_abh[zug]
	else:
		for altnr in altnrs(zug):
			zyklen_abh[zug][altnr] = set(filter(lambda z : altnr in W[zug][nachfolger(zug, zyklen[z])]['fsnrs'], zyklen_zug))
			for zykelnr in zyklen_abh[zug][altnr]:
				zyklen_block[zykelnr].add((zug, altnr))

print(zyklen_abh)
print(zyklen_block)

def hebt_auf(zu_loeschende_zuege):
	global zyklen_abh, zyklen_block, zyklen
	geloeschte_zyklen = set()
	zyklen_abh2 = deepcopy(zyklen_abh)

	while len(zu_loeschende_zuege) > 0 and len(geloeschte_zyklen) < len(zyklen):
		zu_loeschende_zuege_neu = []
		for zug in zu_loeschende_zuege:
			if zug in zyklen_abh2:
				for zykel in set.union(*zyklen_abh2[zug].values()):
					# Dieser Kreis wird aufgehoben, entferne ihn bei allen anderen Zügen
					for zug2, altnr in zyklen_block[zykel]:
						if zug2 != zug and zug2 in zyklen_abh2:
							zyklen_abh2[zug2][altnr].remove(zykel)
							if len(zyklen_abh2[zug2][altnr]) == 0:
								zu_loeschende_zuege_neu.append(zug2)
				del zyklen_abh2[zug]

		zu_loeschende_zuege = list(zu_loeschende_zuege_neu)

	return len(geloeschte_zyklen) >= len(zyklen)

# Schritt 5: Minimale Menge M finden, die alle Kreise aufhebt.

# TODO: Nicht nur einelementige Mengen
for zug in zyklen_abh.keys():
	print(zug, hebt_auf([zug]))

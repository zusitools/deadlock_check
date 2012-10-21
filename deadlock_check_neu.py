#!/usr/bin/python
# coding=utf8

import networkx as nx
import sys
from copy import deepcopy
from itertools import combinations

import dataset1 as dataset
zuege = dataset.zuege
register = dataset.register
try:
	eigener_zug = dataset.eigener_zug
except AttributeError:
	eigener_zug = None

# Hilfsfunktion: Bestimmt den Nachfolger des Elements x in der zyklischen Liste l = [l1 l2 … ln l1]
nachfolger = lambda x, l : l[l.index(x) + 1]

# Hilfsfunktion: Gibt eine Liste der Fahrstraßenalternativen-Nummern eines Zuges zurück
def altnrs(zug):
	global zuege
	return range(0, len(zuege[zug]))

# Hilfsfunktion: Gibt die Liste [0, …, len(zyklen) - 1] zurück, also eine Nummerierung der Kreisliste
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
		# register[reg] enthält den Zug, der Register "reg" belegt, oder None (falls unbelegt).
		waitfor[zug][alt] = set(register[reg] for reg in regs if register[reg] != None)

		for blockierender_zug in waitfor[zug][alt]:
			blockiert[blockierender_zug].update(waitfor[zug][alt])

print("WaitFor:", waitfor)
print("Blockiert-Graph:", blockiert)

# Schritt 2: Nicht blockierte Züge entfernen
# Ein Zug gilt als nicht blockiert, wenn er auf mindestens einer Fahrstraßenalternative nicht durch andere Züge blockiert wird.
# Laufzeit: O(n²)
frei = [key for key in waitfor.keys() if any([len(x) == 0 for x in waitfor[key].values()])]

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
					# Entferne gelöschten Zug aus der Liste blockierender Züge. Damit wird der
					# blockierte Zug gegebenenfalls frei
					alt.remove(zugnr)
					if len(alt) == 0:
						frei_neu.append(blockierter_zug)

	print("Wait-For-Graph: ", waitfor)

	frei = list(frei_neu)

# Alle Züge, die jetzt noch im Wait-for-Graphen sind, sind blockiert; somit existiert ein Deadlock, wenn der Graph nicht leer ist.
if len(waitfor) == 0:
	print("Kein Deadlock")
	sys.exit()

# Schritt 3: Aus restlichen Zügen Wait-for-Graphen W erstellen und darin Kreise finden.
# Jede Kante A -> B wird mit den Fahrstraßenalternativen beschriftet, auf denen Zug B Zug A blockiert.
W = nx.DiGraph()
W.add_edges_from([(zug, waitsfor, {'altnrs' : filter(lambda x : waitsfor in waitfor[zug][x], altnrs(zug))}) for zug in waitfor.keys() for waitsfor in set.union(*waitfor[zug].values())])
zyklen = nx.simple_cycles(W)
print(zyklen)

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
			zyklen_abh[zug][altnr] = set(filter(lambda z : altnr in W[zug][nachfolger(zug, zyklen[z])]['altnrs'], zyklen_zug))
			for zykelnr in zyklen_abh[zug][altnr]:
				zyklen_block[zykelnr].add((zug, altnr))

print(zyklen_abh)
print(zyklen_block)

# Prüft, ob durch das Löschen der gegebene Menge von Zügen alle Kreise aufgehoben werden.
def hebt_auf(zu_loeschende_zuege):
	global zyklen_abh, zyklen_block, zyklen
	geloeschte_zyklen = set()
	zyklen_abh2 = deepcopy(zyklen_abh)

	while len(zu_loeschende_zuege) > 0 and len(geloeschte_zyklen) < len(zyklen):
		zu_loeschende_zuege_neu = set()
		geloeschte_zyklen_neu = set()
		for zug in zu_loeschende_zuege:
			# Füge alle Kreise, in denen dieser Zug enthalten ist, in die Liste zu löschender Kreise ein
			geloeschte_zyklen_neu |= set.union(*zyklen_abh2[zug].values())
			del zyklen_abh2[zug]

		geloeschte_zyklen |= geloeschte_zyklen_neu

		if len(geloeschte_zyklen) >= len(zyklen):
			break

		if len(geloeschte_zyklen_neu) > 0:
			for zug, altnr in set.union(*[zyklen_block[zykel] for zykel in geloeschte_zyklen_neu]):
				if zug in zu_loeschende_zuege_neu or not zug in zyklen_abh2:
					continue

				zyklen_abh2[zug][altnr] -= geloeschte_zyklen_neu
				if len(zyklen_abh2[zug][altnr]) == 0:
					zu_loeschende_zuege_neu.add(zug)

		zu_loeschende_zuege = set(zu_loeschende_zuege_neu)

	return len(geloeschte_zyklen) >= len(zyklen)

# Schritt 5: Minimale Menge M finden, die alle Kreise aufhebt.
# Ist allerdings der eigene Zug in solch einer minimalen Menge enthalten, wird weitergesucht.
aufhebend = []
gefunden = False
for anzahl_zuege in range(1, len(zyklen_abh.keys())):
	for comb in combinations(zyklen_abh.keys(), anzahl_zuege):
		if hebt_auf(comb):
			aufhebend.append(comb)
			if not eigener_zug in comb:
				gefunden = True

	if gefunden:
		break

print(aufhebend)

# Für Debug-Zwecke: Graph zeichnen
if False:
	import matplotlib.pyplot as plt
	import matplotlib as mpl

	edge_labels = dict((edge, nx.get_edge_attributes(W, 'altnrs')[edge]) for edge in W.edges())
	layout = nx.shell_layout(W)
	nx.draw_networkx(W, layout, node_shape = 's', node_size = 1000)
	nx.draw_networkx_edge_labels(W, layout, edge_labels = edge_labels, label_pos = 0.3)

	plt.show()
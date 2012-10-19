#!/usr/bin/python
# coding=utf8

import dataset3 as dataset
zuege = dataset.zuege
register = dataset.register

# Schritt 1: Dataset parsen

# Dazu Registernummern in "zuege"-Dictionary umwandeln in von diesen Zügen belegte Register
# sowie Wait-For-Graph und Blockiert-Graph erstellen.
# Letzterer entsteht aus dem Wait-For-Graphen durch Umdrehen der Kanten und Vernachlässigen der Fahrstraßen.
#
# Zug A blockiert Zug B, wenn Zug A ein Register einer Fahrstraße belegt hält, die Zug B als nächstes benutzen könnte.

# waitfor = { blockierterZug : { FahrstraßenalternativeNr : [Blockierende Züge]  }}
waitfor = dict((key, dict((altnr, set()) for altnr in range(0, len(zuege[key])))) for key in zuege.keys())
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

# Schritt 3: Aus restlichen Zügen Wait-for-Graphen erstellen und darin Zyklen finden

# Schritt 4: Abhängigkeiten unter Zyklen finden

# Zykel A hängt ab von Zykel B, wenn B eine Kante enthält, deren Beschriftung eine Fahrwegalternative ist, die
# in Zykel A nicht enthalten ist.

# Schritt 5: Minimale Menge M finden, die alle Zyklen aufhebt

# Ein Zykel wird dann aufgehoben, wenn a) er einen Knoten aus M enthält oder b) alle Zyklen, von denen er abhängt,
# aufgehoben wurden.

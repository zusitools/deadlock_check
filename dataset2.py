# coding=utf8

# Gibt für jedes Register an, von welchem Zug es belegt ist
register = {
	1 : "A",
	2 : "B",
	3 : "C",
	4 : "D",
	5 : "B"
}

# Gibt für jeden Zug eine Liste möglicher Fahrwege an
# (als Liste der dabei belegten Register)
zuege = {
	"A" : [
		[2, 3],
		[2, 5],
	],

	"B" : [
		[4],
	],

	"C" : [
		[1, 2],
	],

	"D" : [
		[3],
		[5],
	],
}
# coding=utf8

# Gibt für jedes Register an, von welchem Zug es belegt ist
register = {
	1 : "E3541",
	2 : "N7910",
	3 : None,
	4 : None,
	5 : None,
	6 : None,
	7 : "Dstg80248",
	8 : "Gag57566",
	9 : "Dg53842",
	10 : "E5912"
}

# Gibt für jeden Zug eine Liste möglicher Fahrwege an
# (als Liste der dabei belegten Register)
zuege = {
	"E5912" : [
		[1, 4, 6],
		[1, 3, 6],
		[2, 4, 6]
	],

	"N7910" : [
		[7],
		[4, 6, 9]
	],

	"Dstg80248" : [
		[1, 4, 5],
		[2, 4, 5],
	],

	"Gag57566" : [
		[1, 3]
	],

	"Dg53842" : [
		[1, 4],
		[1, 3],
		[2, 4]
	],

	"E3541" : [
		[3, 6, 9]
	]
}
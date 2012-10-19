# coding=utf8

# --A>------<B---
#          \----------

# Gibt für jedes Register an, von welchem Zug es belegt ist
register = {
	1000 : 1,
	1001 : 2,
	1003 : None,
}

# Gibt für jeden Zug eine Liste möglicher Fahrwege an
# (als Liste der dabei belegten Register)
zuege = {
	1 : [[1001], [1003]],
	2 : [[1000]],
}
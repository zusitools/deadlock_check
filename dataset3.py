# coding=utf8

# Beispiel Zusi-Demostrecke (Langeland)
# Die Registernumer XX steht für das Register 53XX

# Gibt für jedes Register an, von welchem Zug es belegt ist
register = {
	11 : None,
	12 : 3541,
	13 : None,
	14 : None,
	15 : 7910,
	16 : 7910,
	16 : None,
	17 : None,
	18 : None,
	19 : None,
	20 : None,
	21 : None,
	22 : None,
	23 : None,
	24 : None,
	25 : None,
	26 : 53842,
	27 : None,
	29 : None,
	31 : 53842,
	33 : 53842,
	34 : 53842,
	43 : 80248,
	44 : None,
	45 : 80248,
	46 : None,
	60 : 53842,
	61 : None,
	63 : 5912,
	64 : None,
	67 : None,
	69 : 5912,
	70 : 57566,
	71 : None,
	73 : 3541,
}

# Gibt für jeden Zug eine Liste möglicher Fahrwege an
# (als Liste der dabei belegten Register)
zuege = {
	5912 : [
		[61,25,11,20,13,21,73,12], # Langeland P2 → Altenbeken F
		[61,25,11,17,22,14,16,15], # Langeland P2 → Altenbeken G
	],

	7910 : [
		[14,22,17,11,25,64,26,31,60,46,67], # Langeland A → Langeland N7
		[14,22,17,18,24,44,45,43], # Langeland A → Langeland N5
	],

	80248 : [
		[44,24,18,17,22,23,21,73,12], # Langeland P5 → Altenbeken F
		[44,24,18,17,22,14,16,15], # Langeland P5 → Altenbeken G
	],

	57566 : [
		[19,20,13,21,73,12] # Langeland P4 → Altenbeken F
	],

	53842 : [
		[64,25,11,20,13,21,73,12], # Langeland P3 → Altenbeken F
		[64,25,11,17,22,14,16,15], # Langeland P3 → Altenbeken G
	],

	3541 : [
		[21,13,20,11,25,64,26,31,60,34,33] # Langeland K → Langeland N3
	]
}
import sys
tab = []
i = 0
while i < 11:
	tab.append(int(0))
	i += 1
try:
	while(True):
		cz = raw_input().split(' ')
		if cz[0] == 'z':
			tab[int(cz[1])] = int(cz[2])
		elif cz[0] == '+':
			print tab[int(cz[1])] + tab[int(cz[2])]
		elif cz[0] == '-':
			print tab[int(cz[1])] - tab[int(cz[2])]
		elif cz[0] == '*':
			print tab[int(cz[1])] * tab[int(cz[2])]
		elif cz[0] == '/':
			print tab[int(cz[1])] / tab[int(cz[2])]
		else:
			print tab[int(cz[1])] % tab[int(cz[2])]
except EOFError:
	sys.exit(0)

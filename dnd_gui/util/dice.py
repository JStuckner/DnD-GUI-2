import random
import re


def parseDice(dice):
	number = int(dice.group(1))
	size   = int(dice.group(2))
	op     = dice.group(3)
	mod    = int(dice.group(4) or 0)
	total = 0
	for i in range(0, number):
		total = total + random.randint(1, size)

	if op == "+":
		total += mod
	elif op == "-":
		total -= mod
	elif op == "*":
		total *= mod
	elif op == "x":
		total *= mod
	elif op == "/":
		total /= mod

	return str(total)

def parse(string):
    diceRegex = "^(\d+)d(\d+)(?:([-x+*/])(\d+))?"
    dice = string.split()
    total = 0
    for i in range(len(dice)):
        diceMatch = re.match(diceRegex, dice[i])
        if diceMatch != None:
                quantity = parseDice(diceMatch)
                total += int(quantity)
                #print(dice[i],'=',quantity)

    return total



    
def roll(dice=20, add=0, show=True):
    total = add
    for i in range(len(dice)):
        this = randint(1,dice[i])
        total += this
        if show:
            print('d%d = %d' % (dice[i], this), end='; ')
    print('TOTAL = %d' %total)
        
#roll()
print(parse('1d8'))

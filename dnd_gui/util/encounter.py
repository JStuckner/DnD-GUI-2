from random import randint, shuffle
import numpy as np

def order(NPCI):
    #print(NPCI)
    #PC initiative
    numPCs = 4
    SethI = 10
    AnastasiaI = 2
    CameronI = 5
    TravisI = 2

    try:
        numNPC = len(NPCI)
    except TypeError:
        numNPC = 1

    #Set up matrix
    order = np.zeros(numPCs+numNPC,
                     dtype=[('name',(str,12)) ,('roll', (int))])
    order['name'][0] = "Travis"
    order['name'][1] = "Cameron"
    order['name'][2] = "Seth"
    order['name'][3] = "Anastasia"
    
    #NPC colors.
    NPCs = ('Blue',
            'Red',
            'Purple',
            'Green',
            'Gray',
            'Yellow',
            'Light Green',
            'Pink',
            )

    for i in range(numNPC):
        if i < len(NPCs):
            try:
                order['name'][4+i] = NPCs[i]
            except TypeError:
                order['name'][4+i] = NPCs
        else:
            order['name'][4+i] = 'NPC_' + str(i+1)



    #Roll for PCs
    order['roll'][2] = SethI + randint(1,20)
    order['roll'][3] = AnastasiaI + randint(1,20)
    order['roll'][1] = CameronI + randint(1,20)
    order['roll'][0] = TravisI + max(randint(1,20), randint(1,20))

    #Roll for NPCs
    for i in range(numNPC):
        try:
            order['roll'][i+4] =  NPCI[i] + randint(1,20) 
        except TypeError:
            order['roll'][i+4] =  NPCI + randint(1,20)
    
    #Sort the array
    np.random.shuffle(order)
    order.sort(order='roll')

    #Print the order
    l = len(order)
    output = ''
    for i in range(l):
        offset = 12 - len(order['name'][l-i-1])
        #print(order['name'][l-i-1],' ' * offset, '=',order['roll'][l-i-1])
        output = output+str(order['name'][l-i-1])+' '*offset+'='+str(order['roll'][l-i-1])+'\n'


    return output
    

def zombie(num=1):
    for i in range(num):
        print("zombie spawns at (%d,%d)." %(randint(1,35),randint(1,25)))

#order((-2,-2,-2,-2))


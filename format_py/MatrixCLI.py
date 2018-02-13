
# coding: utf-8

# In[92]:


import numpy as np
import sys

name = sys.argv[1]
epsilon = float(sys.argv[2])
d = float(sys.argv[3])

def countOccurenceInArray(lst):
    """Fonction de traitement.
 
    Prend en parametre une liste trie contenant une sous liste 
    Renvoie un tableau de type tuple(elt, nbOccurrence).
    """
    occurrence_lst = []
    count = 1
    before = None
    for v in lst:
        if v[0][0] == before:
            count += 1
        elif before != None:
            elt_occur = (before, count)
            occurrence_lst.append(elt_occur)
            count = 1
        before = v[0][0]
    elt_occur = (before, count)
    occurrence_lst.append(elt_occur)
    return occurrence_lst

def getStochasticMatrixFromArray(lst, nbNodes):
    """Fonction de traitement.
 
    Prend en parametre une liste trie contenant une sous liste
    et le nombre de sommet contenu dans le fichier.
    Renvoie la matrice stochastique.
    """
    # Initialise la matrice a 0
    matStocha = np.zeros(shape=(int(nbNodes),int(nbNodes)), dtype=float)
    outDegree = []
    countDegree = 0
    outDegree = countOccurenceInArray(lst)

    # Rempli la matrice creuse
    cpt_iter = 1
    index = 0
    for elt in lst:
        maxBound = outDegree[index][1]
        if cpt_iter < maxBound:
            matStocha[int(elt[0][0])][int(elt[1][0])] = 1/int(outDegree[index][1])
            cpt_iter += 1
        elif cpt_iter == maxBound:
            matStocha[int(elt[0][0])][int(elt[1][0])] = 1/int(outDegree[index][1])                    
            cpt_iter = 1
            index += 1
    return matStocha
         
def getCLIFromStochasticMatrix(stochaMatrix):
    """Fonction de traitement.
 
    Prend en parametre la matrice stochastique.
    Renvoie le CLI 'Compressed Sparse Row' sous forme de 3 tableaux.
    """
    C = []
    L = []
    I = []
    CLI = []
    
    for i in range(stochaMatrix.shape[0]):
        for j in range(stochaMatrix.shape[1]):
            if stochaMatrix[i][j] != 0.0:
                C.append(stochaMatrix[i][j])
    
    copy_c = list(C)
    empty_line = 0
    indexToStartForDelete = 0
    for i in range(stochaMatrix.shape[0]):
        findElementInLineOfMatrix = False
        for j in range(stochaMatrix.shape[1]):
            if findElementInLineOfMatrix == True and stochaMatrix[i][j] != 0.0:
                I.append(j)
            if j == stochaMatrix.shape[1]-1 and stochaMatrix[i][j] == 0 and findElementInLineOfMatrix == False:
                empty_line += 1            
            if stochaMatrix[i][j] != 0.0 and findElementInLineOfMatrix == False:
                findElementInLineOfMatrix = True
                L.append(indexToStartForDelete) # Ajoute l'indice du premier element non nul
                I.append(j) # Ajoute l'indice de la colonne des elements non nul
                if empty_line != 0:
                    for nbEmptyLine in range(empty_line):
                        L.append(indexToStartForDelete) # Ajoute autant de fois qu'il y a de ligne vide dans la matrice
                    empty_line = 0
                for suppEndLine in range(j, stochaMatrix.shape[1]):
                    if indexToStartForDelete != len(C)-1 and stochaMatrix[i][suppEndLine] != 0:
                        copy_c[indexToStartForDelete] = None
                        indexToStartForDelete += 1
                #print(copy_c)
    L.append(len(C))
    print("C =",C)
    print("L =", L)
    print("I =", I)
    CLI.append(C)
    CLI.append(L)
    CLI.append(I)
    print("CLI =", CLI)
    return CLI
    
def getCLIFromGraph(fileName):
    """Fonction de traitement.
 
    Prend un parametre le chemin du fichier .txt,
    lit et traite ligne par ligne le fichier.
    Renvoie la matrice creuse du fichier traité.
    """
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            # Recupere le nombre de noeud et arc ecrit en commentaire
            lst = []
            str1 = file.readline()
            word = str1.split()
            nbNodes = word[2]
            nbEdges = word[4]
            
            # Recupere les Nodes-->Edges et les stockes dans une liste
            for line in file:
                str2 = line.split()
                ss_lst = (str2[0], str2[1])
                lst.append(ss_lst)
                
            lst = list(set(lst)) # Supprime les doublons de la liste
            lst.sort()
            print(lst)
            
            stochaMatrix = getStochasticMatrixFromArray(lst, nbNodes)
            print(stochaMatrix)
            return getCLIFromStochasticMatrix(stochaMatrix)
    except FileNotFoundError as e:
        print('Le fichier {} n\'existe pas !'.format(e.filename))
        exit(1)
        
def matrixTranspositionProduct(CLI, R):
    """Fonction du produit transposé de la matrice.
 
    Prend en parametre le CLI ( CLI[0]=C, CLI[1]=L, CLI[0]=I) et R qui sont des liste
    Renvoie le produit de la matrice transposée.
    """
    Y = []
    n = len(CLI[1])-1
    for i in range(n):
        Y.append(0)
    for i in range(len(Y)):
        for j in range(CLI[1][i], CLI[1][i+1]):
            Y[CLI[2][j]] += CLI[0][j] * R[i]
    #print("Y = ", Y)
    return Y
    
def calculatePR(n, d, R0, CLI):
    """Fonction qui calcul le PageRank
 
    Prend en parametre n, d, R, CLI ( CLI[0]=C, CLI[1]=L, CLI[0]=I) avec:
        n: nombre de sommet
        d: coefficient de zap
        R0: score de depart
        indexR: indice de l'element R
    Renvoie le score R1.
    """
    R1 = []
    for i in range(len(R0)):
        #print(matrixTranspositionProduct(CLI, R0))
        R1.append(d/n + (1-d) * matrixTranspositionProduct(CLI, R0)[i])
    return R1

def isConvergence(R0, R1, eps):
    """Fonction qui test si R0 et R1 converge
 
        Prend en parametre R0, R1 et eps avec:
        R0: vecteur de score R0
        R1: vecteur de score R1
        eps: espilon
    Renvoie le score Vrai/Faux.
    """
    converge = True
    for i in range(len(R0)):
        if(abs(R0[i]-R1[i]) > eps):
            converge = False
    return converge
   
def pageRanking(d, eps, CLI):
    R0 = []
    R1 = []
    n = len(CLI[1])-1 # Nombre de sommet
    for i in range(n):
        R1.append(1/n) # Initialise R1
    while "R0 et R1 ne converge pas":
        R0 = list(R1)
        R1 = calculatePR(n, d, R0, CLI)
        if(isConvergence(R0, R1, eps)):
            break
    return R1

print(pageRanking(d, epsilon, getCLIFromGraph(name)))


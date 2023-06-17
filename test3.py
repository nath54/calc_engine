from calc_engine import *

a = Objet('a')
b = Objet('b')
c = Objet('c')
d = Objet('d')
e = Objet('e')
f = Objet('f')
g = Objet('g')
h = Objet('h')
i = Objet('i')


m2 = Matrice(2, 2, [[a, b], [a, b]])

print(m2)

print("\n\n", m2.pivot_de_gauss_determinant())

# m3 = Matrice(3, 3, [[a, b, c], [d, e, f], [g, h, i]])

# print(m3)

# print(m3.pivot_de_gauss_determinant())

# print("\n\n\n")

# exp = Somme([Oppose(Oppose(Produit([Inverse(Reel(8)), Inverse(Oppose(Reel(4)))]))), Reel(2)])

# print(exp)
# sexp = exp.simplifie() 
# print(sexp)

print(f"\n\nMEMOISATION SIMPLIFICATION ({len(memoisation_simplications.keys())}): ")
for k in memoisation_simplications.keys():
    print(f" - `{k}` : {memoisation_simplications[k]}")


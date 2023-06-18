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


# m2 = Matrice(2, 2, [[a, b], [c, d]])

# print(m2)

# print("\n\n", m2.pivot_de_gauss_determinant())

# print("\n\n Le déterminant de cette matrice est donc : ", m2.determinant())
m3 = Matrice(3, 3, [[a, b, c], [d, e, f], [g, h, i]])

print("\n\nM3 = ", m3)

print("\n\nM3 pivot de gauss déterminant : ", m3.pivot_de_gauss_determinant())
print("\n\nM3 déterminant : ", m3.determinant())
# print("\n\n\n")

# exp = Somme([Oppose(Oppose(Produit([Inverse(Reel(8)), Inverse(Oppose(Reel(4)))]))), Reel(2)])

# print(exp)
# sexp = exp.simplifie() 
# print(sexp)

print(f"\n\nMEMOISATION SIMPLIFICATION ({len(memoisation_simplications.keys())}): ")
for k in memoisation_simplications.keys():
    print(f" - `{k}` : {memoisation_simplications[k]}")


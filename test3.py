from calc_engine import *

a = Objet('a')
b = Objet('b')

m = Matrice(2, 2, [[a, b], [a, b]])

print(m)

print(m.pivot_de_gauss_determinant())

print("\n\n\n")

exp = Somme([Oppose(Oppose(Produit([Inverse(Reel(8)), Inverse(Oppose(Reel(4)))]))), Reel(2)])

print(exp)
print(exp.simplifie())



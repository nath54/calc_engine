from calc_engine import *
from calc_engine import _R, _Q, _D, _Z, _N, _empty


a = Objet("a")
b = Objet("b")
c = Objet("c")

d = Objet("d")
e = Objet("e")
f = Objet("f")

g = Objet("g")
h = Objet("h")
i = Objet("i")

coefs = [[a, b, c], [d, e, f], [g, h, i]]

m = Matrice(3, 3, coefs)


m_gauss = m.pivot_de_gauss()

print("\nMatrice M : ",m, "\n")


print("\nMatrice M après pivot de gauss : ",m_gauss, "\n")

print("\nDéterminant de M : ", m.determinant(), "\n")


coefs = [[a, b], [c, d]]

m2 = Matrice(2, 2, coefs)

m2_gauss = m2.pivot_de_gauss()

print("\nMatrice M2 : ",m2, "\n")

print("\nMatrice M2 après pivot de gauss : ",m2_gauss, "\n")

print("\nDéterminant de M2 : ", m2.determinant(), "\n")


I_10 = matrice_identite(20)

print("\nI_10 = ", I_10, "\n")





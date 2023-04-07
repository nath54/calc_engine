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

print("Matrice M : ",m)

print("Déterminant : ", m.determinant())


coefs = [[a, b], [c, d]]

m2 = Matrice(2, 2, coefs)

print("Matrice M2 : ",m2)

print(m2.determinant())







from calc_engine import *

a = Objet('a')
b = Somme([a, Oppose(Produit([2, Produit([2, Oppose(a)])]))])
print(b.simplifie())
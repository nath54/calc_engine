from calc_engine import *

a = Objet('a')
b = Objet('b')

p1 = Produit([2, b])
f1 = Frac(p1, a)

p2 = Produit([-2, b])
f2 = Frac(p2, a)

p3 = Produit([f2, a])

s1 = Somme([f1, p3])

f3 = Frac(s1, p1)

print(f3)
print(f3.simplifie())


print(f"\n\nMEMOISATION SIMPLIFICATION ({len(memoisation_simplications.keys())}): ")
for k in memoisation_simplications.keys():
    print(f" - `{k}` : {memoisation_simplications[k]}")

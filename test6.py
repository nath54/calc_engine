from calc_engine import *

A = Matrice(4, 4, [[1, 1 , 1 , 1 ],
                   [1, -1, 1 , 1 ],
                   [1, 1 , -1, 1 ],
                   [1, 1 ,  1, -1]])

print("\n\nMatrice A :")
print(A)
print(A.pivot_de_gauss_determinant())
print(A.determinant())


B = Matrice(2, 2, [[1, -1],
                   [3, 4]])

print("\n\nMatrice B :")
print(B)
print(B.pivot_de_gauss_determinant())
print(B.determinant())


C = Matrice(3, 3, [[1, 2 , 3],
                   [0, 4, 5],
                   [0, 0, 6]])

print("\n\nMatrice C :")
print(C)
print(C.pivot_de_gauss_determinant())
print(C.determinant())


D = Matrice(3, 3, [[1, 0 , 2],
                   [2, 4, -1],
                   [-2, 0, 2]])

print("\n\nMatrice D :")
print(D)
print(D.pivot_de_gauss_determinant())
print(D.determinant())


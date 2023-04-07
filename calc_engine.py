""" imports """

from typing import Optional
from mpmath import mp
from copy import deepcopy
from math import *

""" Preparing some variables for later """

_R: Optional['Ensemble'] = None
_Q: Optional['SousEnsemble'] = None
_D: Optional['SousEnsemble'] = None
_Z: Optional['SousEnsemble'] = None
_N: Optional['SousEnsemble'] = None
_empty: Optional['EnsembleVide'] = None

""" Some configurations """

mp.dps = 50


""" useful functions """

def is_iterable(v) -> bool:
    try:
        iterator = iter(v)
        return True
    except:
        return False


""" Elements atomiques """


class Hypothese():
    def __init__(self):
        pass



class Objet():
    def __init__(self, nom: str, ensemble_parent: 'Ensemble'=None, hypotheses: list[Hypothese] = []) -> None:
        self.ensemble_parent: Ensemble = ensemble_parent
        self.nom: str = nom
        self.hypotheses: list[Hypothese] = hypotheses

    def __repr__(self) -> str:
        return self.nom
    
    def __hash__(self) -> int:
        return self.__repr__().__hash__()

    def __eq__(self, __value: object) -> bool:
        if type(__value) == Objet:
            return self.__repr__() == __value.__repr__()
        else:
            return False

    def appartient_a(self, ensemble: 'Ensemble') -> bool:
        if self.ensemble_parent == None:
            return False
        else:
            return self.ensemble_parent.inclus_dans(ensemble)

    def depends_of_var(self, var: 'Variable') -> bool:
        return False
    
    def derive(self, var: 'Variable') -> 'Objet':
        return Reel(0)
    
    def simplifie(self) -> 'Objet':
        return self
        
""" """

class Reel(Objet):
    def __init__(self, valeur) -> None:
        super().__init__(nom=None)
        #
        self.valeur = valeur
    
    def __repr__(self) -> str:
        return str(self.valeur)
    
    def __add__(self, r) -> 'Reel':
        if type(r) == Reel:
            return Reel(self.valeur+r.valeur)
        elif type(r) == float or type(r) == int:
            return Reel(self.valeur+r)
        else:
            raise UserWarning("Erreur de typage !", r, type(r))

    def __mul__(self, r) -> 'Reel':
        if type(r) == Reel:
            return Reel(self.valeur*r.valeur)
        elif type(r) == float or type(r) == int:
            return Reel(self.valeur*r)
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __sub__(self, r) -> 'Reel':
        if type(r) == Reel:
            return Reel(self.valeur-r.valeur)
        elif type(r) == float or type(r) == int:
            return Reel(self.valeur-r)
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __pow__(self, r) -> 'Reel':
        if type(r) == Reel:
            return Reel(self.valeur**r.valeur)
        elif type(r) == float or type(r) == int:
            return Reel(self.valeur**r)
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __eq__(self, r) -> bool:
        if type(r) == Reel:
            return self.valeur == r.valeur
        elif type(r) == float or type(r) == int:
            return self.valeur == r
        else:
            return False

    def __gt__(self, r) -> bool:
        if type(r) == Reel:
            return self.valeur > r.valeur
        elif type(r) == float or type(r) == int:
            return self.valeur > r
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __lt__(self, r) -> bool:
        if type(r) == Reel:
            return self.valeur < r.valeur
        elif type(r) == float or type(r) == int:
            return self.valeur < r
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __geq__(self, r) -> bool:
        if type(r) == Reel:
            return self.valeur >= r.valeur
        elif type(r) == float or type(r) == int:
            return self.valeur >= r
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __leq__(self, r) -> bool:
        if type(r) == Reel:
            return self.valeur <= r.valeur
        elif type(r) == float or type(r) == int:
            return self.valeur <= r
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __neg__(self) -> 'Reel':
        return Reel(-self.valeur)
    
    def __floor__(self) -> 'Reel':
        return Reel(floor(self.valeur))
    
    def __ceil__(self) -> 'Reel':
        return Reel(ceil(self.valeur))

    def __round__(self) -> 'Reel':
        return Reel(round(self.valeur))

    def appartient_a(self, ensemble: 'Ensemble') -> bool:
        return _R.inclus_dans(ensemble)
    
    def depends_of_var(self, var: 'Variable') -> bool:
        return False
    
    def derive(self, var: 'Variable') -> Objet:
        return Reel(0)


class Variable(Objet):
    def __init__(self, nom: str, ensemble_parent: 'Ensemble'=None) -> None:
        super().__init__(nom=nom)
        #
        self.nom: str = nom
        self.ensemble_parent: Ensemble = ensemble_parent

    def __hash__(self) -> int:
        return self.nom.__hash__()

    def __repr__(self) -> str:
        return self.nom
    
    def __eq__(self, v) -> bool:
        if v is Variable:
            return v.nom == self.nom
        return False

    def depends_of_var(self, var: 'Variable') -> bool:
        if var == self:
            return True
        else:
            return False
    
    def derive(self, var: 'Variable') -> Objet:
        if var == self:
            return Reel(1)
        else:
            return Reel(0)


class Function(Objet):
    def __init__(self, nom: str, variables: list[Variable]) -> None:
        super().__init__(nom)
        #
        self.variables: list[Variable] = variables
    
    def __repr__(self) -> str:
        return self.nom+"("+", ".join([v.__repr__() for v in self.variables])+")"
    
    def derive(self, var: Variable):
        return Derive(nom=None, fct=self, var=var)


class Derive(Function):
    def __init__(self, nom: str, fct: Function, var: Variable) -> None:
        super().__init__(nom)
        self.derive_fct: Function = fct
        self.derive_var: Variable = var

    def __repr__(self) -> str:
        order = self.get_order()
        if order == 1:
            numerator = f"d{self.derive_fct.__repr__()}({','.join(v.__repr__() for v in self.derive_fct.variables)})"
            denominator = f"d{self.derive_var.__repr__()}"
            return f"({numerator})/({denominator})"
        else:
            var_orders = self.get_variable_orders()
            numerator = f"d^{order} {self.derive_fct.__repr__()}({','.join(v.__repr__() for v in self.derive_fct.variables)})"
            denominator = ' '.join([f"d{var_i}^{var_orders[var_i]}" for var_i in var_orders])
            return f"({numerator})/({denominator})"

    def get_order(self) -> int:
        if isinstance(self.derive_fct, Derive):
            return 1 + self.derive_fct.get_order()
        else:
            return 1

    def get_variable_orders(self) -> dict[str, int]:
        if isinstance(self.derive_fct, Derive):
            orders = self.derive_fct.get_variable_orders()
        else:
            orders = {v.nom: 0 for v in self.derive_fct.variables}
        orders[self.derive_var.nom] += 1
        return orders
    
    def depends_of_var(self, var: Variable) -> bool:
        return self.derive_fct.depends_of_var(var)

    def derive(self, var: Variable) -> Objet:
        if not self.depends_of_var(var):
            return Reel(0)
        else:
            return Derive(None, self, var)
    
class Oppose(Objet):
    def __init__(self, o: Objet) -> None:
        super().__init__(nom=None)
        #
        self.o = o
        #
        if type(self.o) in [int, float]:
            self.o = Reel(self.o)
    
    def __repr__(self) -> str:
        return "-"+self.o.__repr__()
    
    def depends_of_var(self, var: Variable) -> bool:
        return self.o.depends_of_var()
    
    def derive(self, var: Variable) -> Objet:
        return Oppose(self.o.derive(var))

    def simplifie(self) -> Objet:
        obj = self.o.simplifie()
        if type(obj) == Oppose:
            return (obj.o).simplifie()
        elif obj == Reel(0):
            return Reel(0)
        else:
            return Oppose(obj)
        

class Somme(Objet):
    def __init__(self, objs: list[Objet]) -> None:
        super().__init__(nom=None)
        #
        self.objs: list[Objet] = objs
        #
        for i in range(len(self.objs)):
            if type(self.objs[i]) in [int, float]:
                self.objs[i] = Reel(self.objs[i])

    def __repr__(self) -> str:
        return "("+" + ".join([o.__repr__() for o in self.objs])+")"
    
    def depends_of_var(self, var: Variable) -> bool:
        return any([o.depends_of_var(var) for o in self.objs])
    
    def derive(self, var: Variable) -> Objet:
        if self.depends_of_var(var):
            return Somme([o.derive(var) for o in self.objs if o.depends_of_var(var)])
        else:
            return Reel(0)
    
    def simplifie(self) -> Objet:
        # On rassemble les sommes entre elles
        for o in self.objs:
            if o is Somme:
                o = o.simplifie()
                self.objs.remove(o)
                self.objs.extend(o.objs)
        # pré-tri
        sum_rls = Reel(0)
        sobjs = {}
        #
        for o in self.objs:
            if type(o) == Reel:
                sum_rls += o
            elif o is Produit:
                o = o.simplifie()
                #
                if len(o.objs) == 2 and type(o.objs[0]) == Reel:
                    if o in sobjs:
                        sobjs[o] += o.objs[0].valeur
                    else:
                        sobjs[o] = o.objs[0].valeur
            elif o is Oppose:
                if o in sobjs:
                    sobjs[o] -= 1
                else:
                    sobjs[o] = -1
            else:
                if o in sobjs:
                    sobjs[o] += 1
                else:
                    sobjs[o] = 1
        #
        new_objs = []
        #
        for ko in sobjs.keys():
            if sobjs[ko] == 0:
                continue
            elif sobjs[ko] == 1:
                new_objs.append(ko)
            elif sobjs[ko] < 0:
                new_objs.append(Oppose(Produit([Reel(-sobjs[ko]), ko])))
            else:
                new_objs.append(Produit([Reel(sobjs[ko]), ko]))
        #
        if sum_rls != 0:
            new_objs.append(sum_rls)
        #
        if len(new_objs)==0:
            return Reel(0)
        elif len(new_objs) == 1:
            return new_objs[0]
        else:
            return Somme(new_objs)

class Soustraction(Objet):
    def __init__(self, o1: Objet, o2: Objet):
        super().__init__(nom=None)
        #
        self.o1: Objet = o1
        self.o2: Objet = o2
        #
        if type(self.o1) in [int, float]:
            self.o1 = Reel(self.o1)
        if type(self.o2) in [int, float]:
            self.o2 = Reel(self.o2)

    def __repr__(self) -> str:
        return "("+self.o1.__repr__()+" - "+self.o2.__repr__()+")"
    
    def depends_of_var(self, var: Variable) -> bool:
        return self.o1.depends_of_var(var) or self.o2.depends_of_var(var)
    
    def derive(self, var: Variable) -> Objet:
        if self.depends_of_var(var):
            return Soustraction(self.o1.derive(var), self.o2.derive(var))
        else:
            return Reel(0)


class Produit(Objet):
    def __init__(self, objs: list[Objet]):
        super().__init__(nom=None)
        #
        self.objs: list[Objet] = objs
        #
        for i in range(len(self.objs)):
            if type(self.objs[i]) in [int, float]:
                self.objs[i] = Reel(self.objs[i])

    def __repr__(self) -> str:
        return "("+" * ".join([o.__repr__() for o in self.objs])+")"
    
    def depends_of_var(self, var: Variable) -> bool:
        return any([o.depends_of_var(var) for o in self.objs])
    
    def derive(self, var: Variable) -> Objet:
        dependants: list[Objet] = []
        autres: list[Objet] = []
        for o in self.objs:
            if o.depends_of_var(var):
                dependants.append(o)
            else:
                autres.append(o)
        #
        if len(dependants) == 0:
            return Reel(0)
        # else: 
        derivees: list[Objet] = []
        for i in range(0, len(dependants)):
            derivees.append(Produit([o.derive(var), Produit(dependants[:i]+dependants[i+1:])]))
        #
        return Produit([Produit(autres), Somme(derivees)])
    
    def simplifie(self) -> Objet:
        # On rassemble les produits entre eux, on simplifie les objets, et on teste le produit nul
        objs = []
        for o in self.objs:
            o = o.simplifie()
            if o is Produit:
                objs += o.objs
            elif o == Reel(0):
                return Reel(0)
            else:
                objs.append(o)
        # pré-tri
        prod_rls = Reel(1)
        sobjs = {}
        #
        for o in objs:
            if type(o) == Reel:
                prod_rls *= o
            elif o is Puissance:
                if o.obj in sobjs:
                    sobjs[o.obj].append(o.exposant)
                else:
                    sobjs[o.obj] = [o.exposant]
            else:
                if o in sobjs:
                    sobjs[o].append(Reel(1))
                else:
                    sobjs[o] = [Reel(1)]
        #
        new_objs = []
        #
        if prod_rls == 0:
            return Reel(0)
        elif prod_rls!=1:
            new_objs.append(prod_rls)
        #
        for ko in sobjs.keys():
            if sobjs[ko] == 1:
                new_objs.append(ko)
            else:
                new_objs.append(Puissance(ko, Somme(sobjs[ko]).simplifie()))
        #
        if len(new_objs) == 0:
            return Reel(1)
        elif len(new_objs) == 1:
            return new_objs[0]
        else:
            return Produit(new_objs)

class Frac(Objet):
    def __init__(self, numerateur: Objet, denominateur: Objet):
        super().__init__(nom=None)
        #
        self.numerateur: Objet = numerateur
        self.denominateur: Objet = denominateur
        #
        if type(self.numerateur) in [int, float]:
            self.numerateur = Reel(self.numerateur)
        if type(self.denominateur) in [int, float]:
            self.denominateur = Reel(self.denominateur)
    
    def __repr__(self) -> str:
        return self.numerateur.__repr__()+"/"+self.numerateur.__repr__()

    def depends_of_var(self, var: Variable) -> bool:
        return self.numerateur.depends_of_var(var) or self.denominateur.depends_of_var(var)
    
    def derive(self, var: Variable) -> Objet:
        if not self.depends_of_var(var):
            return Reel(0)
        #
        return Frac(Soustraction(Produit([self.numerateur.derive(var), self.denominateur]), Produit([self.numerateur, self.denominateur.derive(var)])), Puissance(self.denominateur, Reel(2)))
    
    def simplifie(self) -> 'Objet':
        if self.numerateur == self.denominateur:
            return Reel(1)
        elif self.denominateur == 1:
            return self.numerateur()
        else:
            return self

class Ln(Function):
    def __init__(self, f: Objet):
        self.f: Objet = f
        #
        if type(self.f) in [int, float]:
            self.f = Reel(self.f)

    def __repr__(self) -> str:
        return "ln("+self.f.__repr__()+")"
    
    def derive(self, var: Variable):
        if not self.f.depends_of_var(var):
            return Reel(0)
        #
        return Frac(self.f.derive(var), self.f)


class Puissance(Objet):
    def __init__(self, obj: Objet, exposant: Objet):
        super().__init__(nom=None)
        #
        self.obj: Objet = obj
        self.exposant: Objet = exposant
        #
        if type(self.obj) in [int, float]:
            self.obj = Reel(self.obj)
        if type(self.exposant) in [int, float]:
            self.exposant = Reel(self.exposant)

    def __repr__(self) -> str:
        return self.obj.__repr__() + "^" + self.exposant.__repr__()

    def depends_of_var(self, var: Variable) -> bool:
        return self.obj.depends_of_var(var) or self.exposant.depends_of_var(var)

    def derive(self, var: Variable) -> Objet:
        if not self.obj.depends_of_var(var):
            if not self.exposant.depends_of_var(var):
                return Reel(0)
            else:
                return Produit([Ln(self.obj), self.exposant.derive(var), Puissance(self.obj, self.exposant)])
        else:
            if not self.exposant.depends_of_var(var):
                return Produit([self.exposant, self.obj.derive(var), Puissance(self.obj, Soustraction(self.exposant, Reel(1)))])

    def simplifie(self) -> Objet:
        obj = self.obj.simplifie()
        exposant = self.exposant.simplifie()
        #
        if obj == Reel(1):
            return Reel(1)
        elif type(exposant) == Reel and exposant.valeur == 0:
            return Reel(1)
        elif type(exposant) == Reel and exposant.valeur == 1:
            return obj
        else:
            return Puissance(obj, exposant)

# Polynôme 
class Polynome(Objet):
    def __init__(self, coefs:dict[int, Objet], var: Variable):
        assert all([not coef.depends_of_var(var) for coef in coefs.values()]), "Les coefficients d'un polynôme ne peuvent pas dépendre de sa variable !"
        assert all([(type(d) == int and d >= 0) for d in coefs.keys()]), "Les degrés doivent êtres des entiers positifs !"
        #
        super().__init__(nom=None)
        #
        self.var = var
        self.coefficients:dict[int, Objet] = coefs # degré -> coefficient
        #
        for i in self.coefficients.keys():
            if type(self.coefficients[i]) in [int, float]:
                self.coefficients[i] = Reel(self.coefficients[i])
    
    def __repr__(self) -> str:
        degres = list(self.coefficients.keys()).sorted(reverse=True)
        ltxts = []
        #
        for d in degres:
            coef = self.coefficients[d]
            txt = ""
            if coef != Reel(1):
                txt += coef.__repr__() + "*"
            if d >= 10:
                txt += self.var.__repr__()+"^{"+str(d)+"}"
            else:
                txt += self.var.__repr__()+"^"+str(d)
            #
            ltxts.append(txt)
        #
        return " + ".join(ltxts)
    
    def depends_of_var(self, var: Variable) -> bool:
        return self.var == var or any([coef.depends_of_var(var) for coef in self.coefficients.values()])

    def derive(self, var: Variable) -> Objet:
        if self.var == var:
            new_coefs = {}
            for d in self.coefficients.keys():
                if d >= 1:
                    new_coefs[d-1] = Produit([Reel(d), self.coefficients[d]]).simplifie()
            return Polynome(new_coefs).simplifie()
        else:
            new_coefs = {}
            for d in self.coefficients.keys():
                new_coefs[d] = self.coefficients[d].derive(var)
            return Polynome(new_coefs).simplifie()

    def simplifie(self) -> Objet:
        new_coefs = {}
        for d in self.coefficients.keys():
            coef = self.coefficients[d].simplie()
            if coef != Reel(0):
                new_coefs[d] = coef
        #
        if len(new_coefs) == 0:
            return Reel(0)
        elif len(new_coefs) == 1 and list(new_coefs.keys())[0] == 0:
            return list(new_coefs.values())[0]
        else:
            return Polynome(new_coefs)
    
    def degre(self):
        return max(list(self.coefficients.keys()))

    def evalue(self, o: Objet):
        s = []
        #
        for d in self.coefficients.keys():
            s.append(Produit([self.coefficients[d], Puissance(self.var, Reel(d))]))
        #
        return Somme(s)


class Matrice(Objet):
    def __init__(self, nb_lignes: int, nb_colonnes: int, coefs:list[list[Objet]] = None) -> None:
        assert nb_lignes >= 1 and nb_colonnes >= 1
        #
        super().__init__(nom=None)
        #
        self.nb_lignes: int = nb_lignes
        self.nb_colonnes: int = nb_colonnes
        #
        self.coefs: list[list[Objet]] = []
        for i in range(nb_lignes):
            self.coefs.append([])
            for j in range(nb_colonnes):
                if coefs != None and len(coefs) >= i and len(coefs[i]) >= j:
                    if type(coefs[i][j]) in [int, float]:
                        self.coefs[i].append(Reel(coefs[i][j]))
                    else:
                        self.coefs[i].append(coefs[i][j])
                else:
                    self.coefs[i].append(Reel(0))
    
    def aux_repr_colonne(self, i: int) -> str:
            ctxts: list[str] = []
            #
            if self.nb_colonnes <= 16:
                for j in range(self.nb_colonnes):
                    ctxts.append(self.coefs[i][j].__repr__())
            else:
                for j in range(0, 8):
                    ctxts.append(self.coefs[i][j].__repr__())
                #
                ctxts.append("...")
                #
                for j in range(0, -9, -1):
                    ctxts.append(self.coefs[i][j].__repr__())
            #
            return " ".join(ctxts)

    def __repr__(self) -> str:
        ltxts: list[str] = []
        if self.nb_lignes <= 16:
            for i in range(self.nb_lignes):
                ltxts.append(self.aux_repr_colonne(i))
            #
            t: int = max(len(l) for l in ltxts)
            if t%2 == 1:
                t += 1
            #
            for i in range(self.nb_lignes):
                ltxts[i] += " "*(t-len(ltxts[i]))
                ltxts[i] = "|"+ltxts[i]+"|"
            #
        else:
            for i in range(0, 8):
                ltxts.append(self.aux_repr_colonne(i))
            #
            ltxts.append("")
            #
            for i in range(0, -9, -1):
                ltxts.append(self.aux_repr_colonne(i))
            #
            t: int = max(len(l) for l in ltxts)
            if t%2 == 1:
                t += 1
            #
            for i in list(range(0, 8))+list(range(0, -9, -1)):
                ltxts[i] += " "*(t-len(ltxts[i]))
                ltxts[i] = "|"+ltxts[i]+"|"
            #
            ltxts[8] = "|"+" "*(t-2)//2+"...."+" "*(t-2)//2+"|"
            #
        #
        return "\n"+"\n".join(ltxts)
    
    def depends_of_var(self, var: Variable) -> bool:
        return any([any([self.coefs[i][j].depends_of_var(var) for j in range(self.nb_colonnes)]) for i in range(self.nb_lignes)])

    def derive(self, var: Variable) -> 'Matrice':
        new_coefs=[]
        for i in range(self.nb_lignes):
            new_coefs.append([])
            for j in range(self.nb_colonnes):
                new_coefs[i].append(self.coefs[i][j].derive())
        #
        return Matrice(self.nb_lignes, self.nb_colonnes, new_coefs)

    def trace(self) -> Objet:
        s = []
        for i in range(min(self.nb_lignes, self.nb_colonnes)):
            s.append(self.coefs[i][i])
        return Somme(s).simplifie()

    def coefficient(self, i: int, j: int) -> Objet:
        return self.coefs[i][j]
    
    def sous_matrice(self, enleve_lignes: list[int], enleve_colonnes: list[int]) -> 'Matrice':
        new_nb_lignes: int = 0
        new_nb_colonnes: int = 0
        new_coefs: list[list[Objet]] = []
        #
        for i in range(self.nb_lignes):
            if not i in enleve_lignes:
                new_coefs.append([])
                #
                for j in range(self.nb_colonnes):
                    if not j in enleve_colonnes:
                        new_coefs[new_nb_lignes].append(self.coefs[i][j])
                        #
                        new_nb_colonnes += 1
                #
                new_nb_lignes += 1
        #
        return Matrice(new_nb_lignes, new_nb_colonnes, new_coefs)

    def mineur_principal(self, ligne: int, colonne: int) -> Objet:
        return (self.sous_matrice([ligne], [colonne])).determinant()

    def determinant(self) -> Objet:
        assert self.nb_lignes == self.nb_colonnes, "Le déterminant d'une matrice non carrée n'existe pas !"
        #
        if self.nb_lignes == 1:
            return self.coefs[0][0].simplifie()
        elif self.nb_lignes == 2:
            return Somme([Produit([self.coefs[0][0], self.coefs[1][1]]), Oppose(Produit([self.coefs[0][1]])), self.coefs[1][0]]).simplifie()
        else:
            m_triangularisee: 'Matrice' = self.pivot_de_gauss()
            p: list[Objet] = []
            for i in range(self.nb_lignes):
                p.append( m_triangularisee.coefficient(i, i) )
            #
            return Produit(p).simplifie()


    def pivot_de_gauss(self) -> 'Matrice':
        #
        coefs: list[list[Objet]] = deepcopy(self.coefs)
        #
        r: int = 0
        for j in range(0, self.nb_colonnes):
            # On cherche le pivot
            i_max: int = r
            for i in range(0, self.nb_lignes):
                #if coefs[i][j] > coefs[i_max][j]:
                if coefs[i][j] != 0:
                    i_max = i
                    break
            k: int = i_max
            # coefs[k][j] est le pivot
            if coefs[k][j] != 0:
                r = r+1
                if r >= self.nb_lignes:
                    continue
                # On divise la ligne k par A[k][j]
                for i in range(0, self.nb_lignes):
                    print("before frac : ", coefs[i][j], coefs[k][j], coefs[i][j] == coefs[k][j])
                    coefs[i][j] = Frac(coefs[i][j], coefs[k][j]).simplifie()
                    print("frac simplified : ", coefs[i][j])
                # On place le pivot en position r
                if k != r:
                    print(self.nb_lignes, k, r)
                    tmp = coefs[k]
                    coefs[k] = coefs[r]
                    coefs[r] = tmp
                # On simplifie les autres lignes
                for i in range(0, self.nb_lignes):
                    if i != r:
                        # On soustrait à la ligne i la ligne r multipliée par coefs[i][j] (de façon à annuler coefs[i][j])
                        for jj in range(0, self.nb_colonnes):
                            coefs[i][jj] = Somme([coefs[i][jj], Oppose(Produit([coefs[i][j], coefs[r][jj]]))]).simplifie()
        #
        return Matrice(self.nb_lignes, self.nb_colonnes, coefs)

            
            

            
        



""" """

class Ensemble():
    def __init__(self, nom: str) -> None:
        self.nom: str = nom

    def __repr__(self) -> str:
        return self.nom

    def inclus_dans(self, ensemble: 'Ensemble') -> bool:
        return ensemble == self


class EnsembleVide(Ensemble):
    def __init__(self) -> None:
        super().__init__(nom=None)

    def __repr__(self) -> str:
        return "EnsembleVide"

    def inclus_dans(self, ensemble: Ensemble) -> bool:
        return True


class SousEnsemble(Ensemble):
    def __init__(self, nom: str, ensemble_parent: Ensemble) -> None:
        super().__init__(nom)
        #
        self.ensemble_parent = ensemble_parent
    
    def inclus_dans(self, ensemble: Ensemble) -> bool:
        if ensemble == self:
            return True
        if ensemble == self.ensemble_parent:
            return True
        elif self.ensemble_parent.inclus_dans(ensemble):
            return True
        return False


class EnsembleObjets(Ensemble):
    def __init__(self, objets: list[Objet]) -> None:
        super().__init__(nom=None)
        #
        self.objets = objets

    def __repr__(self) -> str:
        return "{"+", ".join([o.__repr__() for o in self.objets])+"}"

    def inclus_dans(self, ensemble: Ensemble) -> bool:
        return all([o.appartient_a(ensemble) for o in self.objets])


class UnionEnsembles(Ensemble):
    def __init__(self, liste_ensembles: list[Ensemble]) -> None:
        super().__init__(nom=None)
        #
        self.liste_ensembles = liste_ensembles

    def __repr__(self) -> str:
        return "Union("+", ".join([o.__repr__() for o in self.objets])+")"

    def inclus_dans(self, ensemble: Ensemble) -> bool:
        return any([e.inclus_dans(ensemble) for e in self.liste_ensembles])


class IntersectionEnsemble(Ensemble):
    def __init__(self, liste_ensembles: list[Ensemble]) -> None:
        super().__init__(nom=None)
        #
        self.liste_ensembles = liste_ensembles
    
    def __repr__(self) -> str:
        return "Intersection("+", ".join([o.__repr__() for o in self.objets])+")"

    def inclus_dans(self, ensemble: Ensemble) -> bool:
        return all([e.inclus_dans(ensemble) for e in self.liste_ensembles])
    

class DifferenceEnsemble(Ensemble):
    def __init__(self, e1: Ensemble, e2: Ensemble) -> None:
        super().__init__(nom=None)
        #
        self.e1 = e1
        self.e2 = e2

    def __repr__(self) -> str:
        return "("+self.e1.__repr__()+"\\"+self.e2.__repr__()+")"
    
    def inclus_dans(self, ensemble: Ensemble) -> bool:
        return self.e1.inclus_dans(ensemble) and IntersectionEnsemble([self.e2, ensemble]).simplifie() == EnsembleVide



"""  """




""" __ Variables globales utiles d'ensembles __ """

_R = Ensemble("_R")
_Q = SousEnsemble("_Q", _R)
_D = SousEnsemble("_D", _Q)
_Z = SousEnsemble("_Z", _D)
_N = SousEnsemble("_N", _Z)

_empty = EnsembleVide()


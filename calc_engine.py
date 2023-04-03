""" imports """

from typing import Optional
from mpmath import mp

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


class Objet():
    def __init__(self, nom: str, ensemble_parent: 'Ensemble'=None) -> None:
        self.ensemble_parent: Ensemble = ensemble_parent
        self.nom: str = nom

    def __repr__(self) -> str:
        return self.nom
    
    def appartient_a(self, ensemble: 'Ensemble') -> bool:
        if self.ensemble_parent == None:
            return False
        else:
            return self.ensemble_parent.inclus_dans(ensemble)
        
    
    def depends_of_var(self, var: 'Variable') -> bool:
        return False
        
""" """


class Reel(Objet):
    def __init__(self, valeur) -> None:
        super().__init__(nom=None)
        #
        self.valeur = mp(valeur)
    
    def appartient_a(self, ensemble: 'Ensemble') -> bool:
        return _R.inclus_dans(ensemble)
    
    def depends_of_var(self, var: 'Variable') -> bool:
        return False
    
    def derive(self, var: 'Variable') -> Objet:
        return Reel(0)


class Variable(Objet):
    def __init__(self, nom: str, ensemble_parent: 'Ensemble'=None) -> None:
        super.__init__(nom)
        #
        self.nom: str = nom
        self.ensemble_parent: Ensemble = ensemble_parent

    def __repr__(self) -> str:
        return self.nom

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
        super.__init__(nom)
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
    

class Somme(Objet):
    def __init__(self, objs: list[Objet]):
        super.__init__(nom=None)
        #
        self.objs: list[Objet] = objs

    def __repr__(self) -> str:
        return "("+" + ".join([o.__repr__() for o in self.objs])+")"
    
    def depends_of_var(self, var: Variable) -> bool:
        return any([o.depends_of_var(var) for o in self.objs])
    
    def derive(self, var: Variable) -> Objet:
        if self.depends_of_var(var):
            return Somme([o.derive(var) for o in self.objs if o.depends_of_var(var)])
        else:
            return Reel(0)


class Soustraction(Objet):
    def __init__(self, o1: Objet, o2: Objet):
        super.__init__(nom=None)
        #
        self.o1: Objet = o1
        self.o2: Objet = o2

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
        super.__init__(nom=None)
        #
        self.objs: list[Objet] = objs

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
        

class Frac(Objet):
    def __init__(self, numerateur: Objet, denominateur: Objet):
        super.__init__(nom=None)
        #
        self.numerateur: Objet = numerateur
        self.denominateur: Objet = denominateur
    
    def __repr__(self) -> str:
        return self.numerateur.__repr__()+"/"+self.numerateur.__repr__()

    def depends_of_var(self, var: Variable) -> bool:
        return self.numerateur.depends_of_var(var) or self.denominateur.depends_of_var(var)
    
    def derive(self, var: Variable) -> Objet:
        if not self.depends_of_var(var):
            return Reel(0)
        #
        return Frac(Soustraction(Produit([self.numerateur.derive(var), self.denominateur]), Produit([self.numerateur, self.denominateur.derive(var)])), Puissance(self.denominateur, Reel(2)))
    

class Ln(Function):
    def __init__(self, f: Objet):
        self.f: Objet = f

    def __repr__(self) -> str:
        return "ln("+self.f.__repr__()+")"
    
    def derive(self, var: Variable):
        if not self.f.depends_of_var(var):
            return Reel(0)
        #
        return Frac(self.f.derive(var), self.f)


class Puissance(Objet):
    def __init__(self, obj: Objet, exposant: Objet):
        super.__init__(nom=None)
        #
        self.obj: Objet = obj
        self.exposant: Objet = exposant

    def __repr__(self) -> str:
        return self.obj.__repr__() + "^" + self.exposant.__repr__()

    def depends_of_var(self, var: 'Variable') -> bool:
        pass

    def derive(self, var: Variable) -> Objet:
        if not self.obj.depends_of_var(var):
            if not self.exposant.depends_of_var(var):
                return Reel(0)
            else:
                return Produit([Ln(self.obj), self.exposant.derive(var), Puissance(self.obj, self.exposant)])
        else:
            if not self.exposant.depends_of_var(var):
                return Produit([self.exposant, self.obj.derive(var), Puissance(self.obj, Soustraction(self.exposant, Reel(1)))])


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

_empty = EnsembleVide("_empty")


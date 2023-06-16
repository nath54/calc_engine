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

NaN: 'Objet' = None
Infinity: 'Objet' = None

#TODO
simplications: dict = {} # Un peu de mémoisation pour accélérer un peu, comme je répète pas mal de fois les fonctions `simplifie()`

""" Some configurations """

mp.dps = 50


""" useful functions """

def is_iterable(v) -> bool:
    try:
        iterator = iter(v)
        return True
    except:
        return False

def complete_string_with_white_spaces(s: str, t: int):
    if len(s) >= t:
        return s
    else:
        return s + " "*(t-len(s))

def aux_simplify_produit_et_frac(objet_initial: 'Objet', objets_du_produit: list['Objet']) -> 'Objet':
    """
        Arguments:
            - objet_initial = Objet du produit ou de la fraction que l'on souhaite simplifier, ne sert que pour l'affichage
            - objets_du_produit = liste des objets du produit qu'il faut simplifier entre eux
    """
    # On va ici décomposer les sous_produits et les sous_fractions pour tout mettre au même niveau
    signe: int = 1
    objets_decomposes: list[Objet] = []

    # Boucle de décomposition
    for objet in objets_du_produit:
        # On simplifie d'abord l'objet
        objet_simplifie = objet.simplifie()
        
        # Et on va donc tester les différents cas possibles
        ### Cas où l'objet est un opposé de la forme -(expression) ###
        while type(objet_simplifie) is Oppose:
            # On va exporter le signe, et retraiter l'objet
            signe *= -1
            objet_simplifie = objet_simplifie.o

        ### Cas où l'objet serait nul ###
        if objet_simplifie == 0:
            # On va pouvoir simplifier très facilement, car toute multiplication avec 0 est égale à 0
            print("Simplifie (Prod/Frac) ", objet_initial, " => ", Reel(0))
            return Reel(0)
        ### Cas où l'objet est un produit ###
        elif type(objet_simplifie) is Produit:
            objets_decomposes += objet_simplifie.objs

        ### Cas où l'objet est une fraction ###
        elif type(objet_simplifie) is Frac:
            ## On traite le numérateur ##
            numerateur = objet_simplifie.numerateur

            # Si le numérateur n'est qu'un simple produit, on va pouvoir directement le mettre en produit avec les éléments au premier niveau
            if type(numerateur) is Produit:
                objets_decomposes += numerateur.objs
            # Sinon, on ne peux pas simplifier plus que cela le produit avec le numérateur de la fraction
            else:
                objets_decomposes.append(numerateur)
            ## On traite le dénominateur ##

            denominateur = objet_simplifie.denominateur
            # Si le dénominateur est un produit, on va pouvoir le décomposer et appliquer la formule `1/(a*b) = 1/a * 1/b)`
            if type(denominateur) is Produit:
                objets_decomposes += [Inverse(sous_objet) for sous_objet in denominateur.objs]
            # Sinon, on ne peux pas simplifier plus que ça
            else:
                objets_decomposes.append(Inverse(denominateur))
    
        ### Cas où l'objet est in inverse de la forme (1/expression) ###
        elif type(objet_simplifie) is Inverse:
            # Si le dénominateur est un produit, on va pouvoir le décomposer et appliquer la formule `1/(a*b) = 1/a * 1/b)`
            if type(objet_simplifie.obj) is Produit:
                objets_decomposes += [Inverse(so) for so in objet_simplifie.obj.objs]
            # Sinon, on ne peux pas simplifier plus que ça
            else:
                objets_decomposes.append(objet_simplifie)
    
        ### Cas où l'on a juste affaire à un objet général, sans plus de précisions ###
        else:
            # On ne peux donc pas simplifier plus que ça
            objets_decomposes.append(objet_simplifie)

    # On va rassembler tous les réels ici pour pouvoir directement simplifier en un produit de réels
    produit_des_nombres_reels: Reel = Reel(signe)
    # On va rassembler ici tous les objets et regrouper les mêmes bases sous une puissance 
    objets_par_puissance: dict[Objet, Objet] = {}
    
    # On va donc parcourir tous les objets qui ont été décomposés précédemment
    for objet in objets_decomposes:
        # On va donc traiter les différents cas possibles, on a déjà une première hypothèse, qui serait qu'aucun objet ne serait nul

        ### Cas où l'objet est un réel ###
        if type(objet) is Reel:
            produit_des_nombres_reels *= objet
    
        ### Cas où l'objet serait déjà une puissance ###
        elif type(objet) is Puissance:
            if objet.obj in objets_par_puissance:
                objets_par_puissance[objet.obj].append(objet.exposant)
            else:
                objets_par_puissance[objet.obj] = [objet.exposant]
        
        ### Cas où l'objet est un inverse ###
        elif type(objet) is Inverse:
            if objet.obj in objets_par_puissance:
                objets_par_puissance[objet.obj].append(Reel(-1))
            else:
                objets_par_puissance[objet.obj] = [Reel(-1)]
    
        ### Cas où l'objet est un objet général, sans plus d'informations que cela ###
        else:
            if objet in objets_par_puissance:
                objets_par_puissance[objet].append(Reel(1))
            else:
                objets_par_puissance[objet] = [Reel(1)]

    # On va ici trier les éléments qui seront au dénominateur et ceux qui seront au numérateur
    nouveau_numerateurs = []
    nouveau_denominateur = []

    # Si on a une multiplication par 0, on simplifie
    if produit_des_nombres_reels == 0:
        print("Simplifie (Prod/Frac) ", objet_initial, " => ", Reel(0))
        return Reel(0)
    # Sinon, si les réels ne se simplifient pas, on les ajoute au numérateur
    elif produit_des_nombres_reels!=1:
        nouveau_numerateurs.append(produit_des_nombres_reels)
    
    # On va parcourir tous les objets que l'on avait trié par base égale
    for base_objet in objets_par_puissance.keys():
        # On simplifie l'expression de la somme des puissances
        somme_puissances_de_base_objet = Somme(objets_par_puissance[base_objet]).simplifie()

        # a^1 = a
        if somme_puissances_de_base_objet == 1:
            nouveau_numerateurs.append(base_objet)
        # a^{-1} = 1/a
        elif somme_puissances_de_base_objet == -1:
            nouveau_denominateur.append(base_objet)
        # Si l'exposant est réel négatif, on ajoute l'élément au dénominateur
        elif type(somme_puissances_de_base_objet) is Reel and somme_puissances_de_base_objet < 0:
            nouveau_denominateur.append(Puissance(base_objet, -somme_puissances_de_base_objet.value).simplifie())
        # Sinon, on ajoute l'élément au numérateur
        else:
            nouveau_numerateurs.append(Puissance(base_objet, somme_puissances_de_base_objet).simplifie())

    # On va maintenant finir en détectant plusieurs cas
    ### Cas où le dénominateur est vide ###
    if len(nouveau_denominateur) == 0 or nouveau_denominateur == [1]:
        ## 1/1 = 1
        if len(nouveau_numerateurs) == 0:
            print("Simplifie (Prod/Frac) ", objet_initial, " => ", Reel(1))
            return Reel(1)
        
        ## (a)/1 = a
        elif len(nouveau_numerateurs) == 1:
            print("Simplifie (Prod/Frac) ", objet_initial, " => ", nouveau_numerateurs[0])
            return nouveau_numerateurs[0]
        
        ## (expr)/1 = expr
        else:
            print("Simplifie (Prod/Frac) ", objet_initial, " => ", Produit(nouveau_numerateurs))
            return Produit(nouveau_numerateurs)

    ### Cas où le dénominateur n'est pas vide ###
    else:
        # On prépare le dénominateur final
        denominateur_final: Objet = nouveau_denominateur[0] if len(nouveau_denominateur) == 1 else Produit(nouveau_denominateur).simplifie()

        ## Si le numérateur est égal à 1, on renvoie juste l'inverse du dénominateur
        if len(nouveau_numerateurs) == 0 or nouveau_numerateurs == [1]:
            print("Simplifie (Prod/Frac) ", objet_initial, " => ", Inverse(Produit(nouveau_denominateur)).simplifie())
            return Inverse(Produit(nouveau_denominateur))
        
        ## Sinon, on prépare le numérateur final, et on renvoie la fraction (expression numérateur)/(expression dénominateur)
        numerateur_final: Objet = nouveau_numerateurs[0] if len(nouveau_numerateurs) == 1 else Produit(nouveau_numerateurs).simplifie()
        print("Simplifie (Prod/Frac) ", objet_initial, " => ", Frac(numerateur_final, denominateur_final))
        return Frac(numerateur_final, denominateur_final)
    
def aux_simplify_produit(prod: 'Produit', p_objs: list['Objet']) -> 'Objet':
    return aux_simplify_produit_et_frac(prod, p_objs)
    
def aux_simplify_frac(frac: 'Frac', f_num: 'Objet', f_denom: 'Objet') -> 'Objet':
    return aux_simplify_produit_et_frac(frac, [f_num, Inverse(f_denom).simplifie()])
    

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
        self_simplifie = self.simplifie()
        if type(__value) is Objet:
            value_simplifie = __value.simplifie()
        else:
            value_simplifie = __value
        if type(__value) is Objet:
            return self_simplifie.__repr__() == value_simplifie.__repr__()
        elif type(self_simplifie) in [int, float, Reel]:
            return self_simplifie == value_simplifie
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
        print("Simplifie (Objet) ", self, " => ", self)
        return self


""" """

class Reel(Objet):
    def __init__(self, valeur) -> None:
        super().__init__(nom=None)
        #
        self.valeur = valeur
    
    def __repr__(self) -> str:
        return str(self.valeur)
    
    def __hash__(self) -> int:
        return self.__repr__().__hash__()
    
    def __add__(self, r) -> 'Reel':
        if type(r) is Reel:
            return Reel(self.valeur+r.valeur)
        elif type(r) is float or type(r) is int:
            return Reel(self.valeur+r)
        else:
            raise UserWarning("Erreur de typage !", r, type(r))

    def __mul__(self, r) -> 'Reel':
        if type(r) is Reel:
            return Reel(self.valeur*r.valeur)
        elif type(r) is float or type(r) is int:
            return Reel(self.valeur*r)
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __sub__(self, r) -> 'Reel':
        if type(r) is Reel:
            return Reel(self.valeur-r.valeur)
        elif type(r) is float or type(r) is int:
            return Reel(self.valeur-r)
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __pow__(self, r) -> 'Reel':
        if type(r) is Reel:
            return Reel(self.valeur**r.valeur)
        elif type(r) is float or type(r) is int:
            return Reel(self.valeur**r)
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __eq__(self, r) -> bool:
        if type(r) is Reel:
            return self.valeur == r.valeur
        elif type(r) is float or type(r) is int:
            return self.valeur == r
        else:
            return False

    def __gt__(self, r) -> bool:
        if type(r) is Reel:
            return self.valeur > r.valeur
        elif type(r) is float or type(r) is int:
            return self.valeur > r
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __lt__(self, r) -> bool:
        if type(r) is Reel:
            return self.valeur < r.valeur
        elif type(r) is float or type(r) is int:
            return self.valeur < r
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __geq__(self, r) -> bool:
        if type(r) is Reel:
            return self.valeur >= r.valeur
        elif type(r) is float or type(r) is int:
            return self.valeur >= r
        else:
            raise UserWarning("Erreur de typage !", r, type(r))
    
    def __leq__(self, r) -> bool:
        if type(r) is Reel:
            return self.valeur <= r.valeur
        elif type(r) is float or type(r) is int:
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
    
    def simplifie(self) -> Objet:
        print("Simplifie (Réel) ", self, " => ", self)
        return self


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
        if type(v) is Variable:
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
    
    def simplifie(self) -> Objet:
        print("Simplifie (Variable) ", self, " => ", self)
        return self


class Fonction(Objet):
    def __init__(self, nom: str, variables: list[Variable]) -> None:
        super().__init__(nom)
        #
        self.variables: list[Variable] = variables
    
    def __repr__(self) -> str:
        return self.nom+"("+", ".join([v.__repr__() for v in self.variables])+")"
    
    def derive(self, var: Variable):
        return Derivee(nom=None, fct=self, var=var)
    
    def simplifie(self) -> Objet:
        print("Simplifie (Fonction) ", self, " => ", self)
        return self
    


class Derivee(Fonction):
    def __init__(self, nom: str, fct: Fonction, var: Variable) -> None:
        super().__init__(nom)
        self.derive_fct: Fonction = fct
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
        if isinstance(self.derive_fct, Derivee):
            return 1 + self.derive_fct.get_order()
        else:
            return 1

    def get_variable_orders(self) -> dict[str, int]:
        if isinstance(self.derive_fct, Derivee):
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
            return Derivee(None, self, var)


class Oppose(Objet):
    def __init__(self, o: Objet) -> None:
        super().__init__(nom=None)
        #
        self.o = o
        #
        if type(self.o) in [int, float]:
            self.o = Reel(self.o)
    
    def __repr__(self) -> str:
        if type(self.o) in [Objet, Variable, 'Fonction']:
            return "-"+self.o.__repr__()
        else:
            return "- "+self.o.__repr__()

    
    def depends_of_var(self, var: Variable) -> bool:
        return self.o.depends_of_var()
    
    def derive(self, var: Variable) -> Objet:
        return Oppose(self.o.derive(var))

    def simplifie(self) -> Objet:
        obj = self.o.simplifie()
        if type(obj) is Oppose:
            while type(obj) is Oppose:
                obj = obj.o
            print("Simplifie (Oppose) ", self, " => ", obj)
            return obj
        elif type(obj) is Produit:
            if type(obj.objs[0]) is Reel and obj.objs[0] < 0:
                return Produit([-1]+obj.objs).simplifie()
            else:
                return Oppose(obj)
        elif type(obj) is Reel:
            print("Simplifie (Oppose) ", self, " => ", Reel(-obj.valeur))
            return Reel(-obj.valeur)
        else:
            print("Simplifie (Oppose) ", self, " => ", Oppose(obj))
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
        txt = "("
        for i in range(len(self.objs)):
            if i != 0:
                if type(self.objs[i]) is Oppose:
                    txt += " "
                else:
                    txt += " + "
            txt += self.objs[i].__repr__()
        txt += ")"
        return txt
    
    def depends_of_var(self, var: Variable) -> bool:
        return any([o.depends_of_var(var) for o in self.objs])
    
    def derive(self, var: Variable) -> Objet:
        if self.depends_of_var(var):
            return Somme([o.derive(var) for o in self.objs if o.depends_of_var(var)])
        else:
            return Reel(0)
    
    def simplifie(self) -> Objet:
        # print("\nDEBUG : SIMPLIFICATION DE SOMME\n")
        # On rassemble les sommes entre elles
        nobjs = []
        for o in self.objs:
            # print("L'élément ", o, " est dans la somme, et est de type ", type(o), "\n")
            if type(o) is Somme:
                # print("Sous-Somme détectée", o)
                o = o.simplifie()
                nobjs.extend(o.objs)
            else:
                nobjs.append(o)
        #
        self.objs = nobjs
        # pré-tri
        sum_rls = Reel(0)
        sobjs = {}
        #
        for o in self.objs:
            o = o.simplifie()
            if type(o) is Reel:
                sum_rls += o
                continue
            if type(o) is Produit:
                if len(o.objs) == 2 and type(o.objs[0]) is Reel:
                    if o in sobjs:
                        sobjs[o] += o.objs[0].valeur
                    else:
                        sobjs[o] = o.objs[0].valeur
                    continue

            if type(o) is Oppose:
                no = o.o.simplifie()
                if no in sobjs:
                    sobjs[no] -= 1
                else:
                    sobjs[no] = -1
                continue
            #
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
            elif sobjs[ko] == -1:
                new_objs.append(Oppose(ko))
            elif sobjs[ko] < 0:
                new_objs.append(Oppose(Produit([Reel(-sobjs[ko]), ko])))
            else:
                new_objs.append(Produit([Reel(sobjs[ko]), ko]))
        #
        if sum_rls != 0:
            new_objs.append(sum_rls)
        #
        if len(new_objs)==0:
            print("Simplifie (Somme) ", self, " => ", Reel(0))
            return Reel(0)
        elif len(new_objs) == 1:
            print("Simplifie (Somme) ", self, " => ", new_objs[0])
            return new_objs[0]
        else:
            print("Simplifie (Somme) ", self, " => ", Somme(new_objs))
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
        
    def simplifie(self) -> 'Objet':
        return Somme([self.o1, Oppose(self.o2)]).simplifie()


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
        return aux_simplify_produit(self, self.objs)

class Inverse(Objet):
    def __init__(self, obj: Objet):
        super().__init__(nom=None)
        #
        self.obj = obj
        #
        if type(self.obj) in [int, float]:
            self.obj = Reel(self.obj)
        
    def __repr__(self):
        return "1/"+self.obj.__repr__()

    def depends_of_var(self, var: Variable) -> bool:
        return self.obj.depends_of_var(var)
    
    def derive(self, var: Variable) -> Objet:
        if not self.depends_of_var(var):
            return Reel(0)
        #
        return Frac(Oppose(self.obj.derive(var)), Puissance(self.obj, 2))
    
    def simplifie(self) -> Objet:        
        obj = self.obj.simplifie()
        opp = False
        if type(obj) is Oppose:
            opp = True
            obj = obj.o
        if type(obj) is Inverse:
            if opp:
                print("Simplifie (Inverse) ", self, " => ", Oppose(obj.obj))
                return Oppose(obj.obj)
            else:
                print("Simplifie (Inverse) ", self, " => ", obj.obj)
                return obj.obj
        if type(obj) is Frac:
            if opp:
                print("Simplifie (Inverse) ", self, " => ", Oppose(obj.inverse()))
                return Oppose(obj.inverse())
            else:
                print("Simplifie (Inverse) ", self, " => ", obj.inverse())
                return obj.inverse()
        #
        print("Simplifie (Inverse) ", self, " => ", Inverse(obj))
        return Inverse(obj)


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
        return self.numerateur.__repr__()+"/"+self.denominateur.__repr__()

    def depends_of_var(self, var: Variable) -> bool:
        return self.numerateur.depends_of_var(var) or self.denominateur.depends_of_var(var)
    
    def derive(self, var: Variable) -> Objet:
        if not self.depends_of_var(var):
            return Reel(0)
        #
        return Frac(Soustraction(Produit([self.numerateur.derive(var), self.denominateur]), Produit([self.numerateur, self.denominateur.derive(var)])), Puissance(self.denominateur, Reel(2)))
    
    def inverse(self) -> 'Frac':
        return Frac(self.denominateur, self.numerateur)

    def simplifie(self) -> Objet:
        num = self.numerateur.simplifie()
        denom = self.denominateur.simplifie()
        return aux_simplify_frac(self, num, denom)

class Ln(Fonction):
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
        return "("+self.obj.__repr__() + "^" + self.exposant.__repr__()+")"

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
        if obj == 1:
            print("Simplifie (Puissance) ", self, " => ", Reel(1))
            return Reel(1)
        
        if exposant == 0:
            print("Simplifie (Puissance) ", self, " => ", Reel(1))
            return Reel(1)
        
        if exposant == 1:
            print("Simplifie (Puissance) ", self, " => ", obj)
            return obj
        
        if exposant == -1:
            print("Simplifie (Puissance) ", self, " => ", Inverse(obj))
            return Inverse(obj)
        
        #
        print("Simplifie (Puissance) ", self, " => ", Puissance(obj, exposant))
        return Puissance(obj, exposant)

# Polynôme 
class Polynome(Objet):
    def __init__(self, coefs:dict[int, Objet], var: Variable):
        assert all([not coef.depends_of_var(var) for coef in coefs.values()]), "Les coefficients d'un polynôme ne peuvent pas dépendre de sa variable !"
        assert all([(type(d) is int and d >= 0) for d in coefs.keys()]), "Les degrés doivent êtres des entiers positifs !"
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
            print("Simplifie (Polynome) ", self, " => ", Reel(0))
            return Reel(0)
        elif len(new_coefs) == 1 and list(new_coefs.keys())[0] == 0:
            print("Simplifie (Polynome) ", self, " => ", list(new_coefs.values())[0])
            return list(new_coefs.values())[0]
        else:
            print("Simplifie (Polynome) ", self, " => ", Polynome(new_coefs))
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
    
    def aux_repr_colonne(self, i: int, col_tmaxs: list[int]) -> str:
            ctxts: list[str] = []
            #
            if self.nb_colonnes <= 16:
                for j in range(self.nb_colonnes):
                    ctxts.append(complete_string_with_white_spaces(self.coefs[i][j].__repr__(), col_tmaxs[j]))
            else:
                for j in range(0, 8):
                    ctxts.append(complete_string_with_white_spaces(self.coefs[i][j].__repr__(), col_tmaxs[j]))
                #
                ctxts.append("...")
                #
                for j in range(-1, -9, -1):
                    ctxts.append(complete_string_with_white_spaces(self.coefs[i][j].__repr__(), col_tmaxs[j]))
            #
            return " ".join(ctxts)

    def __repr__(self) -> str:
        ltxts: list[str] = []
        # On calcule la taille maximale de chaque élément pour chaque colonne
        col_tmaxs: list[int] = [0 for _ in range(0, self.nb_colonnes)]
        for i in range(0, self.nb_lignes):
            for j in range(0, self.nb_colonnes):
                tj = len(self.coefs[i][j].__repr__())
                if tj > col_tmaxs[j]:
                    col_tmaxs[j] = tj
        #
        if self.nb_lignes <= 16:
            for i in range(self.nb_lignes):
                ltxts.append(self.aux_repr_colonne(i, col_tmaxs))
            #
            t: int = max(len(l) for l in ltxts)
            #
            for i in range(self.nb_lignes):
                ltxts[i] += " "*(t-len(ltxts[i]))
                ltxts[i] = "|"+ltxts[i]+"|"
            #
        else:
            for i in range(0, 8):
                ltxts.append(self.aux_repr_colonne(i, col_tmaxs))
            #
            ltxts.append("")
            #
            for i in range(-1, -9, -1):
                ltxts.append(self.aux_repr_colonne(i, col_tmaxs))
            #
            t: int = max(len(l) for l in ltxts)
            # if t%2 == 1:
            #     t += 1
            #
            for i in list(range(0, 8))+list(range(-1, -10, -1)):
                ltxts[i] += " "*(t-len(ltxts[i]))
                ltxts[i] = "|"+ltxts[i]+"|"
            #
            # if t % 2 == 1:
            #     ltxts[8] = "|"+" "*((t-5)//2)+"..."+" "*((t-1)//2)+"|"
            # else:
            #     ltxts[8] = "|"+" "*((t-2)//2)+"...."+" "*((t-2)//2)+"|"
            if self.nb_colonnes <= 16:
                ltxts[8] = "|"+" ".join(["."]*self.nb_colonnes)+"|"
            else:
                ltxts[8] = "|"+" ".join(["."]*8)+" ... "+" ".join(["."]*8)+"|"
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
    
    def transposee(self):
        new_coefs = []
        for j in range(self.nb_colonnes):
            new_coefs.append([])
            for i in range(self.nb_lignes):
                new_coefs[j].append(self.coefs[i][j])
        return Matrice(self.nb_colonnes, self.nb_lignes, new_coefs)
    
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

    def aux_ech_lignes(self, coefs: list[list[Objet]], i: int, j: int) -> Objet:
        tmp = coefs[i]
        coefs[i] = coefs[j]
        coefs[j] = tmp
        return Reel(-1)
    
    def aux_ech_colonnes(self, coefs: list[list[Objet]], i: int, j: int) -> Objet:
        for k in range(len(coefs)):
            tmp = coefs[k][j]
            coefs[k][j] = coefs[k][i]
            coefs[k][i] = tmp
        return Reel(-1)
    
    def aux_mult_ligne(self, coefs: list[list[Objet]], i: int, o: Objet):
        assert o != 0
        #
        for j in range(len(coefs[0])):
            coefs[i][j] = Produit([coefs[i][j], o]).simplifie()
        #
        return o
    
    def aux_mult_col(self, coefs: list[list[Objet]], j: int, o: Objet):
        assert o != 0
        #
        for i in range(len(coefs)):
            coefs[i][j] = Produit([coefs[i][j], o]).simplifie()
        #
        return o
    
    def aux_transvection_ligne(self, coefs: list[list[Objet]], i: int, j: int, o: Objet):
        for k in range(len(coefs[0])):
            coefs[i][k] = Somme([coefs[i][k], Produit([o, coefs[j][k]])]).simplifie()
        #
        return Reel(1)
    
    def aux_transvection_colonne(self, coefs: list[list[Objet]], i: int, j: int, o: Objet):
        for k in range(len(coefs)):
            coefs[k][i] = Somme([coefs[k][i], Produit([o, coefs[k][j]])]).simplifie()
        #
        return Reel(1)

    def pivot_de_gauss_determinant(self) -> tuple[Objet, 'Matrice']:
        # Le coefficient qui change lorsque l'on effectue les opérations élémentaires d'échanges de lignes/colonnes etc... lors de l'application de l'algotithme du pivot de Gauss
        coef_det: Objet = Reel(1)
        #
        coefs: list[list[Objet]] = deepcopy(self.coefs)
        #
        for current_col in range(0, self.nb_colonnes):
            # current_col désigne la colonne actuelle où l'on applique le pivot

            # On cherche le premier coefficient non nul de la colonne
            ligne_pivot: int = 0
            for i in range(0, self.nb_lignes):
                if coefs[i][current_col] != 0:
                    ligne_pivot = i
                    break
            
            # le coefficient coef[ligne_pivot][current_col] est le pivot choisit

            # On le met à la bonne ligne si besoin
            chg = self.aux_ech_lignes(coefs, ligne_pivot, current_col)
            coef_det = Produit([coef_det, chg]).simplifie()

            pivot: Objet = coefs[current_col][current_col]

            # On va annuler les coefficients des lignes d'en dessous
            for i in range(current_col, self.nb_lignes):
                self.aux_transvection_ligne(coefs, i, current_col, Oppose(Frac(coefs[i][current_col], pivot)).simplifie())
            
            # On va normaliser le pivot
            chg = self.aux_mult_ligne(coefs, current_col, Frac(1, pivot).simplifie())
            coef_det = Produit([coef_det, chg]).simplifie()

            # On a fini de traiter la colonne current_col !
        #
        return (coef_det, Matrice(self.nb_lignes, self.nb_colonnes, coefs))
        
    def determinant(self) -> Objet:
        assert self.nb_lignes == self.nb_colonnes, "Le déterminant d'une matrice non carrée n'existe pas !"
        #
        if self.nb_lignes == 1:
            return self.coefs[0][0].simplifie()
        elif self.nb_lignes == 2:
            return Somme( [Produit([self.coefs[0][0], self.coefs[1][1]]).simplifie(), Oppose(Produit([self.coefs[0][1], self.coefs[1][0]])).simplifie() ]).simplifie()
        else:
            t: tuple[Objet, 'Matrice'] = self.pivot_de_gauss_determinant()
            coef_det: Objet = t[0]
            m_triangularisee: 'Matrice' = t[1]
            #
            p: list[Objet] = [coef_det]
            for i in range(self.nb_lignes):
                p.append( m_triangularisee.coefficient(i, i) )
            #
            return Produit(p).simplifie()


# Class Ensemble

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


class IntersectionEnsembles(Ensemble):
    def __init__(self, liste_ensembles: list[Ensemble]) -> None:
        super().__init__(nom=None)
        #
        self.liste_ensembles = liste_ensembles
    
    def __repr__(self) -> str:
        return "Intersection("+", ".join([o.__repr__() for o in self.objets])+")"

    def inclus_dans(self, ensemble: Ensemble) -> bool:
        return all([e.inclus_dans(ensemble) for e in self.liste_ensembles])
    

class DifferenceEnsembles(Ensemble):
    def __init__(self, e1: Ensemble, e2: Ensemble) -> None:
        super().__init__(nom=None)
        #
        self.e1 = e1
        self.e2 = e2

    def __repr__(self) -> str:
        return "("+self.e1.__repr__()+"\\"+self.e2.__repr__()+")"
    
    def inclus_dans(self, ensemble: Ensemble) -> bool:
        return self.e1.inclus_dans(ensemble) and IntersectionEnsembles([self.e2, ensemble]).simplifie() == EnsembleVide



"""  """

def matrice_identite(dim: int) -> Matrice:
    I_n: Matrice = Matrice(dim, dim)
    for i in range(dim):
        I_n.coefs[i][i] = Reel(1)
    #
    return I_n

def matrice_elementaire(nb_lignes: int, nb_colonnes: int, i: int, j: int) -> Matrice:
    assert 0 <= i <= nb_lignes and 0 <= j <= nb_colonnes, "Problèmes d'indices ! Out of bounds !"
    E_ij: Matrice = Matrice(nb_lignes, nb_colonnes)
    E_ij.coefs[i][j] = Reel(1)
    return E_ij



""" """



""" __ Variables globales utiles d'ensembles __ """

_R = Ensemble("_R")
_Q = SousEnsemble("_Q", _R)
_D = SousEnsemble("_D", _Q)
_Z = SousEnsemble("_Z", _D)
_N = SousEnsemble("_N", _Z)

_empty = EnsembleVide()

Nan = Objet("NaN")
Infinity = Objet("Infinity")

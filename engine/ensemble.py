from lib import *
from objet import *


class Ensemble():
    def __init__(self, nom: str):
        self.nom = nom

    def inclus_dans(self, ensemble):
        return ensemble == self

    def __repr__(self) -> str:
        return self.nom



class EnsembleVide(Ensemble):
    def __init__(self, nom:str):
        super().__init__(nom)

    def inclus_dans(self, ensemble: Ensemble):
        return True



class SousEnsemble(Ensemble):
    def __init__(self, nom: str, ensemble_parent: Ensemble):
        super().__init__(nom)
        #
        self.ensemble_parent = ensemble_parent
    
    def inclus_dans(self, ensemble: Ensemble):
        if ensemble == self:
            return True
        if ensemble == self.ensemble_parent:
            return True
        elif self.ensemble_parent.inclus_dans(ensemble):
            return True
        return False


class EnsembleObjets(Ensemble):
    def __init__(self, nom: str, objets: list[Objet]):
        super().__init__(nom)
        #
        self.objets = objets

    def inclus_dans(self, ensemble: Ensemble):
        return all([o.appartient_a(ensemble) for o in self.objets])




class UnionEnsembles(Ensemble):
    def __init__(self, nom: str, liste_ensembles: list[Ensemble]):
        super().__init__(nom)
        #
        self.liste_ensembles = liste_ensembles

    def inclus_dans(self, ensemble: Ensemble):
        return all([e.inclus_dans(ensemble) for e in self.liste_ensembles])













""" __ Variables globales utiles d'ensembles __ """

_R = Ensemble()
_Q = SousEnsemble(_R)
_D = SousEnsemble(_Q)
_Z = SousEnsemble(_D)
_N = SousEnsemble(_Z)

_empty = EnsembleVide()


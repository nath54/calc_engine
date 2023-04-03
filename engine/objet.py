from ensemble import Ensemble
from ensemble import *
from lib import *


class Objet():
    def __init__(self, nom: str, ensemble_parent: Ensemble=None):
        self.ensemble_parent = ensemble_parent
        self.nom = nom


    def appartient_a(self, ensemble: Ensemble) -> bool:
        if self.ensemble_parent == None:
            return False
        else:
            return self.ensemble_parent.inclus_dans(ensemble)
        
    def __repr__(self) -> str:
        return self.nom
        

class Variable():
    def __init__(self, nom: str, ensemble_parent: Ensemble=None):
        self.nom = nom
        self.ensemble_parent = ensemble_parent

    def __repr__(self) -> str:
        return self.nom





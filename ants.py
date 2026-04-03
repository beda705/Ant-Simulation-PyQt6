import threading
import random
import time
from PyQt6.QtCore import pyqtSignal, QObject


class Fourmi(threading.Thread, QObject):

    bouge = pyqtSignal(int)

    facteur_vitesse = 1.0

    def __init__(self, id_fourmi, depart_x, depart_y, liste_nourritures, couleur_nid, carte_pheromones,
                 barrieres, taille_cellule):
        QObject.__init__(self)
        threading.Thread.__init__(self, daemon=True)

        self.id_fourmi = id_fourmi

        self.x = float(depart_x)
        self.y = float(depart_y)

        self.depart_x = depart_x
        self.depart_y = depart_y

        self.liste_nourritures = liste_nourritures

        self.cible_nourriture = None

        self.couleur_nid = couleur_nid
        self.couleur_rgb = (couleur_nid.red(), couleur_nid.green(), couleur_nid.blue())

        self.etat_food = False

        self.event_stop = threading.Event()

        self.carte_pheromones = carte_pheromones

        self.compteur_pas = 0

        self.rayon_vision = 40

        self.barrieres     = barrieres       
        self.taille_cellule = taille_cellule  

        self.compteur_deception    = 0   
        self.seuil_deception       = 20  
        self.pas_exploration_forcee = 0  

    def run(self):
        while not self.event_stop.is_set():
            self.compteur_pas += 1

            if not self.etat_food:
                self._chercher_nourriture()
            else:
                self._retourner_au_nid()

            self.bouge.emit(self.id_fourmi)
            time.sleep(0.05 / Fourmi.facteur_vitesse)

    def _chercher_nourriture(self):
        if self.pas_exploration_forcee > 0:
            self.pas_exploration_forcee -= 1
            dx = random.choice([-2, -1, 0, 1, 2])
            dy = random.choice([-2, -1, 0, 1, 2])
            if not self._est_barriere(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
            return

        nourriture_visible = self._detecter_nourriture_proche()

        if nourriture_visible is not None:
            self.compteur_deception = 0

            self._se_deplacer_vers(nourriture_visible[0], nourriture_visible[1], vitesse=2.5)

            dist = ((self.x - nourriture_visible[0])**2 +
                    (self.y - nourriture_visible[1])**2) ** 0.5
            if dist < 15:
                if nourriture_visible in self.liste_nourritures:
                    self.cible_nourriture = nourriture_visible
                    self.etat_food = True
                else:
                    self._gerer_deception()

            return

        direction = self.carte_pheromones.meilleure_direction(
            self.x, self.y, self.couleur_rgb
        )

        if direction is not None and random.random() < 0.75:
            dx, dy = direction
            self.x += dx * 2.0   
            self.y += dy * 2.0

            self.compteur_deception += 1
            if self.compteur_deception >= self.seuil_deception:
                self._gerer_deception()
            return

        self.compteur_deception = 0
        dx = random.choice([-2, -1, 0, 1, 2])
        dy = random.choice([-2, -1, 0, 1, 2])
        if not self._est_barriere(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def _gerer_deception(self):
        self.compteur_deception = 0
        self.pas_exploration_forcee = 40
        self.carte_pheromones.affaiblir_zone(
            int(self.x), int(self.y), rayon=30, facteur=0.2
        )

    def _detecter_nourriture_proche(self):
        for nourriture in self.liste_nourritures:
            dist = ((self.x - nourriture[0])**2 +
                    (self.y - nourriture[1])**2) ** 0.5
            if dist < self.rayon_vision:
                return nourriture   
        return None

    def _est_barriere(self, x, y):
        cellule = (int(x) // self.taille_cellule, int(y) // self.taille_cellule)
        return cellule in self.barrieres

    def _se_deplacer_vers(self, cible_x, cible_y, vitesse):
        dx = cible_x - self.x
        dy = cible_y - self.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance == 0:
            return

        pas_x = (dx / distance) * vitesse
        pas_y = (dy / distance) * vitesse

        nx = self.x + pas_x
        ny = self.y + pas_y

        if not self._est_barriere(nx, ny):
            self.x, self.y = nx, ny
        elif not self._est_barriere(nx, self.y):
            self.x = nx
        elif not self._est_barriere(self.x, ny):
            self.y = ny

    def _retourner_au_nid(self):
        if self.compteur_pas % 4 == 0:
            self.carte_pheromones.deposer_pheromone(
                int(self.x), int(self.y), self.couleur_rgb, intensite=1.0
            )

        self._se_deplacer_vers(self.depart_x, self.depart_y, vitesse=1.5)

        dist_nid = ((self.x - self.depart_x)**2 + (self.y - self.depart_y)**2) ** 0.5
        if dist_nid < 3:
            self.etat_food = False
            self.x = float(self.depart_x)
            self.y = float(self.depart_y)
            self.cible_nourriture = None

    def stop(self):
        self.event_stop.set()
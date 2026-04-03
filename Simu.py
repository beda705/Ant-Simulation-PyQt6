from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMainWindow, QSlider, QLabel
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QTimer
from ants import Fourmi
from map import SimulationCanvas, COULEURS_NIDS
from pheromones import CartePheromones

QUANTITE_NOURRITURE = 25
NB_FOURMIS_PAR_NID = 50
TAILLE_CELLULE = 6

class Simu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulation de Fourmilière")

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        mise_en_page = QVBoxLayout(widget_central)
        mise_en_page.setContentsMargins(0, 0, 0, 0)
        mise_en_page.setSpacing(0)

        self.mode_configuration = True
        self.simulation_lancee = False
        self.mode_placement = None
        self.en_pause = False

        self.carte_pheromones = CartePheromones()

        self.timer_evaporation = QTimer()
        self.timer_evaporation.setInterval(100)
        self.timer_evaporation.timeout.connect(self._evaporer_pheromones)

        conteneur_boutons = QWidget()
        conteneur_boutons.setStyleSheet("background-color: #2a2a2a; padding: 10px;")
        disposition_boutons = QHBoxLayout(conteneur_boutons)

        self.btn_nid = QPushButton("Ajouter Nid")
        self.btn_nid.setFixedSize(120, 35)
        self.btn_nid.clicked.connect(self.activer_placement_nid)
        self.btn_nid.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")

        self.btn_nourriture = QPushButton("Ajouter Nourriture")
        self.btn_nourriture.setFixedSize(150, 35)
        self.btn_nourriture.clicked.connect(self.activer_placement_nourriture)
        self.btn_nourriture.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")

        self.btn_principal = QPushButton("Lancer Simulation")
        self.btn_principal.setFixedSize(160, 35)
        self.btn_principal.clicked.connect(self.gerer_bouton_principal)
        self.btn_principal.setEnabled(False)
        self.btn_principal.setStyleSheet("background-color: #555; color: gray; border-radius: 5px;")

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFixedSize(100, 35)
        self.btn_reset.clicked.connect(self.tout_reinitialiser)
        self.btn_reset.setStyleSheet("background-color: #d9534f; color: white; border-radius: 5px;")

        self.btn_crayon = QPushButton("✏ Crayon")
        self.btn_crayon.setFixedSize(100, 35)
        self.btn_crayon.clicked.connect(self.activer_crayon)
        self.btn_crayon.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")

        disposition_boutons.addWidget(self.btn_nid)
        disposition_boutons.addWidget(self.btn_nourriture)
        disposition_boutons.addWidget(self.btn_crayon)
        disposition_boutons.addWidget(self.btn_principal)
        disposition_boutons.addWidget(self.btn_reset)
        disposition_boutons.addStretch()

        self.lbl_vitesse = QLabel("Vitesse : 1.0x")
        self.lbl_vitesse.setStyleSheet("color: white; min-width: 90px;")

        self.slider_vitesse = QSlider(Qt.Orientation.Horizontal)
        self.slider_vitesse.setMinimum(10)
        self.slider_vitesse.setMaximum(25)
        self.slider_vitesse.setValue(10)
        self.slider_vitesse.setTickInterval(5)
        self.slider_vitesse.setFixedWidth(120)
        self.slider_vitesse.setStyleSheet("color: white;")
        self.slider_vitesse.valueChanged.connect(self._changer_vitesse)

        disposition_boutons.addWidget(self.lbl_vitesse)
        disposition_boutons.addWidget(self.slider_vitesse)

        self.canvas = SimulationCanvas(self)
        mise_en_page.addWidget(conteneur_boutons)
        mise_en_page.addWidget(self.canvas)

        self.positions_nids = []
        self.couleurs_nids = []
        self.positions_nourriture = []
        self.quantites_nourriture = {}
        self.fourmis = []
        self.fourmis_en_pause = []
        self.barrieres = set()

    def activer_placement_nid(self):
        self.mode_placement = 'nid'
        self.btn_nid.setStyleSheet("background-color: #ff3232; color: white; border-radius: 5px; font-weight: bold;")
        self.btn_nourriture.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")
        self.btn_crayon.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")

    def activer_placement_nourriture(self):
        self.mode_placement = 'nourriture'
        self.btn_nourriture.setStyleSheet("background-color: #00cc00; color: white; border-radius: 5px; font-weight: bold;")
        self.btn_nid.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")
        self.btn_crayon.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")

    def activer_crayon(self):
        self.mode_placement = 'crayon'
        self.btn_crayon.setStyleSheet("background-color: #888; color: white; border-radius: 5px; font-weight: bold;")
        self.btn_nid.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")
        self.btn_nourriture.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")

    def gerer_clic_canvas(self, x, y):
        if self.mode_placement == 'crayon':
            self._peindre_barriere(x, y)
            return

        if not self.mode_configuration:
            return

        if self.mode_placement == 'nid':
            cellule = (x // TAILLE_CELLULE, y // TAILLE_CELLULE)
            if cellule not in self.barrieres:
                self.positions_nids.append([x, y])
                index_couleur = len(self.couleurs_nids) % len(COULEURS_NIDS)
                self.couleurs_nids.append(COULEURS_NIDS[index_couleur])

        elif self.mode_placement == 'nourriture':
            cellule = (x // TAILLE_CELLULE, y // TAILLE_CELLULE)
            if cellule not in self.barrieres:
                self.positions_nourriture.append([x, y])
                self.quantites_nourriture[(x, y)] = QUANTITE_NOURRITURE

        if self.positions_nids and self.positions_nourriture:
            self.btn_principal.setEnabled(True)
            self.btn_principal.setStyleSheet("background-color: #5cb85c; color: white; border-radius: 5px;")

        self.canvas.update()

    def _peindre_barriere(self, x, y):
        cellule = (x // TAILLE_CELLULE, y // TAILLE_CELLULE)
        self.barrieres.add(cellule)
        self.canvas.update()

    def gerer_souris_mouvement(self, x, y):
        if self.mode_placement == 'crayon':
            self._peindre_barriere(x, y)

    def gerer_bouton_principal(self):
        if not self.simulation_lancee:
            self._lancer_simulation()
        else:
            self._basculer_pause()

    def _lancer_simulation(self):
        id_fourmi = 0
        for i, pos_nid in enumerate(self.positions_nids):
            for _ in range(NB_FOURMIS_PAR_NID):
                fourmi = Fourmi(
                    id_fourmi,
                    pos_nid[0], pos_nid[1],
                    self.positions_nourriture,
                    self.couleurs_nids[i],
                    self.carte_pheromones,
                    self.barrieres,
                    TAILLE_CELLULE
                )
                fourmi.bouge.connect(self._quand_fourmi_bouge)
                self.fourmis.append(fourmi)
                fourmi.start()
                id_fourmi += 1

        self.simulation_lancee = True
        self.mode_configuration = False
        self.btn_nid.setEnabled(False)
        self.btn_nourriture.setEnabled(False)
        self.btn_principal.setText("Pause")
        self.btn_principal.setStyleSheet("background-color: #f0ad4e; color: white; border-radius: 5px;")
        self.timer_evaporation.start()

    def _basculer_pause(self):
        if not self.en_pause:
            for f in self.fourmis:
                f.stop()
            for f in self.fourmis:
                f.join()
            self.fourmis_en_pause = self.fourmis[:]
            self.fourmis = []
            self.en_pause = True
            self.timer_evaporation.stop()
            self.btn_principal.setText("▶ Reprendre")
            self.btn_principal.setStyleSheet("background-color: #5cb85c; color: white; border-radius: 5px;")
        else:
            nouvelles_fourmis = []
            for ancienne_fourmi in self.fourmis_en_pause:
                f = Fourmi(
                    ancienne_fourmi.id_fourmi,
                    ancienne_fourmi.depart_x, ancienne_fourmi.depart_y,
                    self.positions_nourriture,
                    ancienne_fourmi.couleur_nid,
                    self.carte_pheromones,
                    self.barrieres,
                    TAILLE_CELLULE
                )
                f.x = ancienne_fourmi.x
                f.y = ancienne_fourmi.y
                f.etat_food = ancienne_fourmi.etat_food
                f.cible_nourriture = ancienne_fourmi.cible_nourriture
                f.bouge.connect(self._quand_fourmi_bouge)
                nouvelles_fourmis.append(f)
                f.start()

            self.fourmis = nouvelles_fourmis
            self.fourmis_en_pause = []
            self.en_pause = False
            self.timer_evaporation.start()
            self.btn_principal.setText("Pause")
            self.btn_principal.setStyleSheet("background-color: #f0ad4e; color: white; border-radius: 5px;")

    def _changer_vitesse(self, valeur_slider):
        facteur = valeur_slider / 10.0
        Fourmi.facteur_vitesse = facteur
        self.lbl_vitesse.setText(f"Vitesse : {facteur:.1f}x")

    def _evaporer_pheromones(self):
        self.carte_pheromones.evaporer()

    def _quand_fourmi_bouge(self, id_fourmi):
        self.canvas.update()

    def _verifier_collecte_nourriture(self):
        toutes_fourmis = self.fourmis if not self.en_pause else self.fourmis_en_pause
        sources_epuisees = []

        for f in toutes_fourmis:
            if f.etat_food and f.cible_nourriture:
                cle = (f.cible_nourriture[0], f.cible_nourriture[1])
                if cle in self.quantites_nourriture and not getattr(f, '_deja_compte', False):
                    self.quantites_nourriture[cle] -= 1
                    f._deja_compte = True
                    if self.quantites_nourriture[cle] <= 0:
                        sources_epuisees.append(cle)
            else:
                f._deja_compte = False

        for cle in sources_epuisees:
            self.quantites_nourriture.pop(cle, None)
            self.positions_nourriture[:] = [
                pos for pos in self.positions_nourriture
                if (pos[0], pos[1]) != cle
            ]

    def tout_reinitialiser(self):
        self.timer_evaporation.stop()
        for f in self.fourmis + self.fourmis_en_pause:
            f.stop()
        for f in self.fourmis:
            f.join()

        self.carte_pheromones = CartePheromones()
        self.mode_configuration = True
        self.simulation_lancee = False
        self.en_pause = False
        self.mode_placement = None
        self.positions_nids = []
        self.couleurs_nids = []
        self.positions_nourriture = []
        self.quantites_nourriture = {}
        self.fourmis = []
        self.fourmis_en_pause = []
        self.barrieres.clear()

        self.btn_nid.setEnabled(True)
        self.btn_nid.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")
        self.btn_nourriture.setEnabled(True)
        self.btn_nourriture.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")
        self.btn_crayon.setStyleSheet("background-color: #555; color: white; border-radius: 5px;")
        self.btn_principal.setText("Lancer Simulation")
        self.btn_principal.setEnabled(False)
        self.btn_principal.setStyleSheet("background-color: #555; color: gray; border-radius: 5px;")
        self.slider_vitesse.setValue(10)
        self.canvas.update()

    def paint_canvas(self, canvas):
        self._verifier_collecte_nourriture()
        peintre = QPainter(canvas)
        #couleur de la map
        peintre.fillRect(canvas.rect(), QColor(180, 160, 100))
        

        peintre.setBrush(QColor(140, 140, 140))
        peintre.setPen(Qt.PenStyle.NoPen)
        for (col, ligne) in self.barrieres:
            peintre.drawRect(
                col * TAILLE_CELLULE,
                ligne * TAILLE_CELLULE,
                TAILLE_CELLULE,
                TAILLE_CELLULE
            )

        for p in self.carte_pheromones.obtenir_toutes():
            r, g, b = p.couleur_rgb
            peintre.setOpacity(p.intensite * 0.6)
            peintre.setBrush(QColor(r, g, b))
            peintre.setPen(Qt.PenStyle.NoPen)
            peintre.drawEllipse(int(p.x) - 3, int(p.y) - 3, 6, 6)

        peintre.setOpacity(1.0)

        for pos in self.positions_nourriture:
            peintre.setBrush(QColor(0, 200, 50))
            peintre.setPen(Qt.PenStyle.NoPen)
            peintre.drawEllipse(pos[0] - 10, pos[1] - 10, 20, 20)
            quantite = self.quantites_nourriture.get((pos[0], pos[1]), 0)
            peintre.setPen(QColor(255, 255, 255))
            peintre.drawText(pos[0] - 10, pos[1] - 14, 20, 12,
                             Qt.AlignmentFlag.AlignCenter, str(quantite))

        for i, pos in enumerate(self.positions_nids):
            peintre.setBrush(self.couleurs_nids[i])
            peintre.setPen(Qt.PenStyle.NoPen)
            peintre.drawEllipse(pos[0] - 10, pos[1] - 10, 20, 20)

        toutes_fourmis = self.fourmis if not self.en_pause else self.fourmis_en_pause
        for f in toutes_fourmis:
            couleur = f.couleur_nid.lighter(170) if f.etat_food else f.couleur_nid
            peintre.setPen(Qt.PenStyle.NoPen)
            peintre.setBrush(couleur)
            peintre.drawRect(int(f.x), int(f.y), 4, 4)

    def closeEvent(self, event):
        self.timer_evaporation.stop()
        for f in self.fourmis + self.fourmis_en_pause:
            f.stop()
        for f in self.fourmis:
            f.join()
        event.accept()
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QColor


# Taille de la fenêtre de simulation (largeur, hauteur) en pixels
TAILLE_MAP = [600, 600]

# Liste des couleurs disponibles pour les nids (une couleur par nid)
COULEURS_NIDS = [
    QColor(255,  50,  50),   # rouge
    QColor( 50, 150, 255),   # bleu
    QColor(255, 200,  50),   # jaune
    QColor(150,  50, 255),   # violet
    QColor( 50, 255, 150),   # vert menthe
    QColor(255, 100, 150),   # rose
    QColor(100, 255, 255),   # cyan
    QColor(255, 150,  50),   # orange
]


class SimulationCanvas(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(TAILLE_MAP[0], TAILLE_MAP[1])
        self.fenetre_principale = parent   # référence à l'objet Simu

    def mousePressEvent(self, event):
        """Transmet le clic à la fenêtre principale."""
        if self.fenetre_principale:
            self.fenetre_principale.gerer_clic_canvas(
                int(event.position().x()),
                int(event.position().y())
            )

    def mouseMoveEvent(self, event):

        if self.fenetre_principale:
            self.fenetre_principale.gerer_souris_mouvement(
                int(event.position().x()),
                int(event.position().y())
            )

    def paintEvent(self, event):
        if self.fenetre_principale:
            self.fenetre_principale.paint_canvas(self)
import sys
from PyQt6.QtWidgets import QApplication
from Simu import Simu


if __name__ == "__main__":
    app = QApplication(sys.argv)  
    fenetre = Simu()
    fenetre.show()
    sys.exit(app.exec())         
import threading

class Pheromone:
    def __init__(self, x, y, couleur_rgb, intensite=1.0):
        self.x = x
        self.y = y
        self.couleur_rgb = couleur_rgb  
        self.intensite = intensite      


class CartePheromones:
    def __init__(self):
        self.pheromones = []           
        self.verrou = threading.Lock() 

    def deposer_pheromone(self, x, y, couleur_rgb, intensite):
        with self.verrou:
            for p in self.pheromones:
                if p.couleur_rgb == couleur_rgb and abs(p.x - x) < 5 and abs(p.y - y) < 5:
                    p.intensite = min(1.0, p.intensite + 0.2)
                    return
            self.pheromones.append(Pheromone(x, y, couleur_rgb, intensite))

    def evaporer(self):
        with self.verrou:
            for p in self.pheromones:
                p.intensite -= 0.005  

            self.pheromones = [p for p in self.pheromones if p.intensite > 0.05]

    def meilleure_direction(self, x, y, couleur_rgb):
        directions_possibles = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),           (1,  0),
            (-1,  1), (0,  1), (1,  1),
        ]

        meilleur_score = 0.0
        meilleure_dir = None
        taille_pas = 15

        with self.verrou:
            for (dx, dy) in directions_possibles:
                case_x = x + dx * taille_pas
                case_y = y + dy * taille_pas

                score = 0.0
                for p in self.pheromones:
                    if p.couleur_rgb != couleur_rgb:
                        continue  
                    distance = ((p.x - case_x)**2 + (p.y - case_y)**2) ** 0.5
                    if distance < 20:   
                        score += p.intensite

                if score > meilleur_score:
                    meilleur_score = score
                    meilleure_dir = (dx, dy)

        return meilleure_dir  

    def affaiblir_zone(self, x, y, rayon, facteur):
        with self.verrou:
            for p in self.pheromones:
                distance = ((p.x - x)**2 + (p.y - y)**2) ** 0.5
                if distance < rayon:
                    p.intensite *= facteur  

    def obtenir_toutes(self):
        with self.verrou:
            return list(self.pheromones)
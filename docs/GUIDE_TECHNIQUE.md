# ✧ GUIDE TECHNIQUE & ARCHITECTURE ✧
## Bébé Snake 3D Kawaii

Ce document détaille l'architecture interne, le fonctionnement du moteur de raycasting 3D rétro, la génération procédurale des sons et des textures, ainsi que les règles physiques du jeu.

---

## 📐 1. Moteur de Rendu Raycasting (DDA 3D)

Le fichier `src/snake/kawaii_raycaster.py` implémente un raycaster basé sur l'algorithme **DDA (Digital Differential Analyzer)** popularisé par *Wolfenstein 3D* (1992), entièrement réadapté avec une esthétique pastel et des calculs vectoriels précis.

### Spécifications du rendu
- **Résolution interne** : $320 \times 170$ pixels (haute performance, 60 FPS constants).
- **Mise à l'échelle (Upscaling)** : Facteur $\times 3$ vers un viewport de $960 \times 510$ pixels, surmontant une barre de statut de $90$ pixels (résolution totale de la fenêtre : $960 \times 600$).
- **Champ de vision (FOV)** : $60^\circ$ ($\pi / 3$ radians).
- **Nombre de rayons** : 320 (un rayon par colonne de pixels de la résolution interne).
- **Correction du Fish-Eye** : Pour éviter l'effet de distorsion en œil de poisson sur les parois planes, la distance brute $d_{\text{raw}}$ est corrigée par le cosinus de l'angle relatif du rayon par rapport à la caméra :
  $$d_{\text{perp}} = d_{\text{raw}} \cdot \cos(\alpha_{\text{ray}} - \alpha_{\text{cam}})$$

### Ciel Panoramique & Sol en Damier
- **Ciel avec nuages** : Texture panoramique à $360^\circ$ ($1920$ pixels de large) avec défilement fluide selon l'angle de regard du joueur.
- **Rendu du sol et du plafond** : Projection de plan horizontal ligne par ligne calculée analytiquement, appliquant une alternance de damier pastel selon la parité des coordonnées cartésiennes de la cellule `(int(x) + int(y)) % 2`.
- **Brume vaporeuse (Pastel Fog)** : Interpolation linéaire (LERP) douce entre la couleur de texture et la teinte guimauve `(248, 238, 246)` en fonction de la distance quadratique.

### Sprites 3D & Billboarding
- **Objets projetés** : Pomme kawaii flottante, corps du serpent (anneaux menthe), tête du serpent (en Chase Cam) et bonus tétine apaisante.
- **Tri en profondeur (Depth Sort)** : Les sprites sont triés par distance décroissante avant affichage pour respecter l'ordre z-buffer et garantir que les objets proches masquent correctement les objets éloignés.

---

## 🐍 2. Physique & Mouvement du Serpent

Le fichier `src/snake/kawaii_game.py` gère l'état logique de la partie indépendamment du framerate.

### Corridor Snapping (Alignement automatique)
Dans les jeux de raycasting en vue subjective, virer à 90° au milieu d'une case peut coincer le joueur contre un angle de mur. `KawaiiSnakeGame._snap_to_grid_corridor()` recentre instantanément la coordonnée orthogonale sur l'axe médian de la case ($y = \lfloor y \rfloor + 0.5$ ou $x = \lfloor x \rfloor + 0.5$). Le serpent est donc toujours parfaitement aligné au centre du couloir.

### Gestion du corps & ondulation
- L'historique des positions est mémorisé sous forme d'un tableau circulaire de points espacés de $0.08$ unité.
- Chaque segment du corps est indexé à intervalle régulier sur cet historique, produisant une ondulation naturelle et continue quelle que soit la vitesse de déplacement.

### Règles de vitesse & Bonus Tétine
- **Vitesse initiale** : $3.8$ unités/seconde.
- **Incrément** : $+0.55$ unité/seconde tous les 5 points.
- **Vitesse max** : $12.0$ unités/seconde.
- **Bonus Tétine** :
  - Apparaît aléatoirement toutes les 18 à 32 secondes.
  - Reste active pendant $5.0$ secondes.
  - Ramassée, elle décrémente la vitesse de 1 cran sans impacter le niveau d'expérience du joueur (`speed_level`) ni la rotation des thèmes visuels (`theme_index`), et sans jamais descendre sous la vitesse plancher ($3.8$).

---

## 🎵 3. Synthèse Audio Procédurale (Chiptune)

Le fichier `src/snake/kawaii_audio.py` génère l'ensemble des sons du jeu sans charger le moindre fichier WAV ou MP3 sur le disque :

- Échantillonnage à **44 100 Hz** stéréo 16-bit.
- **Pomme mangée** : Synthèse d'arpèges ascendants sinusoïdaux avec enveloppe d'amplitude ADSR percussive (effet *nom-nom* rétro).
- **Gain de niveau** : Fanfare de 3 notes harmoniques majeures.
- **Bonus Tétine** :
  - *Apparition* : Glissando scintillant simulant une étoile magique.
  - *Collecte (Apaisement)* : Accord majeur doux et relaxant avec vibrato.
- **Tick d'urgence (Contre-la-montre)** : Onde carrée brève et incisive sous 5 secondes restantes.
- **Choc / Game Over** : Bruit blanc filtré passe-bas pour un son de choc tout doux.

---

## 💾 4. Persistance des Meilleurs Scores

Le fichier `leaderboard.json` est enregistré localement à la racine du projet :

```json
{
  "Classique": [
    {
      "score": 36,
      "mode": "Classique",
      "level": 8,
      "player": "SUS",
      "date": "06/09 18:50"
    }
  ],
  "Chrono": [
    {
      "score": 25,
      "mode": "Chrono",
      "level": 6,
      "player": "LEO",
      "date": "06/09 15:24"
    }
  ]
}
```

- Conserve automatiquement le **Top 5** pour chaque mode de jeu.
- Enregistre le nom arcade sur 3 lettres entré par le joueur en fin de partie.
- Gère automatiquement la migration ascendante des versions antérieures de fichiers de score.

---

## 🧪 5. Suite de Tests Unitaires

Exécutée via :
```bash
uv run pytest -v
```

Les 34 tests couvrent :
- Rendu vectoriel du raycaster et projection sans déformation.
- Non-collision lors des virages en couloir ouvert.
- Comportement des modes Classique et Contre-la-montre (décompte et ajouts de temps).
- Gestion du bonus tétine (apparition, durée de vie, non-dépassement de la vitesse plancher, préservation du thème et du niveau).
- Saisie des initiales, validation et navigation dans le menu de fin de partie.
- Modal de pause (reprise via Échap/P ou retour vers le menu titre).

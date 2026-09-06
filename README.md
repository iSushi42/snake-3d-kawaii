# ✧ BÉBÉ SNAKE 3D KAWAII ✧

Jeu de Snake 3D complet en Python avec moteur de raycasting temps réel, univers kawaii pastel, sons chiptune procéduraux et sol en damier, propulsé par `pygame-ce` et géré par `uv`.

Lancement direct avec :
```bash
uv run kawaii-snake
```

---

## 🌸 Fonctionnalités Clés


- **Moteur Raycasting Rétro 3D dans un univers Kawaii & Bébé Pastel** :
  - Murs en bonbons guimauve rose pastel à petits pois blancs et cubes de jeu en menthe douce avec petits nuages.
  - Ciel bébé bleu/lavande doux et sol crème vanille chaud.
  - Brume de distance vaporeuse façon marshmallow pastel (adieu la noirceur austère !).
  - Pomme kawaii vivante : adorable bébé fraise/pomme avec grands yeux brillants anime, joues roses poudrées (*blush*) et doux sourire, brillant de mille feux dans l'arène.
  - Anneaux du serpent en bonbons menthe pastel avec reflets étincelants.
- **Deux Modes de Caméra (Touche `V`)** :
  - **1ère Personne** : vue immersive avec le petit museau tout doux de bébé serpent et sa petite langue rose en bas de l'écran.
  - **3ème Personne (Chase Cam)** : vue au-dessus de la tête pour observer tous les anneaux pastel onduler dans le labyrinthe.
- **Barre de Statut Kawaii & Bébé** :
  - Cartes et badges arrondis blanc et pastel rose : **POMMES 🍓**, **VITESSE ✨**, **RECORD 🏆**.
  - **Visage animé de Bébé Serpent** :
    - Yeux ronds innocents qui regardent autour.
    - Énorme sourire joyeux `( > ‿ < )` quand vous mangez une pomme.
    - Petit visage qui pleure de mignonnerie `( T ﹏ T )` avec petit pansement quand il se cogne contre un mur.
  - Écran de fin tout doux : *"Oups ! Bébé s'est cogné 💤"*.
- **Boussole Kawaii (Haut de l'écran)** :
  - Affiche en permanence une flèche directionnelle pastel indiquant la direction de la pomme par rapport à votre regard.
  - S'illumine en vert tendre avec *"🍓 Droit devant !"* et affiche la distance exacte en mètres/cases.
- **Minimap / Radar rétractable (Touche `M`)** :
  - Désactivée par défaut pour garder un écran épuré et immersif.
  - Appuyez sur **M** pour l'afficher ou la masquer à tout moment.
- **Contrôles ZQSD** :
  - **Q** : Virer à gauche (90°)
  - **D** : Virer à droite (90°)
  - **Z** : Accélérer / Boost tout doux
  - **M** : Afficher / Masquer la minimap
  - **V** : Basculer entre vue 1ère personne et 3ème personne
  - **P** ou **Espace** : Pause dodo
  - **R** ou **Espace** : Rejouer
  - **Échap** : Quitter
- **Lancement** :
  ```bash
  uv run kawaii-snake
  ```

---

## 🧪 Tests Automatisés

L'ensemble des mécaniques sont couvertes par 24 tests unitaires `pytest` :

```bash
uv run pytest
```

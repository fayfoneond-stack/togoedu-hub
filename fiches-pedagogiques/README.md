# Fiches pédagogiques (LaTeX / Overleaf)

## `fiche-1ereD-systemes-lineaires.tex`

Fiche de préparation de leçon — **Mathématiques, classe de 1re D**.

| | |
|---|---|
| **Thème** | Calculs algébriques |
| **Leçon** | Systèmes linéaires dans $\mathbb{R}^2$ et dans $\mathbb{R}^3$ |
| **Année scolaire** | 2026 – 2027 |
| **Nombre de séances** | 2 (55 min × 2 = 1 h 50) |

### Compilation

```bash
pdflatex fiche-1ereD-systemes-lineaires.tex     # 2 passages recommandés
```

ou dépôt direct du `.tex` sur **Overleaf** (aucun fichier annexe nécessaire).
Dépendances (présentes dans toute distribution TeX Live / Overleaf) :
`babel`, `geometry`, `xcolor` + `table`, `array`, `tabularx`, `enumitem`,
`amsmath` / `amssymb`, `tikz` (+ `arrows.meta`, `babel`), `tcolorbox` (`most`).

### Contenu de la fiche

1. **En-tête** : identification (classe, thème, leçon, année, durée, prérequis,
   support), code couleur des étapes.
2. **Séance 1 ($\mathbb{R}^2$, 55 min)** : tableau *Structure du cours |
   Capacités et contenus | Consignes | Évaluations*, situation-problème
   (cahiers / stylos en F CFA), **trace écrite** (définition, substitution,
   combinaison linéaire, Cramer, tableau de discussion selon $\Delta$,
   interprétation graphique + 2 figures TikZ), exercices d'application.
3. **Séance 2 ($\mathbb{R}^3$, 55 min)** : même structure, avec la **méthode du
   pivot de Gauss**, un exemple échelonné résolu, l'interprétation
   géométrique (trois plans, figure TikZ 3D) et les applications.
4. **Évaluation sommative** (/20) + grille de critères.
5. **Corrigés** détaillés (séance 1, séance 2, évaluation).

### Code couleur des étapes

| Étape | Couleur |
|---|---|
| Mise en situation | violet |
| Découverte / Investigation | orange |
| **Trace écrite** | bleu |
| **Application** | vert |
| Évaluation | rouge |

### À aligner sur le document de référence

Les **consignes** (colonne 3) et les **évaluations** (colonne 4) ont été rédigées
au format standard d'une fiche APC. Dès réception du tableau du programme
(*VF MATHS 1re D*), remplacer ces formulations par le libellé exact de
l'établissement : elles sont regroupées dans les deux tableaux « Structure du
cours », au début de chaque séance.

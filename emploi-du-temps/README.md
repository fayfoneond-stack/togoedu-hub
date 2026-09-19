# Emploi du temps — LaTeX + PDF

Emploi du temps hebdomadaire d'une classe de **3ᵉ B** (collège, Lomé — Togo),
saisi en **LaTeX** et livré avec un **PDF d'aperçu**.

```
emploi-du-temps/
├── edt-data.json         ← source unique (établissement, jours, créneaux, matières, grille)
├── generer_edt.py        ← génère le .tex et le .pdf depuis edt-data.json
├── emploi-du-temps.tex   ← le code LaTeX (document livrable)
└── emploi-du-temps.pdf   ← aperçu PDF couleur, 1 page A4 paysage
```

## Compilation du LaTeX

Le `.tex` ne dépend que de paquets courants (`xcolor` + `table`, `array`,
`babel`, `geometry`), donc il compile partout :

```bash
pdflatex emploi-du-temps.tex        # en local (TeX Live / MiKTeX)
# ou : déposer emploi-du-temps.tex sur Overleaf et compiler
```

## Modifier l'emploi du temps

Tout se joue dans `edt-data.json` — établissement, jours, créneaux, matières
(couleur, enseignant, salle) et grille `jour → créneau → matière`. Puis :

```bash
pip install reportlab        # uniquement pour le PDF d'aperçu
python3 generer_edt.py
```

Le script réécrit `emploi-du-temps.tex` **et** `emploi-du-temps.pdf`, et affiche
le volume horaire par matière (34 séances de 50 min, soit 28 h 20 par semaine).

## À propos du PDF fourni

`emploi-du-temps.pdf` est produit par `reportlab` : l'environnement de travail
n'a pas de distribution TeX installable, impossible d'y lancer `pdflatex`.
C'est un aperçu fidèle — mêmes données, mêmes couleurs, même grille — du
document que sortira `pdflatex` sur le `.tex`.

Le `.tex` a été validé structurellement (accolades et environnements équilibrés,
analyse complète sans erreur, rendu de contrôle sur un moteur LaTeX WebAssembly).

## Détails de la maquette

* A4 **paysage**, marges 1,2 cm, bandeau d'en-tête bleu nuit.
* Grille : `Lundi → Samedi`, 6 séances de 50 min de 07h30 à 12h50,
  récréation 09h10 – 09h30, samedi raccourci (fin à 11h10).
* Une couleur pastel par matière + légende avec le volume horaire hebdomadaire.
* Chaque case : **matière**, enseignant, salle.
* Pied de page : volume horaire, signatures (professeur principal, chef
  d'établissement, CPE).

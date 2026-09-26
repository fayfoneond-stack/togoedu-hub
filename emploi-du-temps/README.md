# Emploi du temps — Famille TAYELEKA (LaTeX + PDF)

Emploi du temps hebdomadaire de la **Famille TAYELEKA** (Lomé — Togo),
saisi en **LaTeX** et livré avec un **PDF d'aperçu**.

```
emploi-du-temps/
├── edt-data.json         ← source unique (famille, jours, créneaux, grille, répétiteurs)
├── generer_edt.py        ← génère le .tex et le .pdf depuis edt-data.json
├── emploi-du-temps.tex   ← le code LaTeX (document livrable)
└── emploi-du-temps.pdf   ← aperçu PDF, 1 page A4 paysage
```

## Contenu du document

* **Bandeau** : « EMPLOI DU TEMPS — FAMILLE TAYELEKA », Lomé, Togo, 2026 – 2027.
* **Grille** : `Lundi → Samedi`, créneaux **7-8h, 8-9h, 9-10h … 16-17h, 17-19h**
  (11 lignes). Toutes les cases sont **vides** sauf :
  * **Mercredi 17-19h** → *Répétition de Math*
  * **Vendredi 17-19h** → *Math*
* **Légende** : Mathématiques / Créneau libre.
* **En bas de page** : tableau des **répétiteurs**
  (Nom et prénom | Matière | Jours et horaires) —
  **Mr KODJONE Kodjo**, Mathématiques, Mercredi 17-19h — Vendredi 17-19h,
  puis 2 lignes vides pour les prochains répétiteurs.

## Compilation du LaTeX

Le `.tex` ne dépend que de paquets courants (`xcolor` + `table`, `array`,
`babel`, `geometry`), donc il compile partout :

```bash
pdflatex emploi-du-temps.tex        # en local (TeX Live / MiKTeX)
# ou : déposer emploi-du-temps.tex sur Overleaf et compiler
```

## Modifier l'emploi du temps

Tout se joue dans `edt-data.json`, puis :

```bash
pip install reportlab        # uniquement pour le PDF d'aperçu
python3 generer_edt.py
```

Exemples de modifications fréquentes :

* **Ajouter un cours** : dans `grille`, sous le jour, ajouter l'id du créneau
  (`"11"` = 17-19h) → `{"matiere": "Mathématiques", "texte": "Répétition de Math"}`.
* **Ajouter un répétiteur** : une entrée de plus dans `repetiteurs`.
* **Ajouter une matière/couleur** : une entrée de plus dans `matieres`.
* **Changer les jours** (dimanche, etc.) : la liste `jours`.
* **Changer les horaires** : la liste `creneaux` (libre à toi d'y mettre
  `7h-8h`, `8h-9h`… si tu préfères cette écriture).

## À propos du PDF fourni

`emploi-du-temps.pdf` est produit par `reportlab` : l'environnement de travail
n'a pas de distribution TeX installable, impossible d'y lancer `pdflatex`.
C'est un aperçu fidèle — mêmes données, mêmes couleurs, même grille — du
document que sortira `pdflatex` sur le `.tex`.

Le `.tex` est validé structurellement à chaque génération (accolades et
environnements équilibrés, analyse complète sans erreur, rendu de contrôle
sur un moteur LaTeX WebAssembly).

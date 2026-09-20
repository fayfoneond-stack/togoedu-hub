#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Met un PDF au format paysage (A4 paysage par défaut).

Trois manières de faire, à choisir selon le résultat voulu :

  rotation    : la page est pivotée de 90°. Le format devient paysage, mais le
                contenu est présenté sur le côté (pratique pour un document
                déjà mis en page qu'on veut juste coucher).

  ajustement  : le contenu reste à l'endroit, il est redimensionné pour tenir
                dans la hauteur du paysage et centré (des marges apparaissent
                à gauche et à droite).

  2en1        : deux pages portrait sont posées côte à côte sur une même page
                paysage (pratique pour imprimer un portrait en paysage).

Usage :
    pip install pymupdf
    python3 pdf_paysage.py entree.pdf                      # rotation, défaut
    python3 pdf_paysage.py entree.pdf -m ajustement
    python3 pdf_paysage.py entree.pdf -m 2en1 -o sortie.pdf

Le fichier de sortie par défaut s'appelle entree-paysage.pdf, à côté de l'original.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# A4 paysage en points (1 pt = 1/72 pouce)
PAYSAGE = (842.0, 595.0)


def convertir(entree: Path, sortie: Path, mode: str) -> None:
    try:
        import pymupdf
    except ImportError:
        sys.exit("pymupdf n'est pas installé :  pip install pymupdf")

    source = pymupdf.open(entree)
    if source.page_count == 0:
        sys.exit(f"{entree} ne contient aucune page.")

    destination = pymupdf.open()

    if mode == "rotation":
        for page in source:
            page.set_rotation((page.rotation + 90) % 360)
        source.save(sortie)
        source.close()
        return

    largeur_cible, hauteur_cible = PAYSAGE

    if mode == "ajustement":
        for page in source:
            nouvelle = destination.new_page(width=largeur_cible, height=hauteur_cible)
            facteur = min(largeur_cible / page.rect.width, hauteur_cible / page.rect.height)
            largeur = page.rect.width * facteur
            hauteur = page.rect.height * facteur
            cadre = pymupdf.Rect(
                (largeur_cible - largeur) / 2,
                (hauteur_cible - hauteur) / 2,
                (largeur_cible + largeur) / 2,
                (hauteur_cible + hauteur) / 2,
            )
            nouvelle.show_pdf_page(cadre, source, page.number)

    elif mode == "2en1":
        for index in range(0, source.page_count, 2):
            nouvelle = destination.new_page(width=largeur_cible, height=hauteur_cible)
            for position, numero in enumerate((index, index + 1)):
                if numero >= source.page_count:
                    break
                page = source[numero]
                marge = 12
                demi = (largeur_cible - 3 * marge) / 2
                facteur = min(demi / page.rect.width, (hauteur_cible - 2 * marge) / page.rect.height)
                largeur = page.rect.width * facteur
                hauteur = page.rect.height * facteur
                x0 = marge + position * (demi + marge) + (demi - largeur) / 2
                cadre = pymupdf.Rect(x0, (hauteur_cible - hauteur) / 2,
                                     x0 + largeur, (hauteur_cible + hauteur) / 2)
                nouvelle.show_pdf_page(cadre, source, numero)

    destination.save(sortie, deflate=True)
    destination.close()
    source.close()


def main() -> None:
    parseur = argparse.ArgumentParser(description="Met un PDF au format paysage.")
    parseur.add_argument("entree", type=Path, help="fichier PDF d'entrée")
    parseur.add_argument("-m", "--mode", choices=("rotation", "ajustement", "2en1"),
                         default="rotation", help="méthode de conversion (défaut : rotation)")
    parseur.add_argument("-o", "--sortie", type=Path,
                         help="fichier de sortie (défaut : <entree>-paysage.pdf)")
    arguments = parseur.parse_args()

    if not arguments.entree.exists():
        sys.exit(f"Introuvable : {arguments.entree}")

    sortie = arguments.sortie or arguments.entree.with_name(f"{arguments.entree.stem}-paysage.pdf")
    convertir(arguments.entree, sortie, arguments.mode)

    import pymupdf  # déjà importé dans convertir, ici juste pour le contrôle
    with pymupdf.open(sortie) as doc:
        print(f"OK  {sortie}  —  {doc.page_count} page(s), "
              f"format {round(doc[0].rect.width)} x {round(doc[0].rect.height)} pt")


if __name__ == "__main__":
    main()

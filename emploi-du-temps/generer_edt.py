#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère l'emploi du temps de la Famille TAYELEKA depuis une source unique :
edt-data.json

Sorties :
  * emploi-du-temps.tex  -> code LaTeX (compile avec pdflatex / xelatex / Overleaf)
  * emploi-du-temps.pdf  -> aperçu PDF couleur (rendu par reportlab)

Usage :
    pip install reportlab        # uniquement pour le PDF d'aperçu
    python3 generer_edt.py       # écrit les deux fichiers à côté du script

Le PDF est généré par reportlab parce que l'environnement de travail n'a pas
de distribution TeX installable : c'est un aperçu fidèle (mêmes couleurs, même
grille, mêmes données) du document que produira `pdflatex emploi-du-temps.tex`.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "edt-data.json"
TEX_FILE = HERE / "emploi-du-temps.tex"
PDF_FILE = HERE / "emploi-du-temps.pdf"

# Réglages de mise en page (cm) — cohérents entre le .tex et le .pdf
HAUTEUR_LIGNE = 0.88      # hauteur d'une ligne de la grille
HAUTEUR_ENTETE = 0.75     # ligne « Horaire / Lundi / Mardi … »
LARGEUR_HORAIRE = 2.00    # colonne des horaires

PALETTE = {
    "entete": "#29405F",     # bandeau + ligne d'en-tête du tableau
    "horaire": "#EAEFF6",    # colonne des horaires
    "libre": "#FFFFFF",      # cases libres
    "grille": "#9AA5B4",     # filets du tableau
    "note": "#5B6675",       # texte des notes de bas de page
}


# --------------------------------------------------------------------------- #
# Utilitaires
# --------------------------------------------------------------------------- #

def nettoyer(donnees: dict) -> dict:
    """Ignore les clés documentaires (_comment) du JSON."""
    if isinstance(donnees, dict):
        return {k: nettoyer(v) for k, v in donnees.items() if not k.startswith("_")}
    return donnees


def slug(texte: str) -> str:
    """Nom de couleur LaTeX ASCII stable (Mathématiques -> Mathematiques)."""
    ascii_texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]", "", ascii_texte) or "couleur"


def hex_to_rgb(couleur: str) -> tuple[int, int, int]:
    couleur = couleur.lstrip("#")
    return tuple(int(couleur[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def echappement_tex(texte: str) -> str:
    """Échappe les caractères réservés de LaTeX."""
    for caractere, remplacement in (
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ):
        texte = texte.replace(caractere, remplacement)
    return texte


def echappement_html(texte: str) -> str:
    return texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def charger() -> dict:
    with DATA_FILE.open(encoding="utf-8") as handle:
        return nettoyer(json.load(handle))


# --------------------------------------------------------------------------- #
# 1. Le code LaTeX
# --------------------------------------------------------------------------- #

def construire_tex(donnees: dict) -> str:
    jours = donnees["jours"]
    creneaux = donnees["creneaux"]
    matieres = donnees["matieres"]
    grille = donnees["grille"]
    repetiteurs = donnees["repetiteurs"]

    L: list[str] = []
    a = L.append

    # --- préambule -------------------------------------------------------- #
    a("% =====================================================================")
    a(f"%  EMPLOI DU TEMPS — {donnees['famille'].upper()} — {donnees['annee']}")
    a("%")
    a("%  Compilation : pdflatex emploi-du-temps.tex  (ou Overleaf / XeLaTeX)")
    a("%  Fichier généré depuis edt-data.json — ne pas éditer à la main :")
    a("%  modifier edt-data.json puis relancer  python3 generer_edt.py")
    a("% =====================================================================")
    a("")
    a("\\documentclass[a4paper,landscape,10pt]{article}")
    a("")
    a("\\usepackage[T1]{fontenc}")
    a("\\usepackage[utf8]{inputenc}")
    a("\\usepackage[french]{babel}")
    a("\\usepackage[margin=1.2cm]{geometry}")
    a("\\usepackage[table]{xcolor}   % \\cellcolor / \\rowcolor")
    a("\\usepackage{array}           % colonnes p{} de largeur fixe")
    a("")

    # --- couleurs --------------------------------------------------------- #
    a("% ---------- Palette ----------")
    for nom, valeur in PALETTE.items():
        r, v, b = hex_to_rgb(valeur)
        a(f"\\definecolor{{{nom}}}{{RGB}}{{{r},{v},{b}}}")
    for matiere, infos in matieres.items():
        r, v, b = hex_to_rgb(infos["couleur"])
        a(f"\\definecolor{{c{slug(matiere)}}}{{RGB}}{{{r},{v},{b}}}   % {matiere}")
    a("")

    # --- commandes -------------------------------------------------------- #
    a("% ---------- Commandes ----------")
    a("% case occupée : \\cours{couleur}{texte}")
    a("\\newcommand{\\cours}[2]{%")
    a("  \\cellcolor{#1}%")
    a(f"  \\begin{{minipage}}[c][{HAUTEUR_LIGNE}cm][c]{{\\dimexpr\\linewidth-2\\tabcolsep\\relax}}%")
    a("    \\centering\\small\\textbf{#2}%")
    a("  \\end{minipage}}")
    a("")
    a("% case libre : même hauteur, aucun contenu")
    a("\\newcommand{\\libre}{%")
    a("  \\cellcolor{libre}%")
    a(f"  \\begin{{minipage}}[c][{HAUTEUR_LIGNE}cm][c]{{\\dimexpr\\linewidth-2\\tabcolsep\\relax}}%")
    a("  \\end{minipage}}")
    a("")
    a("% \\horaire{plage horaire}")
    a("\\newcommand{\\horaire}[1]{%")
    a("  \\cellcolor{horaire}%")
    a(f"  \\begin{{minipage}}[c][{HAUTEUR_LIGNE}cm][c]{{\\dimexpr\\linewidth-2\\tabcolsep\\relax}}%")
    a("    \\centering\\textbf{#1}%")
    a("  \\end{minipage}}")
    a("")
    a("% \\legende{couleur}{libellé}")
    a("\\newcommand{\\legende}[2]{%")
    a("  \\colorbox{#1}{\\rule[-1.5pt]{0pt}{10pt}\\hspace{1.1cm}}~{\\footnotesize #2}}")
    a("")
    a("\\setlength{\\tabcolsep}{3pt}")
    a("\\renewcommand{\\arraystretch}{1.0}")
    a("\\pagestyle{empty}")
    a("")

    # --- document --------------------------------------------------------- #
    a("\\begin{document}")
    a("")
    a("% ---------- Bandeau ----------")
    a("\\noindent\\colorbox{entete}{%")
    a("  \\parbox[c][1.40cm][c]{\\dimexpr\\linewidth-2\\fboxsep\\relax}{%")
    a("    \\centering\\color{white}%")
    a("    {\\Large\\textbf{" + echappement_tex(donnees["titre"]) + " — "
      + echappement_tex(donnees["famille"].upper()) + "}}\\\\[3pt]")
    a("    {\\normalsize " + echappement_tex(donnees["mention"]) + "}\\\\[3pt]")
    a("    {\\small " + echappement_tex(donnees["localite"])
      + " \\quad\\textbullet\\quad " + echappement_tex(donnees["annee"]) + "}")
    a("  }%")
    a("}")
    a("\\vspace{6pt}")
    a("")

    # --- grille ----------------------------------------------------------- #
    nb_jours = len(jours)
    largeur_jour = (25.4 - LARGEUR_HORAIRE) / nb_jours
    a("% ---------- Grille de la semaine ----------")
    a("\\noindent")
    a("\\begin{tabular}{|p{" + f"{LARGEUR_HORAIRE}cm" + "}|*{" + str(nb_jours)
      + "}{p{" + f"{largeur_jour:.2f}cm" + "}|}}")
    a("\\hline")

    entete = ["\\textcolor{white}{\\textbf{" + echappement_tex(j) + "}}" for j in jours]
    a("\\rowcolor{entete}\\cellcolor{entete}\\textcolor{white}{\\textbf{Horaire}} & "
      + " & ".join(entete) + " \\\\")
    a("\\hline")

    for creneau in creneaux:
        cellules = ["\\horaire{" + echappement_tex(creneau["libelle"]) + "}"]
        for jour in jours:
            case = grille.get(jour, {}).get(creneau["id"])
            if case:
                matiere = case["matiere"]
                cellules.append("\\cours{c" + slug(matiere) + "}{" + echappement_tex(case["texte"]) + "}")
            else:
                cellules.append("\\libre")
        a(" & ".join(cellules) + " \\\\")
        a("\\hline")

    a("\\end{tabular}")
    a("")

    # --- légende ---------------------------------------------------------- #
    a("\\vspace{5pt}")
    a("\\noindent\\textbf{Légende :}")
    a("\\vspace{3pt}")
    a("")
    a("\\noindent")
    legendes = ["\\legende{c" + slug(m) + "}{" + echappement_tex(m) + "}" for m in matieres]
    legendes.append("\\legende{libre}{Créneau libre}")
    a(" \\quad ".join(legendes))
    a("")

    # --- répétiteurs ------------------------------------------------------ #
    a("\\vspace{8pt}")
    a("\\noindent\\textbf{Répétiteurs :}")
    a("\\vspace{3pt}")
    a("")
    a("\\noindent")
    a("\\begin{tabular}{|p{6.0cm}|p{4.5cm}|p{12.0cm}|}")
    a("\\hline")
    a("\\rowcolor{entete}\\textcolor{white}{\\textbf{Nom et prénom}} & "
      "\\textcolor{white}{\\textbf{Matière}} & "
      "\\textcolor{white}{\\textbf{Jours et horaires}} \\\\")
    a("\\hline")
    for repetiteur in repetiteurs:
        a(echappement_tex(repetiteur["nom"]) + " & " + echappement_tex(repetiteur["matiere"])
          + " & " + echappement_tex(repetiteur["horaires"]) + " \\\\[6pt]")
        a("\\hline")
    a("\\end{tabular}")
    a("")

    # --- note ------------------------------------------------------------- #
    a("\\vspace{6pt}")
    a("\\noindent\\textcolor{note}{\\footnotesize")
    a(echappement_tex(donnees["note"]))
    a("}")
    a("")
    a("\\end{document}")

    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- #
# 2. L'aperçu PDF (reportlab)
# --------------------------------------------------------------------------- #

def construire_pdf(donnees: dict) -> None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:  # pragma: no cover
        print("  ! reportlab n'est pas installé : PDF non généré (pip install reportlab)")
        return

    jours = donnees["jours"]
    creneaux = donnees["creneaux"]
    matieres = donnees["matieres"]
    grille = donnees["grille"]
    repetiteurs = donnees["repetiteurs"]

    page_w, page_h = landscape(A4)
    marge = 1.2 * cm
    largeur_utile = page_w - 2 * marge

    doc = SimpleDocTemplate(
        str(PDF_FILE),
        pagesize=landscape(A4),
        leftMargin=marge, rightMargin=marge, topMargin=marge, bottomMargin=marge,
        title=f"Emploi du temps — {donnees['famille']}",
        author=donnees["famille"],
        subject="Emploi du temps hebdomadaire — TogoEdu Hub",
    )

    entete_c = colors.HexColor(PALETTE["entete"])
    grille_c = colors.HexColor(PALETTE["grille"])
    note_c = colors.HexColor(PALETTE["note"])

    s_titre = ParagraphStyle("titre", fontName="Helvetica-Bold", fontSize=14, leading=17,
                             alignment=TA_CENTER, textColor=colors.white)
    s_sous = ParagraphStyle("sous", fontName="Helvetica", fontSize=9.5, leading=12,
                            alignment=TA_CENTER, textColor=colors.white)
    s_jour = ParagraphStyle("jour", fontName="Helvetica-Bold", fontSize=9, leading=11,
                            alignment=TA_CENTER, textColor=colors.white)
    s_heure = ParagraphStyle("heure", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                             alignment=TA_CENTER)
    s_cours = ParagraphStyle("cours", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                             alignment=TA_CENTER)
    s_legende = ParagraphStyle("legende", fontName="Helvetica", fontSize=7.5, leading=10)
    s_note = ParagraphStyle("note", fontName="Helvetica", fontSize=7.5, leading=10, textColor=note_c)
    s_cellule = ParagraphStyle("cellule", fontName="Helvetica", fontSize=8, leading=10)
    s_titre_bloc = ParagraphStyle("titrebloc", fontName="Helvetica-Bold", fontSize=9.5, leading=12)

    elements: list = []

    # --- bandeau ---------------------------------------------------------- #
    bandeau = Table(
        [[Paragraph(f"{echappement_html(donnees['titre'])} — "
                    f"{echappement_html(donnees['famille'].upper())}", s_titre)],
         [Paragraph(echappement_html(donnees["mention"]), s_sous)],
         [Paragraph(f"{echappement_html(donnees['localite'])} • "
                    f"{echappement_html(donnees['annee'])}", s_sous)]],
        colWidths=[largeur_utile])
    bandeau.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), entete_c),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(bandeau)
    elements.append(Spacer(1, 6))

    # --- grille ----------------------------------------------------------- #
    col_heure = LARGEUR_HORAIRE * cm
    col_jour = (largeur_utile - col_heure) / len(jours)
    largeurs = [col_heure] + [col_jour] * len(jours)

    donnees_table = [[Paragraph("Horaire", s_jour)] + [Paragraph(echappement_html(j), s_jour) for j in jours]]
    hauteurs = [HAUTEUR_ENTETE * cm]
    commandes = [
        ("BACKGROUND", (0, 0), (-1, 0), entete_c),
        ("GRID", (0, 0), (-1, -1), 0.5, grille_c),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]

    for index, creneau in enumerate(creneaux, start=1):
        ligne = [Paragraph(echappement_html(creneau["libelle"]), s_heure)]
        commandes.append(("BACKGROUND", (0, index), (0, index), colors.HexColor(PALETTE["horaire"])))
        for colonne, jour in enumerate(jours, start=1):
            case = grille.get(jour, {}).get(creneau["id"])
            if case:
                ligne.append(Paragraph(echappement_html(case["texte"]), s_cours))
                commandes.append(("BACKGROUND", (colonne, index), (colonne, index),
                                  colors.HexColor(matieres[case["matiere"]]["couleur"])))
            else:
                ligne.append(Paragraph("", s_cours))
                commandes.append(("BACKGROUND", (colonne, index), (colonne, index),
                                  colors.HexColor(PALETTE["libre"])))
        donnees_table.append(ligne)
        hauteurs.append(HAUTEUR_LIGNE * cm)

    table = Table(donnees_table, colWidths=largeurs, rowHeights=hauteurs, repeatRows=1)
    table.setStyle(TableStyle(commandes))
    elements.append(table)

    # --- légende ---------------------------------------------------------- #
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("<b>Légende :</b>", s_note))
    elements.append(Spacer(1, 3))

    puces = list(matieres.items()) + [("Créneau libre", {"couleur": PALETTE["libre"]})]
    cellules = []
    for libelle, infos in puces:
        bloc = Table([[Paragraph("", s_legende), Paragraph(echappement_html(libelle), s_legende)]],
                     colWidths=[1.0 * cm, 4.2 * cm], rowHeights=[0.38 * cm])
        bloc.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(infos["couleur"])),
            ("BOX", (0, 0), (0, 0), 0.4, grille_c),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ]))
        cellules.append(bloc)

    par_ligne = 4
    lignes = [cellules[i : i + par_ligne] for i in range(0, len(cellules), par_ligne)]
    lignes[-1] += [""] * (par_ligne - len(lignes[-1]))
    legende = Table(lignes, colWidths=[largeur_utile / par_ligne] * par_ligne)
    legende.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    elements.append(legende)

    # --- répétiteurs ------------------------------------------------------ #
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>Répétiteurs :</b>", s_titre_bloc))
    elements.append(Spacer(1, 3))

    entetes = [Paragraph(f"<b><font color='white'>{h}</font></b>", s_cellule)
               for h in ("Nom et prénom", "Matière", "Jours et horaires")]
    lignes_rep = [entetes]
    for repetiteur in repetiteurs:
        lignes_rep.append([Paragraph(echappement_html(repetiteur["nom"]), s_cellule),
                           Paragraph(echappement_html(repetiteur["matiere"]), s_cellule),
                           Paragraph(echappement_html(repetiteur["horaires"]), s_cellule)])

    largeurs_rep = [6.0 * cm, 4.5 * cm, 12.0 * cm]
    table_rep = Table(lignes_rep, colWidths=largeurs_rep,
                      rowHeights=[0.60 * cm] + [0.64 * cm] * len(repetiteurs))
    table_rep.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), entete_c),
        ("GRID", (0, 0), (-1, -1), 0.5, grille_c),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(table_rep)

    # --- note ------------------------------------------------------------- #
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(echappement_html(donnees["note"]), s_note))

    doc.build(elements)


# --------------------------------------------------------------------------- #

def main() -> None:
    donnees = charger()

    TEX_FILE.write_text(construire_tex(donnees), encoding="utf-8")
    print(f"  OK  {TEX_FILE.name}")

    construire_pdf(donnees)
    if PDF_FILE.exists():
        print(f"  OK  {PDF_FILE.name}")

    remplis = sum(len(v) for v in donnees["grille"].values())
    print(f"\n  {len(donnees['jours'])} jours × {len(donnees['creneaux'])} créneaux"
          f" — {remplis} case(s) renseignée(s)")


if __name__ == "__main__":
    main()

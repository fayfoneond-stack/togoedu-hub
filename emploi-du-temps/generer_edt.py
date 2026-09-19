#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère l'emploi du temps à partir d'une source unique : edt-data.json

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

# --------------------------------------------------------------------------- #
# Utilitaires
# --------------------------------------------------------------------------- #

PALETTE = {
    "entete": "#29405F",     # bandeau + ligne d'en-tête du tableau
    "horaire": "#EAEFF6",    # colonne des horaires
    "recre": "#D6D6D6",      # ligne récréation
    "vide": "#F7F7F7",       # cases sans cours
    "grille": "#9AA5B4",     # filets du tableau
    "note": "#5B6675",       # texte des notes de bas de page
}


def slug(texte: str) -> str:
    """Nom de couleur LaTeX ASCII stable (Français -> Francais)."""
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
    return (
        texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def format_duree(minutes: int) -> str:
    """300 -> '5 h 00'"""
    heures, reste = divmod(minutes, 60)
    return f"{heures} h {reste:02d}"


# --------------------------------------------------------------------------- #
# Chargement et calculs
# --------------------------------------------------------------------------- #

def charger() -> dict:
    with DATA_FILE.open(encoding="utf-8") as handle:
        donnees = json.load(handle)
    donnees["matieres"] = {k: v for k, v in donnees["matieres"].items() if not k.startswith("_")}
    donnees["vacants"] = {k: v for k, v in donnees.get("vacants", {}).items() if not k.startswith("_")}
    return donnees


def volume_horaire(donnees: dict) -> dict[str, int]:
    """Nombre de séances par matière (les cases vides ne comptent pas)."""
    compte: dict[str, int] = {}
    for ligne in donnees["grille"].values():
        for matiere in ligne.values():
            compte[matiere] = compte.get(matiere, 0) + 1
    return compte


# --------------------------------------------------------------------------- #
# 1. Le code LaTeX
# --------------------------------------------------------------------------- #

def construire_tex(donnees: dict) -> str:
    duree = donnees["duree_seance_min"]
    jours = donnees["jours"]
    creneaux = [c for c in donnees["creneaux"] if not c["id"].startswith("_")]
    matieres = donnees["matieres"]
    vacants = donnees["vacants"]
    compte = volume_horaire(donnees)
    total_seances = sum(compte.values())

    L: list[str] = []
    a = L.append

    # --- préambule -------------------------------------------------------- #
    a("% =====================================================================")
    a("%  EMPLOI DU TEMPS — " + donnees["etablissement"])
    a("%  " + donnees["intitule"] + " — " + donnees["annee"])
    a("%")
    a("%  Compilation : pdflatex emploi-du-temps.tex  (ou Overleaf / XeLaTeX)")
    a("%  Fichier généré depuis edt-data.py — ne pas éditer à la main,")
    a("%  modifier edt-data.json puis relancer :  python3 generer_edt.py")
    a("% =====================================================================")
    a("")
    a("\\documentclass[a4paper,landscape,10pt]{article}")
    a("")
    a("\\usepackage[T1]{fontenc}")
    a("\\usepackage[utf8]{inputenc}")
    a("\\usepackage[french]{babel}")
    a("\\usepackage[margin=1.2cm]{geometry}")
    a("\\usepackage[table]{xcolor}   % \\cellcolor / \\rowcolor")
    a("\\usepackage{array}           % colonnes p{} paramétrées")
    
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

    # --- commandes du document -------------------------------------------- #
    a("% ---------- Commandes ----------")
    a("% \\cours{couleur}{matière}{enseignant}{salle}")
    a("\\newcommand{\\cours}[4]{%")
    a("  \\cellcolor{#1}%")
    a("  \\begin{minipage}[c][1.25cm][c]{\\dimexpr\\linewidth-2\\tabcolsep\\relax}%")
    a("    \\centering")
    a("    {\\small\\textbf{#2}}\\par\\vspace{2pt}")
    a("    {\\footnotesize #3}\\par\\vspace{1pt}")
    a("    {\\scriptsize #4}%")
    a("  \\end{minipage}}")
    a("")
    a("% \\horaire{libellé}{début -- fin}")
    a("\\newcommand{\\horaire}[2]{%")
    a("  \\cellcolor{horaire}%")
    a("  \\begin{minipage}[c][1.25cm][c]{\\dimexpr\\linewidth-2\\tabcolsep\\relax}%")
    a("    \\centering")
    a("    {\\textbf{#1}}\\par\\vspace{2pt}")
    a("    {\\footnotesize #2}%")
    a("  \\end{minipage}}")
    a("")
    a("% case sans cours")
    a("\\newcommand{\\vide}{%")
    a("  \\cellcolor{vide}%")
    a("  \\begin{minipage}[c][1.25cm][c]{\\dimexpr\\linewidth-2\\tabcolsep\\relax}%")
    a("    \\centering\\footnotesize\\itshape sans cours%")
    a("  \\end{minipage}}")
    a("")
    a("% \\legende{couleur}{libellé}")
    a("\\newcommand{\\legende}[2]{%")
    a("  \\colorbox{#1}{\\rule[-1.5pt]{0pt}{10pt}\\hspace{1.1cm}}~{\\footnotesize #2}}")
    a("")
    a("\\setlength{\\tabcolsep}{3pt}")
    a("\\renewcommand{\\arraystretch}{1.15}")
    a("\\pagestyle{empty}")
    a("")

    # --- document --------------------------------------------------------- #
    a("\\begin{document}")
    a("")
    a("% ---------- Bandeau ----------")
    a("\\noindent\\colorbox{entete}{%")
    a("  \\parbox[c][1.75cm][c]{\\dimexpr\\linewidth-2\\fboxsep\\relax}{%")
    a("    \\centering\\color{white}%")
    a("    {\\Large\\textbf{EMPLOI DU TEMPS — " + echappement_tex(donnees["classe"].upper()) + "}}\\\\[3pt]")
    a("    {\\normalsize " + echappement_tex(donnees["etablissement"]) + " — " + echappement_tex(donnees["localite"]) + "}\\\\[3pt]")
    a("    {\\small " + echappement_tex(donnees["intitule"]) + " \\quad\\textbullet\\quad Année scolaire "
      + echappement_tex(donnees["annee"]) + " \\quad\\textbullet\\quad " + echappement_tex(donnees["periode"])
      + " \\quad\\textbullet\\quad Professeur principal : " + echappement_tex(donnees["prof_principal"]) + "}")
    a("  }%")
    a("}")
    a("\\vspace{6pt}")
    a("")

    # --- grand tableau ---------------------------------------------------- #
    a("% ---------- Grille hebdomadaire ----------")
    a("\\noindent")
    a("\\begin{tabular}{|p{2.4cm}|*{"
      + str(len(jours)) + "}{p{3.85cm}|}}")
    a("\\hline")

    entete = ["\\textcolor{white}{\\textbf{" + echappement_tex(j) + "}}" for j in jours]
    a("\\rowcolor{entete}\\cellcolor{entete}\\textcolor{white}{\\textbf{Horaire}} & " + " & ".join(entete) + " \\\\")
    a("\\hline")

    for creneau in creneaux:
        if creneau["id"] == "RECRE":
            a("\\multicolumn{" + str(len(jours) + 1) + "}{|c|}{\\cellcolor{recre}\\textbf{"
              + echappement_tex(creneau["libelle"]) + " — "
              + echappement_tex(creneau["debut"]) + " à " + echappement_tex(creneau["fin"]) + "}} \\\\")
            a("\\hline")
            continue

        cellules = [
            "\\horaire{" + echappement_tex(creneau["libelle"]) + "}{"
            + echappement_tex(creneau["debut"]) + " – " + echappement_tex(creneau["fin"]) + "}"
        ]
        for jour in jours:
            if creneau["id"] in vacants.get(jour, []):
                cellules.append("\\vide")
                continue
            matiere = donnees["grille"][jour][creneau["id"]]
            infos = matieres[matiere]
            cellules.append("\\cours{c" + slug(matiere) + "}{"
                            + echappement_tex(matiere) + "}{"
                            + echappement_tex(infos["prof"]) + "}{"
                            + echappement_tex(infos["salle"]) + "}")
        a(" & ".join(cellules) + " \\\\")
        a("\\hline")

    a("\\end{tabular}")
    a("")

    # --- légende ---------------------------------------------------------- #
    a("\\vspace{6pt}")
    a("\\noindent\\textbf{Légende des matières} (volume horaire hebdomadaire entre parenthèses) :")
    a("\\vspace{3pt}")
    a("")
    a("\\begin{center}")
    legendes = [
        "\\legende{c" + slug(matiere) + "}{" + echappement_tex(matiere)
        + " (" + format_duree(compte.get(matiere, 0) * duree) + ")}"
        for matiere in matieres
    ]
    a("\\\\[5pt]".join(["\\quad ".join(legendes[i : i + 4]) for i in range(0, len(legendes), 4)]))
    a("\\end{center}")
    a("")

    # --- notes ------------------------------------------------------------ #
    a("\\vspace{8pt}")
    a("\\noindent\\textcolor{note}{\\footnotesize")
    a("Volume horaire hebdomadaire : " + str(total_seances) + " séances de " + str(duree)
      + " min, soit \\textbf{" + format_duree(total_seances * duree) + "}. "
      "Les cours s'achèvent le samedi à 11h10. Toute modification doit être signalée au secrétariat.")
    a("}")
    a("")

    # --- signatures ------------------------------------------------------- #
    a("\\vspace{10pt}")
    a("\\noindent")
    a("\\begin{tabular}{@{}p{0.30\\linewidth}p{0.30\\linewidth}p{0.30\\linewidth}@{}}")
    a("\\textbf{Le Professeur principal} & \\textbf{Le Chef d'établissement} & \\textbf{Visa du CPE} \\\\[14pt]")
    a(echappement_tex(donnees["prof_principal"]) + " &  &  \\\\\\[8pt]")
    a("\\rule{4.5cm}{0.4pt} & \\rule{4.5cm}{0.4pt} & \\rule{4.5cm}{0.4pt} \\\\")
    a("\\end{tabular}")
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

    duree = donnees["duree_seance_min"]
    jours = donnees["jours"]
    creneaux = [c for c in donnees["creneaux"] if not c["id"].startswith("_")]
    matieres = donnees["matieres"]
    vacants = donnees["vacants"]
    compte = volume_horaire(donnees)
    total_seances = sum(compte.values())

    page_w, page_h = landscape(A4)
    marge = 1.2 * cm
    largeur_utile = page_w - 2 * marge

    doc = SimpleDocTemplate(
        str(PDF_FILE),
        pagesize=landscape(A4),
        leftMargin=marge, rightMargin=marge, topMargin=marge, bottomMargin=marge,
        title=f"Emploi du temps {donnees['classe']} — {donnees['annee']}",
        author=donnees["etablissement"],
        subject="Emploi du temps hebdomadaire — TogoEdu Hub",
    )

    entete_c = colors.HexColor(PALETTE["entete"])
    grille_c = colors.HexColor(PALETTE["grille"])
    note_c = colors.HexColor(PALETTE["note"])

    style_bandeau = ParagraphStyle("bandeau", fontName="Helvetica-Bold", fontSize=13,
                                   leading=16, alignment=TA_CENTER, textColor=colors.white)
    style_bandeau2 = ParagraphStyle("bandeau2", fontName="Helvetica", fontSize=9.5,
                                    leading=12, alignment=TA_CENTER, textColor=colors.white)
    style_jour = ParagraphStyle("jour", fontName="Helvetica-Bold", fontSize=9,
                                leading=11, alignment=TA_CENTER, textColor=colors.white)
    style_heure = ParagraphStyle("heure", fontName="Helvetica-Bold", fontSize=8,
                                 leading=10, alignment=TA_CENTER)
    style_heure2 = ParagraphStyle("heure2", fontName="Helvetica", fontSize=7,
                                  leading=9, alignment=TA_CENTER)
    style_cours = ParagraphStyle("cours", fontName="Helvetica-Bold", fontSize=8,
                                 leading=10, alignment=TA_CENTER)
    style_prof = ParagraphStyle("prof", fontName="Helvetica", fontSize=6.8,
                                leading=8.5, alignment=TA_CENTER)
    style_legende = ParagraphStyle("legende", fontName="Helvetica", fontSize=7.5, leading=10)
    style_note = ParagraphStyle("note", fontName="Helvetica", fontSize=7.5, leading=10, textColor=note_c)
    style_sign = ParagraphStyle("sign", fontName="Helvetica", fontSize=8, leading=11)

    elements: list = []

    # --- bandeau ---------------------------------------------------------- #
    bandeau = Table(
        [[Paragraph(f"EMPLOI DU TEMPS — {echappement_html(donnees['classe'].upper())}", style_bandeau)],
         [Paragraph(echappement_html(f"{donnees['etablissement']} — {donnees['localite']}"), style_bandeau2)],
         [Paragraph(echappement_html(
             f"{donnees['intitule']} • Année scolaire {donnees['annee']} • {donnees['periode']}"
             f" • Professeur principal : {donnees['prof_principal']}"), style_bandeau2)]],
        colWidths=[largeur_utile],
    )
    bandeau.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), entete_c),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(bandeau)
    elements.append(Spacer(1, 6))

    # --- grille ----------------------------------------------------------- #
    col_heure = 2.4 * cm
    col_jour = (largeur_utile - col_heure) / len(jours)
    largeurs = [col_heure] + [col_jour] * len(jours)

    donnees_table = [[Paragraph("Horaire", style_jour)]
                     + [Paragraph(echappement_html(j), style_jour) for j in jours]]
    hauteurs = [0.85 * cm]
    commandes: list = [
        ("BACKGROUND", (0, 0), (-1, 0), entete_c),
        ("GRID", (0, 0), (-1, -1), 0.5, grille_c),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]

    for index, creneau in enumerate(creneaux, start=1):
        if creneau["id"] == "RECRE":
            donnees_table.append([Paragraph(
                f"<b>{echappement_html(creneau['libelle'])} — "
                f"{echappement_html(creneau['debut'])} à {echappement_html(creneau['fin'])}</b>",
                style_heure)])
            hauteurs.append(0.62 * cm)
            commandes += [("SPAN", (0, index), (len(jours), index)),
                          ("BACKGROUND", (0, index), (-1, index), colors.HexColor(PALETTE["recre"]))]
            continue

        ligne = [Paragraph(
            f"<b>{echappement_html(creneau['libelle'])}</b><br/>"
            f"<font size=7>{echappement_html(creneau['debut'])} – {echappement_html(creneau['fin'])}</font>",
            style_heure)]

        for colonne, jour in enumerate(jours, start=1):
            if creneau["id"] in vacants.get(jour, []):
                ligne.append(Paragraph("<i>sans cours</i>", style_prof))
                commandes.append(("BACKGROUND", (colonne, index), (colonne, index),
                                  colors.HexColor(PALETTE["vide"])))
                continue
            matiere = donnees["grille"][jour][creneau["id"]]
            infos = matieres[matiere]
            ligne.append(Paragraph(
                f"<b>{echappement_html(matiere)}</b><br/>"
                f"<font size=6.8>{echappement_html(infos['prof'])}</font><br/>"
                f"<font size=6.4>{echappement_html(infos['salle'])}</font>",
                style_cours))
            commandes.append(("BACKGROUND", (colonne, index), (colonne, index),
                              colors.HexColor(infos["couleur"])))

        commandes.append(("BACKGROUND", (0, index), (0, index), colors.HexColor(PALETTE["horaire"])))
        donnees_table.append(ligne)
        hauteurs.append(1.25 * cm)

    table = Table(donnees_table, colWidths=largeurs, rowHeights=hauteurs, repeatRows=1)
    table.setStyle(TableStyle(commandes))
    elements.append(table)

    # --- légende ---------------------------------------------------------- #
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>Légende des matières</b> "
                              "(volume horaire hebdomadaire entre parenthèses) :", style_note))
    elements.append(Spacer(1, 3))

    cellules_legende = []
    for matiere, infos in matieres.items():
        bloc = Table(
            [[Paragraph("", style_legende),
              Paragraph(f"{echappement_html(matiere)} "
                        f"({format_duree(compte.get(matiere, 0) * duree)})", style_legende)]],
            colWidths=[1.0 * cm, 4.0 * cm], rowHeights=[0.42 * cm])
        bloc.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(infos["couleur"])),
            ("BOX", (0, 0), (0, 0), 0.4, grille_c),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ]))
        cellules_legende.append(bloc)

    par_ligne = 6
    lignes_legende = [cellules_legende[i : i + par_ligne] for i in range(0, len(cellules_legende), par_ligne)]
    lignes_legende[-1] += [""] * (par_ligne - len(lignes_legende[-1]))
    legende = Table(lignes_legende, colWidths=[largeur_utile / par_ligne] * par_ligne)
    legende.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(legende)

    # --- note + signatures ------------------------------------------------ #
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        f"Volume horaire hebdomadaire : {total_seances} séances de {duree} min, "
        f"soit <b>{format_duree(total_seances * duree)}</b>. Les cours s'achèvent le samedi à 11h10. "
        "Toute modification doit être signalée au secrétariat.", style_note))
    elements.append(Spacer(1, 14))

    signatures = Table(
        [[Paragraph("<b>Le Professeur principal</b>", style_sign),
          Paragraph("<b>Le Chef d'établissement</b>", style_sign),
          Paragraph("<b>Visa du CPE</b>", style_sign)],
         [Paragraph(echappement_html(donnees["prof_principal"]), style_sign),
          Paragraph("", style_sign),
          Paragraph("", style_sign)],
         [Paragraph("<font color='#9AA5B4'>" + "_" * 34 + "</font>", style_sign),
          Paragraph("<font color='#9AA5B4'>" + "_" * 34 + "</font>", style_sign),
          Paragraph("<font color='#9AA5B4'>" + "_" * 34 + "</font>", style_sign)]],
        colWidths=[largeur_utile / 3.0] * 3)
    signatures.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    elements.append(signatures)

    doc.build(elements)


# --------------------------------------------------------------------------- #

def main() -> None:
    donnees = charger()

    TEX_FILE.write_text(construire_tex(donnees), encoding="utf-8")
    print(f"  OK  {TEX_FILE.relative_to(HERE.parent)}")

    construire_pdf(donnees)
    if PDF_FILE.exists():
        print(f"  OK  {PDF_FILE.relative_to(HERE.parent)}")

    compte = volume_horaire(donnees)
    total = sum(compte.values())
    print(f"\n  {total} séances — {format_duree(total * donnees['duree_seance_min'])} par semaine")
    for matiere, nombre in sorted(compte.items(), key=lambda kv: -kv[1]):
        print(f"    {matiere:<24} {nombre} séances  ({format_duree(nombre * donnees['duree_seance_min'])})")


if __name__ == "__main__":
    main()

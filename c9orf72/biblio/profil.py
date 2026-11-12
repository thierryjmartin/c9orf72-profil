"""Profil personnel : questionnaire et explication à partir des tables de la revue.

Principes (voir aussi web/README.md) :
- aucune probabilité n'est calculée à partir des symptômes ou des traits : les signes précoces sont des différences
  de groupe entre porteurs et témoins, sans valeur diagnostique individuelle connue ;
- le seul calcul est mendélien (risque a priori selon le lien de parenté avec un porteur connu), corrigé par l'âge
  atteint sans maladie à l'aide de courbes de pénétrance publiées (théorème de Bayes, comme en consultation de
  génétique) ; les symptômes n'entrent jamais dans le calcul ;
- tous les chiffres affichés viennent des tables (findings, penetrance, frequencies, modifiers), avec leur PMID.
"""
import re

from .report import DOMAIN_LABELS, OUTCOME_LABELS

DETAILS = ("court", "standard", "detaille")
EARLY = ("presymptomatic_carriers", "prodromal_carriers", "carriers_retrospective")
LIFELONG = ("carriers_retrospective", "relatives_untested", "noncarrier_relatives", "presymptomatic_carriers")

# --- Questionnaire ---------------------------------------------------------------------------------------------

# Chaque signe : libellé, domaines de la table findings, motif cherché dans sign/measure (minuscules).
CHANGES = {
    "apathie": ("Perte d'intérêt, d'élan ou d'initiative (apathie)", ["comportement_personnalite"], r"apath|motivation|initiative"),
    "desinhibition": ("Désinhibition, impulsivité, remarques déplacées", ["comportement_personnalite"], r"d[ée]sinhib|impuls"),
    "empathie": ("Moins d'empathie ou de chaleur envers les proches", ["comportement_personnalite", "cognition"], r"empath|cognition sociale|th[ée]orie de l'esprit|[ée]motion"),
    "compulsions": ("Rituels, rigidité ou comportements répétitifs nouveaux", ["comportement_personnalite"], r"compuls|st[ée]r[ée]otyp|rigid|r[ée]p[ée]tit|ritu"),
    "alimentation": ("Changement des habitudes alimentaires (sucré, appétit accru)", ["comportement_personnalite", "autonome_metabolique"], r"aliment|hyperphag|app[ée]tit|sucr"),
    "memoire": ("Oublis plus fréquents", ["cognition"], r"m[ée]moire|mn[ée]si"),
    "executif": ("Difficultés à organiser, planifier, mener plusieurs tâches", ["cognition"], r"ex[ée]cut|planif|flexib|attention"),
    "langage": ("Difficultés à trouver ses mots ou à comprendre", ["langage_parole", "cognition"], r"langage|fluence|d[ée]nomin|parole|mot"),
    "moteur": ("Faiblesse, crampes, contractions musculaires, gêne pour parler ou avaler", ["moteur_neurophysiologie"], r"moteur|motric|force|fascicul|crampe|bulbaire|faiblesse|dext[ée]rit"),
    "psychose": ("Hallucinations, idées inhabituelles ou délirantes", ["psychiatrie"], r"psycho|hallucin|d[ée]lir"),
    "humeur": ("Anxiété ou dépression nouvelles", ["psychiatrie"], r"anxi|d[ée]press|humeur|affectif"),
    "sommeil": ("Sommeil nettement modifié", ["sommeil"], r"sommeil|fuseau|nrem|[ée]veil"),
    "poids": ("Perte de poids inexpliquée", ["autonome_metabolique"], r"poids|imc|graisse|masse|m[ée]tabol"),
}
TRAITS = {
    "rigidite": ("Besoin de routine, rigidité depuis toujours", ["developpement_vie_entiere", "comportement_personnalite"], r"rigid|routine|autis|obsess"),
    "social": ("Difficultés relationnelles ou d'empathie depuis toujours", ["developpement_vie_entiere", "comportement_personnalite"], r"social|empath|autis|personnalit"),
    "psy_perso": ("Antécédent personnel de trouble psychiatrique (bipolarité, psychose…)", ["psychiatrie"], r"psycho|bipolaire|schizo|psychiatr"),
    "anxiete": ("Anxiété importante depuis l'adolescence", ["psychiatrie", "developpement_vie_entiere"], r"anxi"),
}
RELATIONS = {  # risque a priori d'avoir hérité de l'expansion d'un porteur connu (transmission autosomique dominante)
    "parent": ("Mon père ou ma mère", 50),
    "frere_soeur": ("Un frère ou une sœur (un de nos parents est donc probablement porteur)", 50),
    "grand_parent": ("Un grand-parent (mon parent de ce côté n'a pas été testé)", 25),
    "oncle_tante": ("Un oncle ou une tante (mon parent de ce côté n'a pas été testé)", 25),
    "cousin": ("Un cousin ou une cousine", None),
    "enfant": ("Mon enfant", None),
}

QUESTIONS = [
    {"id": "age", "section": "Vous", "label": "Votre âge", "type": "number", "min": 0, "max": 110},
    {"id": "sexe", "section": "Vous", "label": "Sexe", "type": "choice",
     "options": [["F", "Femme"], ["M", "Homme"], ["nr", "Je préfère ne pas répondre"]]},
    {"id": "test", "section": "Génétique", "label": "Avez-vous fait un test génétique pour C9orf72 ?", "type": "choice",
     "options": [["non", "Non"], ["positif", "Oui : porteur de l'expansion"], ["negatif", "Oui : non porteur"],
                 ["intermediaire", "Oui : allèle intermédiaire (environ 20 à 30 répétitions)"]]},
    {"id": "mutation_famille", "section": "Génétique", "label": "L'expansion C9orf72 a-t-elle été trouvée chez un membre de votre famille ?",
     "type": "choice", "options": [["nsp", "Je ne sais pas"], ["non", "Non"], ["oui", "Oui"]]},
    {"id": "lien_porteur", "section": "Génétique", "label": "Qui est le porteur connu le plus proche de vous ?", "type": "choice",
     "show_if": {"mutation_famille": "oui"}, "options": [[k, v[0]] for k, v in RELATIONS.items()]},
    {"id": "famille_sla_dft", "section": "Famille", "type": "choice",
     "label": "Des membres de votre famille ont-ils eu une SLA (maladie de Charcot) ou une démence frontotemporale ?",
     "options": [["non", "Non, pas à ma connaissance"], ["premier", "Oui, un parent, frère, sœur ou enfant"],
                 ["eloigne", "Oui, seulement des parents plus éloignés"], ["nsp", "Je ne connais pas bien l'histoire familiale"]]},
    {"id": "famille_plusieurs", "section": "Famille", "type": "bool", "show_if": {"famille_sla_dft": ["premier", "eloigne"]},
     "label": "Plusieurs personnes sont-elles atteintes, ou y a-t-il à la fois des SLA et des démences ?"},
    {"id": "famille_psy", "section": "Famille", "type": "bool",
     "label": "Y a-t-il dans la famille des psychoses, schizophrénies, troubles bipolaires ou démences précoces (avant 65 ans) ?"},
    {"id": "changements", "section": "Changements récents", "type": "multi",
     "label": "Depuis quelques années, avez-vous (ou vos proches) remarqué un changement par rapport à votre fonctionnement habituel ?",
     "options": [[k, v[0]] for k, v in CHANGES.items()]},
    {"id": "traits", "section": "Traits de toujours", "type": "multi",
     "label": "Ces traits vous décrivent-ils depuis toujours (sans changement récent) ?",
     "options": [[k, v[0]] for k, v in TRAITS.items()]},
]


# --- Données ---------------------------------------------------------------------------------------------------

def _auteur(first_author):
    """« de Boer SCM » → « de Boer » : on retire seulement les initiales finales."""
    t = (first_author or "?").split()
    if len(t) > 1 and t[-1].isupper() and len(t[-1]) <= 4:
        t = t[:-1]
    return " ".join(t)


def _ref(r):
    return {"pmid": r["pmid"], "auteur": _auteur(r["first_author"]), "annee": r["year"]}


def _rows(con, sql, args=()):
    return [dict(r) for r in con.execute(sql, args)]


def _findings(con, domains, pattern, populations):
    rows = _rows(con, "SELECT f.*, a.first_author, a.year FROM findings f JOIN articles a USING (pmid) "
                      f"WHERE f.domain IN ({','.join('?' * len(domains))}) "
                      f"AND f.population IN ({','.join('?' * len(populations))})", (*domains, *populations))
    rx = re.compile(pattern, re.I)
    return [r for r in rows if rx.search(f"{r['sign'] or ''} {r['measure'] or ''}")]


def _carrier_freq(con, pattern):
    rows = _rows(con, "SELECT f.*, a.first_author, a.year FROM frequencies f JOIN articles a USING (pmid) "
                      "WHERE f.kind='carrier_frequency'")
    rx = re.compile(pattern, re.I)
    out = []
    for r in rows:
        pct = r["percent"] if r["percent"] is not None else (100 * r["n"] / r["total"] if r["n"] is not None and r["total"] else None)
        if pct is not None and rx.search(r["grp"] or ""):
            out.append(dict(r, pct=pct))
    return sorted(out, key=lambda r: r["pct"])


def _penetrance_desc(con, pattern):
    rows = _rows(con, "SELECT p.*, a.first_author, a.year FROM penetrance p JOIN articles a USING (pmid) "
                      "WHERE p.description IS NOT NULL")
    rx = re.compile(pattern, re.I)
    return [r for r in rows if rx.search(r["description"])]


def _item(texte, r=None):
    return {"texte": texte, "ref": _ref(r) if r else None}


def _fmt(v, d=1):
    return f"{v:.{d}f}".rstrip("0").rstrip(".").replace(".", ",")


# --- Algorithme -------------------------------------------------------------------------------------------------

def statut(a):
    """Situation génétique, du plus informatif au moins informatif."""
    test = a.get("test", "non")
    if test == "positif":
        return "porteur"
    if test == "negatif":
        return "non_porteur"
    if test == "intermediaire":
        return "intermediaire"
    if a.get("mutation_famille") == "oui":
        return "apparente_porteur"
    if a.get("famille_sla_dft") == "premier" or (a.get("famille_sla_dft") == "eloigne" and a.get("famille_plusieurs")):
        return "antecedents"
    if a.get("famille_sla_dft") == "eloigne" or a.get("famille_psy"):
        return "antecedents_faibles"
    return "population"


TITRES = {
    "porteur": "Porteur connu de l'expansion",
    "non_porteur": "Non porteur (test négatif)",
    "intermediaire": "Allèle intermédiaire",
    "apparente_porteur": "Apparenté d'un porteur connu",
    "antecedents": "Antécédents familiaux évocateurs, sans mutation connue",
    "antecedents_faibles": "Antécédents familiaux peu spécifiques",
    "population": "Pas d'antécédent familial connu",
}


def prior_mendelien(a):
    """Risque a priori (%) d'avoir hérité de l'expansion, ou None s'il ne se déduit pas du seul lien de parenté."""
    if statut(a) != "apparente_porteur":
        return None
    return RELATIONS.get(a.get("lien_porteur"), (None, None))[1]


# Courbes de pénétrance (SLA ou DFT) utilisées pour corriger le risque a priori par l'âge. Chaque point est une ligne
# de la table penetrance (pmid, âge, début de la méthode). Deux courbes, parce que les estimations divergent selon le
# recrutement : on montre les deux plutôt que d'en choisir une. Point d'ancrage commun : aucun porteur malade avant
# 35 ans dans la série de Majounie 2012 (603 porteurs).
CURVES = [
    {"id": "malades", "label": "porteurs repérés à partir de malades (patients et leurs familles)",
     "points": [("22406228", 35, ""), ("22406228", 45, ""), ("26022924", 50, ""), ("26022924", 57, ""),
                ("26022924", 72, "")]},
    {"id": "population", "label": "porteurs trouvés en population générale (UK Biobank)",
     "points": [("22406228", 35, ""), ("40682810", 65, "Kaplan-Meier"), ("40682810", 70, "Kaplan-Meier"),
                ("40682810", 75, "Kaplan-Meier"), ("40682810", 80, "Kaplan-Meier (SLA ou démence toutes causes)")]},
]


def courbes(con):
    """Points (âge, % de porteurs malades, ligne source) de chaque courbe, lus dans la table penetrance."""
    out = []
    for c in CURVES:
        pts = []
        for pmid, age, method in c["points"]:
            rows = [r for r in _rows(con, "SELECT p.*, a.first_author, a.year FROM penetrance p JOIN articles a "
                                          "USING (pmid) WHERE p.pmid=? AND p.age=? AND p.outcome='any' "
                                          "AND p.cumulative_risk IS NOT NULL", (pmid, age))
                    if (r["method"] or "").startswith(method)]
            if rows:
                pts.append((age, rows[0]["cumulative_risk"], rows[0]))
        if len(pts) >= 2:
            out.append({"id": c["id"], "label": c["label"], "points": pts})
    return out


def penetrance_a(points, age):
    """% de porteurs malades à cet âge : interpolation linéaire, constante au-delà du dernier point publié."""
    if age <= points[0][0]:
        return points[0][1]
    for (a0, v0, _), (a1, v1, _) in zip(points, points[1:]):
        if age <= a1:
            return v0 + (v1 - v0) * (age - a0) / (a1 - a0)
    return points[-1][1]


def prior_age(p0, penetrance):
    """Probabilité (%) d'être porteur sachant qu'on n'est pas malade, à partir du risque a priori p0 (%) et de la
    pénétrance (%) à l'âge atteint : p0·(1−F) / (p0·(1−F) + (1−p0))."""
    p, f = p0 / 100, penetrance / 100
    return 100 * p * (1 - f) / (p * (1 - f) + 1 - p)


def _section_genetique(con, a, st, detail):
    items, texte = [], ""
    age = a.get("age")
    if st == "porteur":
        texte = ("Être porteur ne signifie pas être malade : la pénétrance est incomplète et dépend de l'âge. "
                 "Les estimations varient beaucoup selon que les porteurs ont été trouvés dans des familles malades "
                 "ou en population générale.")
        rows = _rows(con, "SELECT p.*, a.first_author, a.year FROM penetrance p JOIN articles a USING (pmid) "
                          "WHERE p.cumulative_risk IS NOT NULL ORDER BY p.age IS NULL, p.age")
        for r in rows:
            quand = f"à {_fmt(r['age'])} ans" if r["age"] else "sur la vie entière"
            mal = {"any": "SLA ou DFT (ou démence)", "als": "SLA", "ftd": "DFT"}.get(r["outcome"], r["outcome"] or "")
            items.append(_item(f"Risque cumulé de {mal} {quand} : {_fmt(r['cumulative_risk'])} %"
                               + (f" (IC {r['ci']})" if r["ci"] else "") + f" — {r['population']}", r))
        for r in _penetrance_desc(con, r"[âa]ge de d[ée]but"):
            items.append(_item(r["description"], r))
    elif st == "apparente_porteur":
        p = prior_mendelien(a)
        if p:
            texte = (f"La transmission est autosomique dominante : avec ce lien de parenté, le risque a priori d'avoir "
                     f"hérité de l'expansion est de {p} % (1 chance sur {round(100 / p)}). ")
        else:
            texte = ("Avec ce lien de parenté, le risque dépend de qui, entre vos parents, porte l'expansion : "
                     "seul un arbre généalogique examiné en consultation de génétique permet de l'estimer. ")
        texte += ("Ce risque diminue quand on avance en âge sans être malade, puisqu'une partie des porteurs l'aurait "
                  "déjà été. De combien, cela dépend de la courbe de pénétrance retenue, et les études divergent : "
                  "voici le calcul avec les deux principales.")
        if p and age:
            for c in courbes(con):
                f = penetrance_a(c["points"], age)
                last = c["points"][-1]
                note = (f" (au-delà de {_fmt(last[0], 0)} ans, l'étude ne donne plus de chiffre : valeur à "
                        f"{_fmt(last[0], 0)} ans gardée)") if age > last[0] else ""
                src = max(c["points"], key=lambda pt: pt[0] if pt[0] <= age else -1)[2]
                items.append(_item(f"À {age} ans sans maladie, avec la courbe des {c['label']} : probabilité d'être "
                                   f"porteur d'environ {_fmt(prior_age(p, f), 0)} % (au lieu de {p} %){note}", src))
            texte += (" Ce calcul ne tient compte que de l'âge, jamais des symptômes ; c'est celui que fait une "
                      "consultation de génétique, qui l'affinera avec l'histoire familiale.")
        for r in _penetrance_desc(con, r"probabilit[ée] d'[êe]tre porteur|risque [àa] 10 ans"):
            items.append(_item(r["description"], r))
    elif st in ("antecedents", "antecedents_faibles"):
        texte = ("Sans mutation identifiée dans la famille, on ne peut pas calculer votre risque. Ce que disent les "
                 "études : la proportion de familles touchées dont la maladie est due à C9orf72 varie fortement selon "
                 "l'origine géographique (très élevée en Finlande, faible en Asie de l'Est).")
        fam = _carrier_freq(con, r"famil")
        if fam:
            texte += (f" Dans les études de la base, l'expansion est retrouvée chez {_fmt(fam[0]['pct'])} % à "
                      f"{_fmt(fam[-1]['pct'])} % des patients ou familles avec antécédents familiaux ({len(fam)} groupes).")
        for r in fam + _carrier_freq(con, r"SLA-DFT|DFT"):
            items.append(_item(f"{_fmt(r['pct'])} % de porteurs — {r['grp']}", r))
        if st == "antecedents_faibles":
            texte += (" Des parents éloignés atteints, ou des troubles psychiatriques dans la famille, sont des "
                      "indices beaucoup plus faibles.")
    elif st == "non_porteur":
        texte = ("Un test négatif pour l'expansion écarte le risque lié à C9orf72. Les signes éventuels ont d'autres "
                 "causes. Dans une famille où l'expansion est connue, le risque des non-porteurs reste proche, mais "
                 "parfois un peu au-dessus, de celui de la population générale.")
        for r in _penetrance_desc(con, r"non porteurs"):
            items.append(_item(r["description"], r))
    elif st == "intermediaire":
        texte = ("Un allèle intermédiaire (environ 20 à 30 répétitions) n'est pas l'expansion pathogène (plusieurs "
                 "centaines à milliers de répétitions). Son rôle éventuel sur le risque est discuté :")
        for r in _rows(con, "SELECT m.*, a.first_author, a.year FROM modifiers m JOIN articles a USING (pmid) "
                            "WHERE m.modifier_type='intermediate_allele'"):
            items.append(_item(f"{r['modifier']} : {r['effect']}", r))
    else:
        pop = [r for r in _penetrance_desc(con, r"t[ée]moins|g[ée]nomes|population g[ée]n[ée]rale|[ée]chantillon")
               if re.search(r"\bporte|fr[ée]quence", r["description"]) and not re.search(r"non porteurs", r["description"])]
        pcts = [float(m.replace(",", ".")) for r in pop
                for m in re.findall(r"(\d+[,.]\d+) ?%", r["description"]) if float(m.replace(",", ".")) < 1]
        texte = "Sans antécédent familial, la probabilité de porter l'expansion est celle de la population générale"
        if pcts:
            texte += (f" : entre {_fmt(min(pcts), 2)} % et {_fmt(max(pcts), 2)} % des personnes sans maladie connue dans "
                      f"les études de la base, soit environ {_fmt(min(pcts) * 10)} à {_fmt(max(pcts) * 10)} sur 1 000")
        texte += (". Elle est plus élevée chez les personnes déjà malades d'une SLA dite sporadique, et varie selon "
                  "l'origine géographique.")
        for r in pop:
            items.append(_item(r["description"], r))
        for r in _carrier_freq(con, r"sporadique"):
            items.append(_item(f"{_fmt(r['pct'])} % de porteurs — {r['grp']}", r))
    return {"id": "genetique", "titre": "Votre situation génétique", "texte": texte,
            "items": items if detail != "court" else []}


def _resume_signes(rows):
    ab = [r for r in rows if r["direction"] == "abnormal"]
    nd = [r for r in rows if r["direction"] == "no_difference"]
    yrs = [r["years_before_onset"] for r in ab if r["years_before_onset"] is not None]
    return ab, nd, (max(yrs) if yrs else None)


def _section_signes(con, a, st, detail, choix, catalogue, populations, titre, intro):
    if not choix:
        return None
    items, lignes = [], []
    for k in choix:
        label, domains, pattern = catalogue[k]
        rows = _findings(con, domains, pattern, populations)
        ab, nd, yrs = _resume_signes(rows)
        if not rows:
            lignes.append(f"{label} : aucune donnée chez les porteurs avant la maladie dans la base actuelle.")
            continue
        art = len({r["pmid"] for r in rows})
        phrase = (f"{label} : {len(ab)} constat(s) d'anomalie et {len(nd)} sans différence, dans {art} étude(s)")
        if yrs:
            phrase += f" ; jusqu'à environ {_fmt(yrs)} ans avant le début dans les études qui le mesurent"
        lignes.append(phrase + ".")
        limit = None if detail == "detaille" else 3
        for r in (ab + nd)[:limit]:
            dir_ = {"abnormal": "anomalie", "no_difference": "pas de différence", "mixed": "résultats mixtes"}[r["direction"]]
            t = f"{r['sign']} — {dir_}"
            if detail == "detaille":
                t += f" ; {DOMAIN_LABELS.get(r['domain'], r['domain'])}, {r['population']}"
                if r["effect"]:
                    t += f" ; {r['effect']}"
                if r["timing"]:
                    t += f" ; {r['timing']}"
            items.append(_item(t, r))
    return {"id": titre.lower().replace(" ", "_"), "titre": titre,
            "texte": intro(st) + ("\n\n" + "\n".join("- " + l for l in lignes) if detail != "court" else ""),
            "items": items if detail != "court" else []}


def _intro_changements(st):
    if st in ("porteur", "apparente_porteur", "antecedents"):
        return ("Chez les porteurs, certains changements apparaissent des années avant le diagnostic, mais ce sont des "
                "différences de groupe : aucun de ces signes ne permet, seul, de dire si une personne est porteuse ou "
                "va tomber malade. Dans votre situation, un changement nouveau et persistant mérite d'être signalé "
                "à un médecin, idéalement dans un centre expert SLA ou mémoire.")
    if st == "non_porteur":
        return "Votre test étant négatif, ces changements ne sont pas liés à C9orf72 et doivent être explorés pour d'autres causes."
    return ("Ces changements sont fréquents dans la population générale et ont de nombreuses causes (stress, sommeil, "
            "humeur, autres maladies). Sans antécédent familial, ils n'augmentent pas de façon mesurable la "
            "probabilité de porter l'expansion, qui reste rare. Pour information, voici ce que la littérature "
            "observe chez les porteurs :")


def _intro_traits(st):
    return ("Les signes précoces décrits chez les porteurs sont surtout des **changements** par rapport à la personne "
            "d'avant, pas des traits présents toute la vie. Quelques études décrivent des traits de longue date ou "
            "des troubles psychiatriques plus fréquents chez des porteurs ou leurs apparentés ; ils restent "
            "non spécifiques et ne permettent aucune conclusion individuelle.")


LISIBLES = ("penetrance", "age_at_onset", "phenotype_als_vs_ftd", "psychiatric_presentation",
            "survival_progression", "cognitive_behavioural_profile")
POOLED = re.compile(r"non propres? [àa] C9|tous g[èe]nes|confondus|pool", re.I)


def _section_variabilite(con, detail):
    rows = _rows(con, "SELECT m.*, a.first_author, a.year FROM modifiers m JOIN articles a USING (pmid) "
                      "WHERE m.association IN ('associated','mixed') AND m.outcome != 'other'")
    if detail != "detaille":  # lecteur non spécialiste : phénotypes cliniques, résultats propres à C9, confiance suffisante
        rows = [r for r in rows if r["outcome"] in LISIBLES and r["confidence"] != "low"
                and not POOLED.search(r["effect"] or "")]
    groups = {}
    for r in rows:
        groups.setdefault((r["outcome"], r["modifier"].strip().lower()), []).append(r)
    top = sorted(groups.values(), key=lambda rs: -len({r["pmid"] for r in rs}))[: (None if detail == "detaille" else 8)]
    items = []
    for rs in top:
        t = (f"{OUTCOME_LABELS.get(rs[0]['outcome'], rs[0]['outcome'])} — {rs[0]['modifier']} "
             f"({len({r['pmid'] for r in rs})} étude(s))")
        items.append(_item(t + (f" : {rs[0]['effect']}" if detail == "detaille" else ""), rs[0]))
    return {"id": "variabilite", "titre": "Ce qui fait varier la maladie d'un porteur à l'autre",
            "texte": ("Âge de début, forme (SLA, DFT, les deux) et évolution varient même dans une famille. "
                      "Facteurs associés dans la base (le niveau « détaillé » donne les effets et tous les facteurs) :"),
            "items": items}


def _section_conseils(a, st):
    sympt = bool(a.get("changements"))
    c = []
    if st in ("porteur", "apparente_porteur", "antecedents"):
        c.append("Une consultation de génétique permet d'évaluer précisément le "
                 "risque familial et, si vous le souhaitez, d'accéder à un test présymptomatique, encadré par une "
                 "équipe pluridisciplinaire avec un temps de réflexion.")
        if sympt:
            c.append("Des changements récents dans votre situation justifient un avis médical (neurologue, centre "
                     "SLA ou centre mémoire), sans attendre.")
        c.append("Des cohortes de recherche (par exemple GENFI en Europe, ALLFTD en Amérique du Nord) suivent les "
                 "apparentés de porteurs ; votre équipe médicale peut vous orienter.")
    elif st == "non_porteur":
        c.append("Si des changements persistent, parlez-en à votre médecin : ils relèvent d'autres causes.")
    else:
        if sympt:
            c.append("Si des changements sont nouveaux, persistants ou remarqués par vos proches, parlez-en à votre "
                     "médecin traitant ; c'est la démarche normale, indépendamment de C9orf72.")
        c.append("Un test génétique n'est pas recommandé sans antécédent familial : il est réservé à des situations "
                 "précises et doit être prescrit dans un cadre médical.")
    return {"id": "conseils", "titre": "Que faire", "texte": "\n".join("- " + x for x in c), "items": []}


LIMITES = {"id": "limites", "titre": "Limites de cet outil",
           "texte": ("Cet outil résume une revue de littérature en cours, faite en partie automatiquement ; il n'est "
                     "pas un avis médical et ne pose aucun diagnostic. Il ne calcule aucune probabilité à partir des "
                     "signes ou des traits, car les études ne le permettent pas. Vos réponses restent dans votre "
                     "navigateur et sur cet ordinateur : rien n'est envoyé ailleurs."), "items": []}


def profil(con, a, detail="standard"):
    if detail not in DETAILS:
        raise ValueError(f"niveau de détail inconnu : {detail}")
    st = statut(a)
    sections = [_section_genetique(con, a, st, detail)]
    if st != "non_porteur" or a.get("changements"):
        s = _section_signes(con, a, st, detail, a.get("changements") or [], CHANGES, EARLY,
                            "Les changements que vous décrivez", _intro_changements)
        if s:
            sections.append(s)
    s = _section_signes(con, a, st, detail, a.get("traits") or [], TRAITS, LIFELONG,
                        "Vos traits de longue date", _intro_traits)
    if s:
        sections.append(s)
    if st in ("porteur", "apparente_porteur") and detail != "court":
        sections.append(_section_variabilite(con, detail))
    sections.append(_section_conseils(a, st))
    sections.append(LIMITES)
    resume = TITRES[st]
    p = prior_mendelien(a)
    if p:
        resume += f" : risque a priori d'avoir hérité de l'expansion {p} %, qui diminue avec l'âge sans symptôme"
    return {"statut": st, "resume": resume, "prior_mendelien": p, "detail": detail, "sections": sections}


def valider(a):
    """Ne garde que les réponses prévues par le questionnaire, avec des valeurs autorisées."""
    out = {}
    for q in QUESTIONS:
        v = a.get(q["id"])
        if v in (None, "", []):
            continue
        if q["type"] == "number":
            v = int(v)
            if not q["min"] <= v <= q["max"]:
                raise ValueError(f"{q['id']} hors limites")
        elif q["type"] == "bool":
            v = bool(v)
        elif q["type"] == "choice":
            if v not in [o[0] for o in q["options"]]:
                raise ValueError(f"{q['id']} : valeur inconnue")
        elif q["type"] == "multi":
            allowed = {o[0] for o in q["options"]}
            if not isinstance(v, list) or not set(v) <= allowed:
                raise ValueError(f"{q['id']} : valeur inconnue")
        out[q["id"]] = v
    return out


def markdown(res):
    """Rendu texte du profil (ligne de commande)."""
    L = [f"# {res['resume']}", ""]
    for s in res["sections"]:
        L += [f"## {s['titre']}", "", s["texte"], ""]
        for it in s["items"]:
            ref = it["ref"]
            L.append(f"- {it['texte']}" + (f" ({ref['auteur']} {ref['annee']}, PMID {ref['pmid']})" if ref else ""))
        if s["items"]:
            L.append("")
    return "\n".join(L)

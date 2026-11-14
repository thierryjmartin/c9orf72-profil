"""Génération du tableau des signes précoces (markdown) et des exports CSV."""
import csv

from . import DATA, DOMAINS, GENE_CFG, GENE_DIR, GENE_NAME, GENE_SHORT, ROOT

MUTATION = GENE_CFG.get("titre_mutation", GENE_NAME)   # « l'expansion C9orf72 »
OTHER_GENES = GENE_CFG.get("autres_genes", "autres gènes")

EARLY_POPULATIONS = ("presymptomatic_carriers", "prodromal_carriers", "carriers_retrospective")

DOMAIN_LABELS = {
    "cognition": "Cognition",
    "comportement_personnalite": "Comportement et personnalité",
    "psychiatrie": "Psychiatrie",
    "langage_parole": "Langage et parole",
    "moteur_neurophysiologie": "Motricité et neurophysiologie",
    "sommeil": "Sommeil",
    "autonome_metabolique": "Système autonome et métabolisme",
    "imagerie_structurelle": "Imagerie structurelle",
    "imagerie_fonctionnelle_eeg": "Imagerie fonctionnelle et EEG",
    "biomarqueurs_fluides": "Biomarqueurs (LCR, sang)",
    "sensoriel_oculomoteur": "Sensoriel et oculomoteur",
    "developpement_vie_entiere": "Neurodéveloppement et trajectoire de vie",
    "autre": "Autre",
}


def _ref(r):
    author = (r["first_author"] or "?").split()[0]
    return f"{author} {r['year'] or ''} ([{r['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{r['pmid']}/))"


def _fmt_years(v):
    return "" if v is None else f"{v:g}"


def generate(con):
    out_md = GENE_DIR / "syntheses" / "tableau-signes-precoces.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    exports = DATA / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    q = lambda sql: con.execute(sql).fetchone()[0]

    rows = con.execute(
        "SELECT f.*, a.first_author, a.year, a.title, s.cohort, s.design FROM findings f "
        "JOIN articles a USING (pmid) LEFT JOIN studies s USING (pmid)").fetchall()

    _csv(exports / "findings.csv", rows)
    _csv(exports / "studies.csv", con.execute(
        "SELECT s.*, a.first_author, a.year, a.title, a.doi FROM studies s JOIN articles a USING (pmid)").fetchall())

    L = [f"# Tableau des signes cliniques précoces associés à {MUTATION}", "",
         "*Fichier généré par `python -m biblio report` : ne pas éditer à la main.*", "",
         "## Avancement", "",
         "| Étape | Nombre |", "|---|---|",
         f"| Articles récoltés | {q('SELECT COUNT(*) FROM articles')} |",
         f"| Triés (titre/résumé) | {q('SELECT COUNT(*) FROM screening')} |",
         f"| Retenus | {q("SELECT COUNT(*) FROM screening WHERE decision='include'")} |",
         f"| Extraits | {q('SELECT COUNT(*) FROM studies WHERE design IS NOT NULL')} |",
         f"| Constats | {len(rows)} |", "",
         "Populations prises en compte comme « précoces » : porteurs présymptomatiques, porteurs prodromaux, "
         "signes reconstitués avant le début chez des porteurs devenus malades.", ""]

    early = [r for r in rows if r["population"] in EARLY_POPULATIONS]

    # Frise : constats avec un délai chiffré avant le début
    timed = sorted((r for r in early if r["years_before_onset"] is not None and r["direction"] != "no_difference"),
                   key=lambda r: -r["years_before_onset"])
    L += ["## Frise : signes anormaux avec délai estimé avant le début clinique", ""]
    if timed:
        L += ["| Années avant début | Domaine | Signe | Population | Référence |", "|---|---|---|---|---|"]
        for r in timed:
            L.append(f"| {_fmt_years(r['years_before_onset'])} | {DOMAIN_LABELS.get(r['domain'], r['domain'])} | "
                     f"{r['sign']} | {r['population']} | {_ref(r)} |")
    else:
        L.append("*Aucun constat daté pour l'instant.*")
    L.append("")

    # Synthèse par domaine et par signe
    L += ["## Synthèse par domaine", ""]
    for dom in DOMAINS:
        drows = [r for r in early if r["domain"] == dom]
        if not drows:
            continue
        L += [f"### {DOMAIN_LABELS[dom]}", "",
              "| Signe | Études | Anormal / sans différence | Délai max (années) | Populations | Références |",
              "|---|---|---|---|---|---|"]
        by_sign = {}
        for r in drows:
            by_sign.setdefault(r["sign"].strip().lower(), []).append(r)
        for sign, rs in sorted(by_sign.items(), key=lambda kv: -len({r["pmid"] for r in kv[1]})):
            pmids = {r["pmid"] for r in rs}
            ab = sum(r["direction"] in ("abnormal", "mixed") for r in rs)
            nd = sum(r["direction"] == "no_difference" for r in rs)
            yrs = [r["years_before_onset"] for r in rs if r["years_before_onset"] is not None]
            pops = sorted({r["population"] for r in rs})
            refs = []
            seen = set()
            for r in rs:
                if r["pmid"] not in seen:
                    seen.add(r["pmid"])
                    refs.append(_ref(r))
            L.append(f"| {rs[0]['sign']} | {len(pmids)} | {ab} / {nd} | {_fmt_years(max(yrs)) if yrs else ''} | "
                     f"{', '.join(pops)} | {'; '.join(refs)} |")
        L.append("")

    # Contexte familial / apparentés
    fam = [r for r in rows if r["population"] in ("relatives_untested", "noncarrier_relatives")]
    if fam:
        L += ["## Apparentés (non génotypés ou non porteurs)", "",
              "| Domaine | Signe | Population | Résultat | Référence |", "|---|---|---|---|---|"]
        for r in fam:
            L.append(f"| {DOMAIN_LABELS.get(r['domain'], r['domain'])} | {r['sign']} | {r['population']} | "
                     f"{r['direction']} | {_ref(r)} |")
        L.append("")

    out_md.write_text("\n".join(L))
    paths = [out_md, exports / "findings.csv", exports / "studies.csv"]
    paths += _penetrance(con, exports)
    paths += _variability(con, exports)
    paths += _treatments(con, exports)
    return [p.relative_to(ROOT) for p in paths]


def _csv(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        if rows:
            w.writerow(rows[0].keys())
            w.writerows([tuple(r) for r in rows])


ASCERTAINMENT_LABELS = {"familial": "familles", "population": "population générale", "clinic": "consultations", "mixed": "mixte"}


def _frac(r):
    return f"{r['n']}/{r['total']}" if r["n"] is not None and r["total"] else (str(r["n"]) if r["n"] is not None else "")


def _pct(r):
    if r["percent"] is not None:
        return f"{r['percent']:g} %"
    if r["n"] is not None and r["total"]:
        return f"{100 * r['n'] / r['total']:.1f} %"
    return ""


def _penetrance(con, exports):
    rows = con.execute("SELECT p.*, a.first_author, a.year FROM penetrance p JOIN articles a USING (pmid) "
                       "ORDER BY p.cumulative_risk IS NULL, p.age, p.outcome").fetchall()
    _csv(exports / "penetrance.csv", rows)
    L = [f"# Pénétrance de {MUTATION}", "",
         "*Fichier généré par `python -m biblio report` : ne pas éditer à la main.*", "",
         "Le recrutement (familles, population générale, consultations) influence fortement les estimations : "
         "les études familiales tendent à surestimer la pénétrance.", ""]
    num = [r for r in rows if r["cumulative_risk"] is not None]
    L += ["## Risque cumulé selon l'âge", ""]
    if num:
        L += ["| Âge | Risque cumulé | IC | Maladie | Recrutement | Sexe | Porteurs | Méthode | Référence |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in num:
            L.append(f"| {_fmt_years(r['age'])} | {r['cumulative_risk']:g} % | {r['ci'] or ''} | {r['outcome'] or ''} | "
                     f"{ASCERTAINMENT_LABELS.get(r['ascertainment'], r['ascertainment'] or '')} | {r['sex'] or 'tous'} | "
                     f"{r['n_carriers'] or ''} | {r['method'] or ''} | {_ref(r)} |")
    else:
        L.append("*Aucune estimation chiffrée pour l'instant.*")
    other = [r for r in rows if r["cumulative_risk"] is None]
    if other:
        L += ["", "## Autres observations", "", "| Observation | Recrutement | Porteurs | Référence |", "|---|---|---|---|"]
        for r in other:
            L.append(f"| {r['description'] or ''} | {ASCERTAINMENT_LABELS.get(r['ascertainment'], r['ascertainment'] or '')} | "
                     f"{r['n_carriers'] or ''} | {_ref(r)} |")
    freq = con.execute("SELECT f.*, a.first_author, a.year FROM frequencies f JOIN articles a USING (pmid) "
                       "WHERE f.kind='carrier_frequency' ORDER BY f.grp").fetchall()
    if freq:
        L += ["", "## Fréquence de l'expansion selon le groupe", "",
              "Utile pour situer la pénétrance : proportion de porteurs parmi les malades ou dans la population.", "",
              "| Groupe | Porteurs | % | Comparaison | Recrutement | Référence |", "|---|---|---|---|---|---|"]
        for r in freq:
            L.append(f"| {r['grp'] or ''} | {_frac(r)} | {_pct(r)} | {r['comparison'] or ''} | "
                     f"{ASCERTAINMENT_LABELS.get(r['ascertainment'], r['ascertainment'] or '')} | {_ref(r)} |")
    out = GENE_DIR / "syntheses" / "tableau-penetrance.md"
    out.write_text("\n".join(L) + "\n")
    return [out, exports / "penetrance.csv"]


OUTCOME_LABELS = {
    "penetrance": "Pénétrance (malade ou non)",
    "age_at_onset": "Âge de début",
    "phenotype_als_vs_ftd": "Phénotype SLA / DFT / SLA-DFT",
    "psychiatric_presentation": "Présentation psychiatrique",
    "cognitive_behavioural_profile": "Profil cognitif et comportemental",
    "survival_progression": "Survie et progression",
    "neuropathology": "Neuropathologie",
    "imaging_pattern": "Profil d'imagerie",
    "other": "Autre",
}
ASSOCIATION_LABELS = {"associated": "associé", "no_association": "pas d'association", "mixed": "résultats mixtes"}


def is_pooled_modifier(r):
    """Modificateur calculé hors des seuls porteurs du gène (règle 21) : affiché, mais pas compté."""
    pop = (r["population"] or "").strip().lower()
    return pop == "mixed" or pop.startswith("poolé") or pop.startswith("poole")


def _variability(con, exports):
    rows = con.execute("SELECT m.*, a.first_author, a.year FROM modifiers m JOIN articles a USING (pmid)").fetchall()
    _csv(exports / "modifiers.csv", rows)
    L = ["# Variabilité phénotypique : facteurs modificateurs", "",
         "*Fichier généré par `python -m biblio report` : ne pas éditer à la main.*", "",
         "Pour chaque phénotype expliqué : les facteurs étudiés, avec le nombre d'études qui trouvent "
         f"une association et le nombre qui n'en trouvent pas, **chez les porteurs {GENE_SHORT}**. Les résultats poolés "
         "(porteurs et non-porteurs, ou tous gènes) sont signalés à part (« + n poolés ») et ne sont pas comptés.", ""]
    if not rows:
        L.append("*Aucun facteur extrait pour l'instant.*")
    for outcome, label in OUTCOME_LABELS.items():
        orows = [r for r in rows if r["outcome"] == outcome]
        if not orows:
            continue
        L += [f"## {label}", "",
              "| Facteur | Type | Associé / non associé | Effet (exemple) | Références |", "|---|---|---|---|---|"]
        groups = {}
        for r in orows:
            groups.setdefault(r["modifier"].strip().lower(), []).append(r)
        for _, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            c9 = [r for r in rs if not is_pooled_modifier(r)]
            yes = sum(r["association"] in ("associated", "mixed") for r in c9)
            no = sum(r["association"] == "no_association" for r in c9)
            pooled = len(rs) - len(c9)
            refs = "; ".join(dict.fromkeys(_ref(r) for r in rs))
            L.append(f"| {rs[0]['modifier']} | {rs[0]['modifier_type']} | {yes} / {no}{f" (+ {pooled} poolé{'s' if pooled > 1 else ''})" if pooled else ""} | {(c9 or rs)[0]['effect'] or ''} | {refs} |")
        L.append("")
    freq = con.execute("SELECT f.*, a.first_author, a.year FROM frequencies f JOIN articles a USING (pmid) "
                       "WHERE f.kind IN ('phenotype_frequency', 'carrier_vs_noncarrier', 'carrier_vs_other_gene') "
                       "ORDER BY f.kind, f.feature").fetchall()
    for kind, title, intro in (
            ("phenotype_frequency", "Spectre phénotypique : fréquence des traits chez les porteurs",
             "Proportions descriptives, sans facteur explicatif."),
            ("carrier_vs_noncarrier", f"Phénotype des malades {GENE_SHORT} comparé aux malades non porteurs",
             f"Ce qui distingue la maladie {GENE_SHORT} ; ne dit pas pourquoi elle varie d'un porteur à l'autre."),
            ("carrier_vs_other_gene", f"Phénotype {GENE_SHORT} comparé aux autres gènes ({OTHER_GENES})",
             f"Signature propre à {GENE_SHORT} parmi les formes génétiques ; ne dit pas pourquoi elle varie d'un porteur à l'autre.")):
        fr = [r for r in freq if r["kind"] == kind]
        if not fr:
            continue
        L += [f"## {title}", "", intro, "",
              "| Trait | Groupe | n | % | Comparaison | Référence |", "|---|---|---|---|---|---|"]
        for r in fr:
            L.append(f"| {r['feature'] or ''} | {r['grp'] or ''} | {_frac(r)} | {_pct(r)} | {r['comparison'] or ''} | {_ref(r)} |")
        L.append("")
    _csv(exports / "frequencies.csv", freq + con.execute(
        "SELECT f.*, a.first_author, a.year FROM frequencies f JOIN articles a USING (pmid) "
        "WHERE f.kind='carrier_frequency'").fetchall())
    out = GENE_DIR / "syntheses" / "tableau-variabilite.md"
    out.write_text("\n".join(L) + "\n")
    return [out, exports / "modifiers.csv", exports / "frequencies.csv"]


AIM_LABELS = {"prevention": "Prévention (avant les symptômes)", "disease_modifying": "Chez les malades : agir sur la maladie",
              "symptomatic": "Chez les malades : soulager un symptôme"}
RESULT_LABELS = {"benefit": "effet favorable", "no_benefit": "pas d'effet", "harm": "défavorable ou toxique",
                 "mixed": "résultats mixtes", "safety_only": "tolérance seule", "target_engagement": "agit sur sa cible"}


def _treatments(con, exports):
    from .essais import STATUS_LABELS
    rows = con.execute("SELECT t.*, a.first_author, a.year FROM treatments t JOIN articles a USING (pmid) "
                       "ORDER BY t.aim, t.intervention, a.year").fetchall()
    _csv(exports / "treatments.csv", rows)
    trials = con.execute("SELECT * FROM trials ORDER BY aim DESC, status, nct").fetchall()
    _csv(exports / "trials.csv", trials)
    L = [f"# Traitements étudiés chez les porteurs de {MUTATION}", "",
         "*Fichier généré par `python -m biblio report` : ne pas éditer à la main.*", "",
         "Études publiées chez l'humain (essais, cohortes traitées, cas), puis essais enregistrés sur ClinicalTrials.gov.", ""]
    if not rows:
        L.append("*Aucun traitement extrait pour l'instant.*")
    for aim, label in AIM_LABELS.items():
        arows = [r for r in rows if r["aim"] == aim]
        if not arows:
            continue
        L += [f"## {label}", "", "| Traitement | Type | Phase | Résultat | Effet | Porteurs | Référence |",
              "|---|---|---|---|---|---|---|"]
        for r in arows:
            L.append(f"| {r['intervention'] or ''} | {r['intervention_type'] or ''} | {r['phase'] or ''} | "
                     f"{RESULT_LABELS.get(r['result'], r['result'] or '')} | {r['effect'] or ''} | {r['n_carriers'] or ''} | "
                     f"{_ref(r)} |")
        L.append("")
    L += ["## Essais enregistrés (ClinicalTrials.gov)", ""]
    if trials:
        L += ["| Essai | Visée | Phase | Statut | Traitement | Promoteur |", "|---|---|---|---|---|---|"]
        for r in trials:
            L.append(f"| [{r['nct']}](https://clinicaltrials.gov/study/{r['nct']}) {r['title'] or ''} | "
                     f"{'prévention' if r['aim'] == 'prevention' else 'malades'} | {r['phase'] or ''} | "
                     f"{STATUS_LABELS.get(r['status'], r['status'] or '')} | {r['interventions'] or ''} | {r['sponsor'] or ''} |")
    else:
        L.append("*Aucun essai enregistré trouvé (`python3 -m biblio essais`).*")
    out = GENE_DIR / "syntheses" / "tableau-traitements.md"
    out.write_text("\n".join(L) + "\n")
    return [out, exports / "treatments.csv", exports / "trials.csv"]

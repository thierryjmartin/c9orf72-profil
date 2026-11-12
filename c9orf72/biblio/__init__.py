"""Framework de revue de littérature génétique : récolte PubMed, tri, extraction, rapports, site public.

Un dossier par gène (genes/<gène>/ : fiche gene.toml, branches.toml, données, audits) ; le gène est choisi par
`python3 -m biblio --gene <gène> …` ou la variable BIBLIO_GENE (C9orf72 par défaut).
"""
import os
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENE = os.environ.get("BIBLIO_GENE", "c9orf72").lower()
GENE_DIR = ROOT / "genes" / GENE
DATA = GENE_DIR / "data"
CONFIG = GENE_DIR / "branches.toml"
DB_PATH = DATA / "biblio.sqlite"


def _gene_config():
    try:
        return tomllib.loads((GENE_DIR / "gene.toml").read_text())
    except OSError:   # questionnaire statique (Pyodide) : pas de fichiers, la fiche n'y sert pas
        return {}


GENE_CFG = _gene_config()
GENE_NAME = GENE_CFG.get("name", GENE)
GENE_SHORT = GENE_CFG.get("court", GENE_NAME)

AXES = [
    "signes_precoces",   # signes avant le diagnostic
    "penetrance",        # qui tombe malade, à quel âge
    "variabilite",       # pourquoi le phénotype diffère d'un porteur à l'autre
]

# Axe variabilité/pénétrance : facteur étudié et phénotype expliqué. Les types propres à un gène (taille de
# l'expansion, allèles intermédiaires…) sont ajoutés par sa fiche (gene.toml, [vocabulaire] modifier_types).
MODIFIER_TYPES = [
    "methylation",            # méthylation du locus ou épigénétique
    "genetic_modifier",       # gène modificateur (TMEM106B, ATXN2, UNC13A…)
    "polygenic_score",
    "haplotype_ancestry",     # haplotype fondateur, origine
    "sex",
    "age",
    "parental_transmission",  # anticipation, sexe du parent transmetteur
    "environment_lifestyle",
    "comorbidity",
    "molecular_pathology",    # DPR, foci d'ARN, TDP-43, répartition lésionnelle
    "other",
] + GENE_CFG.get("vocabulaire", {}).get("modifier_types", [])

OUTCOMES = [
    "penetrance",                    # malade ou non
    "age_at_onset",
    "phenotype_als_vs_ftd",
    "psychiatric_presentation",
    "cognitive_behavioural_profile",
    "survival_progression",
    "neuropathology",
    "imaging_pattern",
    "other",
]

ASSOCIATIONS = ["associated", "no_association", "mixed"]
ASCERTAINMENTS = ["familial", "population", "clinic", "mixed"]
FREQ_KINDS = [
    "carrier_frequency",      # fréquence de l'expansion dans un groupe (SLP, SLA sporadiques, population…)
    "phenotype_frequency",    # fréquence d'un trait chez les porteurs C9 (psychose, début bulbaire…)
    "carrier_vs_noncarrier",  # trait du phénotype C9 comparé aux malades non porteurs
    "carrier_vs_other_gene",  # trait du phénotype C9 comparé aux porteurs d'autres gènes (GRN, MAPT, SOD1…)
    "cohort_composition",     # part des C9 parmi les porteurs recrutés d'une cohorte multigène : pas une fréquence
]

DOMAINS = [
    "cognition",
    "comportement_personnalite",
    "psychiatrie",
    "langage_parole",
    "moteur_neurophysiologie",
    "sommeil",
    "autonome_metabolique",
    "imagerie_structurelle",
    "imagerie_fonctionnelle_eeg",
    "biomarqueurs_fluides",
    "sensoriel_oculomoteur",
    "developpement_vie_entiere",
    "autre",
]

POPULATIONS = [
    "presymptomatic_carriers",     # porteurs sans symptôme
    "prodromal_carriers",          # porteurs avec signes légers / MBI / MCI, avant diagnostic
    "carriers_retrospective",      # signes reconstitués avant le début chez des porteurs devenus malades
    "symptomatic_carriers",        # porteurs malades (sert de référence, pas un signe précoce)
    "relatives_untested",          # apparentés non génotypés
    "noncarrier_relatives",        # apparentés non porteurs (contrôle familial)
    "mixed",
]

DIRECTIONS = ["abnormal", "no_difference", "mixed"]

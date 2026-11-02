"""Framework de revue de littérature C9orf72 : récolte PubMed, tri, extraction, rapports."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CONFIG = ROOT / "config" / "branches.toml"
DB_PATH = DATA / "biblio.sqlite"

AXES = [
    "signes_precoces",   # signes avant le diagnostic
    "penetrance",        # qui tombe malade, à quel âge
    "variabilite",       # pourquoi le phénotype diffère d'un porteur à l'autre
]

# Axe variabilité/pénétrance : facteur étudié et phénotype expliqué
MODIFIER_TYPES = [
    "repeat_size",            # taille de l'expansion
    "somatic_instability",    # instabilité / mosaïcisme somatique
    "methylation",            # méthylation du locus ou épigénétique
    "intermediate_allele",    # allèles intermédiaires
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
]

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

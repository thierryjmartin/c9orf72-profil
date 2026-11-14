# Jeu de données « GRN en clair »

Résultats extraits d'une revue systématique vivante de la littérature PubMed sur les mutations du gène GRN (démence frontotemporale).
Méthode, limites et diagramme PRISMA : https://thierryjmartin.github.io/c9orf72-profil/grn/s/methode.html

CSV en UTF-8, séparateur virgule. Toutes les lignes portent le `pmid` de l'article
(https://pubmed.ncbi.nlm.nih.gov/PMID/). Les textes libres (`sign`, `effect`, `summary`…) sont en français ; `quote`
est une phrase copiée mot pour mot de l'article (en anglais), qui appuie la ligne. Une cellule vide = inconnu ou sans
objet. `confidence` : `high` (texte intégral, résultat principal), `medium` (résumé seul ou résultat secondaire),
`low` (interprétation incertaine, moins de 10 porteurs, sous-groupe GRN mal séparé).

| Fichier | Lignes | Contenu |
|---|---|---|
| `studies.csv` | 138 | Une ligne par article lu : plan d'étude, cohorte, pays, effectifs de porteurs (`n_presymptomatic` inclut les prodromiques), texte lu (`source_text` : `fulltext`, `abstract` ou `title`), résumé. Un `design` vide = article exclu à la lecture (raison dans `notes`). |
| `findings.csv` | 465 | Signes observés chez les porteurs : un signe × une population × une comparaison. |
| `penetrance.csv` | 11 | Estimations de pénétrance (risque cumulé à un âge donné) ou descriptions de porteurs restés indemnes. |
| `modifiers.csv` | 89 | Facteurs qui expliquent une variation entre porteurs (âge de début, forme SLA ou DFT, survie…). |
| `frequencies.csv` | 319 | Fréquences descriptives : de la mutation dans un groupe, d'un trait chez les porteurs, comparaisons avec les non-porteurs ou d'autres gènes. |
| `treatments.csv` | 10 | Traitements étudiés chez l'humain : un traitement × une population × un critère, avec sa visée et son résultat. |
| `trials.csv` | 11 | Essais enregistrés sur ClinicalTrials.gov qui mentionnent GRN (sélection automatique, sans lecture) : statut, phase, visée, traitements, promoteur. |

## Colonnes principales

- `findings.csv` : `domain` (`cognition`, `comportement_personnalite`, `psychiatrie`, `langage_parole`, `moteur_neurophysiologie`, `sommeil`, `autonome_metabolique`, `imagerie_structurelle`, `imagerie_fonctionnelle_eeg`, `biomarqueurs_fluides`, `sensoriel_oculomoteur`, `developpement_vie_entiere`, `autre`) ; `population` (`presymptomatic_carriers`, `prodromal_carriers`, `carriers_retrospective`, `symptomatic_carriers`, `relatives_untested`, `noncarrier_relatives`, `mixed`) ; `direction` (`abnormal`, `no_difference`, `mixed`) ;
  `years_before_onset` (années avant le début, seulement si l'article le donne pour des porteurs GRN ; la
  référence du délai est dans `timing`) ; `n_carriers`, `n_comparison` (effectifs).
- `penetrance.csv` : `ascertainment` (`familial`, `population`, `clinic`, `mixed` : façon dont les porteurs ont été trouvés, qui change le
  sens du chiffre) ; `outcome` ; `age` et `cumulative_risk` (en %) ; `ci` ; `method`.
- `modifiers.csv` : `modifier_type` (`methylation`, `genetic_modifier`, `polygenic_score`, `haplotype_ancestry`, `sex`, `age`, `parental_transmission`, `environment_lifestyle`, `comorbidity`, `molecular_pathology`, `other`) ; `outcome` (`penetrance`, `age_at_onset`, `phenotype_als_vs_ftd`, `psychiatric_presentation`, `cognitive_behavioural_profile`, `survival_progression`, `neuropathology`, `imaging_pattern`, `other`) ; `association`
  (`associated`, `no_association`, `mixed`). Une `population` égale à `mixed` ou qui commence par « poolé » signale un calcul hors des
  seuls porteurs GRN (tous gènes confondus).
- `treatments.csv` : `aim` (`prevention`, `disease_modifying`, `symptomatic`) ; `intervention_type` (`antisense`, `gene_therapy`, `antibody`, `small_molecule`, `cell_therapy`, `non_drug`, `other`) ; `result`
  (`benefit`, `no_benefit`, `harm`, `mixed`, `safety_only`, `target_engagement`) ; `trial_id` (numéro ClinicalTrials.gov, s'il est donné).
- `trials.csv` : `status` (statut du registre) ; `aim` (`prevention` si l'essai vise des porteurs sans symptôme) ;
  `first_seen` et `status_changed` (dates vues par la revue, pas par le registre).
- `frequencies.csv` : `kind` (`carrier_frequency`, `phenotype_frequency`, `carrier_vs_noncarrier`, `carrier_vs_other_gene`, `cohort_composition`) ; `grp` (groupe dénominateur) ; `feature` (ce qui est compté) ; `n`,
  `total`, `percent` ; `comparison`.

Les articles sont rattachés à une ou plusieurs des questions de la revue (`signes_precoces`, `penetrance`, `variabilite`, `traitements`).

## Limites

Le tri et l'extraction sont faits par un modèle de langage (Claude, Anthropic) selon des protocoles écrits. Les
citations sont vérifiées automatiquement contre le texte de l'article et des échantillons sont relus par des audits,
mais il n'y a pas de double lecture humaine systématique. Ce jeu de données n'est pas validé par des pairs et ne
constitue pas un avis médical.

## Licence et citation

CC BY 4.0 (voir `LICENSE` à la racine), sauf les citations d'articles (`quote`), qui restent la propriété de leurs
auteurs. Citer : Martin T. *Génétique en clair : revues systématiques vivantes de la littérature, gène par gène* [jeu de données]. Zenodo. https://doi.org/10.5281/zenodo.24153922 (DOI de toutes les versions ; la page Zenodo donne
aussi celui de chaque version).

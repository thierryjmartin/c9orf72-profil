# Jeu de données « C9orf72 en clair »

Résultats extraits d'une revue systématique vivante de la littérature PubMed sur l'expansion C9orf72 (SLA, démence frontotemporale).
Méthode, limites et diagramme PRISMA : https://thierryjmartin.github.io/c9orf72-profil/c9orf72/s/methode.html

CSV en UTF-8, séparateur virgule. Toutes les lignes portent le `pmid` de l'article
(https://pubmed.ncbi.nlm.nih.gov/PMID/). Les textes libres (`sign`, `effect`, `summary`…) sont en français ; `quote`
est une phrase copiée mot pour mot de l'article (en anglais), qui appuie la ligne. Une cellule vide = inconnu ou sans
objet. `confidence` : `high` (texte intégral, résultat principal), `medium` (résumé seul ou résultat secondaire),
`low` (interprétation incertaine, moins de 10 porteurs, sous-groupe C9orf72 mal séparé).

| Fichier | Lignes | Contenu |
|---|---|---|
| `studies.csv` | 930 | Une ligne par article lu : plan d'étude, cohorte, pays, effectifs de porteurs (`n_presymptomatic` inclut les prodromiques), texte lu (`source_text` : `fulltext`, `abstract` ou `title`), résumé. Un `design` vide = article exclu à la lecture (raison dans `notes`). |
| `findings.csv` | 1148 | Signes observés chez les porteurs : un signe × une population × une comparaison. |
| `penetrance.csv` | 131 | Estimations de pénétrance (risque cumulé à un âge donné) ou descriptions de porteurs restés indemnes. |
| `modifiers.csv` | 864 | Facteurs qui expliquent une variation entre porteurs (âge de début, forme SLA ou DFT, survie…). |
| `frequencies.csv` | 1977 | Fréquences descriptives : de la mutation dans un groupe, d'un trait chez les porteurs, comparaisons avec les non-porteurs ou d'autres gènes. |

## Colonnes principales

- `findings.csv` : `domain` (`cognition`, `comportement_personnalite`, `psychiatrie`, `langage_parole`, `moteur_neurophysiologie`, `sommeil`, `autonome_metabolique`, `imagerie_structurelle`, `imagerie_fonctionnelle_eeg`, `biomarqueurs_fluides`, `sensoriel_oculomoteur`, `developpement_vie_entiere`, `autre`) ; `population` (`presymptomatic_carriers`, `prodromal_carriers`, `carriers_retrospective`, `symptomatic_carriers`, `relatives_untested`, `noncarrier_relatives`, `mixed`) ; `direction` (`abnormal`, `no_difference`, `mixed`) ;
  `years_before_onset` (années avant le début, seulement si l'article le donne pour des porteurs C9orf72 ; la
  référence du délai est dans `timing`) ; `n_carriers`, `n_comparison` (effectifs).
- `penetrance.csv` : `ascertainment` (`familial`, `population`, `clinic`, `mixed` : façon dont les porteurs ont été trouvés, qui change le
  sens du chiffre) ; `outcome` ; `age` et `cumulative_risk` (en %) ; `ci` ; `method`.
- `modifiers.csv` : `modifier_type` (`methylation`, `genetic_modifier`, `polygenic_score`, `haplotype_ancestry`, `sex`, `age`, `parental_transmission`, `environment_lifestyle`, `comorbidity`, `molecular_pathology`, `other`, `repeat_size`, `somatic_instability`, `intermediate_allele`) ; `outcome` (`penetrance`, `age_at_onset`, `phenotype_als_vs_ftd`, `psychiatric_presentation`, `cognitive_behavioural_profile`, `survival_progression`, `neuropathology`, `imaging_pattern`, `other`) ; `association`
  (`associated`, `no_association`, `mixed`). Une `population` égale à `mixed` ou qui commence par « poolé » signale un calcul hors des
  seuls porteurs C9orf72 (tous gènes confondus).
- `frequencies.csv` : `kind` (`carrier_frequency`, `phenotype_frequency`, `carrier_vs_noncarrier`, `carrier_vs_other_gene`, `cohort_composition`) ; `grp` (groupe dénominateur) ; `feature` (ce qui est compté) ; `n`,
  `total`, `percent` ; `comparison`.

Les articles sont rattachés à une ou plusieurs des questions de la revue (`signes_precoces`, `penetrance`, `variabilite`).

## Limites

Le tri et l'extraction sont faits par un modèle de langage (Claude, Anthropic) selon des protocoles écrits. Les
citations sont vérifiées automatiquement contre le texte de l'article et des échantillons sont relus par des audits,
mais il n'y a pas de double lecture humaine systématique. Ce jeu de données n'est pas validé par des pairs et ne
constitue pas un avis médical.

## Licence et citation

CC BY 4.0 (voir `LICENSE` à la racine), sauf les citations d'articles (`quote`), qui restent la propriété de leurs
auteurs. Citer : Martin T. *Génétique en clair : revues systématiques vivantes de la littérature, gène par gène* [jeu de données]. Zenodo. https://doi.org/10.5281/zenodo.24153922 (DOI de toutes les versions ; la page Zenodo donne
aussi celui de chaque version).

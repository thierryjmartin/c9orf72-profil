# Génétique en clair

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24153922.svg)](https://doi.org/10.5281/zenodo.24153922)

**Site : https://thierryjmartin.github.io/c9orf72-profil/**

Ce que la recherche publiée dit de gènes de maladies génétiques de l'adulte, un sous-site par gène, expliqué
simplement et vérifiable jusqu'à la phrase de chaque article :

- **Qui tombe malade, et à quel âge ?** Les estimations de pénétrance publiées, et pourquoi elles varient autant
  selon la façon dont les porteurs ont été trouvés.
- **Que voit-on avant les premiers symptômes ?** Les différences observées chez des porteurs encore en bonne
  santé (imagerie, sang, cognition, comportement, psychiatrie…), y compris les résultats négatifs.
- **Pourquoi la même mutation donne-t-elle des maladies différentes ?** Les facteurs étudiés (gènes modificateurs,
  sexe, caractéristiques de la mutation…) et ce qu'en disent les études.
- **Explorer** : recherche libre dans tous les constats extraits, avec lien PubMed.

<!-- GENES : tableau généré par biblio/pages.py (write_root) -->
| Gène | Sous-site | Données |
|---|---|---|
| *C9orf72* (l'expansion C9orf72 ; SLA, démence frontotemporale) | [`c9orf72/`](https://thierryjmartin.github.io/c9orf72-profil/c9orf72/) | [`c9orf72/donnees/`](c9orf72/donnees/) |
<!-- /GENES -->

Le sous-site C9orf72 a aussi un **questionnaire** (`c9orf72/profil.html`) qui situe une personne au regard de la
littérature. Le calcul s'exécute dans le navigateur ([Pyodide](https://pyodide.org)) ; aucune réponse n'est envoyée
ni enregistrée. Le seul calcul de risque est mendélien (lien de parenté avec un porteur connu) : aucune probabilité
n'est tirée des symptômes. Jusqu'au 12/11/2026, le site C9orf72 était à la racine : ses anciennes adresses
redirigent vers `c9orf72/`.

**Ce n'est pas un avis médical.** Les études décrivent des groupes, pas des individus. Pour une question de risque
familial ou de test génétique, consulter un service de génétique.

Les données viennent de revues de littérature personnelles, réalisées automatiquement (tri, extraction et synthèses
par IA selon des protocoles écrits, citations vérifiées mot pour mot, audits réguliers). Elles ne sont pas validées
par des pairs. Ce dépôt est mis à jour automatiquement à mesure qu'elles avancent.

## Données

Chaque gène a son dossier `<gène>/donnees/` : le jeu de données complet en CSV (UTF-8), une ligne par résultat
extrait, chaque résultat avec son PMID et une citation exacte de l'article. `LISEZMOI.md` y décrit les fichiers et
les colonnes. La méthode et le diagramme de flux PRISMA, recalculé à chaque mise à jour, sont sur la page Méthode de
chaque sous-site ([C9orf72](https://thierryjmartin.github.io/c9orf72-profil/c9orf72/s/methode.html)).

## Citer

Les versions de ce dépôt sont archivées sur [Zenodo](https://doi.org/10.5281/zenodo.24153922), avec un identifiant
DOI permanent :

> Martin T. *Génétique en clair : revues systématiques vivantes de la littérature, gène par gène* [jeu de données].
> Zenodo. https://doi.org/10.5281/zenodo.24153922

Ce DOI désigne toutes les versions et mène toujours à la plus récente ; la page Zenodo donne aussi le DOI de chaque
version, à citer pour une analyse reproductible. Le bouton « Cite this repository » de GitHub donne la même
référence ([`CITATION.cff`](CITATION.cff)).

## Licence

Données, synthèses et textes : [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr), réutilisation libre
à condition de citer la source. Les citations d'articles (colonne `quote`) restent la propriété de leurs auteurs et
sont reproduites au titre du droit de courte citation. Voir [`LICENSE`](LICENSE).

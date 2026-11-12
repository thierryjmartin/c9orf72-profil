# C9orf72 en clair

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24153922.svg)](https://doi.org/10.5281/zenodo.24153922)

**Site : https://thierryjmartin.github.io/c9orf72-profil/**

Ce que la recherche publiée dit de l'expansion GGGGCC du gène *C9orf72*, cause génétique la plus fréquente de
sclérose latérale amyotrophique (SLA) et de démence frontotemporale (DFT), expliqué simplement et vérifiable
jusqu'à la phrase de chaque article :

- **Qui tombe malade, et à quel âge ?** Les estimations de pénétrance publiées, et pourquoi elles varient autant
  selon la façon dont les porteurs ont été trouvés.
- **Que voit-on avant les premiers symptômes ?** Les différences observées chez des porteurs encore en bonne
  santé (imagerie, sang, cognition, comportement, psychiatrie…), y compris les résultats négatifs.
- **Pourquoi la même mutation donne-t-elle des maladies différentes ?** Les facteurs étudiés (taille de
  l'expansion, gènes modificateurs, sexe…) et ce qu'en disent les études.
- **Explorer** : recherche libre dans tous les constats extraits, avec lien PubMed.
- **Questionnaire** (`profil.html`) : situe une personne au regard de la littérature. Le calcul s'exécute dans le
  navigateur ([Pyodide](https://pyodide.org)) ; aucune réponse n'est envoyée ni enregistrée. Le seul calcul de
  risque est mendélien (lien de parenté avec un porteur connu) : aucune probabilité n'est tirée des symptômes.

**Ce n'est pas un avis médical.** Les études décrivent des groupes, pas des individus. Pour une question de risque
familial ou de test génétique, consulter un service de génétique.

Les données viennent d'une revue de littérature personnelle, réalisée en partie automatiquement (tri et extraction
assistés par IA selon un protocole écrit, citations vérifiées mot pour mot, audits réguliers). Elle n'est pas
validée par des pairs. Ce dépôt est mis à jour automatiquement à mesure qu'elle avance.

## Données

Le dossier [`donnees/`](donnees/) contient le jeu de données complet en CSV (UTF-8), une ligne par résultat extrait,
chaque résultat avec son PMID et une citation exacte de l'article. Voir [`donnees/LISEZMOI.md`](donnees/LISEZMOI.md)
pour la description des fichiers et des colonnes. La méthode et le diagramme de flux PRISMA, recalculé à chaque mise à
jour, sont sur la page [Méthode](https://thierryjmartin.github.io/c9orf72-profil/s/methode.html).

## Citer

Les versions de ce dépôt sont archivées sur [Zenodo](https://doi.org/10.5281/zenodo.24153922), avec un identifiant
DOI permanent :

> Martin T. *C9orf72 en clair : revue systématique vivante de la littérature sur l'expansion C9orf72* [jeu de
> données]. Zenodo. https://doi.org/10.5281/zenodo.24153922

Ce DOI désigne toutes les versions et mène toujours à la plus récente ; la page Zenodo donne aussi le DOI de chaque
version, à citer pour une analyse reproductible. Le bouton « Cite this repository » de GitHub donne la même
référence ([`CITATION.cff`](CITATION.cff)).

## Licence

Données, synthèses et textes : [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr), réutilisation libre
à condition de citer la source. Les citations d'articles (colonne `quote`) restent la propriété de leurs auteurs et
sont reproduites au titre du droit de courte citation. Voir [`LICENSE`](LICENSE).

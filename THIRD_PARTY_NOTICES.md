# Third-Party Notices

Ce fichier sépare explicitement :

- la licence du code de ce dépôt ;
- l'origine des artefacts tiers archivés localement ;
- leurs checksums ;
- la politique de redistribution retenue ici ;
- leur date d'acquisition / d'archivage dans le dépôt.

## Code du dépôt

Le code source de `temporal-chaos-testing` est distribué sous double licence MIT ou Apache-2.0, au choix de l'utilisateur. Voir `LICENSE`, `LICENSE-MIT` et `LICENSE-APACHE`.

## Kernels publics NAIF archivés localement

Les fichiers ci-dessous présents dans `partie-aerospatiale/kernels/` ne relèvent pas de la licence MIT/Apache du code du dépôt. Ils restent des artefacts tiers, conservés séparément du code pour rendre la démonstration SPICE reproductible hors-ligne.

| Fichier | Type | Origine | SHA-256 | Date d'acquisition / archivage | Politique de redistribution retenue ici |
|---|---|---|---|---|---|
| `partie-aerospatiale/kernels/naif0012.tls` | LSK | `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls` | `678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b` | `2026-07-21` | copie publique archivée sans modification ; vérifier les conditions d'utilisation NAIF pour tout autre usage |
| `partie-aerospatiale/kernels/vg100051.tsc` | SCLK Voyager 1 | `https://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/sclk/vg100051.tsc` | `036f5eeee519b6abae055b486e1d9e3c9531588d55ebd6da1956127baa03d1b7` | `2026-07-21` | copie publique archivée sans modification ; vérifier les conditions d'utilisation NAIF pour tout autre usage |

## Conditions d'utilisation et redistribution

- Ces kernels sont fournis ici comme données publiques d'origine NAIF/JPL afin de rendre la démonstration temporelle reproductible.
- Ce dépôt n'accorde aucun droit supplémentaire sur ces artefacts au-delà de leur mise à disposition publique d'origine et de la documentation NAIF associée.
- Toute réutilisation, redistribution élargie ou intégration dans un autre produit doit être relue à la lumière des conditions publiées par NAIF/JPL et de la provenance exacte des fichiers.
- Les checksums SHA-256 ci-dessus sont la référence de vérification utilisée par le manifeste `partie-aerospatiale/manifest.json`.

## Source de vérité compagnon

Le manifeste `partie-aerospatiale/manifest.json` reste la source de vérité opérationnelle pour :

- les noms de kernels ;
- leur URL d'origine ;
- leurs checksums SHA-256 ;
- la fenêtre temporelle pédagogique retenue ;
- les sorties de référence de la démonstration.
# Partie V — Le temps hors de la Terre

Code compagnon de la partie aérospatiale du livre : échelles de temps
astronomiques, SPICE, CCSDS, logiciels de vol et temps lunaire coordonné.

## SPICE en deux mots

**SPICE** (NAIF/JPL) est largement utilisé, notamment dans l'écosystème
NASA/JPL et par de nombreuses missions, pour la géométrie et les conversions
associées au temps. Tout y est fichier de données — un **kernel** :

| Kernel | Contenu | Rôle temporel |
|---|---|---|
| **LSK** (leapseconds) | Table des secondes intercalaires | Conversion UTC ↔ ET/TDB |
| **SCLK** (spacecraft clock) | Coefficients de corrélation horloge bord/sol | Conversion SCLK ↔ ET |
| SPK / CK | Éphémérides / attitude | Données géométriques indexées par le temps |

La question « quelle heure était-il à bord quand cette image a été prise ? »
n'est pas une question d'horloge mais de **base de données** : on convertit le
compte brut de l'horloge bord (SCLK) en temps des éphémérides (ET/TDB) via le
kernel SCLK, entretenu au sol par corrélation régulière — car l'oscillateur de
la sonde dérive, lui aussi.

## Démo

`spice_time_demo.py` convertit UTC → ET → SCLK (Voyager 1) avec
[spiceypy](https://github.com/AndrewAnnex/SpiceyPy) en lisant
`manifest.json` comme source de vérité :

```bash
pip install spiceypy
python3 spice_time_demo.py --download
python3 spice_time_demo.py
```

Le premier appel télécharge les kernels publics NAIF manquants et vérifie leurs
SHA-256. Les kernels archivés localement dans `kernels/` permettent ensuite une
exécution hors-ligne ; le script refuse de s'exécuter si les fichiers locaux ne
correspondent pas aux checksums attendus.

Le manifeste définit aussi une fenêtre pédagogique défendable et un cas de
référence historique (`1979-01-09T12:00:00`). Le programme génère un
meta-kernel valide (`\begindata` / `\begintext`), vérifie que la date choisie
reste dans cette fenêtre, contrôle la partition SCLK et compare les sorties à
des valeurs de référence avec tolérances documentées. Cette condition ne
certifie toujours ni la qualité opérationnelle complète d'une corrélation SCLK,
ni l'adéquation d'un traitement scientifique réel ; elle rend simplement la
démonstration reproductible et falsifiable.

## Références pour la rédaction de la partie

- NAIF / SPICE : <https://naif.jpl.nasa.gov/naif/toolkit.html> (tutoriels « Time » et « SCLK »)
- CCSDS 301.0-B « Time Code Formats » (CUC, CDS)
- ARINC 653, DO-178C (avionique), TTEthernet (Orion)
- cFS (NASA), F´ (JPL), RTEMS — gestion du temps bord
- Temps lunaire coordonné (LTC) : mémo OSTP d'avril 2024, travaux LunaNet
- Cas d'étude : Deep Impact (2013, hypothèse prudente de problème de
  time-tagging/compteur, cause exacte non déterminée publiquement),
  Patriot/Dhahran (1991), GPS week rollover (2019)

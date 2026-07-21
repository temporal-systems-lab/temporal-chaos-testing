# Changelog

## 0.2.0 - 2026-07-20

- Ajout des scénarios packagés `holdover`, `leap-smear-mismatch`, `certificate-expiry`, `lease-pause`, `jwt-totp-skew` et `pedagogical-grandmaster-failover`.
- Extension de la CLI et des tests pour couvrir les budgets de skew applicatifs, les fenêtres de validité et les bascules de grandmaster PTP.
- Mise à jour de la documentation publique du laboratoire de chaos temporel.

## 0.1.0 - 2026-07-10

- Initialisation du dépôt séparé `temporal-chaos-testing`.
- Extraction des scénarios `libfaketime`, horloges contrôlées et démonstrations SPICE hors de `temporal-traps`.
- Ajout d'une CLI Python minimale pour lister et lancer les scénarios de laboratoire.
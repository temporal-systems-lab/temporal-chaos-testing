# Temporal-Chaos-Testing

Laboratoire de chaos temporel et de démonstrations injectées pour tests en
environnement isolé.

Ce dépôt isole les scénarios qui ne doivent pas être confondus avec le noyau
pédagogique ni avec l'outillage d'audit read-only : injections `libfaketime`,
horloges contrôlées, holdover, leap smear incompatible, expiration de
certificats, leases, JWT/TOTP, bascule de grandmaster PTP et démonstration
SPICE avec téléchargement de kernels.

## Sécurité d'exécution

- exécutez ces scénarios dans une VM, un conteneur ou un environnement jetable ;
- ne lancez pas ces commandes sur un hôte de production ;
- privilégiez les horloges injectables et `libfaketime` à toute mutation de
  l'horloge système réelle.

Règle de frontière :
- un scénario injecté, une horloge contrôlée ou une démonstration SPICE vit ici ;
- un algorithme ou une API applicative reste dans `temporal-traps` ;
- une sonde ou un gabarit d'exploitation read-only reste dans `temporal-audit-toolkit`.

## Quick start

```bash
make verify
PYTHONPATH=src python3 -m temporal_chaos_testing.cli list
PYTHONPATH=src python3 -m temporal_chaos_testing.cli controlled-clock
PYTHONPATH=src python3 -m temporal_chaos_testing.cli holdover
PYTHONPATH=src python3 -m temporal_chaos_testing.cli leap-smear-mismatch
PYTHONPATH=src python3 -m temporal_chaos_testing.cli ptp-grandmaster-failover
PYTHONPATH=src python3 -m temporal_chaos_testing.cli faketime --ack-lab-risk
```

La démonstration SPICE reste optionnelle, mais elle est désormais pilotée par
un manifeste versionné, écrit un meta-kernel temporaire, vérifie les SHA-256,
contrôle la fenêtre historique retenue et compare les sorties à une référence
documentée :

```bash
make demo-space
make verify-space-offline
make verify-space-online
PYTHONPATH=src python3 -m temporal_chaos_testing.cli space --download --ack-network-download
```

## Structure

| Chemin | Rôle |
|---|---|
| `src/temporal_chaos_testing/` | CLI légère de lancement et garde-fous |
| `src/temporal_chaos_testing/scenarios/` | scénarios packagés pour wheel et CLI |
| `chaos/` | démonstrations injectées et `libfaketime` |
| `partie-aerospatiale/` | démonstration SPICE et documentation associée |

## Scénarios prioritaires actuels

- `controlled-clock` : rollback déterministe d'horloge civile sans mutation hôte.
- `holdover` : perte de source et dérive locale en mode dégradé.
- `leap-smear-mismatch` : incompatibilité entre UTC strict et lissage de seconde intercalaire.
- `certificate-expiry` : dérive d'horloge et validation `notBefore` / `notAfter`.
- `lease-pause` : pause longue, lease expirée et besoin de fencing token.
- `jwt-totp-skew` : rejet de JWT/TOTP sous skew hors budget.
- `ptp-grandmaster-failover` : perte de grandmaster, holdover et saut de phase.
- `faketime` : laboratoire `libfaketime` en environnement isolé.
- `space` : démonstration SPICE avec téléchargement optionnel.

## Validation

```bash
make verify
make demo-chaos
```

## Relation avec les autres dépôts

- `temporal-traps` : noyau pédagogique et algorithmes.
- `temporal-audit-toolkit` : diagnostics en lecture seule.

## Licence

Code sous double licence MIT ou Apache-2.0.
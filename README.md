# Temporal-Chaos-Testing

Laboratoire de chaos temporel et de démonstrations injectées pour tests en
environnement isolé.

Ce dépôt isole les scénarios qui ne doivent pas être confondus avec le noyau
pédagogique ni avec l'outillage d'audit read-only : injections `libfaketime`,
horloges contrôlées et démonstration SPICE avec téléchargement de kernels.

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
PYTHONPATH=src python3 -m temporal_chaos_testing.cli faketime --ack-lab-risk
```

La démonstration SPICE reste optionnelle :

```bash
make demo-space
PYTHONPATH=src python3 -m temporal_chaos_testing.cli space --download --ack-network-download
```

## Structure

| Chemin | Rôle |
|---|---|
| `src/temporal_chaos_testing/` | CLI légère de lancement et garde-fous |
| `chaos/` | démonstrations injectées et `libfaketime` |
| `partie-aerospatiale/` | démonstration SPICE et documentation associée |

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
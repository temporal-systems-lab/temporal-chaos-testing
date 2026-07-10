#!/usr/bin/env bash
set -euo pipefail

echo "=== 1. Heure réelle ==="
date

echo
echo "=== 2. Processus démarré 5 secondes dans le PASSÉ (step -5s) ==="
faketime -f "-5s" date

echo
echo "=== 3. Horloge accélérée x10 : 1 s réelle = 10 s perçues ==="
faketime -f "+0 x10" bash -c 'date +%T.%N; sleep 1; date +%T.%N'

echo
echo "=== 4. Le piège : durée wall-clock sous horloge qui saute ==="
echo "Un offset fixe appliqué à tout le processus ne suffit pas : il s'annule"
echo "dans une soustraction début/fin. Pour démontrer le bug, il faut que"
echo "l'horloge change entre deux lectures, ou injecter une horloge contrôlable."
echo
"${TEMPORAL_CHAOS_PYTHON:-python3}" -m temporal_chaos_testing.scenarios.controlled_clock

echo
echo "Limites de libfaketime : LD_PRELOAD ne couvre pas tous les runtimes,"
echo "certains appels monotones ne sont pas affectés, et les VM/conteneurs"
echo "peuvent exposer des horloges différentes. Utilisez-le comme outil de"
echo "chaos local, pas comme preuve universelle."
"""Démo SPICE : UTC -> ET (temps des éphémérides) -> SCLK (horloge bord).

Illustre le futur chapitre « SPICE : la mémoire temporelle du système
solaire ». Nécessite spiceypy (pip install spiceypy) et deux kernels publics
NAIF explicitement vérifiés :

  - naif0012.tls : LSK, table des secondes intercalaires (UTC <-> ET)
  - vg100051.tsc : SCLK, corrélation de l'horloge bord de Voyager 1

Le point clé du chapitre : convertir un timestamp spatial n'est PAS un calcul
local, c'est une consultation de kernels entretenus au sol par corrélation,
parce que l'horloge de la sonde dérive comme n'importe quel quartz.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys
import urllib.request

KERNELS = {
    "naif0012.tls": {
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls",
        "sha256": "678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b",
    },
    "vg100051.tsc": {
        "url": "https://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/sclk/vg100051.tsc",
        "sha256": "036f5eeee519b6abae055b486e1d9e3c9531588d55ebd6da1956127baa03d1b7",
    },
}
VOYAGER_1 = -31  # identifiant NAIF de Voyager 1
VOYAGER_1_SCLK_ID = -31


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_kernels(directory: pathlib.Path, *, download: bool) -> list[pathlib.Path]:
    directory.mkdir(exist_ok=True)
    paths = []
    for name, metadata in KERNELS.items():
        path = directory / name
        if not path.exists():
            if not download:
                raise FileNotFoundError(
                    f"{path} manquant. Relancez avec --download pour récupérer "
                    "les kernels publics NAIF et vérifier leurs checksums."
                )
            print(f"Téléchargement de {name} depuis {metadata['url']}")
            with urllib.request.urlopen(metadata["url"], timeout=30) as response:
                data = response.read()
            observed = hashlib.sha256(data).hexdigest()
            if observed != metadata["sha256"]:
                raise RuntimeError(
                    f"Checksum invalide pour {name}: attendu {metadata['sha256']}, obtenu {observed}"
                )
            path.write_bytes(data)
        observed = sha256(path)
        if observed != metadata["sha256"]:
            raise RuntimeError(
                f"Checksum invalide pour {path}: attendu {metadata['sha256']}, obtenu {observed}"
            )
        paths.append(path)
    return paths


def require_sclk_partition_mapping(spice, et: float) -> None:
    # SCLK partitions only verify that the encoded clock value belongs to a
    # declared counter partition. They do not certify correlation accuracy,
    # calibration quality, or operational validity for the requested epoch.
    starts, stops = spice.scpart(VOYAGER_1_SCLK_ID)
    encoded = spice.sce2c(VOYAGER_1, et)
    for start, stop in zip(starts, stops):
        if start <= encoded <= stop:
            return
    raise RuntimeError(
        f"ET {et} converti en SCLK encodé {encoded} hors couverture déclarée "
        f"du kernel SCLK Voyager 1"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--download",
        action="store_true",
        help="télécharge les kernels publics NAIF manquants et vérifie leurs SHA-256",
    )
    parser.add_argument(
        "--utc",
        default="2026-07-09T12:00:00",
        help="UTC epoch to convert; its suitability for the mission kernel must be reviewed",
    )
    args = parser.parse_args()

    try:
        import spiceypy as spice
    except ImportError:
        print("spiceypy est requis : pip install spiceypy")
        return 1

    try:
        kernels = fetch_kernels(pathlib.Path(__file__).parent / "kernels", download=args.download)
    except (FileNotFoundError, RuntimeError) as exc:
        print(exc)
        return 2

    for kernel in kernels:
        spice.furnsh(str(kernel))

    utc = args.utc

    # 1. UTC -> ET/TDB : le LSK fournit les secondes intercalaires (TAI-UTC=37 s)
    et = spice.str2et(utc)
    require_sclk_partition_mapping(spice, et)
    print(f"UTC              : {utc}")
    print(f"ET (TDB, s J2000): {et:,.3f}")
    delta = spice.deltet(et, "ET")
    print(f"ET - UTC         : {delta:.6f} s (valeur SPICE ; inclut TT-TAI, "
          "les secondes intercalaires et les termes périodiques TDB-TT)")

    # 2. ET -> SCLK : le kernel SCLK applique la corrélation bord/sol
    sclk = spice.sce2s(VOYAGER_1, et)
    print(f"Horloge bord VG1 : {sclk}  (format partition/compte de mission)")
    print("Avertissement     : l'appartenance à une partition SCLK ne certifie ni "
          "la précision ni la qualité de la corrélation à cette date.")

    # 3. Aller-retour SCLK -> ET pour vérifier la cohérence de la corrélation
    et_back = spice.scs2e(VOYAGER_1, sclk)
    print(f"Retour SCLK -> ET: écart {abs(et - et_back) * 1000:.3f} ms "
          f"(la granularité de l'horloge bord borne la précision)")

    spice.kclear()
    return 0


if __name__ == "__main__":
    sys.exit(main())

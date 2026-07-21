"""SPICE UTC -> ET -> SCLK demo packaged for CLI and wheel use."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import urllib.request


def default_manifest_path() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    candidate = repo_root / "partie-aerospatiale" / "manifest.json"
    if candidate.exists():
        return candidate
    return Path("partie-aerospatiale/manifest.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_utc(value: str) -> dt.datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def ensure_utc_within_window(manifest: dict[str, object], utc_value: str) -> None:
    coverage_policy = manifest["coverage_policy"]
    window = coverage_policy["defensible_window"]
    candidate = parse_utc(utc_value)
    start = parse_utc(window["start_utc"])
    end = parse_utc(window["end_utc"])
    if candidate < start or candidate > end:
        raise ValueError(
            f"{utc_value} sort de la fenêtre pédagogique défendable [{window['start_utc']}, {window['end_utc']}]."
        )


def fetch_kernels(manifest: dict[str, object], directory: Path, *, download: bool) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for kernel in manifest["kernels"]:
        name = kernel["name"]
        path = directory / name
        if not path.exists():
            if not download:
                raise FileNotFoundError(
                    f"{path} manquant. Relancez avec --download pour récupérer les kernels publics NAIF et vérifier leurs checksums."
                )
            print(f"Téléchargement de {name} depuis {kernel['url']}")
            with urllib.request.urlopen(kernel["url"], timeout=30) as response:
                data = response.read()
            observed = hashlib.sha256(data).hexdigest()
            if observed != kernel["sha256"]:
                raise RuntimeError(
                    f"Checksum invalide pour {name}: attendu {kernel['sha256']}, obtenu {observed}"
                )
            with tempfile.NamedTemporaryFile(dir=directory, delete=False) as handle:
                handle.write(data)
                temp_path = Path(handle.name)
            temp_path.replace(path)
        observed = sha256(path)
        if observed != kernel["sha256"]:
            raise RuntimeError(
                f"Checksum invalide pour {path}: attendu {kernel['sha256']}, obtenu {observed}"
            )
        paths.append(path)
    return paths


def render_meta_kernel(kernel_paths: list[Path], *, source_manifest: Path) -> str:
    lines = [
        "KPL/MK",
        "",
        "\\begindata",
        "KERNELS_TO_LOAD = (",
    ]
    for path in kernel_paths:
        lines.append(f"    '{path.name}'")
    lines.extend(
        [
            ")",
            "\\begintext",
            f"Generated from {source_manifest.name}; all kernels must match the manifest SHA-256 values.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_meta_kernel(manifest: dict[str, object], kernel_paths: list[Path], kernel_dir: Path, manifest_path: Path) -> Path:
    filename = manifest["meta_kernel"]["filename"]
    path = kernel_dir / filename
    path.write_text(render_meta_kernel(kernel_paths, source_manifest=manifest_path), encoding="utf-8")
    return path


def require_sclk_partition_mapping(spice, manifest: dict[str, object], et: float) -> None:
    starts, stops = spice.scpart(manifest["spacecraft"]["sclk_id"])
    encoded = spice.sce2c(manifest["spacecraft"]["spacecraft_id"], et)
    for start, stop in zip(starts, stops):
        if start <= encoded <= stop:
            return
    raise RuntimeError(
        f"ET {et} converti en SCLK encodé {encoded} hors couverture déclarée du kernel SCLK Voyager 1"
    )


def compare_with_reference(observed: dict[str, float | str], manifest: dict[str, object]) -> None:
    reference_case = manifest["reference_case"]
    expected = reference_case["expected"]
    tolerances = reference_case["tolerances"]

    if abs(observed["et_tdb_seconds_j2000"] - expected["et_tdb_seconds_j2000"]) > tolerances["et_seconds"]:
        raise RuntimeError(
            f"ET hors tolérance: attendu {expected['et_tdb_seconds_j2000']}, obtenu {observed['et_tdb_seconds_j2000']}"
        )
    if abs(observed["et_minus_utc_seconds"] - expected["et_minus_utc_seconds"]) > tolerances["et_minus_utc_seconds"]:
        raise RuntimeError(
            f"ET-UTC hors tolérance: attendu {expected['et_minus_utc_seconds']}, obtenu {observed['et_minus_utc_seconds']}"
        )
    if observed["sclk"] != expected["sclk"]:
        raise RuntimeError(f"SCLK inattendu: attendu {expected['sclk']}, obtenu {observed['sclk']}")
    if abs(observed["roundtrip_ms"] - expected["roundtrip_ms"]) > tolerances["roundtrip_ms"]:
        raise RuntimeError(
            f"Écart SCLK->ET hors tolérance: attendu {expected['roundtrip_ms']} ms, obtenu {observed['roundtrip_ms']} ms"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--download",
        action="store_true",
        help="télécharge les kernels publics NAIF manquants et vérifie leurs SHA-256",
    )
    parser.add_argument(
        "--utc",
        help="UTC epoch to convert; defaults to the historical reference case stored in the manifest",
    )
    parser.add_argument(
        "--manifest",
        default=str(default_manifest_path()),
        help="manifest describing kernels, coverage policy, reference case and tolerances",
    )
    parser.add_argument(
        "--kernel-dir",
        help="directory used to store or read the verified kernels",
    )
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path)
    selected_utc = args.utc or manifest["reference_case"]["utc"]
    kernel_dir = Path(args.kernel_dir) if args.kernel_dir else manifest_path.parent / "kernels"

    try:
        ensure_utc_within_window(manifest, selected_utc)
        kernels = fetch_kernels(manifest, kernel_dir, download=args.download)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(exc)
        return 2

    meta_kernel = write_meta_kernel(manifest, kernels, kernel_dir, manifest_path)

    try:
        import spiceypy as spice
    except ImportError:
        print("spiceypy est requis : pip install spiceypy")
        return 1

    try:
        previous_cwd = Path.cwd()
        os.chdir(kernel_dir)
        try:
            spice.furnsh(meta_kernel.name)
        finally:
            os.chdir(previous_cwd)

        spacecraft_id = manifest["spacecraft"]["spacecraft_id"]
        et = spice.str2et(selected_utc)
        require_sclk_partition_mapping(spice, manifest, et)
        delta = spice.deltet(et, "ET")
        sclk = spice.sce2s(spacecraft_id, et)
        et_back = spice.scs2e(spacecraft_id, sclk)
        observed = {
            "et_tdb_seconds_j2000": et,
            "et_minus_utc_seconds": delta,
            "sclk": sclk,
            "roundtrip_ms": abs(et - et_back) * 1000.0,
        }
        compare_with_reference(observed, manifest)

        print(f"Manifest         : {manifest_path}")
        print(f"Meta-kernel      : {meta_kernel}")
        print(f"UTC              : {selected_utc}")
        print(f"ET (TDB, s J2000): {et:,.3f}")
        print(
            f"ET - UTC         : {delta:.6f} s (valeur SPICE ; inclut TT-TAI, les secondes intercalaires et les termes périodiques TDB-TT)"
        )
        print(f"Horloge bord VG1 : {sclk}  (format partition/compte de mission)")
        print(f"Retour SCLK -> ET: écart {abs(et - et_back) * 1000:.3f} ms")
        print(
            "Fenêtre retenue  : "
            + manifest["coverage_policy"]["defensible_window"]["start_utc"]
            + " -> "
            + manifest["coverage_policy"]["defensible_window"]["end_utc"]
        )
        print("Référence        : PASS (sorties conformes au manifeste et dans les tolérances documentées)")
        return 0
    finally:
        spice.kclear()


if __name__ == "__main__":
    sys.exit(main())
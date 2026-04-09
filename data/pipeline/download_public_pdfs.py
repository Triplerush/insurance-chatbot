"""
Download publicly available Chilean insurance policy PDFs for the RAG demo.

Sources: MAPFRE Chile, Mutual de Seguros, SURA Chile, Consorcio.
These are real condiciones generales / pólizas published by Chilean insurers.
"""
import os
import sys
import requests
from pathlib import Path

PDFS = {
    # --- MAPFRE Chile: Vehículos ---
    "mapfre_vehiculos_cond_generales.pdf": "https://www.mapfre.cl/media/pol-y-cads.pdf",
    "mapfre_vehiculos_motorizados.pdf": "https://www.mapfre.cl/media/poliza-seguro-para-vehiculos-motorizados.pdf",
    "mapfre_asistencia_vehiculos.pdf": "https://www.mapfre.cl/media/poliza-seguro-asistencia-vehiculos.pdf",
    "mapfre_accidentes_pasajeros_vehiculos.pdf": "https://www.mapfre.cl/media/poliza-seguro-accidentes-personales-pasajeros-vehiculos.pdf",

    # --- MAPFRE Chile: Hogar / Propiedad ---
    "mapfre_incendio.pdf": "https://www.mapfre.cl/media/poliza-seguro-incendio-pol-120130161.pdf",
    "mapfre_incendio_hogar.pdf": "https://www.mapfre.cl/media/poliza-seguro-incendio-pol-120130907.pdf",
    "mapfre_robo_hogar.pdf": "https://www.mapfre.cl/media/poliza-seguro-robo-poliza-hogar-120131101.pdf",
    "mapfre_cristales.pdf": "https://www.mapfre.cl/media/poliza-seguro-cristales-pol-120131110.pdf",
    "mapfre_responsabilidad_civil.pdf": "https://www.mapfre.cl/media/poliza-seguro-responsabilidad-civil-pol-120130179.pdf",
    "mapfre_perdida_beneficios_incendio.pdf": "https://www.mapfre.cl/media/poliza-seguro-perdida-beneficios-incendio-pol120131179.pdf",

    # --- MAPFRE Chile: Vida / Salud / Accidentes ---
    "mapfre_accidentes_personales_351.pdf": "https://www.mapfre.cl/media/poliza-accidentes-personales-2013-0351.pdf",
    "mapfre_accidentes_personales_085.pdf": "https://www.mapfre.cl/media/poliza-seguro-accidentes-personales-pol-320130085.pdf",
    "mapfre_vida_temporal.pdf": "https://www.mapfre.cl/media/seguro-vida-temporal-renovable-20130477.pdf",
    "mapfre_gastos_medicos_mayores.pdf": "https://www.mapfre.cl/media/cad-reembolso-gastos-medicos-mayores.pdf",
    "mapfre_muerte_accidental.pdf": "https://www.mapfre.cl/media/cad-muerte-accidental.pdf",
    "mapfre_invalidez_permanente.pdf": "https://www.mapfre.cl/media/cad-invalidez-permanente.pdf",
    "mapfre_invalidez_accidental.pdf": "https://www.mapfre.cl/media/cad-invalidez-accidental.pdf",
    "mapfre_invalidez_enfermedad.pdf": "https://www.mapfre.cl/media/cad-invalidez-por-enfermedad.pdf",

    # --- MAPFRE Chile: Viaje ---
    "mapfre_asistencia_viaje.pdf": "https://www.mapfre.cl/media/poliza-seguro-asistencia-personas-viaje.pdf",

    # --- Mutual de Seguros ---
    "mutual_accidentes_personales.pdf": "https://www.mutualdeseguros.cl/uploads/polizas/POL320140014.pdf",
    "mutual_soap.pdf": "https://core.mutualdeseguros.cl/soap_ms/upload/POL320130487.pdf",
    "mutual_vida_proteccion.pdf": "https://www.mutualdeseguros.cl/app/uploads/2024/02/POL220140350.pdf",

    # --- SURA Chile ---
    "sura_vehiculos_consolidada.pdf": "https://seguros.sura.cl/docs/default-source/Sucursal-virtual/condicionados/polizas-consolidadas.pdf",
}


def download_all(output_dir: str) -> int:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0
    failed = 0

    for filename, url in PDFS.items():
        target = out / filename
        if target.exists() and target.stat().st_size > 0:
            skipped += 1
            continue

        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            target.write_bytes(resp.content)
            size_kb = len(resp.content) / 1024
            print(f"  OK  {filename} ({size_kb:.0f} KB)")
            downloaded += 1
        except Exception as e:
            print(f"  FAIL {filename}: {e}", file=sys.stderr)
            failed += 1

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped (already exist), {failed} failed")
    print(f"Total PDFs in {output_dir}: {len(list(out.glob('*.pdf')))}")
    return downloaded + skipped


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Download public Chilean insurance policy PDFs")
    ap.add_argument("--output-dir", default="./data/raw_policies")
    args = ap.parse_args()

    print(f"Downloading {len(PDFS)} public insurance policy PDFs...")
    download_all(args.output_dir)

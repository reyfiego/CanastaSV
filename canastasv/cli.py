"""Comandos de consola: python -m canastasv <comando>"""

import argparse
import logging
import sys
from datetime import date

from canastasv.catalogo import ErrorDeConfiguracion, cargar_productos, cargar_supermercados
from canastasv.config import cargar_ajustes
from canastasv.db.conexion import crear_motor, fabrica_de_sesiones, inicializar
from canastasv.scrapers.fabrica import crear_scraper
from canastasv.scrapers.http import ClienteHttp
from canastasv.servicios.comparador import comparar
from canastasv.servicios.recolector import recolectar


def _sesion():
    motor = crear_motor(cargar_ajustes().ruta_db)
    inicializar(motor)
    return fabrica_de_sesiones(motor)()


def comando_recolectar(args: argparse.Namespace) -> int:
    ajustes = cargar_ajustes()
    if args.supermercado:
        # Nombrar un supermercado a mano permite probar también los marcados como inactivos.
        supermercados = [
            s for s in cargar_supermercados(incluir_inactivos=True) if s.codigo in args.supermercado
        ]
        if not supermercados:
            print("Ningún supermercado coincide con los códigos indicados.")
            return 1
    else:
        supermercados = cargar_supermercados()
    cliente = ClienteHttp(ajustes)
    scrapers = [crear_scraper(s, cliente) for s in supermercados]

    with _sesion() as sesion:
        resumen = recolectar(sesion, scrapers, cargar_productos(), date.today())

    print(f"Precios guardados: {resumen.guardados}")
    print(f"Sin coincidencia: {len(resumen.sin_coincidencia)} {resumen.sin_coincidencia}")
    print(f"Errores de descarga: {len(resumen.errores)} {resumen.errores}")
    return 0 if resumen.hubo_datos else 1


def comando_comparar(_: argparse.Namespace) -> int:
    with _sesion() as sesion:
        resultado = comparar(sesion)
    if resultado.fecha is None:
        print("Todavía no hay precios guardados. Corre primero: python -m canastasv recolectar")
        return 1
    print(f"Comparativa del {resultado.fecha}\n")
    for fila in resultado.filas:
        precios = "  ".join(f"{s}: ${p:.2f}" for s, p in sorted(fila.precios.items()))
        print(f"{fila.producto:<26} {precios}   -> más barato: {fila.mas_barato}")
    if resultado.total_por_supermercado:
        print(f"\nTotales ({resultado.productos_completos} productos presentes en todos):")
        for codigo, total in resultado.total_por_supermercado.items():
            print(f"  {codigo:<10} ${total:.2f}")
        print(f"  Lista óptima ${resultado.total_lista_optima:.2f} "
              f"(ahorro ${resultado.ahorro_vs_mejor_supermercado:.2f})")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="canastasv", description="Comparador de precios de la canasta básica")
    sub = parser.add_subparsers(dest="comando", required=True)

    recolectar_p = sub.add_parser("recolectar", help="Descarga y guarda los precios de hoy")
    recolectar_p.add_argument("--supermercado", nargs="*", help="Códigos a consultar (por defecto, todos)")
    recolectar_p.set_defaults(funcion=comando_recolectar)

    comparar_p = sub.add_parser("comparar", help="Muestra la comparativa del último día con datos")
    comparar_p.set_defaults(funcion=comando_comparar)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = construir_parser().parse_args(argv)
    try:
        return args.funcion(args)
    except ErrorDeConfiguracion as error:
        print(f"Error de configuración: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

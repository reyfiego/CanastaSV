# CanastaSV

Comparador y predictor de precios de la canasta básica en El Salvador.

CanastaSV consulta todos los días los precios publicados en las tiendas en línea de varios supermercados salvadoreños, los guarda como historial y los compara para responder una pregunta sencilla: **¿dónde me sale más barato hacer el súper esta semana?**

Proyecto final de Programación Computacional III.

## Qué hace

- **Recolecta** los precios de una lista de productos de la canasta básica en 4 supermercados.
- **Empareja** cada producto de la canasta con el producto equivalente de cada tienda (por palabras clave y tamaño).
- **Guarda** un precio por producto, supermercado y día en una base de datos SQLite.
- **Compara** precios, calcula el costo total por supermercado y la "lista óptima" (comprar cada producto donde está más barato).
- **Expone** los datos en una API web para el dashboard.
- **Se ejecuta solo** todos los días con GitHub Actions, así el historial crece aunque nadie encienda la computadora.

Próximas etapas: dashboard web y predicción de precios con machine learning.

## Supermercados

| Supermercado | Cómo se obtienen los precios |
|---|---|
| Walmart | API pública de catálogo (plataforma VTEX) |
| Maxi Despensa | API pública de catálogo (plataforma VTEX) |
| La Despensa de Don Juan | API pública de catálogo (plataforma VTEX) |
| Súper Selectos | Página de búsqueda en HTML |

PriceSmart no se incluye porque su `robots.txt` no permite el acceso automatizado.

## Instalación

Requisitos: Python 3.11 o superior y Git.

```bash
git clone https://github.com/reyfiego/CanastaSV.git
```

```bash
cd CanastaSV
```

Crear y activar el entorno virtual:

```bash
python -m venv .venv
```

```bash
# Windows
.venv\Scripts\activate
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Opcional: copiar `.env.example` como `.env` para cambiar la ruta de la base de datos o los tiempos de espera.

## Uso

Recolectar los precios de hoy (todos los supermercados):

```bash
python -m canastasv recolectar
```

Solo algunos supermercados:

```bash
python -m canastasv recolectar --supermercado walmart selectos
```

Ver la comparativa del último día con datos:

```bash
python -m canastasv comparar
```

Levantar la API web (documentación interactiva en http://127.0.0.1:8000/docs):

```bash
uvicorn canastasv.api.app:app --reload
```

Correr las pruebas:

```bash
python -m pytest
```

## Agregar o ajustar productos

Los productos se configuran en `config/productos.json`, sin tocar código:

```json
{
  "codigo": "arroz-blanco-4lb",
  "nombre": "Arroz blanco",
  "categoria": "Granos",
  "busqueda": "arroz blanco",
  "incluir": ["arroz"],
  "excluir": ["precocido", "integral"],
  "tamano": {"valor": 1816, "unidad": "g"}
}
```

- `busqueda`: lo que se escribe en el buscador de cada tienda.
- `incluir` / `excluir`: palabras que el nombre debe tener o no tener.
- `tamano`: tamaño de referencia en `g`, `ml` o `und`. Se aceptan productos con hasta 12 % de diferencia.

Si un producto sale como "sin coincidencia" en la recolección, normalmente basta con ajustar estas palabras o el tamaño.

## Estructura

```
canastasv/
  config.py            Ajustes leídos de .env
  modelos.py           Estructuras de datos compartidas
  catalogo.py          Carga y validación de config/*.json
  cli.py               Comandos de consola
  scrapers/            Un módulo por tipo de tienda (VTEX, Selectos) + cliente HTTP
  emparejamiento/      Normalización de nombres, lectura de tamaños y emparejado
  db/                  Tablas, conexión y consultas (SQLAlchemy)
  servicios/           Recolector y comparador
  api/                 API FastAPI, separada por rutas
config/                Productos y supermercados
data/                  Base de datos SQLite con el historial
docs/                  Documentación técnica
tests/                 Pruebas automáticas (pytest)
.github/workflows/     Recolección diaria y pruebas en cada push
```

## Uso responsable de los datos

- Solo se consultan precios públicos, sin iniciar sesión.
- Se respeta el `robots.txt` de cada sitio.
- Hay una pausa entre peticiones y una sola recolección al día.
- El scraper se identifica con un User-Agent que enlaza a este repositorio.

## Documentación

- [Arquitectura y decisiones de diseño](docs/arquitectura.md)

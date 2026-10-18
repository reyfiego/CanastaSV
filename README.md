# CanastaSV

Comparador y predictor de precios de la canasta básica en El Salvador.

CanastaSV consulta todos los días los precios publicados en las tiendas en línea de varios supermercados salvadoreños, los guarda como historial y los compara para responder una pregunta sencilla: **¿dónde me sale más barato hacer el súper esta semana?**

Proyecto final de Programación Computacional III.

**🌐 Pruébalo en línea: [canastasv.onrender.com](https://canastasv.onrender.com)**

<img src="docs/img/qr-canastasv.png" alt="Código QR a canastasv.onrender.com" width="180">

> El sitio usa el plan gratuito de Render: si nadie lo ha visitado en los últimos 15 minutos, la primera carga tarda cerca de un minuto.

## Qué hace

- **Recolecta** los precios de una lista de productos de la canasta básica en 4 supermercados.
- **Empareja** cada producto de la canasta con el producto equivalente de cada tienda (por palabras clave y tamaño).
- **Guarda** un precio por producto, supermercado y día en una base de datos SQLite.
- **Compara** precios, calcula el costo total por supermercado y la "lista óptima" (comprar cada producto donde está más barato).
- **Marca precios dudosos**: si un precio es menor a la mitad de lo que cuesta en los demás supermercados (posible error de la tienda), se muestra tachado y no entra en la comparación.
- **Muestra** todo en un dashboard web: comparador con buscador y filtros, costo de la canasta por supermercado, lista óptima e historial de cada producto.
- **Se ejecuta solo** todos los días con GitHub Actions, así el historial crece aunque nadie encienda la computadora.

Próxima etapa: predicción de precios con machine learning, cuando haya suficiente historial.

## Supermercados

| Supermercado | Cómo se obtienen los precios |
|---|---|
| Walmart | API pública de búsqueda (plataforma VTEX) |
| Maxi Despensa | API pública de búsqueda (plataforma VTEX) |
| La Despensa de Don Juan | API pública de búsqueda (plataforma VTEX) |
| Súper Selectos | Página de búsqueda en HTML (desactivado en la recolección automática) |

- **Súper Selectos** rechaza (error 403) las peticiones que llegan desde los servidores de GitHub Actions. El scraper está listo, pero el supermercado está marcado con `"activo": false` en `config/supermercados.json` y no se intenta esquivar ese bloqueo. Se puede probar a mano con `python -m canastasv recolectar --supermercado selectos`.
- **PriceSmart** no se incluye porque su `robots.txt` no permite el acceso automatizado.

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

Levantar el dashboard web y la API:

```bash
uvicorn canastasv.api.app:app --reload
```

- Dashboard: http://127.0.0.1:8000
- Documentación interactiva de la API: http://127.0.0.1:8000/docs

Correr las pruebas:

```bash
python -m pytest
```

## Publicación

El dashboard está publicado en **https://canastasv.onrender.com**, gratis en [Render](https://render.com), con la configuración de `render.yaml`:

- Render instala `requirements.txt` y arranca `uvicorn` con Python 3.12 (`.python-version`).
- Cada commit a `main` vuelve a publicar el sitio. Como la recolección diaria hace un commit con la base de datos, la página se actualiza sola cada mañana.
- En el plan gratuito el servicio se duerme tras 15 minutos sin visitas y tarda cerca de un minuto en despertar con la siguiente visita.
- La API también está disponible en línea, con documentación interactiva en [canastasv.onrender.com/docs](https://canastasv.onrender.com/docs).
- El código QR está en `docs/img/qr-canastasv.png` (y en SVG para imprimir en grande).

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
frontend/              Dashboard web (HTML, CSS y JavaScript sin frameworks)
  css/                 tokens, base, layout, components/ y pages/
  js/                  api, formato, dom, componentes/ y paginas/
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

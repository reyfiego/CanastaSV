# Arquitectura y decisiones de diseño

## Flujo general

```
GitHub Actions (diario)
        │
        ▼
python -m canastasv recolectar
        │
        ├─ catalogo.py ──────── lee config/productos.json y config/supermercados.json
        │
        ├─ scrapers/ ────────── busca cada producto en cada tienda
        │     ├─ vtex.py          API JSON de Walmart, Maxi Despensa y Despensa de Don Juan
        │     └─ selectos.py      HTML de Súper Selectos
        │
        ├─ emparejamiento/ ──── elige el producto equivalente (palabras clave + tamaño)
        │
        └─ db/ ──────────────── guarda un precio por producto, supermercado y día
                                    │
                                    ▼
                          servicios/comparador.py
                                    │
                                    ▼
                          api/ (FastAPI) ──► frontend/ (dashboard web)
```

## Capas

| Capa | Responsabilidad | No sabe de |
|---|---|---|
| `scrapers` | Descargar y convertir resultados en `ProductoTienda` | Base de datos, emparejado |
| `emparejamiento` | Decidir qué producto de la tienda corresponde al de la canasta | Internet, base de datos |
| `db` | Guardar y consultar | Cómo se obtuvieron los datos |
| `servicios` | Orquestar el proceso y calcular comparativas | Detalles de cada tienda |
| `api` | Exponer los datos en JSON | Scraping |

Separar así permite probar cada capa por separado: las pruebas usan scrapers falsos y una base de datos en memoria, sin conectarse a internet.

## Decisiones

**API de VTEX en lugar de leer HTML.** Tres de las cuatro cadenas usan la plataforma VTEX. Se usa su API pública "Intelligent Search" (la misma que alimenta el buscador de la tienda), que devuelve JSON. Es más estable que leer HTML (no se rompe si cambia el diseño de la página) y más ligera para el sitio. Con un solo scraper se cubren las tres tiendas. Como respaldo se usa la API de catálogo (`/api/catalog_system/pub/products/search`), que en estas tiendas solo acepta búsquedas de una palabra: si Intelligent Search falla, el scraper busca con la primera palabra ("arroz" en vez de "arroz blanco") y el emparejador filtra el resto. Ante cualquier error, el log muestra el código y el inicio de la respuesta del servidor.

**Súper Selectos desactivado en la recolección automática.** Su sitio responde con 403 a las peticiones que vienen de los servidores de GitHub Actions. En lugar de intentar esquivar el bloqueo (cambiar el User-Agent o usar proxies), el supermercado queda marcado como inactivo. El scraper y sus pruebas se mantienen por si el sitio permite el acceso más adelante.

**Multipacks descartados.** Nombres como "Arroz 2 Pack - 908 g" no dejan claro si el tamaño es por unidad o total, así que el emparejador los ignora para no comparar precios de cantidades distintas.

**HTML para Súper Selectos.** Su tienda no usa VTEX, pero la página de búsqueda (`/products?keyword=`) llega renderizada desde el servidor, así que basta con `requests` + BeautifulSoup, sin un navegador automatizado. El parser busca los enlaces `?productId=` y lee el precio dentro de la tarjeta de cada producto, ignorando ofertas de multicompra ("4X$1.25").

**Productos canónicos configurables.** Cada tienda nombra los productos de forma distinta ("Arroz Blanco San Francisco 1816gr" frente a "Arroz Blanco Dany 1 816 g"). En lugar de escribir el ID de cada producto en cada tienda, se define el producto una sola vez con palabras clave y un tamaño de referencia; el emparejador elige el más barato que cumpla. Así agregar productos no requiere programar.

**Tamaños normalizados.** Los nombres traen tamaños en g, kg, lb, oz, ml, L o unidades. Todo se convierte a g, ml o und para poder comparar (por ejemplo, "2.5 Lb" = 1134 g). En gramos y mililitros, "1,816 g" se lee como 1816 g (separador de miles), mientras que "0,5 kg" se lee como decimal.

**Un precio por día.** La tabla `precios` tiene una restricción única por producto, supermercado y fecha. Si la recolección corre dos veces el mismo día, el segundo valor reemplaza al primero. Esto mantiene un historial limpio para la predicción.

**Comparación justa.** El costo total por supermercado solo suma productos que aparecen en todas las tiendas ese día; si no, un supermercado con menos productos encontrados parecería más barato.

**SQLite.** No necesita servidor, es un solo archivo y se puede guardar en el repositorio para que GitHub Actions acumule el historial. Si el proyecto crece, SQLAlchemy permite cambiar a PostgreSQL cambiando solo la cadena de conexión.

**Precios dudosos.** Un precio menor a la mitad de la mediana de los demás supermercados se aparta de la comparación (la primera recolección encontró un aceite a $0.25 donde los demás cobraban $1.80 y $1.95, lo que hacía parecer más barato a todo un supermercado). Se necesita al menos tres precios para decidirlo; con dos no se sabe cuál está mal. El dashboard lo muestra tachado para que sea transparente.

**Dashboard sin frameworks.** El frontend es HTML, CSS y JavaScript con módulos ES, servido por la misma aplicación FastAPI. No requiere Node.js ni un paso de compilación, y cada pieza vive en su propio archivo (tokens de diseño, componentes de estilo, componentes de JavaScript y una página por vista). Las gráficas se dibujan en SVG a mano, siguiendo el sistema de diseño. Los nombres de productos vienen de sitios externos, así que se insertan siempre como texto (nunca con innerHTML).

**Uso responsable.** Se respeta `robots.txt` (por eso no se incluye PriceSmart), hay una pausa configurable entre peticiones, reintentos con espera creciente ante errores 429/5xx y un User-Agent que identifica el proyecto.

## Librerías

| Librería | Para qué | Por qué esta |
|---|---|---|
| requests | Descargar páginas y JSON | Estándar de facto en Python, con reintentos vía urllib3 |
| beautifulsoup4 | Leer el HTML de Súper Selectos | Tolerante a HTML imperfecto y fácil de consultar con selectores CSS |
| SQLAlchemy | Base de datos | ORM maduro: tablas como clases, consultas seguras y cambio de motor sin reescribir código |
| FastAPI | API web | Valida datos con tipos, genera documentación automática en /docs y es rápido |
| uvicorn | Servidor de la API | Servidor ASGI recomendado para FastAPI |
| python-dotenv | Configuración | Lee ajustes de un archivo .env sin escribirlos en el código |
| pytest | Pruebas | Pruebas simples con funciones y fixtures |
| httpx | Pruebas de la API | Lo usa el cliente de pruebas de FastAPI |

## Modelo de datos

```
supermercados (id, codigo, nombre, url)
productos     (id, codigo, nombre, categoria, tamano_valor, tamano_unidad)
precios       (id, producto_id, supermercado_id, fecha, precio, precio_regular,
               nombre_en_tienda, id_en_tienda, url, capturado_en)
               único: (producto_id, supermercado_id, fecha)
```

`nombre_en_tienda` y `url` permiten verificar cada precio contra la página original.

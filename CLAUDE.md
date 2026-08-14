# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es esto

La landing de una sola página de Delta 4C, en español e inglés. Dos archivos HTML
autónomos, sin build ni framework: todo el CSS y el JS viven dentro de cada archivo.
Lo único externo es Google Fonts; `three.module.min.js` (three.js r160, MIT) va
vendored en el repo para no depender de un CDN que los bloqueadores de contenido cortan.

```
index.html            español · fuente de verdad del contenido
en.html               inglés   · GENERADO, no editar a mano
_i18n/generar-en.py   el traductor
vercel.json           cleanUrls, para que /en funcione sin extensión
robots.txt            permite indexar todo, apunta al sitemap
sitemap.xml           las dos páginas (/ y /en) con sus hreflang
```

Dominio de producción: `https://delta4c.com` (canonical, hreflang, OG y sitemap
apuntan ahí). Si vuelve a cambiar el dominio, hay que tocarlo en: `index.html`
(canonical, hreflang, og:*, twitter:*), los dos pares correspondientes en
`_i18n/generar-en.py` (`TEXTOS`), `robots.txt` y `sitemap.xml`.

## Comandos

Servir en local (abrir el archivo con doble clic bloquea three.js por CORS y la
página cae a su versión sin 3D, así que hace falta un servidor):

```bash
python3 -m http.server 8000
# después: http://localhost:8000  y  http://localhost:8000/en.html
```

Regenerar el inglés después de tocar `index.html`:

```bash
python3 _i18n/generar-en.py
```

Publicar (estático, hoy en Vercel):

```bash
vercel deploy --prod
```

No hay lint, tests ni build: es HTML/CSS/JS plano.

## Flujo de traducción — leer antes de tocar contenido

**El español manda.** Se edita solo `index.html`; `en.html` es generado y nunca se
edita a mano. `_i18n/generar-en.py` aplica un diccionario de pares (español, inglés)
por reemplazo literal de substring, en orden (las cadenas largas van primero para que
una corta no rompa a una larga que la contiene).

- Si una frase del diccionario ya no aparece en `index.html`, el script **aborta sin
  escribir nada** y lista qué cadenas faltan — así una edición en español nunca deja
  el inglés desincronizado en silencio. Cuando pasa, hay que actualizar el par
  correspondiente en `TEXTOS` y correr de nuevo.
- Al final valida que no queden palabras sueltas en español dentro de `<body>` (fuera
  de `<script>` y comentarios) y avisa por stderr si las encuentra, sin abortar.
- Voz en inglés: seca, concreta, sin jerga; "company", nunca "SME"; nada de vender
  "IA"; números y nombres propios no se tocan.

## Arquitectura de cada HTML

Cada archivo (`index.html` / `en.html`) es idéntico en estructura, solo difieren en
texto. Todo vive en un único `<head>`/`<body>`:

- **CSS** en un `<style>` en el `<head>`, organizado en bloques comentados con
  banners `/* === NOMBRE === */`: `TOKENS` (variables de color/tipografía/easing),
  `BASE`, `REVEALS`, `HEADER`, `HERO`, y luego un bloque por sección
  (`01 PROBLEMA`, `02 DOLORES`, `03 CICLO`, `04 AUTOMATIZACIÓN`, `05 NOSOTROS`,
  `06 CTA + FOOTER`), `RESPONSIVE GLOBAL`, `CAPA 3D`, varios bloques `MOTION: *`,
  y `REDUCED MOTION` al final.
- **Secciones del `<body>`**, en orden: `.hero` → `#problema` → `#dolores` →
  `#ciclo` → `#automatizamos` → `#nosotros` → `#cta`.
- **Dos `<script>` al final del `<body>`:**
  1. Un script clásico (IIFE) que maneja todo lo que no es 3D: reveals por
     `IntersectionObserver` (con red de seguridad por `setTimeout` para pestañas en
     segundo plano), la conversación tipo chat en `#dolores`, las flechas SVG que se
     dibujan solas (`pathLength`), la barra de progreso de scroll y el header
     compacto, el indicador de sección activa en la nav, el titular que se
     teclea/borra entre `rompemos → migramos → cambiamos`, y el giro de la órbita SVG
     ligado al scroll.
  2. Un `<script type="module">` que carga three.js (`import('./three.module.min.js')`
     con fallback a unpkg) y monta las escenas 3D: red de nodos en el hero, anillos
     armilares en `#ciclo`, planos que se interpenetran en `#nosotros`, partículas de
     fondo. Si el import falla, o `prefers-reduced-motion` está activo, o el contexto
     WebGL se pierde (`webglcontextlost`), agrega `webgl-off` a `<html>` y no reintenta
     recrear el contexto — la página cae a los diagramas SVG estáticos ya presentes
     en el markup.

## Invariantes de diseño que no hay que romper

- **Todo tiene que leerse sin JavaScript y sin WebGL.** Los lienzos 3D son ornamento:
  con `.webgl-off` la página muestra los diagramas SVG equivalentes y se lee entera.
  Nunca poner contenido real en `opacity:0` esperando que un script lo revele —
  los reveals parten de un estado ya legible.
- **`prefers-reduced-motion` no es "congelar".** Donde el contenido *es* el mensaje —
  el verbo que rota en el titular: rompemos / migramos / cambiamos — tiene que seguir
  cambiando, entera y de golpe (sin tipeo), porque congelarla en la primera palabra
  borra dos tercios del mensaje. Ver el bloque `REDUCED MOTION` en el CSS y la rama
  `rm.matches` en el script del titular.
- **three.js se sirve desde el propio dominio**, no desde un CDN como fuente
  primaria — los bloqueadores de contenido lo cortan. El CDN (`unpkg`) es solo el
  fallback si el import local falla.

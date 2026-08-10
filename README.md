# Delta 4C — Landing

Sitio de una sola página de [Delta 4C](https://delta4c.vercel.app), en español e inglés.

- **Español:** https://delta4c.vercel.app
- **English:** https://delta4c.vercel.app/en

## Cómo está hecho

Dos archivos HTML autónomos. Sin build, sin framework, sin dependencias que instalar:
todo el CSS y el JS van dentro del propio archivo. Lo único externo son las tipografías
de Google Fonts y `three.module.min.js`, que viaja en el repo (ver más abajo).

```
index.html            español · fuente de verdad del contenido
en.html               inglés   · GENERADO, no editar a mano
_i18n/generar-en.py   el traductor
logo.png              monograma sobre fondo claro
logo-blanco.png       monograma sobre fondo oscuro
favicon.png           ícono 512 · apple-touch-icon.png ícono 180
og.png                previsualización al compartir el link (1200x630)
three.module.min.js   three.js r160 (MIT), servido desde el mismo dominio
vercel.json           cleanUrls, para que /en funcione sin extensión
```

## Verla en local

Hace falta un servidor: abrir el archivo con doble clic hace que el navegador
bloquee la carga de three.js por CORS y la página cae a su versión sin 3D.

```bash
python3 -m http.server 8000
# después: http://localhost:8000
```

## Tocar el contenido

**El español manda.** Se edita `index.html` y después se regenera el inglés:

```bash
python3 _i18n/generar-en.py
```

El script tiene un diccionario de ~104 pares. Si una frase del diccionario ya no
aparece en `index.html`, **aborta y avisa cuál**, en vez de escribir un inglés
desincronizado en silencio. Cuando eso pasa, se actualiza el par y se corre de nuevo.

## Detalles que conviene saber antes de tocar

**three.js va en el repo a propósito.** Cargarlo desde un CDN parece más prolijo, pero
los bloqueadores de contenido lo cortan y la página se queda sin los efectos. Se importa
desde el mismo dominio, con el CDN sólo como respaldo:

```js
try{ THREE = await import('./three.module.min.js'); }
catch(e){ try{ THREE = await import('https://unpkg.com/three@0.160.0/build/three.module.js'); }catch(e2){} }
if(!THREE){ document.documentElement.classList.add('webgl-off'); }
```

**Todo tiene que leerse sin JavaScript y sin WebGL.** Los lienzos 3D son ornamento: con
`.webgl-off` la página muestra los diagramas en SVG y se lee entera. Nada de contenido
en `opacity:0` por CSS.

**Con `prefers-reduced-motion` no alcanza con congelar.** Cuando el contenido *es* el
mensaje —la palabra que rota en el titular: rompemos / migramos / cambiamos— tiene que
seguir cambiando, entera y de golpe, sin tipeo. Congelarla borra dos tercios del mensaje.

## Publicar

Contenido estático; hoy vive en Vercel.

```bash
vercel deploy --prod
```

---

three.js © three.js authors, licencia MIT. El resto (diseño, textos, marca) es de Delta 4C.

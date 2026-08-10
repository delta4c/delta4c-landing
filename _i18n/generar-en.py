#!/usr/bin/env python3
"""Genera la versión en inglés de la landing a partir del español.

    python3 _i18n/generar-en.py

Lee  delta4c/index.html  (fuente de verdad, español)
Escribe delta4c/en.html  (traducción)

Cada vez que cambie el español, correr esto de nuevo. Si una cadena del
diccionario ya no aparece en el HTML, el script avisa y no escribe nada:
así una edición en español nunca deja el inglés desincronizado en silencio.

Voz en inglés: seca, concreta, sin jerga. "company", nunca "SME".
Nada de vender "IA". Los números y nombres propios no se tocan.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "delta4c" / "index.html"
DESTINO = RAIZ / "delta4c" / "en.html"

# (español, inglés) — el orden importa: las cadenas largas van primero para que
# una corta no rompa a una larga que la contiene.
TEXTOS = [
    ('<html lang="es"',
     '<html lang="en"'),
    ('<title>Delta 4C — Hacemos que tus sistemas trabajen juntos, para vos</title>',
     '<title>Delta 4C — We make your systems work together, for you</title>'),
    ('content="Hacemos que tus sistemas trabajen juntos, para vos, sin romper lo que ya anda. Leemos tus datos sin tocar lo que factura y construimos arriba lo que te falta."',
     'content="We make your systems work together, for you, without breaking what already runs. We read your data without disrupting your billing and build on top of what’s missing."'),
    ('<link rel="canonical" href="https://delta4c.vercel.app/">',
     '<link rel="canonical" href="https://delta4c.vercel.app/en">'),
    ('<meta property="og:locale" content="es_AR">',
     '<meta property="og:locale" content="en_US">'),
    ('<meta property="og:url" content="https://delta4c.vercel.app/">',
     '<meta property="og:url" content="https://delta4c.vercel.app/en">'),
    ('<meta property="og:title" content="Hacemos que tus sistemas trabajen juntos, para vos">',
     '<meta property="og:title" content="We make your systems work together, for you">'),
    ('<meta property="og:description" content="Leemos tus datos sin tocar lo que factura, y construimos arriba lo que te falta: tu negocio entero, en un solo lugar.">',
     '<meta property="og:description" content="We read your data without disrupting your billing, and build on top of what’s missing: your whole business, in one place.">'),
    ('<meta property="og:image:alt" content="Delta 4C - Hacemos que tus sistemas trabajen juntos, para vos">',
     '<meta property="og:image:alt" content="Delta 4C - We make your systems work together, for you">'),
    ('<meta name="twitter:title" content="Hacemos que tus sistemas trabajen juntos, para vos">',
     '<meta name="twitter:title" content="We make your systems work together, for you">'),
    ('<meta name="twitter:description" content="Leemos tus datos sin tocar lo que factura, y construimos arriba lo que te falta.">',
     '<meta name="twitter:description" content="We read your data without disrupting your billing, and build on top of what’s missing.">'),
    ('<a href="#problema">El problema real</a>',
     '<a href="#problema">The real problem</a>'),
    ('<a href="#ciclo">Cómo trabajamos</a>',
     '<a href="#ciclo">How we work</a>'),
    ('<a href="#nosotros">Por qué nosotros</a>',
     '<a href="#nosotros">Why us</a>'),
    ('Agendá una charla <span class="flecha"',
     'Book a call <span class="flecha"'),
    ('</svg>Lo que hacemos</p>',
     '</svg>What we do</p>'),
    ('Hacemos que tus sistemas trabajen juntos, <em class="vos">para vos</em>.',
     'We make your systems work together, <em class="vos">for you</em>.'),
    ('<span class="l2">No\n',
     '<span class="l2">We don\'t\n'),
    ('<span class="sr">rompemos</span>',
     '<span class="sr">break</span>'),
    ('<span class="rotor-w">rompemos</span>',
     '<span class="rotor-w">break</span>'),
    ('<span class="rotor-w">migramos</span>',
     '<span class="rotor-w">migrate</span>'),
    ('<span class="rotor-w">cambiamos</span>',
     '<span class="rotor-w">replace</span>'),
    ('<span class="txt">rompemos</span>',
     '<span class="txt">break</span>'),
    ("var palabras = ['rompemos','migramos','cambiamos'];",
     "var palabras = ['break','migrate','replace'];"),
    ('          lo que ya anda</span>',
     '          what already works</span>'),
    ('Nos conectamos a los sistemas que ya usás, leemos tus datos sin tocar lo que factura, y construimos arriba lo que te falta: desde responder tus preguntas hasta operar tu día a día.',
     'We connect to the systems you already use, read your data without disrupting your billing, and build on top of what’s missing: from answering your questions to running your day-to-day.'),
    ('>Sobre tus sistemas<',
     '>Built on your systems<'),
    ('>Leemos y construimos arriba<',
     '>We read, then build on top<'),
    ('>Diseñamos, evaluamos, ejecutamos<',
     '>We design, evaluate, execute<'),
    ('</svg>El problema real</p>',
     '</svg>The real problem</p>'),
    ('Tus datos ya existen. Repartidos en sistemas que no se hablan, sin un lugar donde ver el negocio entero.',
     'Your data already exists. Scattered across systems that don’t talk to each other, with nowhere to see the whole business.'),
    ('Tu empresa no tiene un problema de datos: tiene un problema de ',
     'Your company doesn’t have a data problem: it has a '),
    ('<strong>coordinación, visibilidad y ejecución</strong>',
     '<strong>coordination, visibility and execution</strong>'),
    ('. Las ventas en un sistema, el stock en otro, las cobranzas en una planilla. Software enlatado que no toma tus procesos reales — y la operación termina viviendo en la cabeza de la gente.',
     ' problem. Sales in one system, stock in another, receivables in a spreadsheet. Off-the-shelf software that doesn’t fit how you actually work, and the operation ends up living in people’s heads.'),
    ('</svg>Lo que vivís todos los días</p>',
     '</svg>What your business is already telling you</p>'),
    ('Todo esto ya está en tus datos. Nadie te lo está mostrando.',
     'The data is already there. The answers are not.'),
    ('No es falta de información: es que la información no sale del sistema cuando la necesitás.',
     'It’s not that the information is missing: it just doesn’t come out of the system when you need it.'),
    ('No sé cuánto stock tengo parado.',
     'I don’t know how much stock is just sitting there.'),
    ('Plata dormida en mercadería que no rota.',
     'Money trapped in inventory that doesn’t move.'),
    ('El tablero lo muestra solo.',
     'The dashboard surfaces it automatically.'),
    ('¿Quién me debe, y hace cuánto?',
     'Who owes me, and for how long?'),
    ('Te enterás cuando ya es tarde.',
     'You find out when it’s already too late.'),
    ('El sistema te avisa antes.',
     'The system flags it first.'),
    ('Necesito un número y lo tengo que pedir.',
     'I need a number and I have to go ask for it.'),
    ('Días de espera por algo que ya está en tu base.',
     'Days of waiting for something that’s already in your database.'),
    ('Se lo preguntás al asistente: responde en segundos.',
     'You ask the assistant: it answers in seconds.'),
    ('Un buen cliente dejó de comprar.',
     'A good customer stopped buying.'),
    ('Y nadie te avisó a tiempo.',
     'And nobody flagged it in time.'),
    ('Una alerta a tu teléfono, a tiempo.',
     'An alert on your phone, in time.'),
    ('Decido de memoria.',
     'I decide off the top of my head.'),
    ('Porque el dato no está a mano.',
     'Because the number isn’t at hand.'),
    ('El negocio entero en una sola pantalla.',
     'The whole business on a single screen.'),
    ('Ninguno se arregla cambiando tus sistemas. Se arreglan haciéndolos hablar entre ellos — y viéndolos juntos, en un solo lugar.',
     'None of this gets fixed by changing your systems. It gets fixed by making them talk to each other, and seeing them together, in one place.'),
    ('</svg>Cómo trabajamos</p>',
     '</svg>How we work</p>'),
    ('Un solo responsable del camino entero.',
     'One owner, end to end.'),
    ('>Radiografía<',
     '>X-ray<'),
    ('>Conexión<',
     '>Connection<'),
    ('>Construcción<',
     '>Build<'),
    ('>Verificación<',
     '>Verification<'),
    ('>Vigilancia<',
     '>Monitoring<'),
    ('>Mejora<',
     '>Improvement<'),
    ('y el ciclo vuelve a empezar',
     'and the cycle starts again'),
    ('>y el ciclo<',
     '>and the cycle<'),
    ('>vuelve a empezar<',
     '>starts again<'),
    ('De sistemas que no se hablan a procesos eficientes que generan valor.',
     'From systems that don’t talk to processes that create value.'),
    ('</svg>Primero el proceso, después la tecnología</p>',
     '</svg>Process first, technology second</p>'),
    ('No todo se automatiza. Cada paso va a la herramienta correcta.',
     'Not everything gets automated. Each step goes to the right tool.'),
    ('Primero tu flujo y tus procesos; después la tecnología. Automatizamos donde hay retorno: si un paso no devuelve más de lo que cuesta, no se toca.',
     'First your flow and your processes; then the technology. We automate where there’s a return: if a step doesn’t pay for itself, we leave it alone.'),
    ('>un paso del trabajo relevado<',
     '>a step in the work we mapped<'),
    ('>[código]<',
     '>[code]<'),
    ('>Software a medida<',
     '>Custom software<'),
    ('Cuando las reglas son claras y se repiten. Acá viven los números y las tareas que hoy te comen horas.',
     'When the rules are clear and they repeat. This is where the numbers live, and the tasks eating your hours today.'),
    ('>[modelo]<',
     '>[model]<'),
    ('>Un agente<',
     '>An agent<'),
    ('Cuando hay que mirar varias fuentes, decidir el próximo paso y ejecutarlo. Coordina, evalúa y ejecuta: como alguien de tu equipo que nunca se olvida de nada.',
     'When it has to check several sources, decide the next step and carry it out. It coordinates, evaluates and executes: like someone on your team who never forgets a thing.'),
    ('>[humano]<',
     '>[human]<'),
    ('>Un humano en control<',
     '>A human in control<'),
    ('Cuando la decisión tiene ambigüedad, responsabilidad o consecuencias que no se deshacen.',
     'When the decision carries ambiguity, responsibility, or consequences you can’t undo.'),
    ('La autonomía se gana, no se toma: todo corre primero en modo revisión, y recién cuando demuestra que acierta, se enciende solo. La confianza no se automatiza.',
     'Autonomy is earned, not taken: everything runs in review mode first, and it only switches on by itself once it has proven it gets things right. Trust can’t be automated.'),
    ('</svg>Por qué nosotros</p>',
     '</svg>Why us</p>'),
    ('El trabajo pide dos criterios que rara vez viven en la misma persona.',
     'The job asks for two kinds of judgment that rarely live in the same person.'),
    ('<h3>El mundo comercial</h3>',
     '<h3>The commercial world</h3>'),
    ('<li>procesos</li>',
     '<li>processes</li>'),
    ('<li>dónde se gana y se pierde</li>',
     '<li>where you make money and where you lose it</li>'),
    ('<li>riesgo y adopción</li>',
     '<li>risk and adoption</li>'),
    ('<li>valor del negocio</li>',
     '<li>business value</li>'),
    ('<h3>El mundo técnico</h3>',
     '<h3>The technical world</h3>'),
    ('<li>los datos y los sistemas</li>',
     '<li>the data and the systems</li>'),
    ('<li>el código y las reglas</li>',
     '<li>the code and the rules</li>'),
    ('<li>la confiabilidad</li>',
     '<li>reliability</li>'),
    ('<li>no inventar un número</li>',
     '<li>never inventing a number</li>'),
    ('>nosotros</span>',
     '>us</span>'),
    ('<b>A medida, no enlatado</b>',
     '<b>Custom, not off-the-shelf</b>'),
    ('<b>En semanas, no en años</b>',
     '<b>In weeks, not years</b>'),
    ('<b>Atención directa del que lo construye</b>',
     '<b>Direct line to the person who builds it</b>'),
    ('<b>En tu empresa, capacitando a tu equipo</b>',
     '<b>On site, training your team</b>'),
    ('Convertimos entender tu negocio en software que anda: más productividad hoy, listo para escalar mañana.',
     'We turn understanding your business into software that works: more productivity today, ready to scale tomorrow.'),
    ('</svg>El siguiente paso</p>',
     '</svg>The next step</p>'),
    ('Empecemos por la radiografía de tu negocio.',
     'Let’s start with an X-ray of your business.'),
    ('Relevamos tu operación y te mostramos, con tus propios números, cómo están trabajando tus procesos y dónde hay lugar para mejorar. Sin tocar lo que ya anda. Si hay algo para construir, lo ves antes de decidir.',
     'We map your operation and show you, with your own numbers, how your processes are actually working and where there’s room to improve. Without touching what already runs. If there’s something worth building, you’ll see it before you decide.'),
    ('leemos tus datos sin tocar lo que factura',
     'we read your data without disrupting your billing'),
    ('construimos arriba lo que te falta',
     'we build on top of what’s missing'),
    ('Tu negocio, más eficiente cada mes.',
     'Your business, more efficient every month.'),
    ('<p class="idioma"><span class="actual" aria-current="true">ES</span><span class="sep" aria-hidden="true">/</span><a href="/en" hreflang="en" lang="en">EN</a></p>',
     '<p class="idioma"><a href="/" hreflang="es" lang="es">ES</a><span class="sep" aria-hidden="true">/</span><span class="actual" aria-current="true">EN</span></p>'),
]


def main() -> int:
    html = ORIGEN.read_text(encoding="utf-8")
    faltantes = []

    for es, en in TEXTOS:
        if es not in html:
            faltantes.append(es)
            continue
        html = html.replace(es, en)

    if faltantes:
        print("El español cambió: estas cadenas ya no están en index.html.", file=sys.stderr)
        print("Actualizá el diccionario antes de regenerar.\n", file=sys.stderr)
        for f in faltantes:
            print(f"  · {f[:96]}", file=sys.stderr)
        return 1

    # ningún resto de castellano suelto en el cuerpo
    cuerpo = html[html.index("<body>"):html.index("</main>")]
    cuerpo = re.sub(r"<script.*?</script>", "", cuerpo, flags=re.S)
    cuerpo = re.sub(r"<!--.*?-->", "", cuerpo, flags=re.S)   # los comentarios no los ve nadie
    sospechosas = sorted({
        p.lower() for p in re.findall(
            r"(?<![\w-])(que|para|los|las|con|del|una|por|tus|m\u00e1s|est\u00e1|sistemas|nuestro|tambi\u00e9n)(?![\w-])",
            cuerpo, re.I)
    })
    if sospechosas:
        print(f"Aviso: quedan palabras en español en el cuerpo: {', '.join(sospechosas)}", file=sys.stderr)

    DESTINO.write_text(html, encoding="utf-8")
    print(f"{DESTINO.relative_to(RAIZ)} generado · {len(TEXTOS)} reemplazos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

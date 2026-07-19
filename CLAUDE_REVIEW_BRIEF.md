# Brief para Claude: revisión de Gamer Signal

## Contexto

Estoy creando una app en Streamlit llamada **Gamer Signal**. El archivo principal es `app.py` y el motor editorial final está en `editorial_engine_final.py`.

La app busca noticias y señales de conversación sobre gaming, tecnología, anime, cultura geek, indie, nostalgia y debates. Luego convierte esa información en posts para Instagram/Facebook.

No quiero depender de una API pagada de IA. La app usa RSS, memoria local, reglas editoriales y fuentes confiables.

## Marcas

### El Gamer Cave

Comunidad gamer/geek para Puerto Rico y LatAm.

Tono:
- Cercano.
- Conversacional.
- Entusiasta.
- Comunitario.
- Informativo sin sonar corporativo.

Lema: "Tu tribu geek, tu hogar."

Hashtag principal obligatorio:
- `#elgamercave`

### Daviet Gaming

Marca personal gaming/tech/creación.

Tono:
- Casual.
- Gamer.
- Creativo.
- Directo.
- Más personal/opinión que medio de noticias.

Hashtag principal obligatorio:
- `#davietgaming`

## Objetivo editorial

La app debe funcionar como un asistente editorial tipo ChatGPT:

1. Entiende lo que el usuario pide.
2. Si tiene información suficiente, crea un post limpio.
3. Si no tiene suficiente información, busca más contexto en fuentes confiables.
4. Si no puede verificar, NO inventa.
5. Si el tema no es noticia confirmada, lo presenta como editorial, nostalgia o debate.
6. Todo post final debe estar en español natural.
7. Puede usar nombres oficiales de juegos/anime en inglés, pero no debe dejar frases largas o titulares completos en inglés.

## Problemas actuales que hay que revisar

La app ha generado errores como:

- Títulos completos en inglés dentro del post.
- Frases en inglés dentro del cuerpo del caption.
- Posts genéricos con frases como "es un tema reciente" o "lo importante es explicar".
- Repetición del título dentro del primer párrafo.
- Categorías incorrectas: juegos grandes como indie, noticias de gaming como tecnología, etc.
- Hashtags no relacionados con la noticia.
- Radar mostrando temas "rojos" como si fueran oportunidades reales.
- Posts de 5 publicaciones mezclando noticia, nostalgia y debate sin conexión.
- Texto interno apareciendo al usuario.
- Frases con encoding roto.

## Reglas fuertes para posts

Todo post final debe tener:

1. Gancho claro.
2. Contexto real o editorial honesto.
3. Una razón concreta de por qué importa.
4. Una emoción o ángulo comunitario.
5. Pregunta final relacionada con el tema.
6. Exactamente 5 hashtags.
7. Hashtag de la marca como primero.

Debe evitar:

- Inventar datos.
- Copiar titulares en inglés como caption.
- Usar frases genéricas de relleno.
- Mezclar categorías sin sentido.
- Presentar rumores como hechos.
- Meter fuentes, links o notas internas en el caption final.
- Repetir temas usados recientemente.

## Si no hay información suficiente

La lógica correcta es:

- Si es noticia: buscar más contexto y verificar.
- Si no se verifica: no crearla como noticia.
- Si sirve como conversación: convertirla en debate/editorial claramente.
- Si no hay nada útil: decir que no hay suficiente información confiable.

Frase esperada:

> No tengo suficiente información verificada para crear un post confiable sobre este tema. Puedo trabajarlo como debate/opinión, pero no como noticia confirmada.

## Fuentes 2026 para mejorar el criterio editorial

Usar estas ideas como guía editorial, no como texto literal:

- Hootsuite Social Media Trends 2026: autenticidad humana, remix nostálgico, rapidez cultural y análisis de patrones creativos.
  https://www.hootsuite.com/es/research/social-trends

- Hootsuite Social Media Engagement 2026: engagement no es solo likes; importan comentarios, compartidos, guardados, DMs, preguntas reales, storytelling y contenido que invite participación sin engagement bait.
  https://blog.hootsuite.com/social-media-engagement/

- Sprout Social 2026 Content Strategy Report: los usuarios quieren contenido humano, adaptado por plataforma y con entendimiento real del público.
  https://sproutsocial.com/insights/data/2026-social-media-content-strategy-report/

- Sprinklr Social Index 2026: muchas marcas publican mucho, pero pocas logran relevancia sostenida; importa aparecer en momentos que realmente le importan a la audiencia.
  https://www.sprinklr.com/resources/social-index-report/

- Meta for Business: revisar qué contenido recibe alcance/engagement y ajustar según comentarios, compartidos y reacciones reales.
  https://www.facebook.com/business/pages/manage

## Criterio 2026 de engagement que quiero incorporar

La app no debe asumir que un post será bueno solo porque el tema es popular. Antes de redactar debe evaluar:

1. ¿La noticia o tema tiene un dato concreto y verificable?
2. ¿Se puede explicar en español natural sin copiar el titular en inglés?
3. ¿La comunidad puede responder algo personal, como experiencia, opinión, recuerdo o decisión de compra?
4. ¿El post invita a comentar sin sonar a engagement bait?
5. ¿El tema sirve para compartir, guardar o debatir de forma sana?
6. ¿El ángulo encaja con la marca activa: El Gamer Cave o Daviet Gaming?
7. ¿La pregunta final está conectada directamente con el tema?

Regla editorial:

> Si el post no puede explicar qué pasó, por qué importa y qué conversación real abre, no debe publicarse como noticia. Debe convertirse en editorial/debate o rechazarse.

## Fuentes/referencias que Claude debe revisar si puede

- Sprout Social 2026 Content Strategy Report: qué espera la audiencia del contenido de marcas, importancia de autenticidad, valor y adaptación por plataforma.
  https://sproutsocial.com/insights/data/2026-social-media-content-strategy-report/

- Hootsuite Social Media Trends 2026: tendencias de autenticidad, rapidez cultural, remix nostálgico y contenido que se siente humano.
  https://www.hootsuite.com/es/research/social-trends

- Hootsuite Social Media Engagement: engagement como comentarios, compartidos, guardados, DMs y conversación real, no solo likes.
  https://blog.hootsuite.com/social-media-engagement/

- Sprinklr Social Index: relevancia sostenida, conversación de audiencia y evitar publicar mucho sin aportar valor.
  https://www.sprinklr.com/resources/social-index-report/

- Meta for Business: revisar rendimiento de posts, comentarios, compartidos y reacciones para ajustar el contenido.
  https://www.facebook.com/business/pages/manage

Pídele a Claude que use esas fuentes como criterio editorial, no como frases para copiar dentro de los posts.

## Lo que necesito de Claude

Revisa `app.py` y `editorial_engine_final.py` y dime:

1. Qué funciones duplicadas o viejas pueden eliminarse sin romper la app.
2. Qué funciones realmente generan los posts.
3. Dónde se cuelan títulos o frases en inglés.
4. Dónde se clasifican mal las categorías.
5. Cómo mejorar el flujo:
   buscar información -> validar fuente -> clasificar -> redactar -> revisar -> mostrar.
6. Qué pruebas faltan para evitar que regresen estos errores.
7. Qué cambios aplicar para que el app genere posts más parecidos a ChatGPT, pero usando las voces de El Gamer Cave y Daviet Gaming.

Prioridad:

No quiero posts bonitos pero falsos. Quiero posts claros, reales, humanos, útiles para la comunidad y con potencial de comentarios.

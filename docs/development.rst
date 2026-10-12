Desarrollo y documentación
==================================

Organización del repositorio
------------------------------------

.. code-block:: text

   VERSION                       versión publicada del pipeline
   bin/run-workflow              punto de entrada actual
   workflow/Snakefile            reglas y dependencias
   workflow/scripts/             validación, referencia, QC y tablas
   workflow/envs/                YAML y lock Linux x86_64
   config/examples/              plantillas genéricas
   config/local/                 configuración privada, ignorada
   config/*projectcreole*        metadatos/configuración original
   profiles/local/               ejecución local
   profiles/slurm/               perfil de clúster
   tests/                        regresiones sintéticas
   docs/                         fuentes Sphinx y guías Markdown
   .readthedocs.yaml              configuración del sitio existente
   .github/workflows/            validación automática

El Makefile y los scripts Shell/R históricos no son dependencias del workflow
nuevo. Mantén claras las fronteras entre código histórico y comportamiento actual.

Pruebas del pipeline
----------------------------

.. code-block:: bash

   .venv/bin/python -m unittest discover -s tests -v
   bash -n bin/run-workflow
   # Requiere configuración y FASTQ existentes:
   bin/run-workflow --configfile config/local/run.yaml --lint

Las regresiones generan entradas sintéticas temporales. Las pruebas CI no
son un análisis end-to-end de las herramientas bioinformáticas ni validación
biológica. Actualiza tests y documentación al cambiar opciones o fórmulas.

Construir el manual localmente
--------------------------------------

No necesitas datos ni instalar el entorno bioinformático:

.. code-block:: bash

   uv venv --python 3.12 .venv-docs
   uv pip sync --python .venv-docs/bin/python docs/requirements.txt
   .venv-docs/bin/sphinx-build -n -W --keep-going -b html docs docs/_build/html
   .venv-docs/bin/python -m http.server 8000 --directory docs/_build/html

Abre ``http://localhost:8000``. Detén el servidor con Ctrl+C.
La compilación trata avisos y referencias rotas como errores.
``docs/_build/`` y ``.venv-docs/`` están ignorados por Git.

Sphinx usa ``sphinx_rtd_theme`` y MyST para integrar las guías Markdown
sin perder enlaces históricos. ``docs/conf.py`` lee ``VERSION``; la misma
configuración sirve para local, CI y Read the Docs.

Actualizar dependencias de documentación
------------------------------------------------

``docs/requirements.in`` fija las dependencias directas;
``docs/requirements.txt`` contiene la resolución completa con hashes.
Tras revisar compatibilidad de Python, Sphinx, tema y MyST:

.. code-block:: bash

   uv pip compile --python-version 3.12 --generate-hashes --no-emit-index-url \
     docs/requirements.in -o docs/requirements.txt
   uv pip sync --python .venv-docs/bin/python docs/requirements.txt
   .venv-docs/bin/sphinx-build -n -W --keep-going -b html docs docs/_build/html

No incluyas entornos ni HTML generado en los commits.

Read the Docs existente y versiones
-------------------------------------------

Este repositorio ya tiene un sitio público:
`BIOMOLC-PhurejaMutante en Read the Docs <https://biomolc-phurejamutante.readthedocs.io/es/latest/>`_.
Se conserva ``install.html``: la fuente sigue siendo ``docs/install.rst``.
No es necesario crear otro proyecto ni cambiar el dominio.

``.readthedocs.yaml`` declara Ubuntu 24.04, Python 3.12, las dependencias de
documentación y el build Sphinx con errores ante avisos. No instala paquetes
bioinformáticos ni descarga datos para publicar el manual.

* ``latest`` refleja la rama configurada en el proyecto (normalmente ``main``).
* La etiqueta ``0.1.0-beta`` fija un estado del código y la documentación.
* La publicación de una etiqueta depende de que esa versión esté activa
  y de la automatización/webhook configurados en Read the Docs.
* Crear una etiqueta Git no garantiza por sí solo activar una versión o mover
  el alias ``stable``; las preversiones beta pueden no seleccionarse como estables.
* GitHub Actions comprueba la compilación; no sustituye el build del sitio alojado.

Después de un push, revisa el build del **proyecto existente** y la página
pública. Si una versión no aparece, verifica su activación en el panel del
sitio. No compartas tokens para resolver un build: usa los logs del proyecto.

Convención de commits y releases
----------------------------------------

Cada commit debe representar una intención, con implementación/tests juntos
cuando corresponda. Su mensaje es una sola línea:

.. code-block:: text

   type(scope): imperative description

Tipos: ``feat``, ``fix``, ``chore``, ``docs``, ``refactor``, ``style``, ``test``,
``perf``, ``build`` y ``ci``. Usa ámbito corto, inglés, minúsculas, máximo
40 caracteres, sin punto final, cuerpo ni trailers. Ejemplo:

.. code-block:: text

   docs(usage): explain workflow setup

Revisa el staging de forma selectiva y no publiques datos/credenciales.
No reescribas historial ni muevas etiquetas publicadas sin autorización explícita.
Para una nueva versión, actualiza ``VERSION`` y notas, valida, crea commits
atómicos y una etiqueta anotada con la versión acordada.

Licencia y atribución
-----------------------------

El código se distribuye según :download:`LICENSE <../LICENSE>` (GPL versión 2).
Las herramientas y referencias externas conservan sus propios términos.
El proyecto pertenece a BIOMOLC / Semillero de Agrigenómica, Universidad
Distrital Francisco José de Caldas. El DOI histórico y atribución original
se conservan en el repositorio; una beta Git no implica un nuevo depósito DOI.

Configuración y entradas
================================

Archivos y precedencia
------------------------------

El Snakefile carga ``config/reference-spuddb.yaml`` y ``config/smoke.yaml``
como valores iniciales. Los archivos pasados con ``--configfile`` y los
valores de ``--config`` los sobrescriben según la combinación de configuración
de Snakemake. La plantilla genérica sobrescribe muestras, modo smoke,
contrastes y recursos para evitar heredar el ejemplo ProjectCreole.

Las rutas de configuración y de salida se interpretan desde la raíz del
repositorio: el lanzador cambia a esa carpeta incluso si se invoca desde otra.
Las rutas relativas ``fastq1``/``fastq2`` se resuelven contra ``data_root``;
se permiten también rutas absolutas.

.. note::

   Las configuraciones se combinan, no sustituyen necesariamente cada clave
   ausente. Parte de ``config/examples/run.yaml`` en vez de un YAML parcial,
   y revisa ``provenance/config.yaml`` después de ejecutar.

Tabla de muestras TSV
-----------------------------

Se requieren estas siete columnas, separadas por **tabuladores**:

.. list-table::
   :header-rows: 1
   :widths: 23 77

   * - Columna
     - Contenido
   * - ``sample_id``
     - Identificador único, comienza con letra/número y contiene solo letras,
       números, punto, guion o guion bajo.
   * - ``fastq1``
     - Archivo FASTQ de cuatro líneas por registro, plano o gzip; R1 si es paired-end.
   * - ``fastq2``
     - Campo vacío en single-end; archivo R2 distinto de R1 en paired-end.
   * - ``layout``
     - ``single`` o ``paired``.
   * - ``strandedness``
     - ``unstranded``, ``forward`` o ``reverse``, confirmado según protocolo.
   * - ``stage``
     - Estadio/condición no vacío; los contrastes requieren coincidencia entre muestras.
   * - ``genotype``
     - Genotipo/grupo no vacío; no permite inferir por sí mismo replicación biológica.

La plantilla descargable conserva los tabuladores reales:
:download:`samples.tsv <../config/examples/samples.tsv>`.
El archivo de ejemplo usa single-end no orientado: **no es una recomendación
sobre el protocolo de tus bibliotecas**.

Para paired-end, establece ambas rutas, ``layout=paired`` y la orientación
correcta. Los IDs de los prefijos deben concordar; el validador normaliza
sufijos ``/1`` y ``/2``. No reordena ni repara archivos desincronizados.

``unknown`` solo se admite si ``smoke.enabled: true`` y
``allow_unconfirmed_library: true``. Representa una suposición técnica;
no se permite en una ejecución completa. IDs duplicados, archivos ausentes,
mates idénticos y columnas faltantes producen errores.

Parámetros de ejecución
-------------------------------

Descarga el :download:`YAML genérico <../config/examples/run.yaml>` y adapta:

.. list-table::
   :header-rows: 1
   :widths: 36 64

   * - Clave
     - Significado / restricción
   * - ``samples``
     - Ruta al TSV.
   * - ``data_root``
     - Carpeta base de las rutas FASTQ relativas.
   * - ``output_dir``
     - Carpeta de resultados, separada de las entradas.
   * - ``allow_unconfirmed_library``
     - Booleano; ``true`` solo en smoke.
   * - ``smoke.enabled``
     - Booleano: subconjuntos técnicos o datos completos.
   * - ``smoke.reads``
     - Límite positivo de registros por archivo cuando smoke está activo.
   * - ``smoke.contig`` / ``smoke.max_bases``
     - Contig y límite positivo de región, con genes completos.
   * - ``alignment.use_strandedness``
     - Booleano; por defecto ``true``. Si es ``false``, omite orientación en
       HISAT2 sin modificar la orientación de featureCounts.
   * - ``analysis.mode``
     - Debe ser ``exploratory``; no existe modo diferencial implementado.
   * - ``analysis.pseudocount_cpm``
     - Número finito positivo; por defecto 1.0.
   * - ``analysis.low_count_threshold``
     - Entero no negativo; por defecto 10. Marca conteos bajos, no filtra genes.
   * - ``analysis.contrasts``
     - Lista explícita de comparaciones; ``[]`` no genera cocientes.
   * - ``threads.index/align/count``
     - Hilos solicitados por etapa; usa enteros positivos.
   * - ``memory_mb.reference/index/align/count``
     - Memoria solicitada por etapa en MB; ajusta al límite global y al equipo.

Usa booleanos YAML sin comillas. ``"false"`` es texto, no el booleano ``false``.
Los valores de referencia, memoria y hilos deben estar completos en la
configuración resuelta; no todas las claves tienen validación exhaustiva.

Contrastes descriptivos
-------------------------------

.. code-block:: yaml

   analysis:
     mode: exploratory
     pseudocount_cpm: 1.0
     low_count_threshold: 10
     contrasts:
       - name: mutant_vs_control_stage1
         numerator: mutant_1
         denominator: control_1

Ambos IDs deben existir, ser distintos y compartir ``stage``. El orden define
el signo del log2 cociente. El contraste no calcula significancia y no implica
que los grupos tengan un diseño experimental válido: :doc:`methods`.

Referencia predeterminada
---------------------------------

``config/reference-spuddb.yaml`` define SpudDB DM v6.1, FASTA, GFF3, URLs HTTPS,
cache y SHA-256. Los hashes fueron observados en la primera descarga del
proyecto; **no son checksums proporcionados por SpudDB**.
La referencia es específica de versión. Una discrepancia aborta la ejecución;
no sustituyas el hash por el nuevo sin investigar la procedencia.

Referencia local alternativa
------------------------------------

Crea ``config/local/reference.yaml``. El siguiente bloque es conceptual:
las rutas y hashes deben sustituirse por los reales.

.. code-block:: yaml

   reference:
     name: Colombia_VERSION_ANOTACION
     download: false
     fasta: /ruta/colombia/genome.fa
     gff3: /ruta/colombia/genes.gff3
     fasta_sha256: HASH_SHA256_DEL_FASTA
     gff3_sha256: HASH_SHA256_DEL_GFF3

.. code-block:: bash

   sha256sum /ruta/colombia/genome.fa /ruta/colombia/genes.gff3
   bin/run-workflow --profile profiles/local \
     --configfile config/local/run.yaml config/local/reference.yaml \
     --config output_dir=result/colombia_VERSION --dry-run

Calcula los hashes sobre los archivos tal como se suministran, comprimidos
si corresponde. El parser admite FASTA/GFF3 planos o gzip. Necesita
``mRNA``/``transcript`` con un ``ID`` y un ``Parent`` de gen, y exones con
``Parent`` de transcrito; no sustituye CDS por exones ni convierte GTF.
Los contigs, orientación y coordenadas deben concordar con el FASTA.
Usa un nuevo nombre y salida para cada ensamblaje/anotación.

Datos privados y procedencia
------------------------------------

``config/local/``, ``data/`` (salvo la lista histórica de URLs),
``references/``, ``result/`` y los entornos están ignorados por Git.
Las exclusiones no protegen archivos ubicados fuera de esos directorios
ni impiden incorporaciones forzadas: revisa siempre lo que vas a publicar.
``provenance/`` contiene rutas y metadatos de archivos; no lo publiques sin
revisión de privacidad.

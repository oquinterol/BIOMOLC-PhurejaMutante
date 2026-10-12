Resultados y control de calidad
=======================================

Estructura de salida
----------------------------

Dentro de ``output_dir``:

.. code-block:: text

   provenance/
     config.yaml
     runtime.json
   reference/
     genome.fa
     exons.saf
     genes.tsv
     splice_sites.tsv
     manifest.json
     hisat2_index/
   reads/                         # solo smoke, prefijos derivados
   bam/<sample>.bam
   bam/<sample>.bam.bai
   counts/<sample>.tsv
   counts/<sample>.tsv.summary
   tables/
     raw_counts.tsv
     cpm.tsv
     log2_cpm.tsv
     gene_lengths.tsv
     library_sizes.tsv
     samples.tsv
     descriptive_ratios.tsv
     report.json
   qc/
     fastqc/
     alignment/<sample>.flagstat.txt
     multiqc_report.html
     multiqc_report_data/
   logs/

La referencia descargada se conserva aparte en ``references/``. Las salidas
pueden contener datos sensibles; no se distribuyen con el código.

Tablas descriptivas
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Archivo
     - Contenido
   * - ``raw_counts.tsv``
     - ``gene_id`` y una columna de conteos por muestra. Genes ordenados por ID.
   * - ``cpm.tsv``
     - Mismas filas/columnas; CPM respecto a unidades exónicas asignadas.
   * - ``log2_cpm.tsv``
     - ``log2(CPM + pseudocount_cpm)``.
   * - ``gene_lengths.tsv``
     - ``gene_id``, ``union_exonic_length_bp``; longitud de unión exónica.
   * - ``library_sizes.tsv``
     - ``sample_id``, ``assigned_exonic_units``, ``zero_library``.
   * - ``samples.tsv``
     - ID, genotipo, estadio, layout y orientación de la tabla resuelta.
   * - ``descriptive_ratios.tsv``
     - Contraste, gen, numerador, denominador, ``log2_cpm_ratio`` y
       ``low_counts_both``. Solo cabecera si no hay contrastes.
   * - ``report.json``
     - Modo, referencia, número de genes/muestras, asignaciones, estados
       featureCounts, pseudoconteo, umbral, bibliotecas cero y limitaciones.

La suma de cada columna CPM válida es aproximadamente un millón. Si una
biblioteca no tiene unidades asignadas, se conserva ``NA``. No hay columnas
p-value, FDR ni significancia. Consulta las fórmulas en :doc:`methods`.

Los archivos ``counts/<sample>.tsv`` conservan la salida featureCounts de una
sola biblioteca. La etapa de resumen exige IDs/longitudes concordantes entre
muestras y que la suma de conteos coincida con ``Assigned`` del summary.
Una incompatibilidad produce error, no una matriz mezclada silenciosamente.

Qué revisar primero
---------------------------

#. Abre ``qc/multiqc_report.html`` en un navegador.
#. Revisa calidad, composición y secuencias sobrerrepresentadas en FastQC.
#. Contrasta mapeo HISAT2, estadísticas samtools y asignación featureCounts.
#. Busca bibliotecas sin asignaciones en ``tables/report.json``.
#. Comprueba orientación, referencia, estadio y genotipo antes de comparar CPM.

FastQC puede terminar con exit 0 y aun mostrar módulos de aviso/fallo.
No existe un umbral de QC universal impuesto por esta versión.
La baja asignación en un smoke con referencia recortada no mide rendimiento
sobre el genoma completo. No la interpretes como fallo biológico de la muestra.

Procedencia
-------------------

``provenance/config.yaml`` contiene la configuración resuelta.
``provenance/runtime.json`` registra Python, ejecutables/versiones de herramientas,
layout/orientación y rutas, tamaño, mtime y registros de prefijo revisados.
``reference/manifest.json`` documenta las entradas de referencia, SHA-256,
región seleccionada, número de genes y sitios de splicing.
Los logs del extractor registran hashes y número de registros de cada subset.

Estos registros no sustituyen checksums completos de los FASTQ originales
ni una descripción del diseño experimental. Registra también la etiqueta y
hash Git utilizados. Los archivos de procedencia incluyen rutas privadas:
revísalos antes de adjuntarlos a una incidencia o publicación.

Conservación
--------------------

No borres originales para ahorrar espacio desde el pipeline. Si deseas
archivar una ejecución, conserva configuración, metadatos confirmados,
versión/hash, reportes, matrices y checksums junto al respaldo de entradas.
Revisa requisitos de trazabilidad de tu proyecto antes de borrar BAM/índices.
Nunca mezcles matrices de anotaciones o unidades de conteo distintas.

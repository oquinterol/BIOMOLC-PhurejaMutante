Versiones y notas de publicación
========================================

0.1.0-beta
------------------

Primera beta identificada del workflow Snakemake exploratorio reutilizable,
con código y documentación publicados sin archivos de datos ni resultados.
La etiqueta Git ``0.1.0-beta`` fija el contenido de esta versión y ``VERSION``
es la fuente de versión para Sphinx.

Incluye
~~~~~~~~~~~~~~~

* Flujo FASTQ → validación → referencia/exones → HISAT2 → BAM → featureCounts.
* FastQC y MultiQC, matrices de conteos/CPM y cocientes descriptivos.
* Referencia SpudDB DM v6.1 con SHA-256 fijados y alternativa local FASTA/GFF3.
* Orientación por biblioteca y opción de alineamiento neutral independiente
  del modo de conteo.
* Entornos fijados, plantillas genéricas y perfiles local/Slurm.
* Documentación en español con Sphinx y tema Read the Docs: instalación,
  uso, configuración, métodos, resultados y diagnóstico.
* Pruebas sintéticas y compilación de documentación en CI.

Validación y pendientes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Las regresiones sintéticas y la compilación estricta comprueban comportamiento
implementado y referencias del manual, no validez biológica.
La evidencia end-to-end previa se limita a prefijos single-end ProjectCreole
con una región pequeña de DM v6.1.

Quedan pendientes la confirmación de metadatos/integridad completa de
ProjectCreole, el análisis de bibliotecas completas, paired-end real,
benchmark del índice completo y validación real de Slurm.
No se incluye trimming, conversión SRA, SNPs, DESeq2, p-valores ni FDR.

Versiones alpha históricas
----------------------------------

``v0.0.1-alpha``, ``v0.0.2-alpha`` y ``v0.0.3-alpha`` documentan el desarrollo
Shell/Make original. No son versiones del workflow Snakemake actual.
El código histórico se conserva, sin presentarlo como un pipeline validado
para los datos RNA-seq exploratorios actuales.

El historial se normalizó a mensajes del estándar del proyecto, separando
intenciones y manteniendo identidades, fechas de autor/committer y estados
históricos. Los hashes anteriores cambiaron; las etiquetas alpha apuntan
al mismo contenido histórico en el grafo normalizado.

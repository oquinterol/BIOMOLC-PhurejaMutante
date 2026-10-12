BIOMOLC-PhurejaMutante
==============================

Documentación de la versión |release|, un pipeline reproducible de RNA-seq
exploratorio para *Solanum tuberosum* grupo Phureja.

El workflow actual usa **Snakemake, HISAT2 y featureCounts** para generar
control de calidad, conteos exónicos por gen y tablas descriptivas. El código
puede reutilizarse con FASTQ propios y una referencia FASTA/GFF3 compatible.

.. important::

   Se distribuye el **pipeline**, no lecturas, genomas descargados ni archivos
   de resultados. Las configuraciones ProjectCreole contienen metadatos del
   proyecto original. No hay expresión diferencial inferencial, p-valores ni
   FDR en esta versión.

Empieza por :doc:`install`, prepara las entradas con :doc:`configuration`
y sigue :doc:`usage`. Para entender qué mide cada salida, consulta
:doc:`methods` y :doc:`outputs`.

.. toctree::
   :maxdepth: 2
   :caption: Manual de usuario

   overview
   install
   usage
   configuration
   methods
   outputs
   cluster
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Proyecto y versiones

   development
   release-notes

.. toctree::
   :maxdepth: 1
   :caption: Guías complementarias y evidencia histórica

   reuse
   snakemake-workflow
   projectcreole-smoke-tests

* `Código y etiquetas en GitHub <https://github.com/oquinterol/BIOMOLC-PhurejaMutante>`_
* `Reportar problemas <https://github.com/oquinterol/BIOMOLC-PhurejaMutante/issues>`_

Qué hace el pipeline
============================

Objetivo y alcance
--------------------------

El pipeline organiza un análisis exploratorio de RNA-seq: valida muestras,
prepara una referencia anotada, evalúa calidad, alinea lecturas y cuenta
exones agrupados por gen. Permite comparar abundancias descriptivas de
muestras del mismo estadio mediante contrastes explícitos.

Se diseñó para el proyecto Phureja de BIOMOLC, pero las reglas no dependen de
los nombres de los clones. Las plantillas genéricas están en
``config/examples/``. El usuario aporta datos, metadatos y recursos de cómputo.

Flujo
-------------

.. code-block:: text

   FASTQ + muestras TSV + referencia FASTA/GFF3
     ├── validación de entradas y versiones → provenance/
     ├── descarga/cache → SHA-256 → exones SAF + sitios de splicing
     ├── subconjuntos FASTQ (solo smoke) → FastQC
     └── HISAT2 → BAM ordenado + BAI → featureCounts
           ├── conteos / CPM / log2 CPM / razones descriptivas
           └── MultiQC

Etapas implementadas
----------------------------

#. **Validación:** estructura de la configuración, existencia de archivos,
   prefijos FASTQ, correspondencia de IDs en pares y herramientas.
#. **Referencia:** descarga opcional por HTTPS, comprobación SHA-256,
   compatibilidad FASTA/GFF3 y unión de exones del mismo gen.
#. **Alineamiento:** índice HISAT2, sitios de splicing conocidos, BAM ordenado,
   índice BAM y resumen ``samtools flagstat``.
#. **Conteo:** featureCounts por biblioteca con orientación explícita.
#. **Exploración:** matrices, tamaños de bibliotecas asignadas, CPM,
   transformación logarítmica y cocientes configurados.
#. **Calidad:** FastQC por archivo y reporte integrado MultiQC.

Qué no hace
-------------------

* No recorta adaptadores ni filtra lecturas antes de alinear.
* No convierte SRA ni analiza variantes/SNPs en el workflow actual.
* No ejecuta DESeq2, pruebas de expresión diferencial, p-valores ni FDR.
* No infiere orientación, identidad de muestras o replicación biológica.
* No verifica íntegramente todos los FASTQ originales: examina prefijos.
* No cuantifica isoformas por separado ni produce TPM.

.. warning::

   Los estadios no se deben tratar como réplicas biológicas. Los subconjuntos
   técnicos no generan replicación. CPM es composicional, no expresión
   absoluta, y una referencia distinta del genotipo puede sesgar el mapeo.

Estado de validación
----------------------------

Esta beta cuenta con regresiones sintéticas y validación técnica histórica
single-end sobre prefijos ProjectCreole y 2 Mb de la referencia DM v6.1.
No se han validado bibliotecas completas de ProjectCreole, paired-end real,
un índice completo medido en esta máquina ni jobs Slurm reales.
Consulta :doc:`projectcreole-smoke-tests` y :doc:`snakemake-workflow`.

Los scripts Make/R históricos se conservan por trazabilidad. No forman
parte del nuevo workflow y no deben usarse como alternativa validada.

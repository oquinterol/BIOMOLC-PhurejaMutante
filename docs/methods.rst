Métodos e interpretación
================================

Validación de lecturas
------------------------------

El validador inspecciona hasta 100 registros por FASTQ: cabecera, separador,
secuencia no vacía, longitud de calidad y caracteres de calidad. Comprueba
correspondencia de IDs en el prefijo de pares y registra ruta, tamaño y mtime.
No calcula hashes completos de los originales ni verifica su gzip completo.
El extractor smoke valida únicamente los registros copiados.

Referencia y unidad de conteo
-------------------------------------

La anotación se recorre como ``exon → Parent transcript → Parent gene``.
Los intervalos exónicos solapados o adyacentes de las isoformas del mismo gen
se unen y se exportan en SAF. Los sitios de splicing se obtienen de los
intervalos por transcrito y se usan como sitios conocidos de HISAT2.
El GFF3 SpudDB puede omitir filas ``gene``: se aceptan sus IDs Parent de gen.

Se rechazan exones sin Parent, transcritos sin ID/Parent únicos, contigs
incompatibles, coordenadas fuera de rango y orientación desconocida.
En smoke se conservan genes completos dentro del contig/región seleccionados.
No se sustituyen exones faltantes por CDS.

Orientación
-------------------

La orientación se configura por muestra; no se adivina a partir del nombre.

.. list-table::
   :header-rows: 1
   :widths: 28 24 24 24

   * - Biblioteca
     - HISAT2 single-end
     - HISAT2 paired-end
     - featureCounts ``-s``
   * - ``unstranded``
     - Sin opción
     - Sin opción
     - 0
   * - ``forward``
     - ``F``
     - ``FR``
     - 1
   * - ``reverse``
     - ``R``
     - ``RF``
     - 2

Con ``alignment.use_strandedness: false`` se omite ``--rna-strandness`` en
HISAT2, pero featureCounts mantiene el ``-s`` correspondiente a cada biblioteca.
``unknown`` en un smoke autorizado se trata técnicamente como no orientado;
no confirma el protocolo.

Alineamiento y conteo
-----------------------------

HISAT2 alinea contra el índice de la referencia configurada. samtools ordena
el BAM, genera BAI y calcula ``flagstat``. La regla divide recursos de hilos
entre alineamiento y ordenamiento; reserva al menos dos hilos para alineamiento.

featureCounts usa SAF, MAPQ mínimo 10 y alineamientos primarios
(``-Q 10 --primary``). No activa conteo de multimapeos ni asignaciones ambiguas
entre genes. En single-end cuenta lecturas; en paired-end usa
``-p --countReadPairs -B -C``: fragmentos con ambos mates alineados y sin quimeras.
La rama paired-end tiene regresiones de metadatos, pero no validación con
bibliotecas reales en este proyecto.

No cambies la interpretación de lecturas a fragmentos al comparar bibliotecas.
Revisa los estados no asignados y el sesgo de mapeo por genotipo/referencia.

CPM y transformación logarítmica
----------------------------------------

Para cada gen, con conteo ``c`` y suma de conteos exónicos asignados ``N``:

.. math::

   \mathrm{CPM} = \frac{c}{N}\times 10^6

El denominador **no es el total de lecturas secuenciadas**. La longitud exónica
se registra, pero no divide el CPM. No es TPM ni expresión absoluta.
Si ``N=0``, CPM y su transformación son ``NA``; una biblioteca inválida no
se transforma en abundancia cero.

``log2_cpm.tsv`` contiene ``log2(CPM + p)``, donde ``p`` es
``analysis.pseudocount_cpm``. El valor se registra en el reporte.

Cocientes descriptivos
------------------------------

Para contrastes explícitos del mismo estadio:

.. math::

   r = \log_2\left(\frac{\mathrm{CPM}_{numerador}+p}
                        {\mathrm{CPM}_{denominador}+p}\right)

Un valor positivo indica mayor CPM en el numerador, no evidencia estadística
de expresión diferencial. Si alguna biblioteca tiene cero asignaciones,
el cociente es ``NA``. ``low_counts_both`` es verdadero cuando el máximo de
los dos conteos es menor que ``low_count_threshold``: es una marca, no un filtro.

Los cocientes dependen del pseudoconteo y la composición de la biblioteca.
Solo generan hipótesis. No se calculan errores estándar, p-valores o FDR.

Límites biológicos y técnicos
-------------------------------------

* Sin réplicas biológicas y un diseño identificable no se sostiene inferencia
  mutante/control mediante este workflow.
* Un estadio distinto no es una réplica intercambiable.
* La referencia DM puede favorecer lecturas de ciertos genotipos frente a otros.
* Un smoke sobre 2 Mb puede asignar muy pocas lecturas del transcriptoma completo.
* FastQC/MultiQC son diagnósticos: generar HTML no equivale a aprobar QC.
* No hay recorte previo de adaptadores; decide si tus lecturas necesitan una
  preparación externa validada y conserva su procedencia.

Registra diseño experimental, referencia, orientación, versión del pipeline
(y hash Git), configuración y decisiones QC antes de interpretar o compartir
resultados.

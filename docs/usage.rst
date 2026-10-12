Uso paso a paso
=======================

Preparar un proyecto privado
------------------------------------

Instala los entornos según :doc:`install`. Desde la raíz del repositorio:

.. code-block:: bash

   mkdir -p config/local
   cp config/examples/run.yaml config/local/run.yaml
   cp config/examples/samples.tsv config/local/samples.tsv

Edita ambos archivos. Los nombres de la plantilla son ficticios: sustituye
rutas, ``stage``, ``genotype``, ``layout`` y ``strandedness`` por metadatos
confirmados. Consulta el esquema TSV en :doc:`configuration`.

* ``data_root`` apunta a tus FASTQ. El workflow no los modifica.
* ``samples`` apunta al TSV privado.
* ``output_dir`` debe estar separado de los originales, preferiblemente
  dentro de ``result/`` para que Git ignore las salidas.
* Usa una salida nueva para cada referencia, versión o configuración
  que quieras conservar como análisis independiente.

.. warning::

   No ejecutes el lanzador sin ``--configfile`` esperando un ejemplo genérico.
   Por compatibilidad, el comando sin configuración selecciona el smoke
   original ProjectCreole y exige esos FASTQ externos.

Simular antes de ejecutar
---------------------------------

.. code-block:: bash

   bin/run-workflow --profile profiles/local \
     --configfile config/local/run.yaml --dry-run

La simulación valida la tabla y las rutas al cargar el Snakefile y muestra
los trabajos pendientes. No alinea lecturas, descarga referencias ni valida
los prefijos con herramientas: eso ocurre al ejecutar las reglas.
Un dry-run correcto no garantiza que todos los procesos finalizarán.

Prueba técnica pequeña con tus datos
--------------------------------------------

Copia tu configuración a ``config/local/smoke.yaml`` y cambia estas secciones:

.. code-block:: yaml

   output_dir: result/my-project-smoke
   smoke:
     enabled: true
     reads: 10000
     contig: chr01
     max_bases: 2000000
   threads:
     index: 2
     align: 2
     count: 2
   memory_mb:
     reference: 1024
     index: 1024
     align: 1024
     count: 1024

Conserva el resto de tu configuración y el TSV. ``contig`` debe existir en
la referencia y la región debe contener genes completos anotados con exones.
Mantén ``allow_unconfirmed_library: false`` para metadatos ya confirmados.

.. code-block:: bash

   bin/run-workflow --profile profiles/local \
     --configfile config/local/smoke.yaml --dry-run
   bin/run-workflow --profile profiles/local \
     --configfile config/local/smoke.yaml
   .venv/bin/python tests/check_smoke_outputs.py \
     --output-dir result/my-project-smoke

El comprobador exige conteos asignados positivos en todas las bibliotecas,
consistencia de matrices/CPM, hashes de los subconjuntos y metadatos de tamaño/
mtime de los originales. Si no hay asignación, revisa región y datos;
no conviertas un resultado técnico pequeño en una conclusión biológica.

Los subconjuntos son los **primeros** registros, no una muestra aleatoria.
El workflow conserva solo genes completos dentro de la región, sin mover
coordenadas. No evalúes tasas de mapeo del genoma completo con este smoke.

Ejecutar el genoma completo
-----------------------------------

En ``config/local/run.yaml`` usa ``smoke.enabled: false`` y una salida
diferente, por ejemplo ``result/my-project``. La plantilla genérica ya lo hace.
Después de confirmar entradas y recursos:

.. code-block:: bash

   bin/run-workflow --profile profiles/local \
     --configfile config/local/run.yaml --cores 4 --resources mem_mb=24000

Los 24000 MB son un ejemplo de límite global, **no un requisito universal**.
Deben caber en la memoria física disponible. La plantilla solicita 16000 MB
para el índice; el límite original de 5000 MB del perfil local no es adecuado
para ese trabajo. Ajusta ``memory_mb`` y ``threads`` a tu máquina/proyecto.

La referencia SpudDB predeterminada se descarga si hace falta y se comprueba
por SHA-256. Las ejecuciones siguientes reutilizan la cache válida.
Fuera de smoke se leen los FASTQ originales directamente, sin copiarlos.

Reanudar e inspeccionar
-------------------------------

Repite el mismo comando para reanudar. Snakemake compara salidas y sus
metadatos de ejecución; los perfiles activan ``rerun-incomplete``.
Para ver los trabajos que se repetirían usa ``--dry-run``.
No mezcles salidas de versiones distintas ni borres originales para resolver
problemas de reanudación.

.. code-block:: bash

   # Con entradas existentes y configuración válida:
   bin/run-workflow --configfile config/local/run.yaml --lint
   .tools/env/bin/samtools quickcheck result/my-project/bam/*.bam

Revisa ``qc/multiqc_report.html`` y ``tables/report.json`` antes de interpretar
matrices. :doc:`outputs` explica los archivos y :doc:`troubleshooting`
los fallos comunes. El éxito del proceso no implica que QC sea satisfactorio.

ProjectCreole original
------------------------------

Para reproducir exclusivamente la prueba histórica:

.. code-block:: bash

   bin/run-workflow --profile profiles/local \
     --config data_root=/ruta/ProjectCreole --dry-run
   bin/run-workflow --profile profiles/local \
     --config data_root=/ruta/ProjectCreole
   .venv/bin/python tests/check_smoke_outputs.py

Requiere la estructura indicada por ``config/samples-smoke.tsv``. La tabla
completa conserva orientación desconocida y se rechaza hasta confirmar los
metadatos. No desactives esa protección para procesar bibliotecas completas.

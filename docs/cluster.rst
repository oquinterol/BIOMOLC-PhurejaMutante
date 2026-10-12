Ejecución local y Slurm
===============================

Perfil local
--------------------

``profiles/local/config.yaml`` establece executor local, 2 núcleos,
5000 MB globales, comandos visibles y reejecución de tareas incompletas.
Para la plantilla completa debes adaptar recursos:

.. code-block:: bash

   bin/run-workflow --profile profiles/local \
     --configfile config/local/run.yaml --cores 4 --resources mem_mb=24000

El límite global no instala memoria ni sustituye la reserva por regla.
Usa recursos acordes con la RAM física disponible. El índice completo de la
plantilla solicita 16000 MB, pero no se ha medido en esta máquina.
Los requisitos reales varían con la referencia y los datos.

Perfil Slurm
--------------------

.. warning::

   El perfil está preparado, pero no se han enviado ni validado jobs reales
   en un clúster como parte de esta beta. Ajusta políticas, cuenta, partición
   y límites con el administrador del sitio.

El lock Python incluye el executor Slurm. El perfil establece hasta 20 jobs,
``latency-wait: 60``, un reintento, reejecución de salidas incompletas y recursos
predeterminados de 2048 MB/60 minutos; las reglas tienen reservas propias.

Antes de ejecutar:

* Repositorio, datos, referencias, configuración y salida deben ser accesibles
  desde los nodos en un sistema de archivos compartido.
* Los entornos y PATH deben estar disponibles en los nodos y ser compatibles
  con su arquitectura. No basta con instalarlos solo en el nodo login.
* Confirma metadatos y verifica integridad completa de las entradas.
* Adapta cuenta, partición y recursos a las normas del clúster.

.. code-block:: bash

   bin/run-workflow --profile profiles/slurm \
     --configfile config/local/run.yaml \
     --config data_root=/ruta/compartida/fastq output_dir=result/slurm-project \
     --default-resources slurm_account=MI_CUENTA slurm_partition=MI_PARTICION

No copies valores de cuenta/partición del ejemplo sin sustituirlos.
El launcher orquesta desde el nodo permitido; el executor envía tareas.
No ejecutes el procesamiento pesado con executor local en el nodo login.

Ajustar reglas
----------------------

Usa ``threads``/``memory_mb`` en tu YAML o las opciones de Snakemake:

.. code-block:: bash

   bin/run-workflow --profile profiles/slurm \
     --configfile config/local/run.yaml \
     --default-resources slurm_account=MI_CUENTA slurm_partition=MI_PARTICION \
     --set-threads align=4 index_reference=4 \
     --set-resources index_reference:mem_mb=16000 index_reference:runtime=240

Los nombres de reglas y las reservas iniciales están en ``workflow/Snakefile``.
``runtime`` está en minutos. Memoria y tiempo son solicitudes iniciales,
no benchmarks validados; revisa logs y consumo del scheduler.
Evita salidas compartidas entre dos ejecuciones simultáneas.

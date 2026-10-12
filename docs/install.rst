Instalación
===================

Plataforma y requisitos
-------------------------------

El entorno probado es **Linux x86_64, Python 3.12 y Bash**. Se requieren
Git, ``uv``, ``curl`` y ``tar``, acceso HTTPS para instalar paquetes/descargar
la referencia y almacenamiento suficiente para FASTQ, índice y BAM.

La instalación del pipeline no requiere sudo. Si faltan utilidades del
sistema, instálalas mediante el procedimiento de tu equipo o administrador.

* `Instalar uv <https://docs.astral.sh/uv/getting-started/installation/>`_
* `Instalar micromamba <https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html>`_

Obtener una versión fija
--------------------------------

.. code-block:: bash

   git clone --branch 0.1.0-beta --single-branch \
     https://github.com/oquinterol/BIOMOLC-PhurejaMutante.git
   cd BIOMOLC-PhurejaMutante

Clonar una etiqueta deja HEAD separado: es adecuado para reproducir una
versión. Para contribuir, clona la rama ``main`` y crea tu propia rama.

Todos los comandos siguientes se ejecutan desde la raíz del repositorio.
No ejecutes ``make install``: corresponde al código histórico.

Entorno Python del workflow
-----------------------------------

.. code-block:: bash

   uv venv --python 3.12 .venv
   uv pip install --python .venv/bin/python \
     -r requirements-workflow.lock.txt

``requirements-workflow.txt`` fija dependencias directas y el lock registra
la resolución probada. Incluye Snakemake 9.27.0, el executor Slurm 2.8.0 y
PyYAML 6.0.3. No necesitas activar el entorno para usar el lanzador.

Herramientas bioinformáticas
------------------------------------

En Linux x86_64, descarga micromamba y usa el lock explícito:

.. code-block:: bash

   mkdir -p .tools
   curl --fail --location --retry 3 \
     https://micro.mamba.pm/api/micromamba/linux-64/2.3.3 \
     --output .tools/micromamba.tar.bz2
   tar -xjf .tools/micromamba.tar.bz2 -C .tools bin/micromamba

   .tools/bin/micromamba create --yes \
     --root-prefix "$PWD/.tools/mamba" --prefix "$PWD/.tools/env" \
     --file workflow/envs/tools-linux-64.lock.txt

Versiones principales fijadas:

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - Herramienta
     - Versión
     - Función
   * - HISAT2
     - 2.2.1
     - Alineamiento RNA-seq
   * - Subread / featureCounts
     - 2.0.6
     - Conteo exónico
   * - samtools
     - 1.22.1
     - BAM, índices y estadísticas
   * - FastQC
     - 0.12.1
     - Calidad de lecturas
   * - MultiQC
     - 1.32
     - Reporte integrado

``bin/run-workflow`` usa ``.venv/bin/snakemake``, añade ``.tools/env/bin``
al PATH y desactiva paquetes Python del sitio de usuario. Si no encuentra
Snakemake en ``.venv``, busca un ejecutable disponible en PATH.

Otras plataformas y Conda
---------------------------------

El lock explícito es específico de Linux x86_64. En otra plataforma
compatible, con micromamba instalado, resuelve el YAML:

.. code-block:: bash

   micromamba create --yes --override-channels \
     -c conda-forge -c bioconda --prefix "$PWD/.tools/env" \
     --file workflow/envs/tools.yaml

La disponibilidad de paquetes no garantiza validación del pipeline en esa
plataforma. Registra tu resolución y prueba antes de un análisis.
Windows nativo no está validado; usa un entorno Linux compatible.

Las reglas también declaran su entorno Conda. Con Conda instalado puedes
usar ``--software-deployment-method conda`` como alternativa gestionada por
Snakemake; revisa accesibilidad del entorno en nodos si usas Slurm.

Comprobar la instalación sin datos reales
-------------------------------------------------

.. code-block:: bash

   .venv/bin/snakemake --version
   .tools/env/bin/hisat2 --version
   .tools/env/bin/featureCounts -v
   .tools/env/bin/samtools --version
   .tools/env/bin/fastqc --version
   .tools/env/bin/multiqc --version
   .venv/bin/python -m unittest discover -s tests -v
   bash -n bin/run-workflow

Las pruebas generan entradas sintéticas temporales. No descargan genomas
ni requieren ProjectCreole. Para una simulación del workflow debes aportar
FASTQ existentes y una configuración válida: :doc:`usage`.

Recursos para un análisis completo
------------------------------------------

El perfil local predeterminado permite 2 núcleos y 5000 MB globales, adecuado
para la prueba pequeña original. La plantilla completa reserva 16000 MB
para el índice: debes ampliar el límite global y disponer de memoria física
suficiente. Esa reserva no es un benchmark del genoma completo.

La descarga predeterminada de referencias comprimidas fue de aproximadamente
216 MiB en la validación histórica; índice, FASTA descomprimido, BAM y
lecturas requieren espacio adicional variable. No hay una estimación validada
de disco ni tiempo para cada proyecto.

Diagnóstico y preguntas frecuentes
==========================================

Entradas y metadatos
----------------------------

``Missing fastq1/fastq2``
   Comprueba ``data_root``, rutas TSV, permisos y acceso desde el nodo de
   ejecución. El lanzador trabaja desde la raíz del repositorio.

``Sample table requires columns``
   Usa las siete columnas obligatorias, con tabuladores. Un CSV separado
   por comas o una tabla copiada con espacios no es equivalente.

``Confirm strandedness``
   Confirma el protocolo y elige ``unstranded``, ``forward`` o ``reverse``.
   ``unknown`` solo se admite en un smoke explícitamente autorizado.
   No eludas el control en una ejecución completa.

``Layout/read-pair mismatch`` / ``Identical mates``
   Single-end requiere R2 vacío; paired-end necesita dos archivos diferentes.
   No pongas R1 en ambas columnas ni inventes un mate faltante.

``Read-pair IDs are not synchronized``
   Los prefijos no concuerdan. Revisa que R1/R2 pertenezcan a la misma
   biblioteca y estén sincronizados. La herramienta no los reordena.

``Malformed four-line FASTQ prefix``
   Revisa formato FASTQ, compresión y transferencia. El parser espera cuatro
   líneas por registro; los prefijos válidos no garantizan el archivo completo.

Herramientas y recursos
-------------------------------

``Missing hisat2/featureCounts/...``
   Instala ambos entornos de :doc:`install`. Comprueba ejecutables en
   ``.tools/env/bin`` y usa ``bin/run-workflow``. En Slurm valida PATH
   y acceso a entornos desde los nodos, no solo desde el login.

Proceso muerto o memoria insuficiente
   Revisa logs y estado del scheduler. Compara reservas por regla,
   límite global y memoria física. El perfil local de 5000 MB no es
   apropiado para la plantilla que reserva 16000 MB para el índice completo.

Snakemake muestra trabajos pendientes aunque ya existan archivos
   Es posible que código/configuración/entradas hayan cambiado o que una
   ejecución quedara incompleta. Revisa ``--dry-run``. No marques resultados
   como completos sin validar su integridad y procedencia.

Referencia
------------------

``SHA-256 mismatch``
   Comprueba descarga, referencia y versión. La cache inválida no se
   reemplaza silenciosamente. No aceptes un nuevo hash sin verificar su origen.

``Annotation/FASTA coordinate mismatch``
   FASTA y GFF3 no corresponden o sus contigs/coordenadas son incompatibles.
   Usa anotación del ensamblaje elegido, no solo de la misma especie.

``No exon features`` / ``Unknown exon Parent transcript``
   La anotación necesita exones vinculados a transcritos y genes.
   CDS no es un sustituto automático; GTF requiere preparación externa validada.

``No complete exon-annotated genes in selected reference``
   La región smoke no contiene genes completos válidos. Cambia contig/límite
   según tu referencia y usa una salida nueva.

Conteos y calidad
-------------------------

CPM ``NA`` o biblioteca cero
   Revisa orientación, mapeo, anotación y estados featureCounts. ``NA`` evita
   representar una biblioteca sin asignaciones como expresión cero válida.

``Assigned count does not equal matrix total``
   Revisa que counts y summary provengan del mismo trabajo y biblioteca.
   No combines resultados de carpetas/referencias distintas.

``No assigned reads/fragments`` al comprobar smoke
   El comprobador técnico exige asignaciones positivas. Una región pequeña
   puede no cubrir las lecturas del prefijo; ajusta la prueba. No implica
   por sí solo mala calidad del transcriptoma completo.

FastQC muestra fallos aunque el comando terminó
   Exit 0 significa ejecución correcta, no aprobación de todos los módulos.
   Evalúa el protocolo y los diagnósticos antes de interpretar matrices.

Preguntas frecuentes
----------------------------

¿Puedo ejecutar DESeq2 o llamar SNPs desde este workflow?
   No. Los scripts históricos tienen otro alcance y no están validados para
   este análisis. Esta beta solo implementa conteos y exploración descriptiva.

¿Puedo usar datos de otro organismo?
   Las reglas no están ligadas a IDs de clones, pero debes aportar FASTA/GFF3
   compatibles, configurar recursos/contigs y validar el comportamiento en
   tus datos. No se promete validación para otros organismos/plataformas.

¿Puedo publicar ``provenance/`` junto a las matrices?
   Revísalo antes: contiene rutas y metadatos de archivos. No adjuntes datos
   privados ni credenciales sin autorización.

¿Qué se necesita para reportar un problema?
   Indica etiqueta/hash Git, plataforma, comando, configuración anonimizada,
   etapa fallida y fragmento relevante de log. No incluyas FASTQ, credenciales
   o información privada innecesaria. Usa
   `GitHub Issues <https://github.com/oquinterol/BIOMOLC-PhurejaMutante/issues>`_.

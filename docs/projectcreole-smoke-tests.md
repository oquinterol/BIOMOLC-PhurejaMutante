# ProjectCreole: inventario y pruebas técnicas de RNA-seq

## Alcance

Este documento registra el inventario y la primera prueba aislada de FastQC.
Posteriormente se confirmó la ausencia de réplicas biológicas y se implementó
Snakemake para **conteos y comparación exploratoria**, sin DESeq2 ni p-valores.
La ejecución actual y su prueba de extremo a extremo se describen en
[la guía del workflow](snakemake-workflow.md).

Los datos originales están en `/data/ProjectCreole`, fuera del repositorio.
En la primera inspección se usaron las herramientas existentes. Después se
instalaron entornos aislados en el repositorio, sin sudo; los originales y
los scripts históricos de Make permanecen sin alterar.

## Datos encontrados

- `CreoleRawData/RNA-Seq/RawData`: 15 FASTQ gzip, 18.64 GiB comprimidos.
- Cinco archivos en cada carpeta: `25days`, `Flowering` y `Meristem`.
- Los 100 registros iniciales de cada FASTQ tienen estructura válida y 51 nt.
- Solo se encontraron archivos `_1.fastq.gz`, con cabeceras que indican read 1.
  Esto sugiere single-end, pero **no confirma** la configuración de biblioteca.
- El informe de secuenciación del proveedor está en
  `CreoleRawData/RNA-Seq/20240430_HN00216490_TRR_Report/`.
- GBS y lecturas genómicas HiFi también están presentes, pero se excluyen de
  estas pruebas RNA-seq.
- Hay FASTA y GFF de ensamblajes propios en `CreoleProcessedData/GenomeAssembly`.
  No se ha validado su compatibilidad ni seleccionado una referencia.

`config/projectcreole.inventory.tsv` registra rutas relativas a ProjectCreole.
Es un **inventario**, no una tabla de diseño para DESeq2: no asigna condiciones,
réplicas, identidad de planta ni strandedness.

## Diseño experimental pendiente

El usuario recuerda que `R2` corresponde a Flowering y `R3` a Meristem,
y que las muestras de 25 días no tenían sufijo. Esta interpretación se registra
**provisionalmente**; no se deben convertir R2/R3 en réplicas biológicas.

En disco se observa un archivo por identificador de clon y carpeta. Falta
confirmar:

- identidad de las plantas, independencia biológica y posibles muestras agrupadas;
- qué clon constituye el control y qué mutantes se compararán con él;
- tejidos/estadios reales y existencia de otras réplicas;
- relación entre `florblanca` y `Clonmutante` (no se asume equivalencia);
- tipo de biblioteca, orientación y configuración de secuenciación.

Los subconjuntos técnicos no crean replicación biológica. No ejecutar inferencia
mutante/control con DESeq2 sin un diseño identificable y replicación adecuada.
No agrupar distintos estadios como si fueran réplicas intercambiables.

## Integridad

Los dos manifiestos MD5 disponibles difieren para `Clon17R2_1.fastq.gz`:

- `RNA-Seq-md5.txt`: `82b1d5f52ba52b218d34934701ef2e73`
- manifiesto del proveedor: `a517b33297f2fd56dfa0cbcb13561944`

No se calcularon hashes completos de los FASTQ originales ni se validó todo
el flujo gzip. La inspección de prefijos no demuestra integridad completa.
Antes del análisis completo, contrastar los hashes reales con el proveedor.

## Prueba realizada

Se extrajeron los primeros 10000 registros de:

- `Flowering/ClonColombiaR2_1.fastq.gz`
- `Flowering/ClonmutanteR2_1.fastq.gz`

La selección solo prueba lectura y QC, no establece una comparación biológica.
Ambos subconjuntos tienen 51 nt. Tamaño y mtime de los originales permanecieron
sin cambios durante la extracción.

Herramientas y resultados:

- `workflow/scripts/subset_fastq.py`: extractor streaming de prefijos FASTQ;
  valida registros, rechaza sobrescrituras y publica gzip determinista.
- `tests/test_subset_fastq.py`: 9 pruebas unitarias, todas satisfactorias.
- FastQC 0.12.1: ejecución correcta, exit 0, en ambos subconjuntos.
- FastQC reportó avisos/fallos en módulos de composición y secuencias
  sobrerrepresentadas. Exit 0 significa que terminó, no que todos los módulos
  estén aprobados. Los prefijos no son una muestra aleatoria representativa
  ni permiten evaluar la calidad global de las bibliotecas.

Artefactos locales, ignorados por Git:

```text
result/smoke-projectcreole/
  manifest.json
  unittest.log
  fastqc.log
  ClonColombiaR2_1.fastq.gz
  ClonmutanteR2_1.fastq.gz
  fastqc/*_fastqc.html
  fastqc/*_fastqc.zip
```

El manifiesto contiene las rutas originales, número de registros y SHA-256 de
cada subconjunto, no un checksum del original completo.

## Reproducir

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s tests -v

# Usar una salida NUEVA: el extractor no sobrescribe archivos existentes.
python3 workflow/scripts/subset_fastq.py \
  /data/ProjectCreole/CreoleRawData/RNA-Seq/RawData/Flowering/ClonColombiaR2_1.fastq.gz \
  result/smoke-new/ClonColombiaR2_1.fastq.gz --reads 10000

mkdir -p result/smoke-new/fastqc
fastqc --threads 1 --outdir result/smoke-new/fastqc \
  result/smoke-new/ClonColombiaR2_1.fastq.gz
```

El extractor trabaja con FASTQ de cuatro líneas por registro. Copia como máximo
el número solicitado, por lo que archivos cortos producen menos lecturas.
Solo valida el prefijo copiado y rechaza entradas vacías o malformadas.

## Recursos y siguiente paso

La máquina tiene cuatro CPU lógicas, 15.55 GiB RAM total y aproximadamente
6.11 GiB disponibles al inspeccionarla. Snakemake y Salmon/STAR no estaban
en PATH; FastQC, Rscript, samtools, seqkit y Docker sí.

Después de esta inspección se implementó el workflow Snakemake con SpudDB
DM v6.1, HISAT2 y featureCounts. La guía enlazada al inicio contiene los
resultados y comandos actuales. Sigue pendiente confirmar los metadatos y
verificar la integridad completa antes de procesar todas las bibliotecas.
La ausencia de réplicas limita el alcance a exploración; no se prepara DESeq2
para estos datos.

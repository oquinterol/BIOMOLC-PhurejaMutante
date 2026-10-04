# Pipeline RNA-seq exploratorio con Snakemake

## Estado y alcance

Primera versión ejecutable, probada localmente sobre subconjuntos reales de
ProjectCreole y una región de SpudDB DM v6.1. El Makefile y los scripts históricos
se conservan, pero **no se ejecutan** desde este workflow.

```text
validación de muestras y herramientas
  ├── descarga/cache de referencia → SHA-256 → FASTA + exones SAF + splice sites
  ├── prefijos FASTQ (solo smoke) → FastQC
  └── HISAT2 → BAM ordenado/indexado → featureCounts
        ├── matrices de conteos, CPM y razones descriptivas
        └── MultiQC: FastQC, alineamiento, samtools y asignación
```

**No hay réplicas biológicas.** No se ejecuta DESeq2, no se calculan p-valores ni
FDR, ni se declaran genes diferencialmente expresados. Los estadios no se tratan
como réplicas. La referencia DM puede introducir sesgo de mapeo respecto de
Colombia o los mutantes.

Esta versión procesa lecturas sin recorte. Primero se evalúa QC; no se aplica
trimming agresivo a lecturas de 51 nt ni se adivinan adaptadores. Añadir un módulo
configurable de recorte es una mejora posterior, no una etapa ya implementada.
No se incluyen SRA ni variantes en esta nueva versión.

## Instalación aislada, sin sudo

Se necesitan `uv`, `curl`, `tar` y Bash. Desde la raíz del repositorio:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-workflow.lock.txt

mkdir -p .tools
curl --fail --location --retry 3 \
  https://micro.mamba.pm/api/micromamba/linux-64/2.3.3 \
  --output .tools/micromamba.tar.bz2
tar -xjf .tools/micromamba.tar.bz2 -C .tools bin/micromamba

# Lock explícito de los paquetes probados: solo Linux x86_64.
.tools/bin/micromamba create --yes \
  --root-prefix "$PWD/.tools/mamba" --prefix "$PWD/.tools/env" \
  --file workflow/envs/tools-linux-64.lock.txt
```

Para resolver en otra plataforma compatible, usar `workflow/envs/tools.yaml`
en lugar del lock y los canales explícitos:

```bash
micromamba create --yes --override-channels -c conda-forge -c bioconda \
  --prefix "$PWD/.tools/env" --file workflow/envs/tools.yaml
```

`requirements-workflow.txt` fija dependencias directas;
`requirements-workflow.lock.txt` registra la resolución Python probada.
El entorno de herramientas fija HISAT2 2.2.1, Subread 2.0.6, samtools 1.22.1,
FastQC 0.12.1 y MultiQC 1.32. El lock de herramientas fija también builds y
paquetes transitivos. No contiene FASTQ ni genomas.

`bin/run-workflow` usa `.venv/bin/snakemake` y añade `.tools/env/bin` a PATH.
Todas las reglas declaran el entorno Conda: se puede usar también
`--software-deployment-method conda` en equipos con Conda disponible.
La validación registra las versiones/executables realmente usados.

## Prueba local

Editar `data_root` en `config/smoke.yaml` si los datos no están en
`/data/ProjectCreole`, o indicarlo mediante `--config data_root=/otra/ruta`.

```bash
bin/run-workflow --profile profiles/local --dry-run
bin/run-workflow --profile profiles/local
.venv/bin/python tests/check_smoke_outputs.py
bin/run-workflow --profile profiles/local --lint
.venv/bin/python -m unittest discover -s tests -v
```

La primera ejecución descarga aproximadamente 216 MiB de referencias gzip.
Las siguientes reusan la cache y comprueban SHA-256. Los hashes fijados en
`config/reference-spuddb.yaml` provienen de nuestra primera descarga; **no son
checksums publicados por SpudDB**. Si cambian, se rechaza la referencia en vez
de sustituirla silenciosamente.

La prueba predeterminada copia los primeros 10000 registros por muestra de
`ClonColombiaR2` y `ClonmutanteR2`, y usa `chr01:1-2000000`. Solo conserva genes
completos dentro de esa región, sin cambiar las coordenadas.
La biblioteca single-end/no orientada es una **suposición técnica de smoke**,
no una confirmación del protocolo experimental.

### Evidencia de la ejecución local

- Snakemake 9.27.0; 35 pruebas unitarias satisfactorias y lint limpio.
- Referencia smoke: 178 genes y 899 sitios de splicing.
- 10000 lecturas por muestra; featureCounts asignó 28 y 29 lecturas exónicas.
- BAM pasan `samtools quickcheck`; matrices concuerdan con Assigned.
- Columnas CPM no vacías suman un millón.
- FastQC y MultiQC se generan correctamente; hay avisos de composición.
- Repetir el comando devuelve `Nothing to be done`.
- Tamaño y mtime de los FASTQ originales permanecen sin cambios.

La baja asignación es esperable al alinear lecturas de todo el transcriptoma
contra **solo 2 Mb del genoma**. Estos números verifican que funciona el flujo;
**no evalúan la tasa de mapeo real ni diferencias biológicas**.
La prueba no valida hashes/gzip completos de los originales, solo los prefijos
copiados. La discrepancia MD5 de Clon17R2 documentada en el inventario sigue
pendiente antes de un análisis completo.

## Resultados

```text
result/snakemake-smoke/
  provenance/runtime.json        # versiones, rutas y chequeos de prefijos
  provenance/config.yaml         # configuración resuelta
  reference/manifest.json        # referencia, SHA-256, región y agrupación
  bam/                          # BAM, BAI
  counts/                       # featureCounts y estados de asignación
  tables/raw_counts.tsv
  tables/cpm.tsv
  tables/log2_cpm.tsv
  tables/gene_lengths.tsv
  tables/library_sizes.tsv
  tables/samples.tsv
  tables/descriptive_ratios.tsv
  tables/report.json
  qc/multiqc_report.html
  qc/multiqc_report_data/
  logs/
```

El cache `references/`, los resultados, entornos y FASTQ están excluidos de Git.

## Conteo y exploración

Los exones se agrupan mediante `exon → Parent transcript → Parent gene` y se
unen los intervalos solapados entre isoformas del mismo gen. El GFF3 de SpudDB
no tiene filas `gene`; el workflow admite esos identificadores Parent de gen.
No se cuentan CDS como sustituto silencioso de exones. Se validan contigs,
coordenadas, Parent, orientación y límites de la referencia.

featureCounts usa SAF, MAPQ mínimo 10 y alineamientos primarios. Por defecto no
cuenta multimapeos ni asignaciones ambiguas entre genes. En single-end cuenta
lecturas; la rama paired-end cuenta fragmentos con ambos mates alineados y
sin quimeras. La rama paired-end no se ha probado con bibliotecas reales en
esta máquina; hay regresiones para la validación de pares/metadatos.

CPM = conteo / suma de conteos exónicos asignados de la biblioteca × 1000000.
No equivale a expresión absoluta ni elimina sesgos composicionales. Una
biblioteca sin conteos asignados produce `NA`, no una falsa abundancia cero.

Las razones opcionales son `log2((CPM_numerador + p)/(CPM_denominador + p))`.
`p` se configura en `analysis.pseudocount_cpm` y se registra. Los genes con
conteos menores al umbral en ambas muestras quedan marcados. Estos cocientes
son sensibles al pseudoconteo y a la normalización, y solo generan hipótesis.
No son estimaciones inferenciales de DESeq2.

Agregar comparaciones explícitas del mismo estadio, después de confirmar
identidades:

```yaml
analysis:
  mode: exploratory
  pseudocount_cpm: 1.0
  low_count_threshold: 10
  contrasts:
    - name: ejemplo_descriptivo
      numerator: ClonmutanteR2
      denominator: ClonColombiaR2
```

El contraste del smoke se llama `technical_example_only`: no valida que esa
sea la comparación biológica final. La configuración completa tiene la lista
vacía. No se asume que `florblanca` y `Clonmutante` sean equivalentes.

## Datos completos y metadatos

`config/samples-projectcreole.tsv` inventaría las 15 bibliotecas, pero conserva
`strandedness=unknown`. El layout single-end es provisional. Antes de correr:

1. Confirmar layout, orientación y protocolo; indicar `unstranded`, `forward`
   o `reverse` por muestra y revisar los pares cuando corresponda.
2. Confirmar tejido/estadio, identidad de plantas y de cada clon.
3. Verificar integridad de archivos y resolver los manifiestos MD5 discrepantes.
4. Definir comparaciones descriptivas y recursos del clúster.

```bash
# Se rechaza hasta completar los metadatos; esto es intencional.
bin/run-workflow --configfile config/projectcreole.yaml --dry-run --cores 4
```

`allow_unconfirmed_library` solo se permite con `smoke.enabled: true`.
Fuera de smoke se leen los FASTQ originales, sin copiarlos ni modificarlos.
La configuración completa usa el genoma entero y un directorio distinto:
`result/projectcreole`. No reutiliza el índice truncado de smoke.
El índice completo reserva 16 GB: no se ha construido ni medido aquí, y no
se recomienda lanzarlo con los aproximadamente 6 GB RAM libres del equipo.

## Slurm

El perfil está preparado, **pero no se han enviado ni validado jobs reales**.
El repositorio, entornos, referencia, salida y datos deben estar en un sistema
de archivos compartido y ser accesibles desde los nodos.

```bash
# Después de completar metadatos y adaptar cuenta/partición del sitio:
bin/run-workflow --profile profiles/slurm \
  --configfile config/projectcreole.yaml \
  --config data_root=/ruta/compartida/ProjectCreole \
  --default-resources slurm_account=MI_CUENTA slurm_partition=MI_PARTICION
```

Ajustar memoria/tiempo/hilos por regla con `--set-resources` y `--set-threads`
o un perfil local del clúster. No ejecutar el análisis pesado en el nodo login.
La orden se usa allí para orquestar; el executor envía las tareas a Slurm.

## Cambiar la referencia a Colombia

No es necesario cambiar reglas: crear un YAML de referencia local y usarlo
junto a la configuración de ejecución. Ejemplo conceptual (rutas por completar):

```yaml
reference:
  name: Colombia_VERSION_ANOTACION
  download: false
  fasta: /ruta/colombia/genome.fa
  gff3: /ruta/colombia/genes.gff3
  fasta_sha256: SHA256_DEL_FASTA_LOCAL
  gff3_sha256: SHA256_DEL_GFF3_LOCAL
```

```bash
bin/run-workflow --configfile config/projectcreole.yaml config/reference-colombia.yaml \
  --config output_dir=result/colombia_VERSION --dry-run --cores 4
```

La anotación debe tener exones y transcritos con una relación a gen definida,
y concordar con el ensamblaje. Si solo hay CDS o un GFF/GTF distinto, se
necesita preparar/validar esa anotación primero. Usar una nueva versión/nombre
y salida para no mezclar matrices de genes incompatibles entre referencias.

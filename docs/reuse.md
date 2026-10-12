# Usar el pipeline con tus propios datos

## Qué se publica

Este repositorio distribuye código, documentación, entornos fijados, perfiles
de ejecución y configuraciones. **No distribuye lecturas, genomas, BAM, matrices
de resultados ni entornos instalados.** Las tablas ProjectCreole son metadatos
de configuración del proyecto original, no archivos de secuenciación.
Las pruebas generan entradas sintéticas mínimas en directorios temporales.

Los scripts `bin/*.sh` y el Makefile son históricos y no forman parte del
workflow actual. Para el análisis nuevo usa exclusivamente `bin/run-workflow`.

## 1. Obtener e instalar

```bash
git clone https://github.com/oquinterol/BIOMOLC-PhurejaMutante.git
cd BIOMOLC-PhurejaMutante
```

Sigue [Instalación aislada](snakemake-workflow.md#instalación-aislada-sin-sudo):
Python 3.12/Snakemake y las herramientas bioinformáticas se instalan por separado,
sin sudo. El lock de herramientas está probado en Linux x86_64; otras plataformas
requieren resolver el YAML y validar compatibilidad. No ejecutes `make install`.

## 2. Preparar configuración privada

```bash
mkdir -p config/local
cp config/examples/run.yaml config/local/run.yaml
cp config/examples/samples.tsv config/local/samples.tsv
```

Edita ambos archivos: los nombres y valores del ejemplo son **ficticios**.
`config/local/` está ignorado por Git. Cambia `data_root` a la carpeta con tus
FASTQ y mantén `output_dir` dentro de `result/`, separado de los originales.
Las rutas relativas del TSV se resuelven contra `data_root`; también se admiten
rutas absolutas. Las rutas de configuración se resuelven desde la raíz del repo.

| Columna TSV | Valor requerido |
| --- | --- |
| `sample_id` | Identificador único: letras, números, punto, guion o guion bajo; inicia con letra/número |
| `fastq1` | FASTQ/FASTQ.gz single-end o mate R1 |
| `fastq2` | Vacío en single-end; ruta a R2 en paired-end |
| `layout` | `single` o `paired` |
| `strandedness` | `unstranded`, `forward` o `reverse`, confirmado según protocolo |
| `stage` | Estadio/condición de comparación, no vacío |
| `genotype` | Identidad de genotipo/grupo, no vacía |

Ejemplo paired-end (una fila, separada por tabuladores):

```text
sample_id fastq1 fastq2 layout strandedness stage genotype
sample_1 sample_1_R1.fastq.gz sample_1_R2.fastq.gz paired reverse stage_1 mutant
```

El bloque anterior se muestra con espacios por legibilidad: en el archivo usa
**tabuladores**. No copies `reverse` sin confirmar el protocolo. Los mates deben
estar sincronizados y tener nombres de lectura concordantes. La validación
inspecciona prefijos: no sustituye una verificación completa de integridad.

## 3. Revisar recursos y ejecutar

```bash
# Simulación: comprueba configuración, entradas y trabajos, sin ejecutar análisis.
bin/run-workflow --profile profiles/local \
  --configfile config/local/run.yaml --dry-run

# Ejecución completa: adapta núcleos y memoria disponible.
bin/run-workflow --profile profiles/local \
  --configfile config/local/run.yaml --cores 4 --resources mem_mb=24000
```

La plantilla procesa el genoma completo SpudDB DM v6.1; la referencia se descarga
automáticamente y se verifica por SHA-256. Hace falta internet en la primera
ejecución. El índice solicita 16 GB: es una reserva inicial, no una medición
garantizada; necesitas memoria suficiente y espacio para referencia, índice y BAM.
El perfil local original limita memoria a 5000 MB, por eso el ejemplo completo
sobrescribe ese límite. Ajusta también memoria/hilos por regla en tu YAML.

Para una prueba pequeña, añade en tu YAML:

```yaml
output_dir: result/my-project-smoke
smoke:
  enabled: true
  reads: 10000
  contig: chr01
  max_bases: 2000000
```

`contig` y límites deben corresponder a la referencia. El subconjunto técnico
no permite evaluar la tasa real de mapeo ni sacar conclusiones biológicas.
No mezcles salidas smoke y completas: usa directorios diferentes.

Consulta [la guía detallada](snakemake-workflow.md) para referencias locales,
Slurm, orientación de alineamiento, parámetros de conteo y fórmulas.
Al repetir el mismo comando, Snakemake reutiliza las salidas actualizadas;
`rerun-incomplete` está activado en el perfil local.

## 4. Leer resultados

En `output_dir` encontrarás:

- `qc/multiqc_report.html`: QC integrado y resumen de alineamiento/asignación.
- `tables/raw_counts.tsv`: conteos exónicos por gen y biblioteca.
- `tables/cpm.tsv` y `tables/log2_cpm.tsv`: abundancia normalizada descriptiva.
- `tables/descriptive_ratios.tsv`: solo comparaciones explícitas del mismo estadio.
- `provenance/` y `reference/manifest.json`: configuración resuelta,
  herramientas y procedencia de referencia.
- `logs/`: diagnósticos por etapa.

**No se realiza expresión diferencial inferencial, DESeq2 ni llamado de variantes.**
El workflow no recorta adaptadores. Evalúa QC y los sesgos de la referencia antes
de interpretar conteos. La rama paired-end y el perfil Slurm requieren validación
en datos y entorno propios.

## 5. Pruebas y diagnóstico

Sin datos reales ni descarga de referencias:

```bash
.venv/bin/python -m unittest discover -s tests -v
bash -n bin/run-workflow
```

GitHub Actions ejecuta esas pruebas con entradas sintéticas. No es una ejecución
end-to-end de las herramientas bioinformáticas.

- `Missing fastq1/fastq2`: corrige `data_root`, rutas TSV y permisos.
- `Confirm strandedness`: confirma metadatos; no evites el control en un análisis completo.
- Falta de herramientas: revisa `.tools/env/bin` e instalación de ambos entornos.
- Error SHA-256: investiga la descarga/versionado; no cambies el hash a ciegas.
- Trabajo sin recursos suficientes: compara `memory_mb` por regla con el límite
  global y la memoria física antes de ejecutar.
- Para lint se necesitan entradas existentes porque el Snakefile valida el TSV
  al cargarse: `bin/run-workflow --configfile config/local/run.yaml --lint`.

Para reportar un problema adjunta comando, versiones y fragmento del log;
no publiques FASTQ, archivos de procedencia con rutas privadas ni credenciales.

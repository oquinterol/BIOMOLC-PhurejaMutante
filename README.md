# Pipeline RNA-seq exploratorio — Phureja

[![Pipeline tests](https://github.com/oquinterol/BIOMOLC-PhurejaMutante/actions/workflows/tests.yml/badge.svg)](https://github.com/oquinterol/BIOMOLC-PhurejaMutante/actions/workflows/tests.yml)
[![DOI](https://zenodo.org/badge/525475132.svg)](https://zenodo.org/badge/latestdoi/525475132)
[![License](https://img.shields.io/github/license/oquinterol/BIOMOLC-PhurejaMutante)](LICENSE)

Pipeline de BIOMOLC / Semillero de Agrigenómica, Universidad Distrital
Francisco José de Caldas, para explorar RNA-seq de *Solanum tuberosum* grupo
Phureja. Reutilizable con tus propios FASTQ y una referencia anotada compatible.

**Este repositorio publica el pipeline, no los datos ni resultados del análisis.**
Incluye configuraciones de ejemplo y metadatos del proyecto original.
Las pruebas usan entradas sintéticas temporales; no requieren ProjectCreole.

## Qué hace

```text
FASTQ + muestras TSV + referencia FASTA/GFF3
  → validación y procedencia
  → FastQC → HISAT2 → BAM ordenado/indexado → featureCounts
  → conteos por gen / CPM / razones descriptivas
  → MultiQC
```

Referencia predeterminada: **SpudDB DM v6.1** con hashes fijados.
El workflow usa Snakemake y entornos versionados.

**Alcance exploratorio:** sin réplicas biológicas no se ejecuta DESeq2 ni se
reportan p-valores/FDR. Los estadios no son réplicas. No incluye trimming,
procesamiento SRA ni llamado de variantes. La referencia DM puede introducir
sesgo respecto a Colombia y los mutantes.

## Empezar

1. Clona el repositorio e instala los entornos según la
   [guía de instalación](docs/snakemake-workflow.md#instalación-aislada-sin-sudo).
2. Copia las [plantillas genéricas](config/examples/) a `config/local/` y
   configura rutas, muestras, orientación y recursos.
3. Ejecuta desde la raíz del repositorio:

```bash
bin/run-workflow --profile profiles/local \
  --configfile config/local/run.yaml --dry-run
bin/run-workflow --profile profiles/local \
  --configfile config/local/run.yaml --cores 4 --resources mem_mb=24000
```

El segundo comando es un ejemplo para el genoma completo: ajusta la memoria a
la máquina y al YAML. El índice solicita inicialmente 16 GB. Las plantillas
no incluyen FASTQ: debes aportar tus propios archivos y confirmar metadatos.

**[Guía de reutilización paso a paso](docs/reuse.md)**: entradas, single/paired-end,
prueba pequeña, ejecución completa, salidas, reanudación y diagnóstico.

## Documentación

| Documento | Contenido |
| --- | --- |
| [Reutilización](docs/reuse.md) | Cómo usar el pipeline en otro proyecto |
| [Workflow detallado](docs/snakemake-workflow.md) | Instalación, métodos, referencia, resultados y Slurm |
| [Validación histórica ProjectCreole](docs/projectcreole-smoke-tests.md) | Evidencia y límites de las pruebas originales |

## Organización

```text
workflow/Snakefile          reglas del pipeline actual
workflow/scripts/          validación, referencia y tablas
workflow/envs/             herramientas y lock Linux x86_64
config/examples/           plantillas genéricas sin archivos de datos
config/local/              configuración privada (ignorada, creada por el usuario)
config/*projectcreole*      configuraciones/metadatos del proyecto original
profiles/local/            ejecución local
profiles/slurm/            perfil de clúster, pendiente de validación real
bin/run-workflow            punto de entrada recomendado
tests/                     regresiones con entradas sintéticas temporales
docs/                      documentación
```

`data/`, `references/`, `result/`, `results/`, `.venv/` y `.tools/` están excluidos
para nuevas incorporaciones a Git (salvo la lista histórica de URLs
`data/referencefiles.txt`). Mantén datos privados fuera del repositorio o en
`data/`, salidas en `result/` y rutas personales en `config/local/`.

## Validación y limitaciones

```bash
.venv/bin/python -m unittest discover -s tests -v
bash -n bin/run-workflow
```

GitHub Actions ejecuta pruebas unitarias sin datos reales. La guía detallada
registra pruebas end-to-end históricas con subconjuntos single-end de
ProjectCreole; no equivalen a validar bibliotecas completas, otros proyectos,
paired-end real ni Slurm. El comando sin `--configfile` mantiene el smoke
ProjectCreole original y requiere esos datos externos.

## Código histórico

El Makefile y los demás scripts `bin/*.sh`/R se conservan como antecedente de
la tesis. Tienen problemas conocidos, no están validados para el flujo actual
y **no los invoca Snakemake**. No uses `make install` ni `make dea` para ejecutar
este pipeline.

## Contribuir y licencia

Reporta problemas en [GitHub Issues](https://github.com/oquinterol/BIOMOLC-PhurejaMutante/issues)
con comando, versiones y log mínimo, sin datos privados ni credenciales.
Antes de enviar cambios ejecuta las pruebas. Consulta [LICENSE](LICENSE)
para los términos del código; las referencias externas conservan sus propios términos.

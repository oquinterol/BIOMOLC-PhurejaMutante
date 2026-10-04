# RNA-seq exploratorio de mutantes de *Solanum tuberosum* grupo Phureja
___

[![DOI](https://zenodo.org/badge/525475132.svg)](https://zenodo.org/badge/latestdoi/525475132)
[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![GitHub issues](https://img.shields.io/github/issues/oquinterol/BIOMOLC-PhurejaMutante)](https://github.com/oquinterol/BIOMOLC-PhurejaMutante/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-blue.svg)
[![GitHub license](https://img.shields.io/github/license/oquinterol/BIOMOLC-PhurejaMutante)](https://github.com/oquinterol/BIOMOLC-PhurejaMutante/blob/main/LICENSE)

<h1 align="center">
  <a href="https://github.com/oquinterol/BIOMOLC-PhurejaMutante">
    <img alt="BIOMOLC logo" src="./docs/biomolc.png" width="300">
  </a>
  <br>Grupo de Investigación BIOMOLC
  <br>Semillero de Agrigenómica
</h1>
<h3 align="center">Universidad Distrital Francisco José de Caldas</h3>

## Pipeline actual: Snakemake, RNA-seq exploratorio

El nuevo flujo usa **SpudDB DM v6.1 + HISAT2 + featureCounts**, con FastQC,
MultiQC y matrices de conteos/CPM. La referencia se configura en YAML para
sustituirla después por un ensamblaje anotado de Colombia.

**Sin réplicas biológicas: no se ejecuta DESeq2 ni se reportan p-valores/FDR.**
Las razones de abundancia son descriptivas y se comparan muestras del mismo
estadio. Los estadios no se convierten en réplicas.

```text
validación → referencia y exones por gen → HISAT2 → BAM → featureCounts
           └── FastQC / MultiQC           └── conteos / CPM / razones descriptivas
```

Instalación aislada, configuración, resultados y perfiles local/Slurm:
[guía del workflow](docs/snakemake-workflow.md).

Los datos de ProjectCreole no se distribuyen en este repositorio. Antes de la
prueba, ajustar `data_root` en `config/smoke.yaml` o pasarlo con
`--config data_root=/ruta/ProjectCreole`.

```bash
# Desde la raíz del repositorio, después de instalar los entornos de la guía:
bin/run-workflow --profile profiles/local --dry-run
bin/run-workflow --profile profiles/local
.venv/bin/python tests/check_smoke_outputs.py
bin/run-workflow --profile profiles/local --lint
.venv/bin/python -m unittest discover -s tests -v
```

La prueba predeterminada usa dos prefijos de 10000 lecturas de ProjectCreole
y 2 Mb de chr01. **Solo valida funcionamiento técnico**, no resultados
biológicos. Para ejecutar datos completos primero se deben confirmar layout y
strandedness. El perfil Slurm está preparado, pero aún no se ha probado en un
clúster. No se modifican los FASTQ originales.

**Validado localmente:** 35 pruebas unitarias, lint de Snakemake y dos ejecuciones
de extremo a extremo con salidas independientes. La reejecución reutiliza los
resultados actualizados. No se han procesado las 15 bibliotecas completas.

| Archivo | Función |
|---|---|
| `workflow/Snakefile` | Etapas del análisis exploratorio |
| `config/reference-spuddb.yaml` | FASTA, GFF3 y SHA-256 de DM v6.1 |
| `config/smoke.yaml` | Prueba técnica pequeña |
| `config/projectcreole.yaml` | Configuración para las bibliotecas completas |
| `config/samples-projectcreole.tsv` | Muestras y metadatos pendientes de confirmar |
| `profiles/local/` y `profiles/slurm/` | Entornos de ejecución |

Resultados de la prueba en `result/snakemake-smoke/`: matrices en `tables/`
y reporte integrado en `qc/multiqc_report.html`. Datos, referencias descargadas,
resultados y entornos instalados están excluidos de Git.

## Instalación histórica con Make (no recomendada para el nuevo flujo)

Los scripts siguientes se conservan como antecedente de la tesis. Contienen
problemas conocidos y no están validados para el análisis actual. El nuevo
workflow no los invoca ni requiere `make install`.

- Para las principales distribuciones basadas en Debian y en Arch Linux.

    - Distribución basada en Debian (Ubuntu, Linux Mint, Pop OS!, etc)
        
        ```sh
        sudo apt install make git curl
        ```

    - Distribución basada en Arch (Manjaro, Crystal, etc)
        
        ```sh
        sudo pacman -Syyu make git curl
        ```
    
    Esas son las dependencias básicas que permitirán automatizar la instalación de las otras dependencias y programas necesarios.

    ```sh
    git clone https://github.com/oquinterol/BIOMOLC-PhurejaMutante.git Pipeline_Phureja
    cd Pipeline_Phureja
    make install
    ```
    
## Uso histórico con Make
Agregar los archivos SRA dentro de `./data/sra` para hacer uso de la herramienta, para ello con **make** se puede acceder a todas las opciones.

- Limpieza y Filtrado

    ```sh
    make trim
    ```

- Alineamiento
    
    ```sh
    make align
    ```

- DEA: Análisis de Expresión Diferencial

    ```sh
    make dea
    ```

- SNPs: Llamado de variantes

    ```sh
    make snp
    ```

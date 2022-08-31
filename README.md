# Análisis de Mutantes Sólidos de *Solanum Tuberosum Gr. Phureja*
___

[![DOI](https://zenodo.org/badge/525475132.svg)](https://zenodo.org/badge/latestdoi/525475132)
[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![GitHub issues](https://img.shields.io/github/issues/quinterol/BIOMOLC-PhurejaMutante)](https://github.com/quinterol/BIOMOLC-PhurejaMutante/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-blue.svg)
[![GitHub license](https://img.shields.io/github/license/quinterol/BIOMOLC-PhurejaMutante)](https://github.com/quinterol/BIOMOLC-PhurejaMutante/blob/main/LICENSE)

<h1 align="center">
  <a href="https://github.com/quinterol/BIOMOLC-PhurejaMutante">
    <img alt="BIOMOLC logo" src="./docs/biomolc.png" width="300">
  </a>
  <br>Grupo de Investigación BIOMOLC
  <br>Semillero de Agrigenómica
</h1>
<h3 align="center">Universidad Distrital Francisco José de Caldas</h3>

## Instalación
- Las dependencias necesarias para hacer uso del pipeline.

    ```sh
    git clone https://github.com/quinterol/BIOMOLC-PhurejaMutante.git Pipeline_Phureja
    cd Pipeline_Phureja
    make install
    ```
## Uso
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

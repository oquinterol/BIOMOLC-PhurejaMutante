#!/bin/sh
. ./bin/var.sh # Se usa la ruta en el repositorio
echo "La ruta de los datos es" $DATA

## Prueba de mover los archivos sam a la carpeta sam
#find $DIR -iname "*.sam" -type f -not -path '*/sam/*' -execdir mv {} $SAM \;

# Ejemplo de manipulacion de rutas estaticas
# Given:
# foo=/tmp/my.dir/filename.tar.gz
# We can use these expressions:
#  path = ${foo%/*}
#   To get: /tmp/my.dir (like dirname)
# file = ${foo##*/}
#   To get: filename.tar.gz (like basename)
# base = ${file%%.*}
#   To get: filename
# ext = ${file#*.}
#   To get: tar.gz


#Renombrado de archivos validados luego del trimming
# Renombrado de todas las secuencias quitando el _ _var
#find $FQTRIM -iname "*val*.fq.gz" -type f -execdir \
	#rename _1_ _ {} \;
#find $FQTRIM -iname "*val*.fq.gz" -type f -execdir \
    #rename _2_ _ {} \;


# Capura de nombre de archivo
for file in $FQTRIM/*1.fq.gz; do
  filesF+=( "${file##*/}" )
done
printf '%s\n' "${filesF[@]}"

# Captura del ID
for nameid in "${filesF[@]}"; do
    id+=(${nameid%%_*})
done
printf '%s\n' "${id[@]}"

for ((c=0; c<=$((${#id[@]}-1)); c++)); do
    echo ${id[$c]}
done






exit 0
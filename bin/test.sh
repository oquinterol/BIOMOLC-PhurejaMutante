#!/bin/sh
. ./bin/var.sh # Se usa la ruta en el repositorio
echo "La ruta de los datos es:" $DATA

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

## Alineaminto
for file in $FQTRIM/*1.fq.gz; do
  filesF+=( "${file##*/}" )
done
# Guarda los nombres de reverse
for file in $FQTRIM/*2.fq.gz; do
  filesR+=( "${file##*/}" )
done
# Captura del ID
for nameid in "${filesF[@]}"; do
    id+=(${nameid%%_*})
done

## Prueba de SAM
#for file in $SAM/*.sam; do
#  samF+=( "${file##*/}" )
#done
# Captura del ID
#for nameid in "${samF[@]}"; do
#    id+=(${nameid%%_*})
#done
# Numero de secuencias para contar desde 0
numseq=$((${#id[@]}-1))
echo 'El numero de secuencias encontradas es: '$(($numseq+1))
#c=0
#for file in "${id[@]}"; do
#    echo ${id[$c]}
#    echo $file
#    c+=1
#done
#for ((c=0; c<=$((${#id[@]}-1)); c++))
#do
#    echo '.....................'
#    echo $FQTRIM/${filesF[$c]}
#    echo $FQTRIM/${filesR[$c]}
#    echo $SAM/${id[$c]}.sam
#    echo '.....................'
#done
bwa index $TREF

#echo 'Prueba de sam2bam'
#find $SAM -iname "*.sam" -print | parallel 'samtools view -S -b {} > {}.bam'

exit 0
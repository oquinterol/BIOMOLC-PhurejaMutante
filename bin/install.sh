#!/bin/bash
echo "Detectando Distro Linux"

printf "\nPrimer script busca archivos especificos a cada distro\n"
# Fedora/RHEL/CentOS distro
 if [ -f /etc/redhat-release ]; then
    echo "FED"
# Debian/Ubuntu
elif [ -r /lib/lsb/init-functions ]; then
    echo "DEB"
elif [ -f /etc/arch-release ]; then
  echo "ARCH"
fi
printf "\n"
## Otra prueba de script
printf "Segundo script de prueba usa /etc/os-release\n"
DISTRIB=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
if [[ ${DISTRIB} = "Ubuntu"* ]]; then
	if uname -a | grep -q '^Linux.*Microsoft'; then
		# ubuntu via WSL Windows Subsystem for Linux
		echo "Windows Subsystem for Linux"
	else
		# Native Ubuntu
		echo "Ubuntu"
	fi
elif [[ ${DISTRIB} = '"Debian"'* ]]; then
	echo "Debian"
elif [[ ${DISTRIB} = '"Pop!_OS"'* ]]; then
	echo "Pop! OS"
fi

# Este archivo es el que me va a servir
printf "\nEste archivo es el que va a servir, probar con maquinas virtuales /etc/os-release\n"
printf "Pues al filtrar nos daria algo como esto: "$(awk -F= '/^NAME/{print $2}' /etc/os-release)"\n"

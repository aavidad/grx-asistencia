#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
        echo "Ha pulsado ctrl-c, saliendo..."
	exit
}

###ATENCION####
###Para crear el paquete deb, necesitamos tener instalado fakeroot, python-stdeb, python-all, build-essential y python2.7
###############
echo ""
echo "Creando grx-asistencia"
echo "Comprobando dependencias:"
echo ""


for paquete in fakeroot python-stdeb python-all build-essential python2.7
do 
	echo "Comprobando si tenemos el paquete $paquete"
	pkg=$(dpkg -s $paquete 2>&1|grep -m 1 "Version:"|awk "{print $2}")
	if [ -z "$pkg" ]
        	then 
                	echo -e "\e[31mFalta $paquete\e[0m"
                        echo "###ATENCION###"
                        echo "Alguno de los paquetes necesarios falta, ¿desea instalarlos?"
			select sn in "Si" "No"; do
				case $sn in
				        Si ) sudo apt-get install fakeroot python-stdeb python-all build-essential python2.7; break;;

				        No )    echo "Pruebe con:" 
						echo -e "\e[1msudo apt-get install fakeroot python-stdeb python-all build-essential python2.7\e[0m"
			                        echo "##############"
			                        echo "Saliendo....."
			                        exit;; 
				esac
			done

     	   	else 
        	        echo -e "\e[32m$paquete  $pkg\e[0m"
	fi 
done

# MENU PRINCIPAL

OPTION=$(whiptail --title "GrX - Asistencia configurador/instalador" --menu "Selecciona una opcion" 14 78 3 \
"CREAR" "Crear paquete DEB." \
"INSTALAR" "Instalar Paquete." \
"EJECUTAR" "Ejecutar programar." 3>&1 1>&2 2>&3 )


case $OPTION in

    
CREAR)
dependencias="python-apt,zenmap,linphone,fabric,nmap,python-vte,gir1.2-webkit-3.0,python-webkit,python-nmap,python-stdeb,rdesktop,clamav,proxychains,ldap-utils,winbind,python-configobj,sshfs"
version=$(grep version setup.py |cut -d'=' -f2 |sed -e 's/"//g'|sed -e 's/,//g')

if (python setup.py --command-packages=stdeb.command sdist_dsc --depends $dependencias bdist_deb); then
        echo "Compilado el paquete version $version"
        echo -e "\e[1m¿Quieres instalar el programa?\e[0m"
        select sn in "Si" "No"; do
           case $sn in
                Si )   if (sudo dpkg -i deb_dist/python-grx-asistencia_$version-1_all.deb); then
                                echo "Instalado el deb, cambiamos los permisos"
                                if (sudo chmod 755 /usr/share/grx/ldap/*)&&(sudo chmod 777 /usr/share/grx/auxiliar/Packages)
                                then 
                                        if (sudo grep "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-monta.sh" /etc/sudoers)
                                        then
                                                echo "ya estaba"
                                        else
                                                echo  "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-monta.sh" | sudo tee --append /etc/sudoers
                                        fi
                                        if (sudo grep "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-limpiar.sh" /etc/sudoers)
                                        then
                                                echo "ya estaba"
                                        else
                                                echo  "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-limpiar.sh" | sudo tee --append /etc/sudoers
                                        fi

                                        if (sudo grep "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-desmonta.sh" /etc/sudoers)
                                        then
                                                echo "ya estaba"
                                        else
                                                echo "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-desmonta.sh"  | sudo tee --append /etc/sudoers
                                        fi
                                fi
                        else
                                echo "No se ha podido cambiar los permisos"
                        fi
                        break;;
                No ) exit;;
           esac
        done
else

	    echo "No se ha podido instalar el deb"
        exit
fi
;;


INSTALAR)

if (sudo dpkg -i deb_dist/python-grx-asistencia_$version-1_all.deb); then
                                echo "Instalado el deb, cambiamos los permisos"
                                if (sudo chmod 755 /usr/share/grx/ldap/*)&&(sudo chmod 777 /usr/share/grx/auxiliar/Packages)
                                then 
                                        if (sudo grep "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-monta.sh" /etc/sudoers)
                                        then
                                                echo "ya estaba"
                                        else
                                                echo  "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-monta.sh" | sudo tee --append /etc/sudoers
                                        fi
                                        if (sudo grep "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-desmonta.sh" /etc/sudoers)
                                        then
                                                echo "ya estaba"
                                        else
                                                echo "ALL ALL= NOPASSWD: /usr/bin/sudo-asistencia-desmonta.sh"  | sudo tee --append /etc/sudoers
                                        fi
                                fi
                        else
                                echo "No se ha podido cambiar los permisos"
                        fi

;;
EJECUTAR)
    grx-asistencia.sh
;;
esac



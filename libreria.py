from __future__ import with_statement
from fabric.api import settings, sudo, put
from gi.repository import Gtk
import os, subprocess
from datetime import datetime, timedelta
##################Esta clase sirve para mostrar mensajes con un dialog box#####################
#Parametros:
#texto para mostrar ; encabezado del mensaje ; tipo de mensaje (atencion, info,error, pregunta)
###############################################################################################
atencion = Gtk.MessageType.WARNING
info = Gtk.MessageType.INFO
error = Gtk.MessageType.ERROR
pregunta = Gtk.MessageType.QUESTION

class Mensaje(Gtk.MessageDialog):
    def __init__(self, texto,cabecera,tipo):
        Gtk.MessageDialog.__init__(self, parent=None,
                                          flags=Gtk.DialogFlags.MODAL,
                                          type=tipo,
                                          buttons=Gtk.ButtonsType.OK,
                                          message_format=cabecera)
        self.format_secondary_text(texto)
        self.set_default_size(150, 100)
        self.show_all()

#################################################################################################
###Esta clase sirve para mostrar un dialogo de consulta
class Consulta(Gtk.MessageDialog):
    def __init__(self, texto,cabecera):
        Gtk.MessageDialog.__init__(self, parent=None,
                                          flags=Gtk.DialogFlags.MODAL,
                                          type=Gtk.MessageType.QUESTION,
                                          buttons=Gtk.ButtonsType.OK_CANCEL,
                                          message_format=cabecera)
        self.format_secondary_text(texto)
        self.set_default_size(150, 100)
        self.show_all()
#################################################################################################
def convierte_fecha(timestamp):
    epoch_start = datetime(year=1601, month=1,day=1)
    seconds_since_epoch = timestamp/10**7
    return epoch_start + timedelta(seconds=seconds_since_epoch)


############################################
##Esta clase crea un dialogo de archivo para subir un paquete
##le cambia el owner al de usuario y
class Sube_Paquete(Gtk.Window):
    def __init__(self,widget,ip,usuario,puerto,password,nombre):
        Gtk.Window.__init__(self)
        self.set_default_size(200,300)
        dialog = Gtk.FileChooserDialog("Selecciona un archivo", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        path=dialog.get_filename()
        paquete=path.split("/")
        paquete=paquete[-1]
        path_remoto='/home/'+nombre+'/'+paquete

        if response == Gtk.ResponseType.OK:
            with settings(host_string=ip,port=puerto,password=password,user=usuario):
                try:
                    datos = put(use_sudo=True, remote_path=path_remoto, local_path=path)
                    sudo('chown '+nombre+'."usuarios del dominio" '+path_remoto)
                    mensaje(self,"\nSe ha guardado en la carpeta de usuario como:\n"+path_remoto,"   Se ha subido con exito",info)
                except:
                    mensaje(self,"No se ha podido subir el paquete","Atencion",atencion)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancelar Pulsado")
        dialog.destroy()

##Funcion que muestra un mensaje emergente con cabecera, texto y tipo
##Los tipos son
## atencion=Gtk.MessageType.WARNING
## info=Gtk.MessageType.INFO
## error=Gtk.MessageType.ERROR
## pregunta=Gtk.MessageType.QUESTION

def mensaje(self,texto,cabecera,tipo):
        dialog = Mensaje(texto,cabecera,tipo)
        dialog.run()
        dialog.destroy()

def Restaura(self,usuario,nombre,ip ,puerto,password,clave_cifrado):
        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            directorio="/home/"+nombre+"/"
            try:
                datos=put (use_sudo=True, remote_path="/usr/bin/recupera_private.sh", local_path="/usr/bin/recupera_private.sh")
                sudo ("chmod 700 /usr/bin/recupera_private.sh")
                tmp_dir=sudo("/usr/bin/recupera_private.sh "+directorio+" "+clave_cifrado)
                if (tmp_dir=="ERROR") or (tmp_dir=="")or ("mount:" in tmp_dir):
                    mensaje (self,"No se ha podido montar la carpeta cifrada","ATENCION Se ha producido un ERROR:",error)
                    return
                monta = subprocess.check_output (['mktemp','-d','-t',ip+'-cifrado-XXXXXX'])
                sudo ('ecryptfs-setup-private -u '+nombre+' -l "$password" --nopwcheck -m "'+clave_cifrado+'"')
                os.system('sshfs -p '+puerto+' -o reconnect -C -o workaround=all '+usuario+'@'+ip+':'+tmp_dir+' '+monta)
                os.system('xdg-open '+monta)
            except:
                mensaje(self,"No se ha podido restaurar la carpeta en el equipo remoto","Atencion",atencion)




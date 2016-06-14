from __future__ import with_statement
from fabric.api import settings, sudo, put
from gi.repository import Gtk, Gdk
import os, subprocess
import tablabel,libreria


atencion = Gtk.MessageType.WARNING
info = Gtk.MessageType.INFO
error = Gtk.MessageType.ERROR
pregunta = Gtk.MessageType.QUESTION

#def convierte_fecha(timestamp):
#     epoch_start = datetime(year=1601, month=1,day=1)
#     seconds_since_epoch = timestamp/10**7
#     return epoch_start + timedelta(seconds=seconds_since_epoch)

############################################

class Usuarios(Gtk.Grid):
    def __init__(self,widget,nombre,ip,usuario,puerto,password,tecnico,password_tecnico,clave_cifrado):
        Gtk.Grid.__init__(self, row_spacing=20, column_spacing=20)
        builder = Gtk.Builder()
        builder.add_from_file("/usr/share/grx/glade/usuario_off.glade")
        box_usuario = builder.get_object("box_usuario")
        notebook_usuario = builder.get_object("notebook_usuario")
        spinner = builder.get_object("spinner")
        estado = builder.get_object("estado")
        entry_nombre = builder.get_object("entry_nombre")
        entry_usuario = builder.get_object("entry_usuario")
        entry_dir = builder.get_object("entry_dir")
        entry_veleta = builder.get_object("entry_veleta")
        entry_estado = builder.get_object("entry_estado")
        entry_caduca = builder.get_object("entry_caduca")
        entry_correo = builder.get_object("entry_correo")
        entry_clave_antigua = builder.get_object("entry_clave_antigua")
        entry_clave_nueva = builder.get_object("entry_clave_nueva")
        entry_intentos = builder.get_object("entry_intentos")
        entry_usuario.set_text(nombre)
        entry_dir.set_text("/home/"+nombre)

        entry_cambio_clave = builder.get_object("entry_cambio_clave")
        entry_cambio_clave.connect("icon-press",self.on_entry_cambio_clave,ip,usuario,puerto,password,tecnico,password_tecnico,nombre,entry_clave_nueva,entry_clave_antigua,spinner,estado)

        entry_estado.connect("icon-press",self.on_entry_estado_icon_press, usuario,nombre,ip ,puerto,password,tecnico,password_tecnico)
        entry_correo.connect("icon-press",self.on_entry_correo_icon_press)

        entry_veleta.connect("icon-press",self.on_entry_veleta_icon_press, ip, usuario,nombre, puerto,password)

        Btn_usado = builder.get_object("Btn_usado")
        Btn_usado.connect("clicked", self.on_Btn_usado_clicked,nombre, ip,usuario,puerto,password)

        Btn_Config_pam_mount = builder.get_object("Btn_Config_pam_mount")
        Btn_Config_pam_mount.connect("clicked", self.on_Btn_Config_pam_mount_clicked,ip,usuario,nombre,puerto,password,notebook_usuario)

        Btn_Info = builder.get_object("Btn_Info")
        Btn_Info.connect("clicked", self.on_Btn_Info_clicked,usuario,nombre,ip ,puerto,password,tecnico,password_tecnico,entry_usuario,entry_veleta,entry_estado,entry_nombre,entry_caduca,entry_correo,entry_intentos,notebook_usuario)

        Btn_Carpeta = builder.get_object("Btn_Carpeta")
        Btn_Carpeta.connect("clicked", self.on_Btn_Carpeta_clicked,usuario,nombre,ip,puerto,password,clave_cifrado,spinner,estado)

        Btn_Restaura = builder.get_object("Btn_Restaura")
        Btn_Restaura.connect("clicked", self.on_Btn_Restaura_clicked,usuario,nombre,ip,puerto,password,clave_cifrado,spinner,estado)

        Btn_archivo = builder.get_object("Btn_archivo")
        Btn_archivo.connect("clicked", self.on_Btn_archivo_clicked,ip, usuario, puerto,password,nombre)


        self.on_Btn_Info_clicked("NULL", usuario,nombre,ip ,puerto,password,tecnico,password_tecnico, entry_usuario,entry_veleta,entry_estado,entry_nombre,entry_caduca,entry_correo,entry_intentos,notebook_usuario)
        self.add(box_usuario)

    def mensaje(self,texto,cabecera,tipo):
        dialog = libreria.Mensaje(texto,cabecera,tipo)
        dialog.run()
        dialog.destroy()

    def on_entry_veleta_icon_press(self, widget,enum,void, ip, usuario,nombre, puerto,password):
        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            try:
                archivo="""<?xml version="1.0" encoding="utf-8" ?>
<pam_mount>
<volume options="nodev,nosuid,dir_mode=0750,workgroup=GRUPO,user=%(USER)" mountpoint="/home/%(USER)/.veleta"
"""
                archivo=archivo+'path="'+widget.get_text()+'" server="10.1.1.185" fstype="cifs" />'
                archivo=archivo+'</pam_mount>'
                tmp = subprocess.check_output (['mktemp'])
                archi=open(tmp,'w')
                archi.write(archivo)
                archi.close()
                put (use_sudo=True, remote_path="/home/"+nombre+"/.pam_mount.conf.xml", local_path=tmp)
                self.mensaje("Se ha modificado el archivo .pam_mount.conf.xml de "+nombre,"Se ha modificado el archivo .pam_mount.conf.xml:",info)
            except:
                self.mensaje("No se ha podido grabar el archivo .pam_mount en el equipo","ATENCION Se ha producido un ERROR:",error)	


    def on_Btn_Config_pam_mount_clicked(self, widget, ip,usuario,nombre,puerto,password,notebook):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        grid=Gtk.Grid()
        boton=Gtk.Button(label='Grabar')
        grid.attach(boton, 1,0, 2, 1)
        page = Gtk.TextView()
        page.set_editable(True)
        grid.attach_next_to(page, boton, Gtk.PositionType.BOTTOM, 1, 2)
        scrolledwindow.add(grid)
        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            ruta = subprocess.check_output (['mktemp'])
            boton.connect("clicked", self.graba_pam_mount,ip,usuario,nombre,puerto,password,page)
            try:
                archivo=sudo ('cat /home/'+nombre+'/.pam_mount.conf.xml')
            except:
                self.mensaje("No se ha podido abrir el archivo .pam_mount.conf.xml","ATENCION Se ha producido un ERROR:",error)
                return

            textbuffer = page.get_buffer()
            textbuffer.set_text(archivo)
            tab_label = tablabel.TabLabel(".pam_mount.conf.xml "+ ip,Gtk.Image.new_from_file("./icons/info.png"))
            tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
            notebook.append_page(scrolledwindow ,tab_label)
            self.show_all()


    def graba_pam_mount(self, widget, ip, usuario,nombre, puerto,password,page):
        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            try:
                textbuffer = page.get_buffer()
                start_iter = textbuffer.get_start_iter()
                end_iter = textbuffer.get_end_iter()
                archivo=textbuffer.get_text(start_iter, end_iter, True)
                archivo=archivo.replace("\n","")
                tmp = subprocess.check_output (['mktemp'])
                archi=open(tmp,'w')
                archi.write(archivo)
                archi.close()
                put (use_sudo=True, remote_path="/home/"+nombre+"/.pam_mount.conf.xml", local_path=tmp)
            except:
                self.mensaje("No se ha podido grabar el archivo de iptables en el equipo","ATENCION Se ha producido un ERROR:",error)	


    def on_entry_correo_icon_press(self, widget,enum,void):

        os.system("xdg-email "+widget.get_text())

    def on_Btn_usado_clicked(self, widget,nombre, ip,usuario,puerto,password):
        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            try:
                sudo ('apt-get install baobab')
            except:
                print ("nada")
            try:
                sudo ('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/baobab" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/baobab" >>/etc/sudoers   ; fi')
                os.system('ssh -l '+usuario+' -Y -A -C -X -2 -4 -f -p '+puerto+' '+ip+' "sudo baobab /home/'+nombre+'" &')
            except:
                self.mensaje ("No se puede abrir gestor de espacion en disco equipo remoto","ATENCION Se ha producido un ERROR:",error)


##################################################
    def on_Btn_Info_clicked(self, widget, usuario,nombre,ip ,puerto,password,tecnico,password_tecnico,entry_usuario,entry_veleta,entry_estado,entry_nombre,entry_caduca,entry_correo,entry_intentos,notebook):
        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            tecnico=tecnico.split("@")[0]

            try:
                ldap= subprocess.check_output (['/usr/share/grx/ldap/ldap.sh',nombre])
            except:
                self.mensaje ("No se ha podido realizar la consulta AD","ATENCION Se ha producido un ERROR:",error)

#		archi=open('/usr/share/grx/ldap/ldap','r')   ###En casa#		
#		ldap = archi.read()		###En casa

            ldap_lista=ldap.split("\n")

		#####Busca y comprueba el estado de la cuenta
            try:
                lock=filter(lambda x:'lockoutTime:' in x, ldap_lista)
                strl=''.join(lock)
                if (strl.split(":")[1]).strip()=="0":
                    entry_estado.override_color (Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1.0))
                    estado="Activa"
                else:
                    entry_estado.override_color (Gtk.StateFlags.NORMAL, Gdk.RGBA(127, 0, 0, 1.0))
                    estado="BLOQUEADA"
                entry_estado.set_text(estado)
            except:
                entry_estado.set_text("NSNC")

            ######Busca veleta en el archivo .pam_mount
            try:
                archivo=sudo ('cat /home/'+nombre+'/.pam_mount.conf.xml')
                archivo=archivo.split()
                for path in archivo:
                    if "path" in path:
                        ruta=(path.split("=")[1]).strip()
                        ruta=ruta.replace('"','')
                        entry_veleta.set_text(ruta)

            except:
                entry_veleta.set_text("NS/NC")

            ######Busca el correo y lo coloca en entry_correo
            try:
                tmp=filter(lambda x:'mail:' in x, ldap_lista)
                mail=''.join(tmp)
                entry_correo.set_text((mail.split(":")[1]).strip())
            except:
                entry_correo.set_text("NSNC")

            ######Busca las veces que hemos introducido la clave mal
            try:
                tmp=filter(lambda x:'badPwdCount:' in x, ldap_lista)
                badpwd=''.join(tmp)
                entry_intentos.set_text((badpwd.split(":")[1]).strip())
            except:
                entry_intentos.set_text("NSNC")

            ######Busca el nombre completo
            try:
                tmp=filter(lambda x:'cn:' in x, ldap_lista)
                ncompleto=''.join(tmp)
                entry_nombre.set_text((ncompleto.split(":")[1]).strip())
            except:
                entry_nombre.set_text("NSNC")

        #######Busca el ultimo login
		#tmp=filter(lambda x:'lastLogon:' in x, ldap_lista)
		#lastlogon=''.join(tmp)
		#entry_caduca.set_text((lastlogon.split(":")[1]).strip())

		#######Busca cuando expira la cuenta
            try:
                tmp=filter(lambda x:'accountExpires:' in x, ldap_lista)
                expira=''.join(tmp)
                fecha=(expira.split(":")[1]).strip()
                if fecha=="9223372036854775807" or fecha=="0":
                    entry_caduca.set_text("No Caduca")
                else:
                    tmp=libreria.convierte_fecha(int(fecha)).strftime("%d-%m-%y %H:%M")	
                    entry_caduca.set_text(tmp)
            except:
                entry_caduca.set_text("NSNC")	


		#######Busca el ultimo cambio de contrasena
		#tmp=filter(lambda x:'pwdLastSet:' in x, ldap_lista)
		#pwdLastSet=''.join(tmp)
		#entry_caduca.set_text((pwdLastSet.split(":")[1]).strip())

		#######Busca cuando se creo la cuenta
		#tmp=filter(lambda x:'whenCreated:' in x, ldap_lista)
		#whenCreated=''.join(tmp)
		#entry_caduca.set_text((whenCreated.split(":")[1]).strip())

		#######Busca cuando se modifico por ultima vez
		#tmp=filter(lambda x:'whenChanged:' in x, ldap_lista)
		#whenChanged=''.join(tmp)
		#entry_caduca.set_text((whenChanged.split(":")[1]).strip())
		
		#######Muestra el numero de inicios de sesion de la cuenta
		#tmp=filter(lambda x:'logonCount:' in x, ldap_lista)
		#logonCount=''.join(tmp)
		#entry_caduca.set_text((logonCount.split(":")[1]).strip())


            scrolledwindow = Gtk.ScrolledWindow()
            scrolledwindow.set_hexpand(True)
            scrolledwindow.set_vexpand(True)
            page = Gtk.TextView()
            scrolledwindow.add(page)
            textbuffer = page.get_buffer()
            textbuffer.set_text(ldap)
            tab_label = tablabel.TabLabel("ldap "+ nombre,Gtk.Image.new_from_file("./icons/info.png"))
            tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
            notebook.append_page(scrolledwindow ,tab_label)
            self.show_all()
################################################


    def on_entry_cambio_clave(self, widget,pos, otro,ip,usuario,puerto,password, tecnico,password_tecnico,nombre,clave_nueva,clave_antigua,spinner,estado):
        spinner.start()
        estado.set_text("Montando carpeta...")
        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            clave=widget.get_text()
            clave_antigua=clave_antigua.get_text()
            clave_nueva=clave_nueva.get_text()
            try:
                tecnico=tecnico.split("@")[0]
                validar_tecnico= subprocess.check_output (['/usr/share/grx/ldap/validar_tecnico.sh',tecnico, password_tecnico])
                print validar_tecnico
                cmd2 = '((echo  "' + clave_antigua + '" ; echo "' + clave_nueva + '"  ; echo  "' + clave + '" ;)| ecryptfs-rewrap-passphrase /home/'+nombre+'/.ecryptfs/wrapped-passphrase)'
                resultado = sudo(cmd2)
                cmd='(echo '+clave_nueva+'; echo '+clave+' ;)| net ads password -U '+tecnico+'%'+password_tecnico+' '+nombre
                os.system(cmd)
                self.mensaje ("Se ha cambiado la clave de "+nombre+" con exito","Cambio de clave",info)
            except:
                self.mensaje ("No se ha podido cambiar la clave. Compruebe la clave antigua","ATENCION Se ha producido un ERROR:",error)

        spinner.stop()
        estado.set_text("")

    def on_entry_estado_icon_press(self, widget, pos, otro, usuario,nombre,ip ,puerto,password,tecnico,password_tecnico):
            try:
                tecnico=tecnico.split("@")[0]
                validar_tecnico= subprocess.check_output (['/usr/share/grx/ldap/validar_tecnico.sh',tecnico, password_tecnico])
                ldap = subprocess.check_output(['/usr/share/grx/ldap/ldap.sh',nombre])
                ldap_lista = ldap.split("\n")

                #######Busca el dn:
                tmp=filter(lambda x:'dn:' in x, ldap_lista)
                dn=''.join(tmp)
                archivo=dn+'\nchangetype: modify\nreplace: lockoutTime\nlockoutTime: 0'
                tmp_ruta = subprocess.check_output (['mktemp'])
                archi=open(tmp_ruta,'w')
                archi.write(archivo)
                archi.close()
                resultado = subprocess.check_output (['ldapmodify', '-f',tmp_ruta])
                widget.set_text("Activa")
            except:
                self.mensaje ("No se ha podido validar al tecnico. Compruebe la clave","ATENCION Se ha producido un ERROR:",error)


    def	on_Btn_archivo_clicked(self, widget, ip, usuario, puerto,password,nombre):
        win = libreria.Sube_Paquete(self,ip,usuario,puerto,password,nombre)
        self.show_all()


    def on_Btn_Carpeta_clicked(self, widget, usuario,nombre,ip ,puerto,password,clave_cifrado,spinner,estado):
        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            directorio="/home/"+nombre+"/"
            try:
                datos = put(use_sudo=True, remote_path="/usr/bin/recupera_private.sh", local_path="/usr/bin/recupera_private.sh")
                sudo ("chmod 700 /usr/bin/recupera_private.sh")
                tmp_dir=sudo("/usr/bin/recupera_private.sh "+directorio+" "+clave_cifrado)
                if (tmp_dir=="ERROR") or (tmp_dir=="")or ("mount:" in tmp_dir):
                    self.mensaje ("No se ha podido montar la carpeta cifrada","ATENCION Se ha producido un ERROR:",error)
                    return
                monta = subprocess.check_output (['mktemp','-d','-t',ip+'-cifrado-XXXXXX'])
                os.system('sshfs -p '+puerto+' -o reconnect -C -o workaround=all '+usuario+'@'+ip+':'+tmp_dir+' '+monta)
                os.system('xdg-open '+monta)
            except:
                self.mensaje("No se ha podido montar la carpeta en el equipo remoto","Atencion",atencion)


    def on_Btn_Restaura_clicked(self, widget, usuario,nombre,ip ,puerto,password,clave_cifrado,spinner,estado):

        libreria.Restaura(self,usuario,nombre,ip ,puerto,password,clave_cifrado)



from __future__ import with_statement
from fabric.api import settings, abort, run, env, sudo, local, get , put, hosts
from fabric.contrib.console import confirm
from gi.repository import Gtk
import os,tablabel,subprocess
import time
class Mensaje(Gtk.MessageDialog):
    def __init__(self, texto):
        Gtk.MessageDialog.__init__(self, parent=None,
                                          flags=Gtk.DialogFlags.MODAL,
                                          type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK,
                                          message_format="ATENCION se ha producido un ERROR:")
        self.set_default_size(150, 100)
        label = Gtk.Label(texto)
        box = self.get_content_area()
        box.add(label)
        self.show_all()

class Usuarios(Gtk.Grid):
    def __init__(self,widget,nombre,ip,usuario,puerto,password,tecnico,password_tecnico):
        Gtk.Grid.__init__(self, row_spacing=20, column_spacing=20)
        builder = Gtk.Builder()
        builder.add_from_file("/usr/share/grx/glade/usuario.glade")
	box_usuario = builder.get_object("box_usuario")
	notebook_usuario = builder.get_object("notebook_usuario")
	spinner = builder.get_object("spinner")
	estado = builder.get_object("estado")
	entry_nombre = builder.get_object("entry_nombre")
	entry_usuario = builder.get_object("entry_usuario")
	entry_dir = builder.get_object("entry_dir")
	entry_veleta = builder.get_object("entry_veleta")
	entry_estado = builder.get_object("entry_estado")
	entry_ultimo_login = builder.get_object("entry_ultimo_login")
	entry_correo = builder.get_object("entry_correo")
	entry_badpwd = builder.get_object("entry_badpwd")
	entry_usuario.set_text(nombre)
	entry_dir.set_text("/home/"+nombre)
	entry_cambio_clave = builder.get_object("entry_cambio_clave")
	entry_cambio_clave.connect("icon-press",self.on_entry_cambio_clave,tecnico,password_tecnico,nombre)

	entry_usuario.connect("activate",self.on_Btn_Info_clicked,usuario,nombre,ip ,puerto,password,tecnico,password_tecnico,entry_usuario,entry_estado,entry_nombre,entry_ultimo_login,entry_correo,entry_badpwd,notebook_usuario)
	
	entry_estado.connect("icon-press",self.on_entry_estado_icon_press, usuario,nombre,ip ,puerto,password,tecnico,password_tecnico)
	entry_correo.connect("icon-press",self.on_entry_correo_icon_press)

	Btn_Config_pam_mount = builder.get_object("Btn_Config_pam_mount")
	Btn_Config_pam_mount.connect("clicked", self.on_Btn_Config_pam_mount_clicked,ip,usuario,nombre,puerto,password,notebook_usuario)

	Btn_Refres = builder.get_object("Btn_Refres")
	Btn_Refres.connect("clicked", self.on_Btn_Refres_clicked,usuario,nombre,ip,puerto,password)

	Btn_Info = builder.get_object("Btn_Info")
	Btn_Info.connect("clicked", self.on_Btn_Info_clicked,usuario,nombre,ip ,puerto,password,tecnico,password_tecnico,entry_usuario,entry_estado,entry_nombre,entry_ultimo_login,entry_correo,entry_badpwd,notebook_usuario)
	
	Btn_Carpeta = builder.get_object("Btn_Carpeta")
	Btn_Carpeta.connect("clicked", self.on_Btn_Carpeta_clicked,usuario,nombre,ip,puerto,password,spinner,estado)

	#Btn_Refres2 = builder.get_object("Btn_Refres")
	#Btn_Refres.connect("clicked", self.on_Btn_Refres_clicked,nombre,notebook)

	#Btn_Backup2 = builder.get_object("Btn_Backup_impresora")
	#Btn_Backup.connect("clicked", self.on_Btn_Backup_clicked,nombre)

        self.add(box_usuario)

    def mensaje(self,texto):
        dialog = Mensaje(texto)
	dialog.run()
        dialog.destroy()

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
			self.mensaje("No se ha podido abrir el archivo .pam_mount.conf.xml")
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
			tmp = subprocess.check_output (['mktemp'])
			archi=open(tmp,'w')
			archi.write(archivo)
			archi.close()
			put (use_sudo=True, remote_path="/home/"+nombre+"/.pam_mount.conf.xml", local_path=tmp)
		except:
			self.mensaje("No se ha podido grabar el archivo de iptables en el equipo")	

    def on_entry_correo_icon_press(self, widget,enum,void):

	os.system("xdg-email "+widget.get_text())
	
    def on_Btn_Refres_clicked(self, widget, usuario,nombre,ip ,puerto,password):
      with settings(host_string=ip,port=puerto,password=password,user=usuario):
		try:
			monta = subprocess.check_output (['mktemp','-d','-t',ip+'-'+nombre+'-XXXXXX'])
			sudo ('chmod 777 /home/'+nombre+';chown -R administrador /home/'+nombre+'/.Private')
			os.system ('sshfs -p '+puerto+' -o reconnect -C -o workaround=all '+usuario+'@'+ip+':/home/'+nombre+'/.Private'+' '+monta+'')
			#os.system('printf "%s\0" "clave" | ecryptfs-add-passphrase $fnek | grep "^Inserted" | sed -e "s/^.*\[//" -e "s/\].*$//" -e "s/[^0-9a-f]//g")
			result = os.system('nemo '+monta)
		except:
			self.mensaje ("No se ha podido montar la carpeta remota")

####################################################      
    def on_Btn_Info_clicked(self, widget, usuario,nombre,ip ,puerto,password,tecnico,password_tecnico,entry_usuario,entry_estado,entry_nombre,entry_ultimo_login,entry_correo,entry_badpwd,notebook):
	with settings(host_string=ip,port=puerto,password=password,user=usuario):
		tecnico=tecnico.split("@")[0]
		try:
			validar_tecnico= subprocess.check_output (['/usr/share/grx/ldap/validar_tecnico.sh',tecnico, password_tecnico])
		except:
			print "No se ha podido validar al tecnico. Compruebe la clave"
		try:		
			ldap= subprocess.check_output (['/usr/share/grx/ldap/ldap.sh',nombre])
		except:
			print "No se ha podido realizar la consulta AD"
		#archi=open('/usr/share/grx/ldap/ldap','r')   ###En casa
		#ldap = archi.read()		###En casa
		ldap_lista=ldap.split("\n")    
		#####Busca y comprueba el estado de la cuenta
		lock=filter(lambda x:'lockoutTime:' in x, ldap_lista)
		strl=''.join(lock)
		if (strl.split(":")[1]).strip()=="0":
			estado="Activa"
		else:
			estado="BLOQUEADA"
		entry_estado.set_text(estado)
		######Busca el correo y lo coloca en entry_correo
		tmp=filter(lambda x:'mail:' in x, ldap_lista)
		mail=''.join(tmp)
		entry_correo.set_text((mail.split(":")[1]).strip())
		######Busca las veces que hemos introducido la clave mal
		tmp=filter(lambda x:'badPwdCount:' in x, ldap_lista)
		badpwd=''.join(tmp)
		entry_badpwd.set_text((badpwd.split(":")[1]).strip())
		######Busca el nombre completo
		tmp=filter(lambda x:'cn:' in x, ldap_lista)
		ncompleto=''.join(tmp)
		entry_nombre.set_text((ncompleto.split(":")[1]).strip())
		#######Busca el ultimo login
		#tmp=filter(lambda x:'lastLogon:' in x, ldap_lista)
		#lastlogon=''.join(tmp)
		#entry_ultimo_login.set_text((lastlogon.split(":")[1]).strip())

		#######Busca cuando expira la cuenta
		tmp=filter(lambda x:'accountExpires:' in x, ldap_lista)
		lastlogon=''.join(tmp)
		fecha=(lastlogon.split(":")[1]).strip()
		if fecha=="9223372036854775807":
			entry_ultimo_login.set_text("No Caduca")
		else:
			#$(expr $(expr $1 / 10000000) - 11644473600)" sec GMT" +"%d/%m/%Y %H:%M:%S"
			try:
				tmp=time.strftime("%D %H:%M", time.localtime(int(fecha)))
			except:
				tmp="Desconocido"			
			entry_ultimo_login.set_text(tmp)		


		#######Busca el ultimo cambio de contrasena
		#tmp=filter(lambda x:'pwdLastSet:' in x, ldap_lista)
		#pwdLastSet=''.join(tmp)
		#entry_ultimo_login.set_text((pwdLastSet.split(":")[1]).strip())

		#######Busca cuando se creo la cuenta
		#tmp=filter(lambda x:'whenCreated:' in x, ldap_lista)
		#whenCreated=''.join(tmp)
		#entry_ultimo_login.set_text((whenCreated.split(":")[1]).strip())

		#######Busca cuando se modifico por ultima vez
		#tmp=filter(lambda x:'whenChanged:' in x, ldap_lista)
		#whenChanged=''.join(tmp)
		#entry_ultimo_login.set_text((whenChanged.split(":")[1]).strip())
		
		#######Muestra el numero de inicios de sesion de la cuenta
		#tmp=filter(lambda x:'logonCount:' in x, ldap_lista)
		#logonCount=''.join(tmp)
		#entry_ultimo_login.set_text((logonCount.split(":")[1]).strip())


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

	
    def on_entry_cambio_clave(self, widget,pos, otro, tecnico,password_tecnico,nombre):

		clave=widget.get_text()	
		try:
			tecnico=tecnico.split("@")[0]
			validar_tecnico= subprocess.check_output (['/usr/share/grx/ldap/validar_tecnico.sh',tecnico, password_tecnico])
			cmd='(echo '+clave+'; echo '+clave+' ;)| net ads password -U '+tecnico+'%'+password_tecnico+' '+nombre
			os.system(cmd)
		except:
			print "No se ha podido validar al tecnico. Compruebe la clave"


			
    def on_entry_estado_icon_press(self, widget, pos, otro, usuario,nombre,ip ,puerto,password,tecnico,password_tecnico):
			
			
		try:
			tecnico=tecnico.split("@")[0]
			validar_tecnico= subprocess.check_output (['/usr/share/grx/ldap/validar_tecnico.sh',tecnico, password_tecnico])
			ldap= subprocess.check_output (['/usr/share/grx/ldap/ldap.sh',nombre])

			#archi=open('/usr/share/grx/ldap/ldap','r')   ###En casa
			#ldap = archi.read()		###En casa
			
			ldap_lista=ldap.split("\n")    

			#######Busca el dn:
			tmp=filter(lambda x:'dn:' in x, ldap_lista)
			dn=''.join(tmp)
			archivo=dn+'\nchangetype: modify\nreplace: lockoutTime\nlockoutTime: 0'
			tmp_ruta = subprocess.check_output (['mktemp'])
			archi=open(tmp_ruta,'w')
			archi.write(archivo)
			archi.close()
			resultado = subprocess.check_output (['ldapmodify', '-f',tmp_ruta])
			print resultado
			widget.set_text("Activa")
		except:
			print "No se ha podido validar al tecnico. Compruebe la clave"
		

    def on_Btn_Carpeta_clicked(self, widget, usuario,nombre,ip ,puerto,password,spinner,estado):
        spinner.start()
        estado.set_text("Montando carpeta...")
	with settings(host_string=ip,port=puerto,password=password,user=usuario):
		try:
			monta = subprocess.check_output (['mktemp','-d','-t',ip+'-'+nombre+'-XXXXXX'])
			os.system ('sshfs -p '+puerto+' -o reconnect -C -o workaround=all '+usuario+'@'+ip+':/home/'+nombre+' '+monta+'')
			result = os.system('nemo '+monta)
		except:
			self.mensaje ("No se ha podido montar la carpeta remota")
        spinner.stop()
        estado.set_text("")



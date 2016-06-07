from __future__ import with_statement
from fabric.api import settings, abort, run, env, sudo, local, get , put, hosts
from fabric.contrib.console import confirm
from gi.repository import Gtk
import os,subprocess
import tablabel,conexiones,libreria


atencion=Gtk.MessageType.WARNING
info=Gtk.MessageType.INFO
error=Gtk.MessageType.ERROR
pregunta=Gtk.MessageType.QUESTION


class Muestra(Gtk.ScrolledWindow):
       
    def __init__(self,widget, ip,usuario,puerto,password,notebook,texto,cabecera):
	Gtk.ScrolledWindow.__init__(self)
	self.set_hexpand(True)
        self.set_vexpand(True)
 	grid=Gtk.Grid()
    	page = Gtk.TextView()
	page.set_editable(False)
	grid.add(page)
    	self.add(grid)
	textbuffer = page.get_buffer()
	textbuffer.set_text(texto)
	tab_label = tablabel.TabLabel(cabecera+ ip,Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
        tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, self)
        notebook.append_page(self ,tab_label)
	self.show_all()

class Muestra_lista(Gtk.ScrolledWindow):
    def __init__(self,widget,notebook,lista,columnas,cabecera,icono):
	Gtk.ScrolledWindow.__init__(self)
	self.set_hexpand(True)
        self.set_vexpand(True)
	grid=Gtk.Grid()

        self.liststore = Gtk.ListStore(str,str,str,str,str,str,str)
	for i in range(len(lista)):
	    self.liststore.append(lista[i])
        treeview = Gtk.TreeView(model=self.liststore)
        for i in range(len(columnas)):
            cell = Gtk.CellRendererText()
	    col = Gtk.TreeViewColumn(columnas[i], cell, text=i)
            treeview.append_column(col)
	treeview.get_selection().connect("changed", self.on_celda_clicked)
	grid.add(treeview)
	self.add(grid)
	tab_label = tablabel.TabLabel(cabecera,Gtk.Image.new_from_file(icono))
        tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, self)
        notebook.append_page(self ,tab_label)
	self.show_all()

    def on_celda_clicked(self, seleccion):
       (model, iter) = seleccion.get_selected()
       print model[iter][5]
       return True


class Muestra_usuario(Gtk.ScrolledWindow):
    def __init__(self,widget,ip,puerto,usuario,password,notebook,lista,columnas,cabecera,icono):
	Gtk.ScrolledWindow.__init__(self)
	self.set_hexpand(True)
        self.set_vexpand(True)
	grid=Gtk.Grid()
	grid_texto=Gtk.Grid()
    	mensaje=Gtk.Entry()
	label=Gtk.Label("Escribe el mensaje")
	grid_texto.add(label)
	grid_texto.attach_next_to(mensaje,label, Gtk.PositionType.BOTTOM, 1, 2)
	grid.add(grid_texto)
        self.liststore = Gtk.ListStore(str,str,str,str,str,str)
	for i in range(len(lista)):
	    self.liststore.append(lista[i])
        treeview = Gtk.TreeView(model=self.liststore)
        for i in range(len(columnas)):
            cell = Gtk.CellRendererText()
	    col = Gtk.TreeViewColumn(columnas[i], cell, text=i)
            treeview.append_column(col)
	treeview.get_selection().connect("changed", self.on_celda_clicked,ip,puerto,usuario,password,mensaje)
	grid.add(treeview)
	self.add(grid)
	tab_label = tablabel.TabLabel(cabecera,Gtk.Image.new_from_file(icono))
        tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, self)
        notebook.append_page(self ,tab_label)
        
	self.show_all()

    def on_celda_clicked(self, seleccion,ip,puerto,usuario,password,mensaje):
	try:
	        (model, iter) = seleccion.get_selected()
		mensa=mensaje.get_text()
		if mensa=="":
			seleccion.unselect_iter(iter)
			return True
		with settings(host_string=ip,port=puerto,user=usuario,password=password):
			displa=model[iter][5]
			usu=model[iter][0]
			sudo (' DISPLAY='+displa+' XAUTHORITY=/home/'+usu+'/.Xauthority notify-send -t 5000 "'+mensa+'";sleep 1')
			seleccion.unselect_iter(iter)
			os.system('notify-send "Mensaje: '+mensa+' enviado a '+usu+'"')
		return True
	except:
		print "Rebote de la iteracion"


class Informacion(Gtk.Grid):
    def __init__(self,widget,ip,usuario,puerto,password):
        Gtk.Grid.__init__(self, row_spacing=20, column_spacing=20)
        builder = Gtk.Builder()
        builder.add_from_file("/usr/share/grx/glade/informacion.glade")
	box_informacion = builder.get_object("box_informacion")
	notebook_informacion = builder.get_object("notebook_informacion")
	Btn_procesos = builder.get_object("Btn_procesos")
	Btn_procesos.connect("clicked", self.on_Btn_procesos_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_conexiones_red = builder.get_object("Btn_conexiones_red")
	Btn_conexiones_red.connect("clicked", self.on_Btn_conexiones_red_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_lspci = builder.get_object("Btn_lspci")
	Btn_lspci.connect("clicked", self.on_Btn_lspci_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_mount = builder.get_object("Btn_mount")
	Btn_mount.connect("clicked", self.on_Btn_mount_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_who = builder.get_object("Btn_who")
	Btn_who.connect("clicked", self.on_Btn_who_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_lsblk = builder.get_object("Btn_lsblk")
	Btn_lsblk.connect("clicked", self.on_Btn_lsblk_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_usado = builder.get_object("Btn_usado")
	Btn_usado.connect("clicked", self.on_Btn_usado_clicked, ip,usuario,puerto,password)

	Btn_lscpu = builder.get_object("Btn_lscpu")
	Btn_lscpu.connect("clicked", self.on_Btn_lscpu_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_lsusb = builder.get_object("Btn_lsusb")
	Btn_lsusb.connect("clicked", self.on_Btn_lsusb_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_lsmod = builder.get_object("Btn_lsmod")
	Btn_lsmod.connect("clicked", self.on_Btn_lsmod_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_discos = builder.get_object("Btn_discos")
	Btn_discos.connect("clicked", self.on_Btn_discos_clicked,ip,usuario,puerto,password,notebook_informacion)

	Btn_konekta = builder.get_object("Btn_konekta")
	Btn_konekta.connect("clicked", self.on_Btn_konekta_clicked,ip,usuario,puerto,password,notebook_informacion)
	
	Btn_mensaje = builder.get_object("Btn_mensaje")
	Btn_mensaje.connect("clicked", self.on_Btn_mensaje_clicked,ip,usuario,puerto,password,notebook_informacion)


	self.add(box_informacion)


    def mensaje(self,texto,cabecera,tipo):
        dialog = libreria.Mensaje(texto,cabecera,tipo)
	dialog.run()
        dialog.destroy()


    def on_Btn_conexiones_red_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			proc=sudo ("cat /proc/net/tcp")
			proc=proc.split("\n")
			proc.pop(0)
			columnas = ["id","Usuario","IP:Puerto_local","IP:Puerto_remoto","Estado","Proceso","Programa"]
			lista=conexiones.netstat(proc)
			procesos=Muestra_lista(self,notebook,lista,columnas,"Conexiones\n"+ip,"/usr/share/grx/icons/info.png")
		except:
			self.mensaje("No se ha podido ejecutar 'red' en el equipo remoto\n","Error",error)	


    def on_Btn_mensaje_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		
		who=sudo ("who | grep ' \:[0-9]' ")
		who=who.split("\n")
		lista = []
    		for line in who:
			dat=line.split()
 			usuar=dat[0]
			disp=dat[1]
			mes=dat[2]
			dia=dat[3]
			hora=dat[4]
			tmp_display=dat[5].replace(")","")
			tmp_display=tmp_display.replace("(","")
			terminal=tmp_display
	       		nline = [usuar, disp,mes,dia,hora,terminal]
  	  		lista.append(nline)
    		columnas = ["Usuario","Dispositivo","Mes","Dia","Hora","Terminal"]
		mens=Muestra_usuario(self,ip,puerto,usuario,password,notebook,lista,columnas,"Conexiones\n"+ip,"/usr/share/grx/icons/info.png")
		

    def on_Btn_procesos_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		sudo ('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/lxtask" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/lxtask" >>/etc/sudoers   ; fi')
		cabecera="Procesos\n"
		texto=sudo("ps x")
		procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)
		self.show_all()

	try:
		os.system('ssh -l '+usuario+' -Y -A -C -X -2 -4 -f -p '+puerto+' '+ip+' "sudo lxtask" &')
	except:
		self.mensaje("No se ha podido ejecutar 'lxtask' en el equipo remoto\n","Error",error)


    def on_Btn_lsusb_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			cabecera="USB\n"
			texto=sudo("lsusb")
			procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)
		except:
			self.mensaje("No se ha podido ejecutar 'lsusb' en el equipo remoto\n","Error",error)	

    def on_Btn_lspci_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			cabecera="lspci\n"
			texto=sudo("lspci")
			procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)
		except:
			self.mensaje("No se ha podido ejecutar 'lxtask' en el equipo remoto\n","Error",error)	

    def on_Btn_mount_clicked(self, widget, ip,usuario,puerto,password,notebook):

	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			cabecera="mount\n"
			texto=sudo("mount")
			procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)
		except:
			self.mensaje("No se ha podido ejecutar 'mount' en el equipo remoto\n","Error",error)	


    def on_Btn_who_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			cabecera="who\n"
			texto=sudo("who | grep ' \:[0-9]'")
			procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)
		except:
			self.mensaje("No se ha podido ejecutar 'who' en el equipo remoto\n","Error",error)	

    def on_Btn_lsblk_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			cabecera="lsblk\n"
			texto=sudo("lsblk")
			procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)
		except:
			self.mensaje("No se ha podido ejecutar 'lsblk' en el equipo remoto\n","Error",error)	


    def on_Btn_lscpu_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			cabecera="lscpu\n"
			texto=sudo("lscpu")
			procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)
		except:
			self.mensaje("No se ha podido ejecutar 'lscpu' en el equipo remoto\n","Error",error)	

    def on_Btn_lsmod_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			cabecera="lsmod\n"
			texto=sudo("lsmod")
			procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)
		except:
			self.mensaje("No se ha podido ejecutar 'lsmod' en el equipo remoto\n","Error",error)	


    def on_Btn_discos_clicked(self, widget, ip,usuario,puerto,password,notebook):
	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		sudo ('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/gnome-disks" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/gnome-disks" >>/etc/sudoers   ; fi')
		cabecera="Discos\n"
		texto=sudo("fdisk -l")
		procesos=Muestra(self, ip,usuario,puerto,password,notebook,texto,cabecera)

	try:
		os.system('ssh -l '+usuario+' -Y -A -C -X -2 -4 -f -p '+puerto+' '+ip+' "sudo gnome-disks" &')
	except:
		self.mensaje("No se ha podido ejecutar 'gnome-disks' en el equipo remoto\n","Error")

    def on_Btn_konekta_clicked(self, widget, ip,usuario,puerto,password,notebook):
 	with settings(host_string=ip,port=puerto,user=usuario,password=password):
		try:
			os.system('ssh -l '+usuario+' -Y -A -C -X -2 -4 -f -p '+puerto+' '+ip+' "sudo /usr/bin/grx-konekta.sh" &')
		except:
			self.mensaje("No se ha podido ejecutar 'konekta' en el equipo remoto\n","Error",error)	

 
    def on_Btn_usado_clicked(self, widget, ip,usuario,puerto,password):
 	with settings(host_string=ip,port=puerto,password=password,user=usuario):
		try:	
			sudo ('apt-get install baobab')
		except:
			print "nada"
		try:
			sudo ('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/baobab" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/baobab" >>/etc/sudoers   ; fi')
			os.system('ssh -l '+usuario+' -Y -A -C -X -2 -4 -f -p '+puerto+' '+ip+' "sudo baobab" &')
		except:
			self.mensaje ("No se puede abrir gestor de espacion en disco equipo remoto","ATENCION Se ha producido un ERROR:",error)







#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk,Gdk, GObject, GLib, Vte,WebKit,Pango
import os, subprocess,sys,socket,  threading
import tablabel,usuarios_win
reload(sys)  
sys.setdefaultencoding('utf8')


class Antivirus(Gtk.Window):
    def __init__(self):
	Gtk.Window.__init__(self)
    	self.set_default_size(200,300)
        dialog = Gtk.FileChooserDialog("Selecciona un directorio", self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
	path=dialog.get_filename()
	if response == Gtk.ResponseType.OK:
            	try:
			salida=os.popen("clamscan -r -i "+path).read()
			print salida
		except:
			print("Error: No se ha podido escanear el equipo")
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancelar Pulsado")
	dialog.destroy()

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

class Equipos_Windows(Gtk.Grid):

    def __init__(self,ip,usuario,puerto,password,tecnico,password_tecnico):
        Gtk.Grid.__init__(self, row_spacing=20, column_spacing=20)
        builder = Gtk.Builder()
        builder.add_from_file("/usr/share/grx/glade/equipo_windows.glade")
	box_equipo = builder.get_object("box_equipo")
	notebook = builder.get_object("notebook_equipo")
	spinner = builder.get_object("spinner1")
	estado = builder.get_object("estado")
	Btn_win_rdesktop = builder.get_object("Btn_win_rdesktop")
	Btn_win_rdesktop.connect("clicked", self.on_Btn_win_rdesktop_clicked,usuario,password,ip)

	Btn_win_log = builder.get_object("Btn_win_log")
	Btn_win_log.connect("clicked", self.on_Btn_win_log_clicked,usuario,password,ip,notebook)

	Btn_win_desmonta = builder.get_object("Btn_win_desmonta")
	Btn_win_desmonta.connect("clicked", self.on_Btn_win_desmonta_clicked,ip)

	Btn_win_monta = builder.get_object("Btn_win_monta")
	Btn_win_monta.connect("clicked", self.on_Btn_win_monta_clicked,ip,usuario,password,tecnico,notebook)

	Btn_win_color = builder.get_object("Btn_win_color")
	Btn_win_color.connect("color-set",self.on_Btn_win_color_color_set,notebook)

	Btn_win_nmap = builder.get_object("Btn_win_nmap")
	Btn_win_nmap.connect("clicked", self.on_Btn_win_nmap_clicked,ip,notebook)

	Btn_win_usuarios = builder.get_object("Btn_win_usuarios")
	Btn_win_usuarios.connect("clicked", self.on_Btn_win_usuarios_clicked,usuario,password,ip,notebook)

	Btn_clamav = builder.get_object("Btn_clamav")
	Btn_clamav.connect("clicked", self.on_Btn_clamav_clicked)


        self.add(box_equipo)


    def on_Btn_win_nmap_clicked(self,widget,ip,notebook):
	try:
		resultado=os.popen('nmap -Pn '+ip+' &').read()
	except:
		print "No se ha podido ejecutar nmap"
	scrolledwindow = Gtk.ScrolledWindow()
	scrolledwindow.set_hexpand(True)
	scrolledwindow.set_vexpand(True)
	page = Gtk.TextView()
	scrolledwindow.add(page)
	textbuffer = page.get_buffer()
	textbuffer.set_text(resultado)
	tab_label = tablabel.TabLabel("nmap "+ ip,Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
	tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
	notebook.append_page(scrolledwindow ,tab_label)
	notebook.show_all()

    def on_Btn_win_usuarios_clicked(self,widget, usuario,password,ip,notebook):
	try:
		usuarios=os.popen('rpcclient -c enumdomusers -W'+ip+' -U'+usuario+'%'+password+' '+ip+' |cut -d " " -f1| cut -d ":" -f2  ').read()
		if "Cannot" in usuarios:
			self.mensaje_win('No se ha podido ejecutar la busqueda de usuarios \nPosiblemente no se pueda acceder al equipo')
			return
		usuarios=usuarios.replace("[","")
		usuarios=usuarios.replace("]","")
		usuarios=usuarios.split()
		tab_label = tablabel.TabLabel(ip,Gtk.Image.new_from_file("/usr/share/grx/icons/usuarios35.png"))
		scroll= Gtk.ScrolledWindow()
		scroll.set_hexpand(True)
		scroll.set_vexpand(True)
		grid_usuarios=Gtk.Grid()
		scroll.add(grid_usuarios)
		tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scroll)
		notebook.append_page(scroll ,tab_label)
	except:
		self.mensaje_win('No se ha podido ejecutar la busqueda de usuarios \n')		
	contador=0
	for user in usuarios:
	     	grid = Gtk.Grid () 
	     	image = Gtk.Image()
		if user=="Administrador":
			image.set_from_file('/usr/share/grx/icons/administrador.png')
		else:
			image.set_from_file('/usr/share/grx/icons/usuario.png')
	     	label = Gtk.Label (user)
	     	grid.attach (image, 0, 0, 1, 1)
	     	grid.attach (label, 0, 1, 1, 1)
	     	boton=Gtk.Button()
	     	boton.id=(ip)
	     	boton.add(grid)
	     	boton.connect("clicked",self.panel_win,boton,user,ip, usuario, 8080,notebook,password,"prueba","clave")
	     	boton.set_always_show_image (True)
	     	grid_usuarios.add(boton)
	     	contador+=1
	
	self.show_all()

    def panel_win(self,widget,button,user,ip, usuario, puerto,notebook,password,tecnico,password_tecnico):
			           
	grid = usuarios_win.Usuarios(button.id,user,ip,usuario,puerto,password,tecnico,password_tecnico)
	if user=="administrador":
		imagen='/usr/share/grx/icons/administrador35.png'
	else:
		imagen='/usr/share/grx/icons/usuario35.png'
	tab_label = tablabel.TabLabel(user,Gtk.Image.new_from_file(imagen))
	tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, grid)
	notebook.append_page(grid ,tab_label)	
	self.show_all()

    def on_Btn_win_info_clicked(self,widget, usuario,password,ip,notebook):
	usuarios=os.popen('rpcclient -c queryuser -W'+ip+' -U'+usuario+'%'+password+' '+ip).read()
	print usuarios

    def on_Btn_win_color_color_set(self, widget, notebook):
	color=widget.get_color()
	rgba = Gdk.RGBA.from_color(color)
        self.override_background_color(0, rgba)


    def on_Btn_clamav_clicked(self, *args):
	clamav=Antivirus()
	#t = threading.Thread(target=Clamav_antivirus)	
	#t.start()


    def on_Btn_win_monta_clicked(self,widget,ip,usuario,password,tecnico,notebook):
	carpetas=os.popen('rpcclient -c netshareenumall -W'+ip+' -U'+usuario+'%'+password+' '+ip+' |grep netname | cut -d ":" -f2').read()
	carpetas=carpetas.replace(" ","")
	if "Cannot" in carpetas:
		self.mensaje_win('No se ha podido ejecutar la busqueda de usuarios \nPosiblemente no se pueda acceder al equipo')
		return
	carpetas=carpetas.split("\n")
	tab_label = tablabel.TabLabel(ip,Gtk.Image.new_from_file("/usr/share/grx/icons/folder-remote35.png"))
	scroll= Gtk.ScrolledWindow()
	scroll.set_hexpand(True)
	scroll.set_vexpand(True)
	grid_carpetas=Gtk.Grid()
	scroll.add(grid_carpetas)
	tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scroll)
	notebook.append_page(scroll ,tab_label)
	for comp in carpetas:
		if comp=="" :
			continue
	     	grid = Gtk.Grid () 
	     	image = Gtk.Image()
		image.set_from_file('/usr/share/grx/icons/folder-remote.png')
	     	label = Gtk.Label (comp)
	     	grid.attach (image, 0, 0, 1, 1)
	     	grid.attach (label, 0, 1, 1, 1)
	     	boton=Gtk.Button()
	     	boton.id=(comp)
	     	boton.add(grid)
	     	boton.connect("clicked",self.panel_comparte,comp,ip, usuario,password,tecnico)
	     	boton.set_always_show_image (True)
	     	grid_carpetas.add(boton)
	
	
	self.show_all()


    def panel_comparte(self,widget,comp,ip, usuario,password,tecnico):
	tmp_ruta = subprocess.check_output (['mktemp','-d','-t','WIN-'+ip+'-XXXXXX']) 
	tmp_ruta=tmp_ruta[:-1]
	try:
		
		error=os.system('sudo /usr/bin/sudo-asistencia-monta.sh '+ip+' '+password+' '+comp+' '+tmp_ruta+' '+tecnico+' '+usuario)
		if not error:
			os.system('xdg-open '+tmp_ruta)
		else:
			self.mensaje_win('No se ha podido montar la carpeta. Compruebe los permisos')
	except:
		self.mensaje_win('No se ha podido montar la carpeta. Compruebe los permisos')

    def on_Btn_win_desmonta_clicked(self,widget,ip):
	try:
		os.system('sudo /usr/bin/sudo-asistencia-desmonta.sh '+ip)
		
	except:
		self.mensaje_win('No se ha podido desmontar la carpeta.')


    def on_Btn_win_rdesktop_clicked(self,widget, usuario,password,ip):
        try:
	        os.system('rdesktop -g 1200x800 -d '+ip+' -u '+usuario+' -p '+password+' '+ip+'  &')
	except:
       		self.mensaje_win("No ha sido posible ejecutar rdesktop")

    def on_Btn_win_log_clicked(self,widget, usuario,password,ip,notebook):
	lista=['srvinfo','enumdomusers','retrieveprivatedata','getusername','netconnenum',  'netdiskenum','netsessenum','netshareenum','netshareenumall','netfileenum','netremotetod','queryuser','lsaenumsid']

	resultado=""
	#try:
	for i in lista:
		datos=os.popen('rpcclient -c '+i+' -W'+ip+' -U'+usuario+'%'+password+' '+ip).read()
		#datos=os.popen('rpcclient -c '+i+' -W'+ip+' -U'+usuario+'%'+password+' '+ip).read()
		if "Cannot" in datos:
			self.mensaje_win('No se ha podido ejecutar la busqueda '+i+' \nPosiblemente no se pueda acceder al equipo')
			return
		else:
			resultado=resultado+datos
	print resultado
	#except:
	#	self.mensaje_win('No se ha podido ejecutar la busqueda de usuarios \nPosiblemente no se pueda acceder al equipo')
	#	return
		

        #try:
	scrolledwindow = Gtk.ScrolledWindow()
	scrolledwindow.set_hexpand(True)
	scrolledwindow.set_vexpand(True)
	page = Gtk.TextView()
	scrolledwindow.add(page)
	textbuffer = page.get_buffer()
	textbuffer.set_text(resultado)
	tab_label = tablabel.TabLabel("Info "+ ip,Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
	tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
	notebook.append_page(scrolledwindow ,tab_label)
	notebook.show_all()
	#except:
       	#	self.mensaje_win("No ha sido posible ejecutar rdesktop")


    def mensaje_win(self,texto):
        dialog = Mensaje(texto)
	dialog.run()
        dialog.destroy()









##########################
###Funciones windows######
##Podemos usar############
#       EVENTLOG		
# eventlog_readlog		Read Eventlog
# eventlog_numrecord		Get number of records
# eventlog_oldestrecord		Get oldest record
# eventlog_reportevent		Report event
# eventlog_reporteventsource		Report event and source
# eventlog_registerevsource		Register event source
# eventlog_backuplog		Backup Eventlog File
# eventlog_loginfo		Get Eventlog Information
#------------------------
#         WKSSVC		
# wkssvc_wkstagetinfo		Query WKSSVC Workstation Information
# wkssvc_getjoininformation		Query WKSSVC Join Information
# wkssvc_messagebuffersend		Send WKSSVC message
# wkssvc_enumeratecomputernames		Enumerate WKSSVC computer names
# wkssvc_enumerateusers		Enumerate WKSSVC users
#----------------------
#       EPMAPPER		
#         epmmap		Map a binding
#      epmlookup		Lookup bindings
#---------------------
#         SRVSVC		
#        srvinfo		Server query info
#   netshareenum		Enumerate shares
# netshareenumall		Enumerate all shares
# netsharegetinfo		Get Share Info
# netsharesetinfo		Set Share Info
#    netfileenum		Enumerate open files
#   netremotetod		Fetch remote time of day
# netnamevalidate		Validate sharename
#  netfilegetsec		Get File security
#     netsessdel		Delete Session
#    netsessenum		Enumerate Sessions
#    netdiskenum		Enumerate Disks
#    netconnenum		Enumerate Connections
#----------------
#       NETLOGON		
#     logonctrl2		Logon Control 2
#   getanydcname		Get trusted DC name
#      getdcname		Get trusted PDC name
#  dsr_getdcname		Get trusted DC name
# dsr_getdcnameex		Get trusted DC name
# dsr_getdcnameex2		Get trusted DC name
# dsr_getsitename		Get sitename
# dsr_getforesttrustinfo		Get Forest Trust Info
#      logonctrl		Logon Control
#        samsync		Sam Synchronisation
#      samdeltas		Query Sam Deltas
#       samlogon		Sam Logon
# change_trust_pw		Change Trust Account Password
#    gettrustrid		Get trust rid
# dsr_enumtrustdom		Enumerate trusted domains
# dsenumdomtrusts		Enumerate all trusted domains in an AD forest
# deregisterdnsrecords		Deregister DNS records
# netrenumtrusteddomains		Enumerate trusted domains
# netrenumtrusteddomainsex		Enumerate trusted domains
# getdcsitecoverage		Get the Site-Coverage from a DC
#  database_redo		Replicate single object from a DC
#   capabilities		Return Capabilities
#---------------		----------------------
#           SAMR		
#      queryuser		Query user info
#     querygroup		Query group info
#queryusergroups		Query user groups
#queryuseraliases		Query user aliases
#  querygroupmem		Query group membership
#  queryaliasmem		Query alias membership
# queryaliasinfo		Query alias info
#    deletealias		Delete an alias
#  querydispinfo		Query display info
# querydispinfo2		Query display info
# querydispinfo3		Query display info
#   querydominfo		Query domain info
#   enumdomusers		Enumerate domain users
#  enumdomgroups		Enumerate domain groups
#  enumalsgroups		Enumerate alias groups
#    enumdomains		Enumerate domains
#  createdomuser		Create domain user
# createdomgroup		Create domain group
# createdomalias		Create domain alias
# samlookupnames		Look up names
#  samlookuprids		Look up names
# deletedomgroup		Delete domain group
#  deletedomuser		Delete domain user
# samquerysecobj		Query SAMR security object
#   getdompwinfo		Retrieve domain password info
# getusrdompwinfo		Retrieve user domain password info
#   lookupdomain		Lookup Domain Name
#      chgpasswd		Change user password
#     chgpasswd2		Change user password
#     chgpasswd3		Change user password
# getdispinfoidx		Get Display Information Index
#    setuserinfo		Set user info
#   setuserinfo2		Set user info2
#---------------		----------------------
#      LSARPC-DS		
#  dsroledominfo		Get Primary Domain Information
#---------------		----------------------
#         LSARPC		
#       lsaquery		Query info policy
#     lookupsids		Convert SIDs to names
#    lookupsids3		Convert SIDs to names
#    lookupnames		Convert names to SIDs
#   lookupnames4		Convert names to SIDs
# lookupnames_level		Convert names to SIDs
#      enumtrust		Enumerate trusted domains
#      enumprivs		Enumerate privileges
#    getdispname		Get the privilege name
#     lsaenumsid		Enumerate the LSA SIDS
# lsacreateaccount		Create a new lsa account
# lsaenumprivsaccount		Enumerate the privileges of an SID
# lsaenumacctrights		Enumerate the rights of an SID
#     lsaaddpriv		Assign a privilege to a SID
#     lsadelpriv		Revoke a privilege from a SID
# lsaaddacctrights		Add rights to an account
# lsaremoveacctrights		Remove rights from an account
# lsalookupprivvalue		Get a privilege value given its name
# lsaquerysecobj		Query LSA security object
# lsaquerytrustdominfo		Query LSA trusted domains info (given a SID)
# lsaquerytrustdominfobyname		Query LSA trusted domains info (given a name), only works for Windows > 2k
# lsaquerytrustdominfobysid		Query LSA trusted domains info (given a SID)
# lsasettrustdominfo		Set LSA trusted domain info
#    getusername		Get username
#   createsecret		Create Secret
#   deletesecret		Delete Secret
#    querysecret		Query Secret
#      setsecret		Set Secret
# retrieveprivatedata		Retrieve Private Data
# storeprivatedata		Store Private Data
# createtrustdom		Create Trusted Domain
# deletetrustdom		Delete Trusted Domain
#---------------		----------------------


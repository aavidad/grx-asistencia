#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
from fabric.api import settings, run, sudo, local, get, put
from gi.repository import Gtk, Gdk, GLib, Vte, WebKit, Pango
import os
import subprocess
import sys
from sshtunnel import SSHTunnelForwarder
from shutil import copyfile
import tablabel
import usuarios_on
import usuarios_off
import informacion
import libreria
import threading
import random
import glob
reload(sys)
sys.setdefaultencoding('utf8')


atencion = Gtk.MessageType.WARNING
info = Gtk.MessageType.INFO
error = Gtk.MessageType.ERROR
pregunta = Gtk.MessageType.QUESTION


class Lista(Gtk.Grid):
    def __init__(self, columnas, paquetes, boton):
        Gtk.Grid.__init__(self, row_spacing=20, column_spacing=20)
        self.liststore = Gtk.ListStore(str, str, str, bool)
        for i in range(len(paquetes)):
            self.liststore.append(paquetes[i])

        treeview = Gtk.TreeView(model=self.liststore)
        for i in range(len(columnas)):
            cell = Gtk.CellRendererText()
            celda = Gtk.CellRendererToggle()

            if i == 0:
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD

            if i == 3:
                col = Gtk.TreeViewColumn(columnas[i], celda, active=i)
            else:
                col = Gtk.TreeViewColumn(columnas[i], cell, text=i)

            treeview.append_column(col)

        celda.connect("toggled", self.on_celda_toggled)
        # Cuando seleccionamos una fila emitimos una senal
        #treeview.get_selection().connect("changed", self.on_changed)

        grid = Gtk.Grid()
        grid.attach(treeview, 0, 0, 1, 1)
        grid.attach(boton, 1, 0, 1, 1)
        self.add(grid)

    def on_celda_toggled(self, widget, path):
        self.liststore[path][3] = not self.liststore[path][3]

    def dev_lista(self):
        return self.liststore

#    def on_changed(self, selection):
#       (model, iter) = selection.get_selected()
#    model[iter][3]="False"
#    selection.set_selected(model[iter][0],  model[iter][1], model[iter][2],model[iter][3])
#       self.label.set_text("\n %s %s %s" % (model[iter][0],  model[iter][1], model[iter][2]))
#    print (model[iter][0],  model[iter][1], model[iter][2],model[iter][3])
#       return True


class GrabaArchivo(Gtk.Window):
    def __init__(self, ip, usuario, puerto, password, tmp, texto):
        Gtk.Window.__init__(self)
        self.set_default_size(200, 300)
        dialog = Gtk.FileChooserDialog("Selecciona un destino", self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        ruta = os.path.expanduser('~') + '/Descargas/'
        dialog.set_current_folder(ruta)
        dialog.set_current_name(ip + '-' + texto + '.tar.gz')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            with settings(host_string=ip, port=puerto, password=password, user=usuario):
                try:
                    get(remote_path=tmp, local_path=dialog.get_filename())
                except:
                    print("Error: No se ha podido descargar el paquete.")
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancelar Pulsado")

        dialog.destroy()

############################################
##Esta clase crea un dialogo de archivo para instalar un paquete deb


class InstalaPaquete(Gtk.Window):
    def __init__(self, ip, usuario, puerto, password):
        Gtk.Window.__init__(self)
        self.set_default_size(200, 300)
        dialog = Gtk.FileChooserDialog("Selecciona un archivo", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.add_filters(dialog)
        response = dialog.run()
        path = dialog.get_filename()
        if response == Gtk.ResponseType.OK:
            with settings(host_string=ip, port=puerto, password=password, user=usuario):
                try:
                    datos = put(use_sudo=True, remote_path="/tmp/paquete.deb", local_path=path)
                    error = sudo("dpkg -i /tmp/paquete.deb;if [ $? -gt 0 ]; then apt-get -f --force-yes --yes install;dpkg -i /tmp/paquete.deb;dpkg -i /tmp/paquete.deb;fi")
                    self.mensaje("Se ha instalado el paquete en el equipo remoto", "Instalacion con exito", info)
                except:
                    self.mensaje("No se ha podido instalar el paquete, compruebe las dependencias", "Atencion", atencion)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancelar Pulsado")
        dialog.destroy()

    def add_filters(self, dialog):
        filter_deb = Gtk.FileFilter()
        filter_deb.set_name(".deb")
        filter_deb.add_pattern("*.deb")
        dialog.add_filter(filter_deb)
        filter_any = Gtk.FileFilter()
        filter_any.set_name("Todos")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def mensaje(self, texto, cabecera, tipo):
        dialog = libreria.Mensaje(texto, cabecera, tipo)
        dialog.run()
        dialog.destroy()

############################


##############################################
####Esta clase crea los paneles de equipos Linux para trabajar sobre ellos

class Equipos_Linux(Gtk.Grid):
    def __init__(self, ip, usuario, puerto, password, tecnico, password_tecnico, clave_cifrado, clave_remoto):
        Gtk.Grid.__init__(self, row_spacing=20, column_spacing=20)
        builder = Gtk.Builder()
        builder.add_from_file("/usr/share/grx/glade/equipo_linux.glade")
        box_equipo = builder.get_object("box_equipo")
        notebook = builder.get_object("notebook_equipo")
        spinner = builder.get_object("spinner1")
        estado = builder.get_object("estado")
        Btn_vncviewer = builder.get_object("Btn_vncviewer")
        Btn_vncviewer.connect("clicked", self. on_Btn_vncviewer_clicked, ip, usuario, puerto, password, clave_remoto, spinner, estado)

        Btn_log = builder.get_object("Btn_log")
        Btn_log.connect("clicked", self.on_Btn_log_clicked, ip, usuario, puerto, password, notebook, spinner, estado)

        Btn_dominio_clicked = builder.get_object("Btn_dominio")
        Btn_dominio_clicked.connect("clicked", self.on_Btn_dominio_clicked, ip, usuario, puerto, password, notebook, spinner, estado)

        Btn_update = builder.get_object("Btn_update")
        Btn_update.connect("clicked", self.on_Btn_update_clicked,ip,usuario,puerto,password,notebook,spinner,estado)

        Btn_iptables = builder.get_object("Btn_iptables")
        Btn_iptables.connect("clicked", self.on_Btn_iptables_clicked,ip,usuario,puerto,password,notebook,spinner,estado)

        Btn_terminal = builder.get_object("Btn_terminal")
        Btn_terminal.connect("clicked", self.on_Btn_terminal_clicked,ip,usuario,puerto,notebook,spinner,estado)

        Btn_instala = builder.get_object("Btn_instala")
        Btn_instala.connect("clicked", self.on_Btn_instala_clicked,ip,usuario,puerto,password)

        Btn_info = builder.get_object("Btn_info")
        Btn_info.connect("clicked", self.on_Btn_info_clicked,ip,usuario,puerto,password,notebook,spinner,estado)

        Btn_monta_log = builder.get_object("Btn_monta_log")
        Btn_monta_log.connect("clicked", self.on_Btn_monta_log_clicked,ip,usuario,puerto,spinner,estado)

        Btn_cifrar = builder.get_object("Btn_cifrar")
        Btn_cifrar.connect("clicked", self.on_Btn_cifrar_clicked,ip,usuario,puerto,password,notebook,spinner,estado)

        Btn_cups = builder.get_object("Btn_cups")
        Btn_cups.connect("clicked", self.on_Btn_cups_clicked,ip,usuario,password,puerto,notebook,spinner,estado)

        Btn_impre = builder.get_object("Btn_impre")
        Btn_impre.connect("clicked", self.on_Btn_impre_clicked,ip,usuario,password,puerto,spinner,estado)

        Btn_hp = builder.get_object("Btn_hp")
        Btn_hp.connect("clicked", self.on_Btn_hp_clicked,ip,usuario,password,puerto,spinner,estado)

        Btn_hp_plugin = builder.get_object("Btn_hp_plugin")
        Btn_hp_plugin.connect("clicked", self.on_Btn_hp_plugin_clicked, ip, usuario, password, puerto, spinner, estado)

        Btn_impre_backup = builder.get_object("Btn_impre_backup")
        Btn_impre_backup.connect("clicked", self.on_Btn_impre_backup_clicked, ip, usuario, puerto, password, spinner, estado)

        Btn_carpetas = builder.get_object("Btn_carpetas")
        Btn_carpetas.connect("clicked", self.on_Btn_carpetas_clicked, ip, usuario, puerto, spinner, estado)

        Btn_backup = builder.get_object("Btn_backup")
        Btn_backup.connect("clicked", self.on_Btn_backup_clicked, ip, usuario, puerto, password, spinner, estado)

        Btn_network = builder.get_object("Btn_network")
        Btn_network.connect("clicked", self.on_Btn_network_clicked, ip, usuario, puerto, password, spinner, estado)

        Btn_color = builder.get_object("Btn_color")
        Btn_color.connect("color-set", self.on_Btn_color_color_set, notebook)

        Btn_nmap = builder.get_object("Btn_nmap")
        Btn_nmap.connect("clicked", self.on_Btn_nmap_clicked, ip, usuario, password, puerto, spinner, estado, notebook)

        Btn_usuarios = builder.get_object("Btn_usuarios")
        Btn_usuarios.connect("clicked", self.on_Btn_usuarios_clicked, ip, usuario, puerto, notebook, password, tecnico, password_tecnico, clave_cifrado, spinner,estado)

        Btn_mame = builder.get_object("Btn_mame")
        Btn_mame.connect("clicked", self.on_Btn_mame_clicked, notebook)

        Btn_escaner = builder.get_object("Btn_escaner")
        Btn_escaner.connect("clicked", self.on_Btn_escaner_clicked, ip, usuario, puerto, password, spinner, estado)

        self.add(box_equipo)

##########################
###Funciones Linux########
    def on_Btn_dominio_clicked(self, widget, ip, usuario, puerto, password, notebook, spinner, estado):
        with settings(host_string=ip, port=puerto, user=usuario, password=password):
            try:
                sudo('if  grep "administrador ALL=(root) NOPASSWD: /usr/sbin/grx-dominio" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/sbin/grx-dominio" >>/etc/sudoers   ; fi')
                os.system('ssh -l ' + usuario + ' -Y -A -C -X -2 -4 -f -p ' + puerto + ' ' + ip + ' "lxterminal -e sudo /usr/sbin/grx-dominio" &')
            except:
                self.mensaje("No se ha podido ejecutar grx-dominio en el equipo remoto", "Atencion", atencion)

    def on_Btn_log_clicked(self, widget, ip, usuario, puerto, password, notebook, spinner, estado):
        spinner.start()
        estado.set_text("Ejecutando dmesg en remoto")
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        page = Gtk.TextView()
        scrolledwindow.add(page)
        with settings(host_string=ip, user=usuario, port=puerto, password=password):
            try:
                equipo = self.nombre_PC(widget, ip, usuario, puerto)
                res = run('dmesg')
                textbuffer = page.get_buffer()
                textbuffer.set_text(res)
                tab_label = tablabel.TabLabel("dmesg " + ip + '\n' + equipo, Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
                tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
                notebook.append_page(scrolledwindow, tab_label)
                self.show_all()
            except:
                self.mensaje('No se ha podido ejecutar dmesg en el equipo remoto', "Atencion", atencion)
        spinner.stop()
        estado.set_text("")

##########################

    def paquete_instalado(self, pkg_name, ip, usuario, puerto, password):
        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            cmd_f = 'dpkg-query -l "%s" | grep -q ^.i'
            cmd = cmd_f % (pkg_name)
            with settings(warn_only=True):
                result = run(cmd)
            return result.succeeded

    def instala(self, pkg_name, ip, usuario, puerto, password):
        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            sudo('apt-get --force-yes --yes install %s' % (pkg_name))

    def comprueba_si_instalado(self, pkg_name, ip, usuario, puerto, password):
        if not self.paquete_instalado(pkg_name, ip, usuario, puerto, password):
            self.instala(pkg_name, ip, usuario, puerto, password)

    def Actualiza_Equipo(self, widget, ip, usuario, puerto, password, notebook, spinner, estado):
        spinner.start()
        estado.set_text("Buscando paquetes instalados")
        archivo = "/usr/share/grx/auxiliar/Packages"
        tmp = subprocess.check_output(['mktemp'])
        tmp = tmp.replace("\n", "")
        with settings(host_string=ip, port=puerto, password=password, user=usuario):
                columnas = ["Nombre del Paquete", "Version Disponible", "Version Instalada", "Instalar/actualizar"]
                paquetes = []
                lista_pkg = ""
                try:
                    error = os.system('wget -O ' + tmp + ' http://incidencias.dipgra.es/ubuntu/dists/grx/main/binary-amd64/Packages')
                except IOError as e:
                    print "I/O error({0}): {1}".format(e.errno, e.strerror)
                if not error:
                    copyfile(tmp, archivo)
                for line in open(archivo):
                    if "Package:" in line:
                        pkg = line.split(":")[1]
                        pkg = pkg.rstrip('\n')
                        pkg = pkg.strip()
                        lista_pkg = lista_pkg + " " + pkg
                fila = []
                tmp = run('lista="' + lista_pkg + '"; for pkg in $lista;do    echo $pkg;apt=$(apt-cache show $pkg 2>&1|grep -m 1 "Version:"|awk "{print $2}");echo $apt;dpkg=$(dpkg -s $pkg 2>&1|grep -m 1 "Version:"|awk "{print $2}");echo $dpkg; done')
                tmp = tmp.replace("nohup: ignoring input and appending output to 'nohup.out'", "")
                tmp = tmp.split("\n")
                tmp = [x.replace("\r", "") for x in tmp]
                try:
                    if tmp[0] == "":
                        del tmp[0]
                except:
                    print "no borramos vacios"
                tam = len(tmp) / 3
                for i in range(0, tam):
                    fila = []
                    nombre = tmp[i + (i * 2)]
                    apt = tmp[i + (i * 2 + 1)]
                    dpkg = tmp[i + (i * 2 + 2)]
                    if (apt == ""):
                        apt = "No instalado"
                    if (dpkg == ""):
                        dpkg = "No instalado"
                    fila.append(nombre)
                    fila.append(apt)
                    fila.append(dpkg)
                    fila.append("True")
                    paquetes.append(fila)
                boton = Gtk.Button("Instala")
                lista = Lista(columnas, paquetes, boton)
                boton.connect("clicked", self.on_clicked_instalar, lista, ip, usuario, puerto, password)
                tab_label = tablabel.TabLabel("update " + ip, Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
                tab_label.connect("close-clicked", tablabel. on_close_clicked, notebook, lista)
                notebook.append_page(lista, tab_label)
                self.show_all()
                spinner.stop()
                estado.set_text("")

    def on_clicked_instalar(self, widget, lista, ip, usuario, puerto, password):
        tmp = lista.dev_lista()
        for i in range(len(tmp)):
            if tmp[i][3]:
                print "Instala " + tmp[i][0]
                try:
                    self.instala(tmp[i][0], ip, usuario, puerto, password)
                except:
                    print "No se puede instalar"
            elif not tmp[i][3]:
                print "Desinstala " + tmp[i][0]

    def on_Btn_update_clicked(self, widget, ip, usuario, puerto, password, notebook, spinner, estado):
        t = threading.Thread(target=self. Actualiza_Equipo, args=(widget, ip, usuario, puerto, password, notebook, spinner, estado))
        t.setDaemon(True)
        t.start()

###############################ADFASDFADSF
    def graba_iptables(self, widget, ip, usuario, puerto, password, page):
        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            try:
                textbuffer = page.get_buffer()
                start_iter = textbuffer.get_start_iter()
                end_iter = textbuffer.get_end_iter()
                archivo = textbuffer.get_text(start_iter, end_iter, True)
                tmp = subprocess.check_output(['mktemp'])
                archi = open(tmp, 'w')
                archi.write(archivo)
                archi.close()
                put(use_sudo=True, remote_path="/etc/grx-iptables.conf", local_path=tmp)
            except:
                self.mensaje("No se ha podido grabar el archivo de iptables en el equipo", "Atencion", atencion)

    def on_Btn_iptables_clicked(self, widget, ip, usuario, puerto, password, notebook, spinner, estado):

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        grid = Gtk.Grid()
        builder = Gtk.Builder()
        builder.add_from_file("/usr/share/grx/glade/equipo_linux.glade")
        botones_iptables = builder.get_object("botones_iptables")
        Btn_inicia = builder.get_object("Btn_inicia")
        Btn_parar = builder.get_object("Btn_parar")
        Btn_recargar = builder.get_object("Btn_recargar")
        Btn_config = builder.get_object("Btn_config")
        Btn_estado = builder.get_object("Btn_estado")
        grid.attach(botones_iptables, 1, 0, 2, 1)
        page = Gtk.TextView()
        page.set_editable(True)
        grid.attach_next_to(page, botones_iptables, Gtk.PositionType.BOTTOM, 1, 2)
        scrolledwindow.add(grid)
        with settings(host_string=ip, port=puerto, password=password, user=usuario):

            try:
                version = run('dpkg -s grx-iptables 2>&1|grep -m 1 "Version:"|awk "{print $2}"')
                version = version.replace("nohup: ignoring input and appending output to 'nohup.out'", "")
                version = version.split(":")[1]
                if version != " 2016.01.28":
                    self.mensaje("Es necesario actualizar la version de grx-iptables. Pulse aceptar para actualizar", "Atencion", atencion)
                    sudo('apt-get update;cp /etc/init.d/grx-iptables /etc/init.d/grx-iptables.' + str(random.randint(0000, 9999)) + '.old')
                    self.instala("grx-iptables", ip, usuario, puerto, password)
            except:
                self.mensaje("No se ha podido comprobar la version del paquete grx-iptables instalado", "Atencion", atencion)

        ruta = subprocess.check_output(['mktemp'])
        Btn_inicia.connect("clicked", self.inicia_iptables, ip, usuario, puerto, password)
        Btn_parar.connect("clicked", self.parar_iptables, ip, usuario, puerto, password)
        Btn_recargar.connect("clicked", self.recargar_iptables, ip, usuario, puerto, password)
        Btn_config.connect("clicked", self.graba_iptables, ip, usuario, puerto, password, page)
        Btn_estado.connect("clicked", self.estado_iptables, ip, usuario, puerto, password, notebook)
        try:
            archivo = sudo('cat /etc/grx-iptables.conf')
            archivo = archivo.replace("nohup: ignoring input and appending output to 'nohup.out'", "")
            archivo = archivo.strip()
        except:
            self.mensaje("No se ha podido abrir el archivo grx-iptables.conf, se crea", "Atencion", atencion)
            archivo = "#Coloque aqui las ips de las impresoras/escaneres"
        textbuffer = page.get_buffer()
        textbuffer.set_text(archivo)
        tab_label = tablabel.TabLabel("iptables " + ip, Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
        tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
        notebook.append_page(scrolledwindow ,tab_label)
        self.show_all()

    def inicia_iptables(self, widget, ip, usuario, puerto, password):
        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            try:
                estado = sudo('service grx-iptables start')
            except:
                self.mensaje("No ha sido posible arrancar iptables", "Atencion", atencion)

    def parar_iptables(self, widget, ip, usuario, puerto, password):
        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            try:
                estado = sudo('service grx-iptables stop')
            except:
                self.mensaje("No ha sido posible parar iptables", "Atencion", atencion)

    def recargar_iptables(self, widget, ip, usuario, puerto, password):

        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            try:
                estado = sudo('service grx-iptables restart')
            except:
                self.mensaje("No ha sido posible re-arrancar iptables", "Atencion", atencion)

    def estado_iptables(self, widget, ip, usuario, puerto, password, notebook):
        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            try:
                scrolledwindow = Gtk.ScrolledWindow()
                scrolledwindow.set_hexpand(True)
                scrolledwindow.set_vexpand(True)
                page = Gtk.TextView()
                page.set_editable(False)
                estado = sudo('service grx-iptables status')
                scrolledwindow.add(page)
                textbuffer = page.get_buffer()
                textbuffer.set_text(estado)
                tab_label = tablabel.TabLabel("Estado_iptables " + ip, Gtk.Image.new_from_file("/usr/share/grx/icons/firewall25.png"))
                tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, page)
                notebook.append_page(scrolledwindow, tab_label)

                if "DROP" in estado:
                    widget.set_image(Gtk.Image.new_from_file("/usr/share/grx/icons/si.png"))
                else:
                    widget.set_image(Gtk.Image.new_from_file("/usr/share/grx/icons/no.png"))
                self.show_all()
            except:
                self.mensaje("No ha sido posible comprobar el estado", "Atencion", atencion)

    def mensaje(self, texto, cabecera, tipo):
        dialog = libreria.Mensaje(texto, cabecera, tipo)
        dialog.run()
        dialog.destroy()

    def on_Btn_instala_clicked(self, widget, ip, usuario, puerto, password):
        win = InstalaPaquete(ip, usuario, puerto, password)
        self.show_all()

    def on_Btn_monta_log_clicked(self, widget, ip, usuario, puerto, spinner, estado):
        spinner.start()
        estado.set_text("Montado Carpera LOG")
        try:
            monta = subprocess.check_output (['mktemp','-d','-t', ip + '-LOG-XXXXXX'])
            os.system('sshfs -p ' + puerto + ' -o reconnect -C -o workaround=all ' + usuario + '@' + ip + ':/var/log ' + monta + '')
            result = os.system('xdg-open ' + monta)
        except:
            self.mensaje("No se ha podido montar la carpeta remota", "Atencion", atencion)
        spinner.stop()
        estado.set_text("")

##################################################
########################################
    def on_Btn_cifrar_clicked(self, widget, ip, usuario, puerto, password, notebook, spinner, estado):
        with settings(host_string=ip, port=puerto, user=usuario, password=password):
            try:
                sudo('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/ecryptfs-recover-private" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/ecryptfs-recover-private" >>/etc/sudoers   ; fi')
                monta = subprocess.check_output (['mktemp', '-d', '-t', ip + '-cifrado-XXXXXX'])
                os.system('ssh -l ' + usuario + ' -Y -A -C -X -2 -4 -f -p ' + puerto + ' ' + ip + ' "lxterminal -e sudo /usr/bin/ecryptfs-recover-private" &')
                os.system('sshfs -p ' + puerto + ' -o reconnect -C -o workaround=all ' + usuario + '@' + ip + ':/tmp/ ' + monta + '')
                os.system('xdg-open ' + monta)
            except:
                self.mensaje("No se ha podido montar la carpeta en el equipo remoto", "Atencion", atencion)
###################################
###################################

    def on_Btn_cups_clicked(self, widget, ip, usuario, password, puerto, notebook, spinner, estado):
        ssh_path = os.environ['HOME'] + '/.ssh/id_rsa'
        spinner.start()
        estado.set_text("Creando tunel...")
        puerto = int(puerto)
        try:
            #Borra en el archivo cupsd.conf la autentificacion
            with settings(host_string=ip, port=puerto, password=password, user=usuario):
                sudo('sed -i."old" "/Require user @SYSTEM/d" /etc/cups/cupsd.conf;sed -i."old2" "/AuthType Default/d" /etc/cups/cupsd.conf;/etc/init.d/cups reload')
            server = SSHTunnelForwarder((ip, puerto), ssh_username=usuario, ssh_private_key=ssh_path, remote_bind_address=('127.0.0.1', 631))
            server.start()
            puerto_local = str(server.local_bind_port)
            scrolledwindow = Gtk.ScrolledWindow()
            scrolledwindow.set_hexpand(True)
            scrolledwindow.set_vexpand(True)
            page = WebKit.WebView()
            page.set_border_width(10)
            page.open("http://127.0.0.1:" + puerto_local)
            scrolledwindow.add(page)
            tab_label = tablabel.TabLabel("CUPS " + ip, Gtk.Image.new_from_file("/usr/share/grx/icons/cups32.png"))
            tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, page)
            notebook.append_page(scrolledwindow, tab_label)
            self.show_all()
        except:
            self.mensaje("No se ha podido ejecutar cups", "Atencion", atencion)
        spinner.stop()
        estado.set_text("")

    def on_Btn_impre_backup_clicked(self, widget, ip, usuario, puerto, password, spinner, estado):
        spinner.start()
        estado.set_text("Creando archivo comprimido")

        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            try:
                tmp = run('mktemp -t ' + ip + '-impresoras-XXXXXX.tar.gz')
                sudo('tar -czvf ' + tmp + ' /etc/cups/')
                win = GrabaArchivo(ip, usuario, puerto, password, tmp, "impresora")
                self.show_all()
            except:
                self.mensaje("No se ha podido guardar la configuracion", "Atencion", atencion)
        spinner.stop()
        estado.set_text("")

    def on_Btn_backup_clicked(self, widget, ip, usuario, puerto, password, spinner, estado):
        spinner.start()
        estado.set_text("Creando archivo comprimido")

        with settings(host_string=ip, port=puerto, password=password, user=usuario):
            try:
                tmp = run('mktemp -t ' + ip + '-etc-XXXXXX.tar.gz')
                sudo('tar -czvf ' + tmp + ' /etc/')
                win = GrabaArchivo (ip, usuario, puerto, password, tmp, "etc")
                self.show_all()
            except:
                self.mensaje("No se ha podido guardar la configuracion", "Atencion", atencion)
        spinner.stop()
        estado.set_text("")

    def on_Btn_carpetas_clicked(self, widget, ip, usuario, puerto, spinner, estado):
        spinner.start()
        estado.set_text("Montando carpeta...")

        try:
            monta = subprocess.check_output(['mktemp','-d','-t', ip + '-' + usuario + '-XXXXXX'])
            os.system('sshfs -p ' + puerto + ' -o reconnect -C -o workaround=all ' + usuario + '@' + ip + ':/home/' + usuario + ' ' + monta + '')
            result = os.system('xdg-open ' + monta)
        except:
            self.mensaje ("No se ha podido montar la carpeta remota", "Atencion", atencion)
        spinner.stop()
        estado.set_text("")

    def on_Btn_info_clicked(self, widget, ip, usuario, puerto, password, notebook, spinner, estado):
        info = informacion.Informacion(self, ip, usuario, puerto, password)
        imagen = '/usr/share/grx/icons/info_equipo.png'
        tab_label = tablabel.TabLabel("Info", Gtk.Image.new_from_file(imagen))
        tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, info)
        notebook.append_page(info, tab_label)
        self.show_all()

    def on_Btn_terminal_clicked(self, widget, ip, usuario, puerto, notebook, spinner, estado):
        v = Vte.Terminal()
        try:
            v.fork_command_full(Vte.PtyFlags.DEFAULT, os.environ['HOME'], ["/usr/bin/ssh", "-p" + puerto, usuario + "@" + ip,],[],GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None,)
        except:
            v.spawn_sync(Vte.PtyFlags.DEFAULT,os.environ['HOME'], ["/usr/bin/ssh","-p" + puerto , usuario + "@" + ip,],[],GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None,)
        tab_label = tablabel.TabLabel("SSH " + ip, Gtk.Image.new_from_file("/usr/share/grx/icons/ssh.png"))
        tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, v)
        notebook.append_page(v ,tab_label)
        self.show_all()


    def on_Btn_network_clicked(self, widget, ip, usuario, puerto,password,spinner,estado):
        with settings(host_string=ip, port=puerto, user=usuario, password=password):
            sudo ('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/nm-connection-editor" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/nm-connection-editor" >>/etc/sudoers   ; fi')
        try:
                os.system('ssh -l ' + usuario + ' -Y -A -C -X -2 -4 -f -p ' + puerto + ' ' + ip + ' "sudo nm-connection-editor" &')
        except:
                self.mensaje("No se ha podido ejecutar 'nm-connection-editor' en el equipo remoto", "Atencion", atencion)


    def on_Btn_color_color_set(self, widget, notebook):
        color = widget.get_color()
        rgba = Gdk.RGBA.from_color(color)
        self.override_background_color(0, rgba)


    def on_Btn_nmap_clicked(self, widget, ip, usuario, password, puerto, spinner, estado, notebook):
        try:
            t = threading.Thread(target=self.cliente_nmap,args=(widget, ip, usuario, puerto, password, notebook, spinner, estado))
            t.setDaemon(True)
            t.start()
        except:
#############################3
#############################3 Al ser un daemon sale sin saber si se ha roto. Hay que buscar la manera de comprobar una excepcion
##############################
            self.mensaje('No se ha podido ejecutar nmap en el equipo remoto', "Atencion", atencion)

    def cliente_nmap(self, widget, ip, usuario, puerto, password, notebook, spinner, estado):

        spinner.start()
        estado.set_text("Ejecutando nmap ...")
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        page = Gtk.TextView()
        scrolledwindow.add(page)

        with settings(host_string=ip,port=puerto,password=password,user=usuario):
            tmp=ip.split(".")[0]+'.'+ip.split(".")[1]+'.'+ip.split(".")[2]+'.1-254'
            res = sudo('nmap -F -T4 ' + tmp)
            res = res.replace("nohup: ignoring input and appending output to 'nohup.out'", "")
            textbuffer = page.get_buffer()
            textbuffer.set_text(res)
            tab_label = tablabel.TabLabel("nmap " + ip,Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
            tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
            notebook.append_page(scrolledwindow ,tab_label)
            self.show_all()
        spinner.stop()
        estado.set_text("")

    def nombre_PC(self, widget, ip, usuario, puerto):

        with settings(host_string=ip,port=puerto,user=usuario):
            nombre=run ('hostname')
            nombre=nombre.split("\n")
            if "nohup:" in nombre[0]:
                return nombre[1]
            else:
                return nombre[0]

    def usuarios_pc(self, widget, ip, usuario, puerto, password):
        usuarios = []
        with settings(host_string=ip,port=puerto,user=usuario,password=password):
            nombre = run ('ls /home/')
            nombre = nombre.replace("nohup: ignoring input and appending output to 'nohup.out'", "")
            nombre = nombre.split()
#        activos=sudo ("who | grep ' \:[0-9]'|cut -d ' ' -f1 ")
            try:
                activos = sudo("who | grep ' \:[0-9]'")
                activos = activos.replace("nohup: ignoring input and appending output to 'nohup.out'", "")
                nombre_activos = activos.split(" ")[0]
                display_activos = activos.split(" ")[-1]
                activos = activos.split()
            except:
                activos = ""

            for user in nombre:
                 if user != "lost+found" and user[0:5] != "guest":
                    if user in activos:
                        tmp = [user, True,]
                        usuarios.append(tmp)
                 else:
                    tmp=[user,False,None]
                    usuarios.append(tmp)
        return usuarios


    def on_Btn_usuarios_clicked(self, widget, ip, usuario, puerto,notebook,password,tecnico,password_tecnico,clave_cifrado,spinner,estado):
        spinner.start()
        estado.set_text("Buscando usuarios...")
        usuarios=[]
        try:
            equipo=self.nombre_PC(widget,ip, usuario, puerto)
            tab_label = tablabel.TabLabel(ip+'\n'+equipo,Gtk.Image.new_from_file("/usr/share/grx/icons/usuarios35.png"))
            scroll= Gtk.ScrolledWindow()
            scroll.set_hexpand(True)
            scroll.set_vexpand(True)
            grid_usuarios=Gtk.Grid()
            scroll.add(grid_usuarios)
            tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scroll)
            notebook.append_page(scroll ,tab_label)
            usuarios = self.usuarios_pc(widget,ip, usuario, puerto,password)

        except:
            self.mensaje('No se ha podido ejecutar la busqueda de usuarios', "Atencion", atencion)
        contador = 0
        for user in usuarios:
                grid = Gtk.Grid ()
                image = Gtk.Image()
                if user[0] == "administrador":
                    image.set_from_file('/usr/share/grx/icons/administrador.png')
                else:
                    if user[1]==True:
                        image.set_from_file('/usr/share/grx/icons/usuario_on.png')
                    else:
                        image.set_from_file('/usr/share/grx/icons/usuario_off.png')
                #display=user[2]
                display = ":0"
                label = Gtk.Label(user[0])
                grid.attach(image, 0, 0, 1, 1)
                grid.attach(label, 0, 1, 1, 1)
                boton = Gtk.Button()
                boton.id = (equipo)
                boton.add(grid)
                boton.connect("clicked", self.panel, boton, user, display, ip, usuario, puerto, notebook, password, tecnico, password_tecnico, clave_cifrado)
                boton.set_always_show_image(True)
                grid_usuarios.add(boton)
                contador += 1
        self.show_all()
        spinner.stop()
        estado.set_text("")

    def panel(self, widget, button, user, display, ip, usuario, puerto, notebook, password, tecnico, password_tecnico, clave_cifrado):
        #user[0] es el nombre
        #user[1] si esta o no activo
        if user[1] == True:
            grid = usuarios_on.Usuarios(button.id, user[0], display, ip, usuario, puerto, password, tecnico, password_tecnico, clave_cifrado)
        else:
            grid = usuarios_off.Usuarios(button.id,user[0], ip, usuario, puerto, password, tecnico, password_tecnico, clave_cifrado)
        if user == "administrador":
            imagen = '/usr/share/grx/icons/administrador35.png'
        else:
            if user[1] == True:
                imagen = '/usr/share/grx/icons/usuario35_on.png'
            else:
                imagen = '/usr/share/grx/icons/usuario35_off.png'
        tab_label = tablabel.TabLabel(user[0], Gtk.Image.new_from_file(imagen))
        tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, grid)
        notebook.append_page(grid ,tab_label)
        self.show_all()

    def on_Btn_mame_clicked(self, widget, notebook):
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        tab_label = tablabel.TabLabel("MAME ", Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
        grid_mame = Gtk.Grid()
        scroll.add(grid_mame)
        tab_label.connect("close-clicked", tablabel. on_close_clicked, notebook, scroll)
        notebook.append_page(scroll, tab_label)
        juegos = glob.glob('/usr/share/games/mame/roms/*.zip')
        col = 0
        fil = 0
        for juego in juegos:
            grid = Gtk.Grid()
            imagen = juego.replace("zip", "png")
            image = Gtk.Image()
            image.set_from_file(imagen)
            grid.add(image)
            boton = Gtk.Button()
            boton.id = (juego)
            boton.add(grid)
            boton.connect("clicked", self.panel_mame, juego)
            boton.set_always_show_image(True)
            #grid.attach(child, left, top, width, height)
            if col != 5:
                grid_mame.attach(boton, col, fil, 1, 1)
                col = col + 1
            else:
                col = 0
                fil = fil + 1
                grid_mame.attach(boton, col, fil, 1, 1)
        self.show_all()

    def panel_mame(self, widget, juego):
        os.system("mame " + juego + "&")

    def on_Btn_hp_plugin_clicked(self, widget, ip, usuario,password, puerto,spinner,estado):
        with settings(host_string=ip, port=puerto, user=usuario, password=password):
                sudo ('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/hp-plugin" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/hp-plugin" >>/etc/sudoers   ; fi')
            #try:
                tmp = sudo ('dpkg -s hplip 2>&1| grep -m 1 "Version:"|awk "{print $2}"')
                if tmp=="":
                    dialogo=Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,Gtk.ButtonsType.OK_CANCEL, "Atencion hplip no instalado")
                    dialogo.format_secondary_text("Pulse aceptar si desea instalarlo")
                    dialogo.set_default_size(150, 100)
                    label = Gtk.Label("hplip no esta instalado en el equipo. \nPulse Aceptar para instalar el paquete")
                    box = dialogo.get_content_area()
                    box.add(label)
                    dialogo.show_all()
                    respuesta=dialogo.run()
                    dialogo.destroy()
                    if respuesta == Gtk.ResponseType.OK:
                        error = sudo ( "apt-get install -f --force-yes --yes hplip hplip-gui")
                    elif respuesta == Gtk.ResponseType.CANCEL:
                        print("Cancelar Pulsado")
                        return
                dialog = Gtk.FileChooserDialog("Selecciona un archivo...", None,  Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
                dialog.set_current_folder("/usr/share/grx/hp/")
                response = dialog.run()
                path=dialog.get_filename()
                dialog.destroy()
                if response == Gtk.ResponseType.OK:
                    tmp = path.split("/")
                    datos = put (use_sudo=True, remote_path="/home/administrador/"+tmp[-1], local_path=path)
                    os.system('ssh -l ' + usuario + ' -Y -A -C -X -2 -4 -f -p ' + puerto + ' ' + ip + ' "sudo hp-plugin" &')
                elif response == Gtk.ResponseType.CANCEL:
                        print("Cancelar Pulsado")

         #except:
        #    self.mensaje("No se ha podido ejecutar 'hp-plugin' en el equipo remoto","Atencion",atencion)

############################
############################

    def on_Btn_hp_clicked(self, widget, ip, usuario,password, puerto,spinner,estado):
        with settings(host_string=ip, port=puerto, user=usuario, password=password):
            try:
                sudo ('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/hp-setup" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/hp-setup" >>/etc/sudoers   ; fi')
                tmp = sudo ('dpkg -s hplip 2>&1| grep -m 1 "Version:"|awk "{print $2}"')
                print tmp
                if tmp == "":
                    dialogo = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                        Gtk.ButtonsType.OK_CANCEL, "Atencion hplip no instalado")
                    dialog.format_secondary_text(
                        "Pulse aceptar si desea instalarlo")
                    dialogo.set_default_size(150, 100)
                    label = Gtk.Label("hplip no esta instalado en el equipo. \nPulse Aceptar para instalar el paquete")
                    box = dialogo.get_content_area()
                    box.add(label)
                    dialogo.show_all()
                    respuesta=dialogo.run()
                    dialogo.destroy()
                    if respuesta == Gtk.ResponseType.OK:
                        error = sudo ( "apt-get install -f --force-yes --yes hplip hplip-gui")
                    elif respuesta == Gtk.ResponseType.CANCEL:
                            print("Cancelar Pulsado")
                            return
                os.system('ssh -l ' + usuario + ' -Y -A -C -X -2 -4 -f -p ' + puerto + ' ' + ip + ' "sudo hp-setup" &')
            except:
                self.mensaje("No se ha podido ejecutar 'hp-setup' en el equipo remoto", "Atencion", atencion)
########################################################3
###########################################################

    def on_Btn_impre_clicked(self, widget, ip, usuario,password, puerto,spinner,estado):
        with settings(host_string=ip, port=puerto, user=usuario, password=password):
            sudo ('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/system-config-printer" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/system-config-printer" >>/etc/sudoers   ; fi')
        try:
            os.system('ssh -l ' + usuario + ' -Y -A -C -X -2 -4 -f -p ' + puerto + ' ' + ip + ' "sudo system-config-printer" &')
        except:
            self.mensaje("No se ha podido ejecutar 'system-config-printer' en el equipo remoto", "Atencion", atencion)

    def on_Btn_vncviewer_clicked(self, widget, ip, usuario, puerto, password, clave_remoto, spinner, estado):
        spinner.start()
        estado.set_text("Conectando con el equipo")
        ssh_path=os.environ['HOME'] + '/.ssh/id_rsa'

        try:
            puerto = int(puerto)
            server = SSHTunnelForwarder((ip, puerto), ssh_username=usuario,ssh_private_key=ssh_path,remote_bind_address=(ip, 5900))
            server.start()
            puerto_local = str(server.local_bind_port)
            msg = local('echo "' + clave_remoto + '" | vncviewer -autopass -compresslevel 9 -bgr233 127.0.0.1:' + puerto_local + ' &')
            #msg=local('echo "'+clave_remoto+'" | vinagre -autopass -compresslevel 9 -bgr233 127.0.0.1:'+puerto_local+' &')
        except:
            self.mensaje("No se ha podido ejecutar 'vncviewer' en el equipo remoto", "Atencion", atencion)
        spinner.stop()
        estado.set_text("")


    def on_Btn_escaner_clicked(self, widget, ip, usuario, puerto, password, spinner, estado):
        with settings(host_string=ip, port=puerto, user=usuario, password=password):
            try:
                sudo('if  grep "administrador ALL=(root) NOPASSWD: /usr/bin/grx-escaner" /etc/sudoers; then echo 1; else echo "administrador ALL=(root) NOPASSWD: /usr/bin/grx-escaner" >>/etc/sudoers   ; fi')
                datos = put (use_sudo=True, remote_path="/usr/bin/grx-escaner", local_path="/usr/share/grx/auxiliar/grx-escaner",mode=700)
                os.system('ssh -l ' + usuario + ' -Y -A -C -X -2 -4 -f -p '+puerto+' ' + ip + ' "sudo grx-escaner" &')

            except:
                self.mensaje("No se ha podido ejecutar grx-escaner en el equipo remoto", "Atencion", atencion)
            spinner.stop()
            estado.set_text("")















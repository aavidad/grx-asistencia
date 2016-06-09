'''
Created on 09/5/2016
@author: Alberto Avidad Fernandez
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from fabric.api import settings, run
import sys
import pygtk
pygtk.require("2.0")
import os
import socket
import subprocess
from datetime import datetime, timedelta
from gi.repository import Gtk, Gdk, GObject, WebKit
from gi.repository import GdkPixbuf
from configobj import ConfigObj
import nmap
import threading
import tablabel
import equipos_linux
import equipos_win
import impresoras
import router
import desconocido
import libreria

atencion = Gtk.MessageType.WARNING
info = Gtk.MessageType.INFO
error = Gtk.MessageType.ERROR
pregunta = Gtk.MessageType.QUESTION


def convierte_fecha(timestamp):
        epoch_start = datetime(year=1601, month=1, day=1)
        seconds_since_epoch = timestamp / 10 ** 7
        return epoch_start + timedelta(seconds=seconds_since_epoch)


def ip_valida(ip):
        try:
            datos = busca_sede(ip)
            sede = datos.split(";")[0]
            if sede == "Desconocido":
                entry_tlf.set_text("")
                entry_ext.set_text("")
                entry_direccion.set_text("")
                entry_mapa.set_text("")
                entry_centro.set_text("")
                entry_tlf_centro.set_text("")

            else:
                tlf = datos.split(";")[1]
                ext = datos.split(";")[2]
                direccion = datos.split(";")[3]
                mapa = datos.split(";")[4]
                centro = datos.split(";")[5]
                tlf_centro = datos.split(";")[6]
                entry_sedes.set_text(sede)
                entry_tlf.set_text(tlf)
                entry_ext.set_text(ext)
                entry_centro.set_text(centro)
                entry_tlf_centro.set_text(tlf_centro)
                entry_direccion.set_text(direccion)
                entry_mapa.set_text(mapa)
        except:
            entry_sedes.set_text("")
            entry_tlf.set_text("")
            entry_ext.set_text("")
            entry_direccion.set_text("")
            entry_mapa.set_text("")
            entry_centro.set_text("")
            entry_tlf_centro.set_text("")
        if is_valid_ipv4_address(ip):
            entry_ip.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1.0))
        else:
            entry_ip.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(127, 0, 0, 1.0))


###########################################################################
def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False

    return True


def conecta():
    ip = entry_ip.get_text()
    puerto = entry_puerto.get_text()
    if is_valid_ipv4_address(ip):
        try:
            prueba = os.system('nc -vnz -w 1 ' + ip + ' ' + puerto)
            if prueba == 0:
                return True
            else:
                return False
        except:
            mensaje("Error al intentar conectar con " + ip)


class Handler:

    def mensaje(self, texto, cabecera, tipo):
        dialog = libreria.Mensaje(texto, cabecera, tipo)
        dialog.run()
        dialog.destroy()

    def on_Limpiar_clicked(self, *args):
        entry_busca_usuario.set_text("")
        entry_numero_logon.set_text("")
        entry_ultimo_cambio_clave.set_text("")
        entry_ultima_modificacion.set_text("")
        entry_ultimo_login.set_text("")
        entry_intentos.set_text("")
        entry_clave_caduca.set_text("")
        entry_correo_creada.set_text("")
        entry_busca_nombre.set_text("")
        entry_correo.set_text("")
        entry_estado.set_text("")
        entry_telefono.set_text("")
        entry_creada.set_text("")
        entry_caduca.set_text("")
        entry_cambio_clave.set_text("")

    def on_acercade(self, text):
        aboutdialog = Gtk.AboutDialog()
        aboutdialog.set_name("GrX Asistencia")
        aboutdialog.set_version("0.5")
        aboutdialog.set_comments("Aplicacion para el mantenimiento de los equipos informaticos linux de la Diputacion de Granada")
        aboutdialog.set_website("http://incidencias.dipgra.es")
        aboutdialog.set_website_label("Asistencia Tecnica")
        aboutdialog.set_license_type(Gtk.License.GPL_3_0)
        aboutdialog.set_transient_for(window)
        aboutdialog.set_authors(["Oficina de Software Libre de la Diputacion de Granada \nProgramador encargado de la aplicacion: Alberto Avidad Fernandez"])
        pixbuf = GdkPixbuf.Pixbuf.new_from_file('/usr/share/grx/icons/Linux.png')
        aboutdialog.set_logo(pixbuf)
        aboutdialog.run()
        aboutdialog.destroy()

    def on_tecnico_activate(self, *args):
        print ("nada")

    def busca_mac(self, mac):
        for line in open("/usr/share/grx/auxiliar/MAC.cvs"):
            if mac in line:
                return line

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def on_Btn_glpi_clicked(self, *args):
        try:
            os.system("xdg-open https://incidencias.dipgra.es/glpi/ &")
        except:
            self.mensaje("No ha sido posible abrir la pagina de incidencias", "Atencion", atencion)

    def on_Btn_cronos_clicked(self, *args):
        try:
            os.system("xdg-open http://cronos.grx &")
        except:
            self.mensaje("No ha sido posible abrir la pagina de cronos.grx", "Atencion", atencion)

    def on_Btn_WebMail_clicked(self, *args):
        try:
            os.system("xdg-open https://correoweb.dipgra.es/owa/ &")
        except:
            self.mensaje("No ha sido posible abrir la pagina del correoweb", "Atencion", atencion)

    def on_Btn_centros_clicked(self, *args):
        try:
            os.system("xdg-open /usr/share/grx/auxiliar/DATOS_USUARIOS.pdf &")
        except:
            self.mensaje("No ha sido posible abrir el cuadrante, compruebe que tenga pdf instalado", "Atencion", atencion)

    def on_Btn_Beiro_clicked(self, *args):
        try:
            os.system("xdg-open http://beiro.grx:55555 &")
        except:
            self.mensaje("No ha sido posible abrir la pagina de beiro.grx:55555", "Atencion", atencion)

    def on_Btn_zenmap_clicked(self, *args):
        try:
            clave = entry_password_tecnico.get_text()
            command = 'zenmap &'
            p = os.system('echo %s|sudo -S %s' % (clave, command))
        except:
            self.mensaje("No ha sido posible ejecutar zenmap, compruebe que lo tiene instalado", "Atencion", atencion)

    def buscarElemento(lista, elemento):
        for i in range(0, len(lista)):
            if(lista[i] == elemento):
                return i

    def crea_lista_usuarios(self, listado):
        listado = listado.split()
        orden = sorted(listado)
        centro = Gtk.ListStore(str)
        for usuarios in orden:
            centro.append([usuarios])
        return centro

    def crea_lista_nombres(self, listado):
        listado = listado.split("\n")
        orden = sorted(listado)
        print (orden)
        if orden[0] == "":
            del orden[0]
        print (orden)
        nombre = Gtk.ListStore(str)
        for tmp in orden:
            nombre.append([tmp])
        return nombre

    def on_entry_busca_nombre_icon_press(self, widget, *args):
        nombre = widget.get_text()
        if nombre != "":
            try:
                ldap = subprocess.check_output(['/usr/share/grx/ldap/ldap_nombre.sh', nombre])
            except:
                self.mensaje("No se ha podido realizar la consulta AD", "Atencion", atencion)
            listado_nombres = self.crea_lista_nombres(ldap)
            scrolledwindow = Gtk.ScrolledWindow()
            scrolledwindow.set_hexpand(True)
            scrolledwindow.set_vexpand(True)
            page = Gtk.TextView()
            scrolledwindow.add(page)
            textbuffer = page.get_buffer()
            textbuffer.set_text(ldap)
            tab_label = tablabel.TabLabel("ldap " + nombre, Gtk.Image.new_from_file("/usr/share/grx/icons/usuarios35.png"))
            tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
            notebook.append_page(scrolledwindow, tab_label)
            notebook.show_all()

    def on_Btn_actualiza_sedes_clicked(self, widget):
            try:
                os.system("wget http://incidencias.dipgra.es/ubuntu/sedes.txt.csv -O /usr/share/grx/auxiliar/sedes.txt.csv &")
            except:
                self.mensaje("No se ha podido descargar el archivo. Compruebe la conexion.", "Atencion", atencion)

    def on_Btn_color_color_set(self, widget):
        color = widget.get_color()
        rgba_soporte = Gdk.RGBA.from_color(color)
        Box_soporte.override_background_color(0, rgba_soporte)
        self.show_all()

    def on_Btn_color2_color_set(self, widget):
        color = widget.get_color()
        rgba_usuarios = Gdk.RGBA.from_color(color)
        Box_usuarios.override_background_color(0, rgba_usuarios)
        self.show_all()

    def on_entry_cambio_clave_icon_press(self, widget, *args):
        nombre = entry_busca_usuario.get_text()
        clave = widget.get_text()
        tecnico = entry_tecnico.get_text()
        password_tecnico = entry_password_tecnico.get_text()
        try:
            tecnico = tecnico.split("@")[0]
            cmd = '(echo ' + clave + '; echo ' + clave + ' ;)| net ads password -U ' + tecnico + '%' + password_tecnico + ' ' + nombre
            print (cmd)
            os.system(cmd)
            self.mensaje("Se ha cambiado la clave de " + nombre + " con EXITO", "Informacion", info)
        except:
            self.mensaje("No se ha podido validar al tecnico. Compruebe la clave y el ticket kerberos", "Atencion", atencion)

    def on_entry_estado_icon_press(self, widget, *args):
            nombre = entry_busca_usuario.get_text()
            password_tecnico = entry_password_tecnico.get_text()
            tecnico = entry_tecnico.get_text()
            try:
                tecnico = tecnico.split("@")[0]
                ldap = subprocess.check_output(['/usr/share/grx/ldap/ldap.sh', nombre])
                ldap_lista = ldap.split("\n")
                #######Busca el dn:
                tmp = filter(lambda x: 'dn:' in x, ldap_lista)
                dn = ''.join(tmp)
                archivo = dn + '\nchangetype: modify\nreplace: lockoutTime\nlockoutTime: 0'
                tmp_ruta = subprocess.check_output(['mktemp'])
                archi = open(tmp_ruta, 'w')
                archi.write(archivo)
                archi.close()
                resultado = subprocess.check_output(['ldapmodify', '-f', tmp_ruta])
                widget.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1.0))
                widget.set_text("Activa")
                self.mensaje("Se ha cambiado el estado de la cuenta " + nombre + " con EXITO", "Informacion", info)
            except:
                self.mensaje("No se ha podido validar al tecnico. Compruebe la clave", "Atencion", atencion)

    def on_Btn_ticket_clicked(self, widget):
            glpi_usuario = entry_busca_usuario.get_text()
            if glpi_usuario != "":
                try:
                    os.system('xdg-open "https://incidencias.dipgra.es/glpi/front/ticket.php?is_deleted=0&field[0]=4&searchtype[0]=contains&contains[0]=' + glpi_usuario + '&itemtype=Ticket&start=0&_glpi_csrf_token=0" &')
                except:
                    self.mensaje("No ha sido posible abrir la pagina de incidencias", "Atencion", atencion)

    def on_Btn_equipo_clicked(self, widget):
            glpi_usuario = entry_busca_usuario.get_text()
            if glpi_usuario != "":
                try:
                    os.system('xdg-open "https://incidencias.dipgra.es/glpi/front/computer.php?is_deleted=0&field[0]=view&searchtype[0]=contains&contains[0]=' + glpi_usuario + '&itemtype=Computer&start=0&_glpi_csrf_token=0" &')
                except:
                    self.mensaje("No ha sido posible abrir la pagina de incidencias", "Atencion", atencion)

    def on_Btn_glpi2_clicked(self, widget):
        glpi_usuario = entry_busca_usuario.get_text()
        if glpi_usuario != "":
            try:
                os.system('xdg-open "https://incidencias.dipgra.es/glpi/front/user.php?is_deleted=0&field[0]=view&searchtype[0]=contains&contains[0]=' + glpi_usuario + '&itemtype=User&start=0&_glpi_csrf_token=0" &')
            except:
                self.mensaje("No ha sido posible abrir la pagina de incidencias", "Atencion", atencion)

    def on_entry_busca_usuario_icon_press(self, widget, *args):
        usuario = widget.get_text()
        if usuario != "":
            ldap = subprocess.check_output(['/usr/share/grx/ldap/ldap_usuario.sh', usuario])
            listado_usuarios = self.crea_lista_usuarios(ldap)
            completion_usuarios = Gtk.EntryCompletion()
            completion_usuarios.set_model(listado_usuarios)
            completion_usuarios.set_text_column(0)
            widget.set_completion(completion_usuarios)

    def on_entry_busca_usuario_changed(self, widget, *args):
        entry_numero_logon.set_text("")
        entry_ultimo_cambio_clave.set_text("")
        entry_ultima_modificacion.set_text("")
        entry_ultimo_login.set_text("")
        entry_intentos.set_text("")
        entry_clave_caduca.set_text("")
        entry_correo_creada.set_text("")
        entry_busca_nombre.set_text("")
        entry_correo.set_text("")
        entry_estado.set_text("")
        entry_telefono.set_text("")
        entry_creada.set_text("")
        entry_caduca.set_text("")
        entry_cambio_clave.set_text("")
        usuario = widget.get_text()
        if (usuario != "") and (len(usuario) == 2):
            ldap = subprocess.check_output(['/usr/share/grx/ldap/ldap_usuario.sh', usuario])
            listado_usuarios = self.crea_lista_usuarios(ldap)
            completion_usuarios = Gtk.EntryCompletion()
            completion_usuarios.set_model(listado_usuarios)
            completion_usuarios.set_text_column(0)
            widget.set_completion(completion_usuarios)

    def on_Btn_usuario_clicked(self, widget):
            nombre = entry_busca_usuario.get_text()
            if nombre == "":
                return
            tecnico = entry_tecnico.get_text()
            password_tecnico = entry_password_tecnico.get_text()
            tecnico = tecnico.split("@")[0]
            try:
                ldap = subprocess.check_output(['/usr/share/grx/ldap/ldap.sh', nombre])
            except:
                self.mensaje("No se ha podido realizar la consulta AD", "Atencion", atencion)

            scrolledwindow = Gtk.ScrolledWindow()
            scrolledwindow.set_hexpand(True)
            scrolledwindow.set_vexpand(True)
            page = Gtk.TextView()
            scrolledwindow.add(page)
            textbuffer = page.get_buffer()
            textbuffer.set_text(ldap)
            tab_label = tablabel.TabLabel("ldap " + nombre, Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
            tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, scrolledwindow)
            notebook.append_page(scrolledwindow, tab_label)
            notebook.show_all()

    def on_entry_busca_usuario(self, widget, *args):
            nombre = widget.get_text()
            if nombre == "":
                return
            tecnico = entry_tecnico.get_text()
            password_tecnico = entry_password_tecnico.get_text()
            tecnico = tecnico.split("@")[0]
#            archi = open('/usr/share/grx/ldap/ldap', 'r')   ###En casa
#            ldap = archi.read()   ###En casa

            try:##DESCOMENTA SI ESTAS INTEGRADO EN UN DOMINIO ACTIVE DIRECTORY Y COMENTA CASA
                ldap= subprocess.check_output (['/usr/share/grx/ldap/ldap.sh',nombre])
            except:
                self.mensaje("No se ha podido realizar la consulta AD","Atencion",atencion)

            ldap_lista = ldap.split("\n")

            #####Busca y comprueba el estado de la cuenta
            try:
                lock = filter(lambda x: 'lockoutTime:' in x, ldap_lista)
                strl = ''.join(lock)
                if (strl.split(":")[1]).strip() == "0":
                    entry_estado.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1.0))
                    estado = "Activa"
                else:
                    entry_estado.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(127, 0, 0, 1.0))
                    estado = "BLOQUEADA"
                entry_estado.set_text(estado)
            except:
                entry_estado.set_text("NSNC")
            ######Busca el correo y lo coloca en entry_correo
            try:
                tmp = filter(lambda x: 'mail:' in x, ldap_lista)
                mail = ''.join(tmp)
                entry_correo.set_text((mail.split(":")[1]).strip())
            except:
                entry_correo.set_text("NSNC")
            ######Busca las veces que hemos introducido la clave mal
            try:
                tmp = filter(lambda x: 'badPwdCount:' in x, ldap_lista)
                badpwd = ''.join(tmp)
                entry_intentos.set_text((badpwd.split(":")[1]).strip())
            except:
                entry_intentos.set_text("NSNC")
            ######Busca el nombre completo
            try:
                tmp = filter(lambda x: 'cn:' in x, ldap_lista)
                ncompleto = ''.join(tmp)
                entry_busca_nombre.set_text((ncompleto.split(":")[1]).strip())
            except:
                entry_busca_nombre.set_text("NSNC")

            #######Busca el ultimo login
            #try:
            tmp = filter(lambda x: 'lastLogon:' in x, ldap_lista)
            expira = ''.join(tmp)
            fecha = (expira.split(":")[1]).strip()
            tmp = convierte_fecha(int(fecha)).strftime("%d-%m-%y %H:%M")
            entry_ultimo_login.set_text(tmp)
            #except:
            #	entry_ultimo_login.set_text("NSNC")		

            #######Busca cuando caduca la clave
            try:
                tmp = filter(lambda x: 'badPasswordTime:' in x, ldap_lista)
                expira = ''.join(tmp)
                fecha = (expira.split(":")[1]).strip()
                tmp = convierte_fecha(int(fecha)).strftime("%d-%m-%y %H:%M")
                entry_clave_caduca.set_text(tmp)
            except:
                entry_clave_caduca.set_text("NSNC")

            #######Busca cuando expira la cuenta
            try:
                tmp = filter(lambda x: 'accountExpires:' in x, ldap_lista)
                expira = ''.join(tmp)
                fecha = (expira.split(":")[1]).strip()
                if fecha == "9223372036854775807" or fecha == "0":
                    entry_caduca.set_text("No Caduca")
                else:
                    tmp = convierte_fecha(int(fecha)).strftime("%d-%m-%y %H:%M")
                    entry_caduca.set_text(tmp)
            except:
                entry_caduca.set_text("NSNC")

        #######Busca el ultimo cambio de contrasena

            try:
                tmp = filter(lambda x: 'pwdLastSet:' in x, ldap_lista)
                expira = ''.join(tmp)
                fecha = (expira.split(":")[1]).strip()
                tmp = convierte_fecha(int(fecha)).strftime("%d-%m-%y %H:%M")
                entry_ultimo_cambio_clave.set_text(tmp)
            except:
                entry_ultimo_cambio_clave.set_text("NSNC")

            #######Busca cuando se creo la cuenta
            try:
                tmp = filter(lambda x: 'whenCreated:' in x, ldap_lista)
                creada = ''.join(tmp)
                creada = (creada.split(":")[1]).strip()
                anio = creada[0:4]
                mes = creada[4:6]
                dia = creada[6:8]
                entry_creada.set_text(dia + '/'  +mes + '/' + anio)
            except:
                entry_creada.set_text("NSNC")

            #######Busca cuando se modifico por ultima vez
            try:
                tmp = filter(lambda x: 'whenCreated:' in x, ldap_lista)
                modificada = ''.join(tmp)
                modificada = (modificada.split(":")[1]).strip()
                anio = modificada[0:4]
                mes = modificada[4:6]
                dia = modificada[6:8]
                entry_ultima_modificacion.set_text(dia + '/' + mes + '/' + anio)
            except:
                entry_ultima_modificacion.set_text("NSNC")
            #######Busca cuando se creo la cuenta de correo
            try:
                tmp = filter(lambda x: 'msExchWhenMailboxCreated:' in x, ldap_lista)
                creada = ''.join(tmp)
                creada = (creada.split(":")[1]).strip()
                anio = creada[0:4]
                mes = creada[4:6]
                dia = creada[6:8]
                entry_correo_creada.set_text(dia + '/' + mes + '/' + anio)
            except:
                entry_correo_creada.set_text("NSNC")

            #######Muestra el numero de telefono
            try:
                tmp = filter(lambda x: 'telephoneNumber:' in x, ldap_lista)
                if tmp != []:
                    telefono = ''.join(tmp)
                    telefono = (telefono.split(":")[1]).strip()
                    entry_telefono.set_text(telefono)
            except:
                entry_telefono.set_text("NSNC")

            #######Muestra el numero de inicios de sesion de la cuenta
            try:
                tmp = filter(lambda x: 'logonCount:' in x, ldap_lista)
                logonCount = ''.join(tmp)
                entry_numero_logon.set_text((logonCount.split(":")[1]).strip())
            except:
                entry_numero_logon.set_text("NSNC")

    def on_entry_sedes_icon_press(self, widget, *args):
            for col in listado_sedes:
                if col[0] == widget.get_text():
                    res = ''.join(col[1])
                    entry_ip.set_text(res + "*")
                    entry_tlf.set_text(''.join(col[2]))
                    entry_ext.set_text(''.join(col[3]))
                    entry_direccion.set_text(''.join(col[4]))
                    entry_mapa.set_text(''.join(col[5][:-1]))
                    break

    def on_Btn_kerberos_clicked(self, widget):
        try:
            tecnico = entry_tecnico.get_text()
            tecnico = tecnico.split("@")[0]
            password_tecnico = entry_password_tecnico.get_text()
            validar_tecnico = subprocess.check_output(['/usr/share/grx/ldap/validar_tecnico.sh', tecnico, password_tecnico])
            if "NT_STATUS_LOGON_FAILURE" in validar_tecnico:
                self.mensaje("No se ha podido validar al tecnico. Compruebe la clave o la conexion con el servidor\n FUNCIONES DE BUSQUEDA DE USUARIO INACTIVAS", "Atencion", atencion)
            elif "NETLOGON_CACHED_ACCOUNT" in validar_tecnico:
                self.mensaje("No se ha podido validar al tecnico en el servidor de dominio. \n Usando CUENTA CACHEADA", "Atencion", atencion)
            elif "succeeded" in validar_tecnico:
                self.mensaje("Credenciales validadas", "Informacion", info)
        except:
            self.mensaje("No se ha podido validar al tecnico. Compruebe la clave. Funciones mermadas", "Atencion", atencion)

    def on_Btn_ocs_clicked(self, *args):
        try:
            os.system("xdg-open https://incidencias.dipgra.es/ocsreports/ &")
        except:
            self.mensaje("No ha sido posible abrir la pagina de ocs", "Atencion", atencion)

    def on_Btn_samba_clicked(self, *args):
        try:
            os.system("xdg-open smb://10.2.10.213/ &")
        except:
            self.mensaje("No ha sido posible abrir petete", "Atencion", atencion)

    def on_llamada_telefono(self, widget, *args):
        numero = widget.get_text()
        numero = numero.replace(" ", "")
        try:
            os.system('linphone -c ' + numero + ' &')
        except:
            self.mensaje("No ha sido posible abrir linphone","Atencion", atencion)

    def on_entry_mapa_icon_press(self, *args):
        try:
            mapa = entry_mapa.get_text()
            centro = entry_sedes.get_text()
            if entry_mapa.get_text() != "":
                scrolledwindow = Gtk.ScrolledWindow()
                scrolledwindow.set_hexpand(True)
                scrolledwindow.set_vexpand(True)
                page = WebKit.WebView()
                page.set_border_width(10)
                os.system("cat /usr/share/grx/auxiliar/si_proxy |dconf load /")
                page.open(mapa)
                scrolledwindow.add(page)
                tab_label = tablabel.TabLabel("Mapa \n" + centro, Gtk.Image.new_from_file("/usr/share/grx/icons/maps.jpeg"))
                tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, page)
                notebook.append_page(scrolledwindow, tab_label)
                window.show_all()
        except:
            self.mensaje("No se ha podido ejecutar maps", "Atencion", atencion)

    def on_Btn_isl_clicked(self, *args):
        try:
            output = os.system("proxychains /opt/ISLOnline/ISLLight/ISLLight &")
        except:
            self.mensaje("No ha sido posible ejecutar ISL", "Atencion", atencion)

    def on_Btn_tserv_clicked(self, *args):
        usuario = entry_tecnico.get_text()
        clave = entry_password_tecnico.get_text()
        tserv = entry_server.get_text()
        geometria = entry_geometria.get_text()
        if radio_freerdp.get_active():
            try:
                os.system('xfreerdp -g ' + geometria + ' -u ' + usuario + ' -p ' + clave + ' ' + tserv + '  &')
            except:
                self.mensaje("No ha sido posible ejecutar rdesktop", "Atencion", atencion)
        else:
            try:
                os.system('rdesktop -g ' + geometria + ' -u ' + usuario + ' -p ' + clave + ' ' + tserv + '  &')
            except:
               self.mensaje("No ha sido posible ejecutar rdesktop", "Atencion", atencion)

    def on_Btn_Busca_Host_activate(self, *args):
            t = threading.Thread(target=Busca_Host)
            t.start()

    def on_Btn_Busca_Host_clicked(self, widget, icon, event):
        if icon.value_name == "GTK_ENTRY_ICON_PRIMARY":
            t = threading.Thread(target=Busca_Host)
            t.start()
        elif icon.value_name == "GTK_ENTRY_ICON_SECONDARY":
            entry_ip.set_progress_pulse_step(0)

    def on_entry_correo_icon_press(self, widget, enum, void):
        os.system("xdg-email " + widget.get_text())

###################FIN HANDLER

def onSalir(self, *args):
    graba_configuracion(self, *args)
    limpiar(self, *args)
    Gtk.main_quit(*args)


def do_pulse(self):
    entry_ip.progress_pulse()
    return True


def panel(self, button, pc, sede, ip, usuario, puerto, password, tecnico, password_tecnico, clave_cifrado, clave_remoto):
    etiqueta = button.id + '\n' + sede
    if pc == "Linux":
            grid = equipos_linux.Equipos_Linux(button.id,usuario,puerto,password,tecnico,password_tecnico,clave_cifrado,clave_remoto)
            tab_label = tablabel.TabLabel(etiqueta,Gtk.Image.new_from_file("/usr/share/grx/icons/Linux_pc.png"))
    elif pc == "Impresora":	
            grid = impresoras.Impresoras(button.id)
            tab_label = tablabel.TabLabel(etiqueta, Gtk.Image. new_from_file("/usr/share/grx/icons/Printer_pc.png"))
    elif pc == "Windows":
            grid = equipos_win.Equipos_Windows(button.id, usuario, puerto, password, tecnico, password_tecnico)
            tab_label = tablabel.TabLabel(etiqueta,Gtk.Image.new_from_file("/usr/share/grx/icons/Windows_pc.png"))
    elif pc == "Router":
            grid = router.Router(button.id)
            tab_label = tablabel.TabLabel(etiqueta,Gtk.Image.new_from_file("/usr/share/grx/icons/Router.png"))
    elif pc == "Desconocido":
            grid = desconocido.Desconocido(button.id)
            tab_label = tablabel.TabLabel(etiqueta,Gtk.Image.new_from_file("/usr/share/grx/icons/Desconocido_pc.png"))

    tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, grid)
    notebook.append_page(grid ,tab_label)
    window.show_all()


def crea_lista():

    linea = Gtk.ListStore(str, str, str, str, str, str, str, str)
    try:
            for line in open("/usr/share/grx/auxiliar/sedes.txt.csv"):
                sede = line.split(";")[0]
                dirip = line.split(";")[1]
                tlf = line.split(";")[2]
                ext = line.split(";")[3]
                direccion = line.split(";")[4]
                mapa = line.split(";")[5]
                centro = line.split(";")[6]
                tlf_centro = line.split(";")[7]
                linea.append([sede, dirip, tlf, ext, direccion, mapa, centro, tlf_centro])
            return linea
    except:
            print "No ha sido posible leer el archivo sedes.txt.csv"


def nombre_PC(ip, usuario, puerto):
    with settings(host_string=ip, port=puerto, user=usuario):
            nombre = run('hostname')
            nombre = nombre.split("\n")
            if "nohup:" in nombre[0]:
                return nombre[1]
            else:
                return nombre[0]


def busca_sede(ip):
    sede = "Desconocido"
    tlf = "Desconocido"
    ext = "Desconocido"
    direccion = "Desconocido"
    mapa = "Desconocido"
    centro = "Desconocido"
    tlf_centro = "Desconocido"
    tmp = ip.split(".")[0] + '.' + ip.split(".")[1] + '.' + ip.split(".")[2] + '.'
    try:
        for line in open("/usr/share/grx/auxiliar/sedes.txt.csv"):
            if tmp in line:
                sede = line.split(";")[0]
                tlf = line.split(";")[2]
                ext = line.split(";")[3]
                direccion = line.split(";")[4]
                mapa = line.split(";")[5]
                centro = line.split(";")[6]
                tlf_centro = line.split(";")[7][:-1]
                continue
        return (sede + ';' + tlf + ';' + ext + ';' + direccion + ';' + mapa + ';' + centro + ';' + tlf_centro)

    except:
        print ("No se ha podido ejecutar busca_sede")

def Busca_Host():
    ip = entry_ip.get_text()
    entry_ip.set_progress_pulse_step(0.2)
    timeout_id = GObject.timeout_add(100, do_pulse, None)
    usuario = entry_usuario.get_text()
    puerto = entry_puerto.get_text()
    tecnico = entry_tecnico.get_text()
    password_tecnico = entry_password_tecnico.get_text()
    password = entry_password.get_text()
    clave_cifrado = entry_clave_cifrado.get_text()
    clave_remoto = entry_clave_remoto.get_text()
    try:
        sede = busca_sede(ip).split(";")[0]
    except:
        print ("No se ha podido")

    tab_label = tablabel.TabLabel(ip + '\n' + sede, Gtk.Image.new_from_file("/usr/share/grx/icons/equipos.gif"))
    scroll =  Gtk.ScrolledWindow()
    grid_nmap = Gtk.Grid()
    scroll.add(grid_nmap)
    tab_label.connect("close-clicked", tablabel. on_close_clicked, notebook, scroll)
    notebook.append_page(scroll, tab_label)
    try:
        nm = nmap.PortScanner()
    except nmap.PortScannerError:
        print('Error, nmap esta instalado en su sistema?', sys.exc_info()[0])
        return
    except:
        print('No se ha podido ejecutar la busqueda de equipos \n')
        return

    try:
        arguments = "-Pn -p"
        if checkwin.get_active():
            arguments = arguments + "135,"
        if checkimpre.get_active():
            arguments = arguments + "9100,"
        if checklinux.get_active():
            arguments = arguments + "8080,"
        if checkrouter.get_active():
            arguments = arguments + "23,80"
        print arguments
        nm.scan(hosts=ip, arguments=arguments)

    except:
        print('No se ha podido ejecutar nmap \n')
        return
    contador = 0

    for host in nm.all_hosts():
        grid = Gtk.Grid()
        image = Gtk.Image()
        if checkimpre.get_active() and nm[host]['tcp'][9100]['state'] == 'open':
            image.set_from_file('/usr/share/grx/icons/Printer.png')
            pc = "Impresora"
        elif checkwin.get_active() and nm[host]['tcp'][135]['state'] == 'open':
            image.set_from_file('/usr/share/grx/icons/Windows.png')
            pc = "Windows"
        elif checkrouter.get_active() and (nm[host]['tcp'][80]['state'] == 'open' or nm[host]['tcp'][23]['state'] == 'open'):
            if (host.split(".")[0] == "10" and host.split(".")[3] == "254")or (host.split(".")[0] == "192" and host.split(".")[3] == "1"):
                image.set_from_file('/usr/share/grx/icons/Router-128.png')
                pc = "Router"
            elif checklinux.get_active() and nm[host]['tcp'][8080]['state'] == 'open':
                image.set_from_file('/tecnico=tecnico.split("@")[0]usr/share/grx/icons/Linux.png')
                pc = "Linux"
            else:
                image.set_from_file('/usr/share/grx/icons/Desconocido.png')
                pc = "Desconocido"
        elif checklinux.get_active() and nm[host]['tcp'][8080]['state'] == 'open':
            image.set_from_file('/usr/share/grx/icons/Linux.png')
            pc = "Linux"
        elif nm[host]['tcp'][80]['state'] == 'open':
            image.set_from_file('/usr/share/grx/icons/Desconocido.png')
            pc = "Desconocido"

        else:
            continue

        label = Gtk.Label(host + '\n' + sede)
        grid.attach(image, 0, 0, 1, 1)
        grid.attach(label, 0, 1, 1, 1)
        boton = Gtk.Button()
        boton.id = (host)
        boton.add(grid)
        boton.connect("clicked", panel, boton, pc, sede, ip, usuario, puerto, password, tecnico, password_tecnico, clave_cifrado, clave_remoto)
        boton.set_always_show_image(True)
        grid_nmap.add(boton)
        contador += 1
    GObject.source_remove(timeout_id)
    timeout_id = None
    entry_ip.set_progress_pulse_step(0)
    window.show_all()
    print('Equipos encontrados en ' + ip + ' : %i \n' %  contador)
    return True

def mensaje(texto, cabecera, tipo):
    dialog = libreria.Mensaje(texto, cabecera, tipo)
    dialog.run()
    dialog.destroy()


def validar_tecnico(entry_tecnico,entry_password_tecnico):
    try:
        tecnico = entry_tecnico.get_text()
        tecnico = tecnico.split("@")[0]
        password_tecnico = entry_password_tecnico.get_text()
        validar_tecnico = subprocess.check_output (['/usr/share/grx/ldap/validar_tecnico.sh',tecnico, password_tecnico])
    except:
        if os.access('/usr/share/grx/ldap/validar_tecnico.sh', os.X_OK):
            mensaje ("         No se ha podido validar al tecnico en el dominio.\n               Compruebe la clave o la conexion de red. \n Las funciones de busqueda de usuarios no funcionaran.\n--------------------------------------------------------------------------------------------\n     Puede volver a validarse en cualquier momento\n pulsando sobre el boton kerberos en el apartado del tecnico","Atencion",atencion)
        else:
            mensaje("Los archivos de busqueda de ldap no son ejecutables\nSe le va a pedir la clave para realizar los cambios necesarios\nEn caso contrario no podra realizar busquedas ldap","Atencion",atencion)
            os.system("gksudo chmod 755 /usr/share/grx/ldap/*")

def lee_configuracion():
    ruta=os.path.expanduser('~')+'/.grx/asistencia.ini'
    if os.path.isfile(ruta):
        try:
            config = ConfigObj(ruta)
            buffer_entry_ip.set_text(config['IP'], -1)
            buffer_entry_usuario.set_text(config['USUARIO'], -1)
            buffer_entry_tecnico.set_text(config['TECNICO'], -1)
            buffer_entry_password_tecnico.set_text(config['PASSWORD_TECNICO'], -1)
            buffer_entry_server.set_text(config['SERVIDOR'], -1)
            buffer_entry_password.set_text(config['PASSWORD'], -1)
            buffer_entry_puerto.set_text(config['PUERTO'], -1)
            buffer_entry_clave_cifrado.set_text(config['CLAVE_CIFRADO'], -1)
            buffer_entry_clave_remoto.set_text(config['CLAVE_REMOTO'], -1)
            geometria = config['GEOMETRIA']
            if geometria == "":
                geometria = "1200x800"
            buffer_entry_geometria.set_text (geometria, -1)
            if config['FREERDP'] == "False":
                radio_freerdp.set_active(False)
            else:
                radio_freerdp.set_active(True)

#	     color_usuarios=config['COLOR_USUARIOS']
#	     color_soporte=config['COLOR_SOPORTE']
#	     rgba_usuarios = Gdk.RGBA.from_color(color_usuarios)
#	     rgba_soporte = Gdk.RGBA.from_color(color_soporte)
#	     Box_usuarios.override_background_color(0, rgba_usuarios)
#	     Box_soporte.override_background_color(0, rgba_soporte)

        except:
            print("archivo de configuracion erroneo")

def graba_configuracion(self,*args):
    ruta = os.path.expanduser('~') + '/.grx/'
    fichero = ruta + 'asistencia.ini'
    if not os.path.exists(ruta):
        os.mkdir(ruta, 0700)
    config = ConfigObj()
    config.filename = fichero
    config['IP'] = buffer_entry_ip.get_text()
    config['USUARIO'] = buffer_entry_usuario.get_text()
    config['PASSWORD'] = buffer_entry_password.get_text()
    config['PUERTO'] = buffer_entry_puerto.get_text()
    config['TECNICO'] = buffer_entry_tecnico.get_text()
    config['PASSWORD_TECNICO'] = buffer_entry_password_tecnico.get_text()
    config['SERVIDOR'] = buffer_entry_server.get_text()
    config['GEOMETRIA'] = buffer_entry_geometria.get_text()
    config['CLAVE_CIFRADO'] = buffer_entry_clave_cifrado.get_text()
    config['CLAVE_REMOTO'] = buffer_entry_clave_remoto.get_text()
    config['FREERDP'] = radio_freerdp.get_active()
  #  tmp_color_usuarios=Btn_color.get_color()
  #  tmp_color_soporte= Btn_color2.get_color()
  #  config['COLOR_SOPORTE'] = Gdk.RGBA.from_color(tmp_color_soporte)
  #  config['COLOR_USUARIOS'] =  Gdk.RGBA.from_color(tmp_color_usuarios)
    config.write()
def limpiar(self,*args):
    os.system('sudo /usr/bin/grx-asistencia-limpiar.sh')

if __name__ == '__main__':
    builder = Gtk.Builder()
    builder.add_from_file("/usr/share/grx/glade/asistencia.glade")
    builder.connect_signals(Handler())
    window = builder.get_object("window1")
    window.set_default_size(1024,768)

# Inicializa variables
    notebook = builder.get_object("notebook1")
    entry_ip = builder.get_object("entry_ip")
    entry_usuario = builder.get_object("entry_usuario")
    entry_puerto = builder.get_object("entry_puerto")
    entry_password = builder.get_object("entry_password")
    entry_tecnico = builder.get_object("entry_tecnico")
    entry_password_tecnico = builder.get_object("entry_password_tecnico")
    entry_server = builder.get_object("entry_server")
    entry_estado = builder.get_object("entry_estado")
    entry_caduca = builder.get_object("entry_caduca")
    buffer_entry_ip = builder.get_object("buffer_entry_ip")
    buffer_entry_usuario = builder.get_object("buffer_entry_usuario")
    buffer_entry_password = builder.get_object("buffer_entry_password")
    buffer_entry_password_tecnico = builder.get_object("buffer_entry_password_tecnico")
    buffer_entry_server = builder.get_object("buffer_entry_server")
    buffer_entry_tecnico = builder.get_object("buffer_entry_tecnico")
    buffer_entry_puerto = builder.get_object("buffer_entry_puerto")
    buffer_entry_geometria = builder.get_object("buffer_entry_geometria")
    buffer_entry_clave_cifrado = builder.get_object("buffer_entry_clave_cifrado")
    buffer_entry_clave_remoto = builder.get_object("buffer_entry_clave_remoto")
    Entry_glpi_password = builder.get_object("Entry_glpi_password")
    entry_correo = builder.get_object("entry_correo")
    entry_correo.connect("icon-press",lambda correo, event:on_entry_correo_icon_press(),'')
    entry_sedes = builder.get_object("entry_sedes")
    entry_busca_usuario = builder.get_object("entry_busca_usuario")
    entry_correo_creada = builder.get_object("entry_correo_creada")
    entry_busca_nombre = builder.get_object("entry_busca_nombre")
    entry_clave_cifrado = builder.get_object("entry_clave_cifrado")
    entry_clave_remoto = builder.get_object("entry_clave_remoto")
    entry_ultimo_cambio_clave = builder.get_object("entry_ultimo_cambio_clave")
    entry_clave_caduca = builder.get_object("entry_clave_caduca")
    entry_intentos = builder.get_object("entry_intentos")
    entry_cambio_clave = builder.get_object("entry_cambio_clave")
    entry_tlf = builder.get_object("entry_tlf")
    entry_ext = builder.get_object("entry_ext")
    entry_direccion = builder.get_object("entry_direccion")
    entry_creada = builder.get_object("entry_creada")
    entry_telefono = builder.get_object("entry_telefono")
    entry_centro = builder.get_object("entry_centro")
    entry_tlf_centro = builder.get_object("entry_tlf_centro")
    entry_numero_logon = builder.get_object("entry_numero_logon")
    entry_ultimo_login = builder.get_object("entry_ultimo_login")
    entry_geometria = builder.get_object("entry_geometria")
    entry_ultima_modificacion = builder.get_object("entry_ultima_modificacion")
    entry_mapa = builder.get_object("entry_mapa")
    radio_freerdp = builder.get_object("radio_freerdp")
    Btn_usuario = builder.get_object("Btn_usuario")
    checkwin = builder.get_object("checkwin")
    checkrouter = builder.get_object("checkrouter")
    checkimpre = builder.get_object("checkimpre")
    checklinux = builder.get_object("checklinux")
    listado_sedes = crea_lista()
    completion = Gtk.EntryCompletion()
    completion.set_model(listado_sedes)
    completion.set_text_column(0)
    entry_sedes.set_completion(completion)
    Btn_color = builder.get_object("Btn_color")
    Btn_color2 = builder.get_object("Btn_color2")
    Box_soporte = builder.get_object("Box_soporte")
    Box_usuarios = builder.get_object("Box_usuarios")
    entry_ip.connect('changed', lambda entry, event: ip_valida(entry_ip.get_text()), '')
    window.connect('delete-event', lambda window, event: onSalir(''))

    lee_configuracion()
    validar_tecnico(entry_tecnico, entry_password_tecnico)

    window.show_all()
    Gtk.main()


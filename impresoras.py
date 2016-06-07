from gi.repository import Gtk, WebKit
from gi.repository import Soup
import os,tablabel

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

class Impresoras(Gtk.Grid):
    def __init__(self,ip):
        Gtk.Grid.__init__(self, row_spacing=20, column_spacing=20)
        builder = Gtk.Builder()
        builder.add_from_file("/usr/share/grx/glade/impresora.glade")
	box_impresora = builder.get_object("box_impresora")
	notebook = builder.get_object("notebook_impresora")

	Btn_web = builder.get_object("Btn_web")
	Btn_web.connect("clicked", self.on_Btn_web_clicked,ip)

	Btn_impre = builder.get_object("Btn_impre")
	Btn_impre.connect("clicked", self.on_Btn_impre_clicked,ip,notebook)

        self.add(box_impresora)

    def mensaje(self,texto):
        dialog = Mensaje(texto)
	dialog.run()
        dialog.destroy()

    def on_Btn_web_clicked(self, widget, ip):
        try:
	        os.system("xdg-open http://"+ip+" &")
	except:
        
		self.mensaje("No ha sido posible abrir la pagina web")

    def on_Btn_impre_clicked(self, widget, ip,notebook):

	scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
	page = WebKit.WebView()
	page.set_border_width(10)
	#proxy_uri = Soup.URI.new("http://proxy:8080")
	#session = WebKit.get_default_session()
	#session.set_property("proxy-uri",proxy_uri)
    	page.open("http://"+ip)  
	scrolledwindow.add(page)
        try:
		tab_label = tablabel.TabLabel("web "+ ip,Gtk.Image.new_from_file("/usr/share/grx/icons/info.png"))
		tab_label.connect("close-clicked", tablabel.on_close_clicked, notebook, page)
		notebook.append_page(scrolledwindow,tab_label)
		self.show_all()
	except:
		self.mensaje('No se ha podido abrir la web de la impresora')	
	


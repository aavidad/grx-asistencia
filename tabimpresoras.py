from gi.repository import Gtk, GObject

class BtnImpre(Gtk.Button):
    __gsignals__ = {
        "button-clicked": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    def __init__(self, label_text,icon):
        Gtk.Button.__init__(self)
        # click button
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NORMAL)
        button.set_focus_on_click(False)
        button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
        button.connect("button-clicked", self.button_clicked)
        data =  ".button {\n" \
                "-GtkButton-default-border : 0px;\n" \
                "-GtkButton-default-outside-border : 0px;\n" \
                "-GtkButton-inner-border: 0px;\n" \
                "-GtkWidget-focus-line-width : 0px;\n" \
                "-GtkWidget-focus-padding : 0px;\n" \
                "padding: 0px;\n" \
                "}"
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(data))
        # 600 = GTK_STYLE_PROVIDER_PRIORITY_APPLICATION
        button.get_style_context().add_provider(provider, 600)
        
        self.show_all()
   
    def button_clicked(self, buttonbox, data=None):
        self.emit("button-clicked")
 

def on_button_clicked(self, t):
    """ Callback for the "close-clicked" emitted by custom TabLabel widget. """
    self.BtnImpre.delete()
 

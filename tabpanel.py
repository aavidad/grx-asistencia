from gi.repository import Gtk, GObject

class TabLabel(Gtk.Box):
    __gsignals__ = {
        "close-clicked": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    def __init__(self, label_text):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(5) # spacing: [icon|5px|label|5px|close]  
        
        # icon
        icon = Gtk.Image.new_from_stock(Gtk.STOCK_FILE, Gtk.IconSize.MENU)
        self.pack_start(icon, False, False, 0)
        
        # label 
        label = Gtk.Label(label_text)
        self.pack_start(label, True, True, 0)
        
        # close button
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
        button.connect("clicked", self.button_clicked)
        data =  ".button {\n" \
                "-GtkButton-default-border : 0px;\n" \
                "-GtkButton-default-outside-border : 0px;\n" \
                "-GtkButton-inner-border: 0px;\n" \
                "-GtkWidget-focus-line-width : 0px;\n" \
                "-GtkWidget-focus-padding : 0px;\n" \
                "padding: 0px;\n" \
                "}"
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(data, "ascii"))
        # 600 = GTK_STYLE_PROVIDER_PRIORITY_APPLICATION
        button.get_style_context().add_provider(provider, 600) 
        self.pack_start(button, False, False, 0)
        
        self.show_all()
    
    def button_clicked(self, button, data=None):
        self.emit("close-clicked")

def on_close_clicked(tab_label, notebook, tab_widget):
    """ Callback for the "close-clicked" emitted by custom TabLabel widget. """
    notebook.remove_page(notebook.page_num(tab_widget))

if __name__ == "__main__":
    notebook = Gtk.Notebook()
    for x in range(1, 4):
        tab_widget = Gtk.TextView()
        tab_label = TabLabel("Page %d" % x)
        tab_label.connect("close-clicked", on_close_clicked, notebook, tab_widget)
        notebook.append_page(tab_widget, tab_label)
          
    window = Gtk.Window(title="Gtk.Notebook Close Buttons")
    window.set_default_size(350, 200)
    window.connect("destroy", lambda w: Gtk.main_quit())
    window.add(notebook)
    window.show_all()

    Gtk.main()

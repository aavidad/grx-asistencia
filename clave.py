from gi.repository import Gtk


def get_user_pw(parent, message, title=''):
    # Returns user input as a string or None
    # If user does not input text it returns None, NOT AN EMPTY STRING.
    dialogWindow = Gtk.MessageDialog(parent,
                          Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                          Gtk.MessageType.QUESTION,
                          Gtk.ButtonsType.OK_CANCEL,
                          message)

    dialogWindow.set_title(title)

    dialogBox = dialogWindow.get_content_area()
    userEntry = Gtk.Entry()
    userEntry.set_visibility(False)
    userEntry.set_invisible_char("*")
    userEntry.set_size_request(250, 0)
    dialogBox.pack_end(userEntry, False, False, 0)

    dialogWindow.show_all()
    response = dialogWindow.run()
    text = userEntry.get_text()
    dialogWindow.destroy()
    if (response == Gtk.ResponseType.OK) and (text != ''):
        return text
    else:
        return None


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="MyWindowTitle")
        userPassword = get_user_pw(self, "Please enter your password", "Password")


if __name__ == '__main__':

    main = MainWindow()
    main.show_all()
    Gtk.main()


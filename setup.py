from distutils.core import setup
import glob
lista_auxiliar=glob.glob("./auxiliar/*")
lista_icons=glob.glob("./icons/*")
lista_ldap=glob.glob("./ldap/*")
lista_glade=glob.glob("./glade/*")
lista_hp=glob.glob("./hp/*")
lista_scripts=glob.glob("./scripts/*")
lista_modulos=glob.glob("*.py")
lista_modulos = [w.replace('.py', '') for w in lista_modulos]
setup(name="grx-asistencia",
          version="0.2.25",
          description="Aplicacion para la Asistencia de los equipos Linux",
          author="Alberto Avidad Fernandez",
          author_email="avidad@dipgra.es",
          url="http://incidencias.dipgra.es/",
          license="GPL",
          scripts=lista_scripts,
	  py_modules=lista_modulos,
	  data_files=[('/usr/share/grx/icons', lista_icons), ('/usr/share/grx/ldap',lista_ldap),('/usr/share/grx/glade',lista_glade),('/usr/share/grx/auxiliar',lista_auxiliar),('/usr/share/applications', ['./grx-asistencia.desktop']),('/usr/share/icons/hicolor/22x22/apps', ['./iconos/icons/hicolor/24x24/apps/grx-asistencia.png']), ('/usr/share/icons/hicolor/24x24/apps', ['./iconos/icons/hicolor/24x24/apps/grx-asistencia.png']),('/usr/share/icons/hicolor/48x48/apps', ['./iconos/icons/hicolor/48x48/apps/grx-asistencia.png']),('/usr/share/icons/hicolor/64x64/apps', ['./iconos/icons/hicolor/64x64/apps/grx-asistencia.png']), ('/usr/share/grx/hp',lista_hp) ])


import sys
from PyQt4 import QtGui,QtCore, uic

class VentanaCliente(QtGui.QMainWindow):
    def __init__(self):
        '''
        Constructor de la ventana principal del cliente, misma
        que se encarga de estar haciendo peticiones al servidor
        xmlrpc para conocer el estado actual del juego de snake.
        '''
        super(VentanaCliente, self).__init__()
        uic.loadUi('cliente.ui', self) #Cargamos la interfaz creada con QtDesigner.
        self.expandir_cuadros_tabla() #Hacemos que las columnas y filas siempre llenen todo el widget y sean proporcionales en cuanto a tamaño.
        self.show() #Mostrando la ventana y todo su contenido.

    def expandir_cuadros_tabla(self):
        '''
        Función encargada de lograr que las celdas del TableWidget de expandan
        dinámicamente para ajustarse a las dimensiones del mismo sin importar 
        que cambien las dimensiones de la ventana princiapal del cliente.
        Se especifica --para las filas y columnas-- que pueden expandirse para llenar
        el espacio del tableWidget y ésto lo hacen de forma uniforme considerando el tamaño
        total y el número de celdas para ajustar su tamaño. El tamaño mínimo
        de los encabezados respectivos fue establecido para que tuviera como mínimo un pixel.
        '''
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv) #Creando la aplicación.
    ventana = VentanaCliente() #Ya con la aplicación creada, podemos crear un objeto del tipo ventana principal de tipo cliente.
    sys.exit(app.exec_()) #Y continúa la ejecución en tanto que no se considere lo contrario.
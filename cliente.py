import sys
from PyQt4 import QtGui,QtCore, uic
from xmlrpc.client import ServerProxy #Para poder comunicarse con el servidor.

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
        self.pushButton.clicked.connect(self.manejo_servidor) #Asociando los botones con las funciones.
        self.pushButton_2.clicked.connect(self.participar_juego)
        self.pushButton_2.clicked.connect(self.reiniciar)
        self.id_usuario = 0 #Tenemos una variable para el id del usuario que luego se verá modificada.
        self.direccion = 2 #Y una dirección por defecto en la que se moverá su serpiente.
        self.label_5.setStyleSheet("QLabel { color : #F4D442; }")
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection) #Para que no se resalten las celdas al darles click.
        self.creado_usuario = False #Bandera que indica si el usuario ya está jugando.
        self.doomed = False #Y si su serpiente ya murió.
        self.intervalo_server = 0 #El intervalo (ms) en el que se está actualizando el servidor-
        self.timer= QtCore.QTimer(self)
        self.timer.timeout.connect(self.poner_tabla_bien) #Conectando el QTimer con las funciones que se tienen que esar constantemente ejecutando.
        self.timer.timeout.connect(self.comenzar_juego)
        self.timer.timeout.connect(self.actualizar_timer_interval)
        self.timer.timeout.connect(self.actualizar_highscore)
        self.timer.start(self.intervalo_server)
        self.show() #Mostrando la ventana y todo su contenido.
        self.server = None

    def poner_tabla_bien(self):
        '''
        Se encarga de que el número de filas y columnas que hay en la tabla 
        del servidor sean exactamente las mismas que las que se despliegan en 
        la tabla del UI del cliente.
        '''
        if self.creado_usuario:
            #La información se obtiene del diccionario que devuelve la función del servidor.
            game = self.server.estado_del_juego()
            self.tableWidget.setRowCount(game["tamY"])
            self.tableWidget.setColumnCount(game["tamX"])
            self.llenar_tabla() #Se crean los items para poder colorearlos en la tabla.
    
    def actualizar_highscore(self):
        '''
        Constantemente está viendo cuál es el highscore del juego --
        la serpiente que más ha comido-- para poder mostrarlo en el lcdNumber
        del UI. Para poder conocer el highscore del juego, tuve que registrar otra
        función al servidor dado que esta información ya era conocida por éste.
        '''
        if self.creado_usuario:
            high = self.server.highscore_game()
            self.lcdNumber.display(high) #Mostrando el highscore.


    def llenar_tabla(self):
        '''
        Se encaga de colorear adecuadamente la tabla, poniendo la comida 
        en las celdas que debe ir y pintando las demás del color del fondo.
        '''
        guisantes = self.server.posiciones_de_guisantes() #Tuve que registrar otra función al servidor para poder regresar este diccionario de posiciones que ya tenía en servidor.py.
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QtGui.QTableWidgetItem()) #Si le corresponde la celda a un guisante,
                if [i,j] in guisantes:  
                    self.tableWidget.item(i,j).setBackground(QtGui.QColor(64,244,167)) #Se pone del color verde.
                else:
                    self.tableWidget.item(i,j).setBackground(QtGui.QColor(82,135,135)) #Si no, es parte del fondo y se pinta del otro color.

    def comenzar_juego(self):
        '''
        Se encarga de estar actualizando la partida.
        '''
        if self.creado_usuario:
            if self.ha_muerto():
                #Muestra un mensaje si la serpiente del cliente ya no existe (chocó consigo misma o con otra víbora).
                self.lineEdit.setText("¡MORISTE!")
            self.llenar_tabla() #Se tiene que estar llenando la tabla como debe ir.
            self.tableWidget.installEventFilter(self)  #Asociando la tabla con el eventfilter para poder detectar las flechas del teclado.
            diccionario = self.server.estado_del_juego()
            lista_viboras = diccionario["viboras"]
            for vibora in lista_viboras:
                lista_camino = vibora["camino"]
                colores = vibora["color"]
                self.dibuja_vibora(lista_camino, colores) #Se dibujan todas las víboras a partir del "camino" de las mismas.
    
    def actualizar_timer_interval(self):
        '''
        En caso de que el juego haya comenzado y se modifique la espera en el servidor,
        entonces tenemos que modificar el intervalo del timer del cliente
        para no estar preguntando más de lo debido por el estado del juego ya que 
        es innecesario.
        '''
        if self.creado_usuario:
            diccionario = self.server.estado_del_juego()
            intervalo = diccionario["espera"] #Se ve de cuánto es la espera del servidor.
            if self.intervalo_server != intervalo:
                self.intervalo_server = intervalo
                self.timer.setInterval(self.intervalo_server) #Y con base en ello se puede modificar, en caso de ser necesario, el intervalo del QTimer del cliente.

    '''
    def dibujar_guisantes(self):
        lista_guisantes = self.server.posiciones_de_guisantes()
        for x in lista_guisantes:
            print(x[0], x[1])
            self.tableWidget.item(x[0],x[1]).setBackground(QtGui.QColor(244,212,66)) #Finalmente, esta celda se pinta de un color distinto.
            '''

    def dibuja_vibora(self, lista_camino, colores):
        '''
        Se encarga de dibujar una víbora en la tabla del cliente a través de 
        su color (RGB) y la lista de tuplas que representa las celdas que ocupa en 
        cada momento.
        '''
        for tupla in lista_camino:
            self.tableWidget.item(tupla[0], tupla[1]).setBackground(QtGui.QColor(colores['r'], colores['g'], colores['b']))

    def manejo_servidor(self):
        '''
        Función que debuggea la conexión con el servidor a través del botón de 
        Ping.
        '''
        self.pushButton.setText("Pinging...") #Temporalmente se cambia el texto del botón.
        try:
            self.crea_servidor() #Intenta crear el servidor.
            pong = self.server.ping() #Mandamos llamar a la función registrada en el servidor.
            self.pushButton.setText("¡Pong!") #Y si todo funciona óptimamente, el texto del botón cambia.
        except: #Si no se puede crear el servidor, el texto del botón debe ser otro.
            self.pushButton.setText("No PONG :(")

    def crea_servidor(self):
        '''
        Función que crea un servidor a partir de los valores que están en el LineEdit
        y en el SpinBox del UI.
        '''
        self.url = self.lineEdit_3.text() #Se extraen estos valores de la interfaz.
        self.port = self.spinBox.value() 
        self.direccion = "http://" + self.url + ":" + str(self.port) #Se almacena la dirección del servidor.
        self.server = ServerProxy(self.direccion) #Y finalmente se manda crear el servidor con esta dirección.
 
    def participar_juego(self):
        '''
        Función que hace inicializa el juego para el cliente cuando éste presiona el botón de 
        Participar.
        '''
        try:
            self.crea_servidor() #Se crea el servidor.
            informacion = self.server.yo_juego()
            self.lineEdit.setText(informacion["id"])
            self.id_usuario = informacion["id"]
            self.color = informacion["color"]
            self.red = self.color["r"]
            self.green = self.color["g"]
            self.blue = self.color["b"]
            #Se coloca el id del jugador y el color de la serpiente en los campos adecuados de la UI.
            self.lineEdit_2.setText("R:" + str(self.red) + " G:" + str(self.green) + " B:" + str(self.blue))
            #Para hacer más fácil el reconocimiento del color del jugador, el fondo del LineEdit del color se cambia justo a ese color.
            self.lineEdit_2.setStyleSheet('QLineEdit {background-color: rgb('+str(self.red)+','+ str(self.green) + ',' + str(self.blue)+');}')
            self.creado_usuario = True #El usuario ya fue creado-
        except: #Si ocurren anomalías, se le notifica al usuario.
            self.lineEdit.setText("Conexión fallida: servidor inalcanzable.")
            self.lineEdit_2.setText("Verifica que el URL y puerto sean correctos.")


    def ha_muerto(self):
        '''
        Verifica si la serpiente del jugador ya murió, ya sea porque 
        chocó consigo misma o con alguna otra serpiente. 
        '''
        diccionario = self.server.estado_del_juego()
        lista_serpientes = diccionario["viboras"]
        #Lo que se hace es comparar el id del cliente con el de todas las serpientes del juego para ver si coincide con alguna.
        for vibora in lista_serpientes:
            if vibora["id"] == self.id_usuario:
                return False
        self.doomed = True
        return True #Si no coincide con ninguna, es porque su serpiente ya no existe, i.e., murió.

    def reiniciar(self):
        '''
        Función que se encarga de reiniciar el juego para el cliente, esto es, 
        crear una nueva serpiente asociada a él cuando ya había muerto 
        para seguir jugando.
        '''
        if self.doomed: 
            self.doomed = False #Decimos que el jugador no ha muerto.
            self.lineEdit.setText("") #Reiniciamos el texto de los LineEdits.
            self.lineEdit.setText("")
            self.participar_juego() #Creamos una nueva serpiente para el jugador.
            self.timer.start() #Iniciamos el timer.
            self.comenzar_juego() #Y comenzamos el juego llenando la tabla con la nueva serpiente, etc.


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

    def eventFilter(self, source, event):
        '''
        Permite detectar si el cliente presiona las teclas de flechas para 
        intentar mover a su víbora. Este escucha depende de la flecha que se presione
        para poder validar el movimiento de la serpiente como se hizo en el caso 
        del servidor, esto es, por ejemplo una serpiente no puede moverse hacia arriba
        si actualmente se mueve hacia abajo.
        '''
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.tableWidget): 
                key = event.key() 
                if (key == QtCore.Qt.Key_Up and
                    source is self.tableWidget):
                    if self.direccion != 2:
                        self.direccion = 0
                elif (key == QtCore.Qt.Key_Down and
                    source is self.tableWidget):
                    if self.direccion != 0:
                        self.direccion = 2
                elif (key == QtCore.Qt.Key_Right and
                    source is self.tableWidget):
                    if self.direccion != 3:
                        self.direccion = 1
                elif (key == QtCore.Qt.Key_Left and
                    source is self.tableWidget):
                    if self.direccion != 1:
                        self.direccion = 3
                #Al final de todo, solamente tenemos que mover a la serpiente del usuario a través de su identificador empleando la función registrada en el servidor.
                self.server.cambia_direccion(self.id_usuario, self.direccion)
        return QtGui.QMainWindow.eventFilter(self, source, event) #Requiere un regreso la función.

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv) #Creando la aplicación.
    ventana = VentanaCliente() #Ya con la aplicación creada, podemos crear un objeto del tipo ventana principal de tipo cliente.
    sys.exit(app.exec_()) #Y continúa la ejecución en tanto que no se considere lo contrario.

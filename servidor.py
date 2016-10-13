import sys
from PyQt4 import QtGui, QtCore, uic
from random import randint #Para poder generar la celda en donde aparece la comida.

class Serpiente():
    '''
    Permite modelar objetos que serán controlados por los usuarios del programa. 
    Se crea una serpiente con un color definido a partir de los valores que son pasados
    como parámetros. Falta todavía implementar que la serpiente se cree en un lugar donde
    no haya ya otra, pero por ahora no nos preocupa porque es un juego de un solo jugador.
    '''
    def __init__(self, red, green, blue):
        self.color = (red, green, blue)
        self.casillas = [[3,0],[4,0],[5,0], [6,0], [7,0], [8,0], [9,0],[10,0], [11,0]] #La serpiente se representa como una lista de listas, donde cada una de las sublistas representa una celda que ocupa en la tabla.
        self.tam = len(self.casillas)
        self.direccion = "Abajo" #Bandera que servirá para poder dibujar correctamente a la serpiente y validar ciertos movimientos del usuario.
        self.veces_ha_comido = 0

class VentanaServidor(QtGui.QMainWindow):

    def __init__(self):
        '''
        Constructor de la ventana principal del servidor mismo que se 
        encarga de llevar a cabo la acción del juego y mandar el estado del mismo
        a la ventana del cliente.
        '''
        super(VentanaServidor, self).__init__() #Se crea la ventana del servidor.
        uic.loadUi('servidor.ui', self) #Se carga el archivo hecho en QtDesigner.
        self.label_8.setStyleSheet("QLabel { color : #f442b0; }")
        self.pushButton_3.hide() #Este botón solamente aparece hasta que se comienza el juego.
        self.juego_empezado = False #Un par de banderas para conocer el estado del juego.
        self.juego_pausado = False
        self.timer = None #Se especifica que la ventana tendrá contadores asociados; por ahora no han sido creados.
        self.timer_comida = None
        self.timer_guisantes = None 
        self.highscore = 0
        self.serpientes_juego = [] #Lista que contendrá todas las serpientes.
        self.guisantes = [] #Lista que contiene las posiciones de la comida de las serpientes.
        self.expandir_cuadros_tabla() #Especificando que las celdas tienen que cubrir el tamaño del QTableWidget.
        self.llenar_tabla() #Se crean Items en todas las celdas de la tabla para poder pintarlos a nuestra conveniencia; inicialmente se pintado del mismo color.
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection) #Para que no se resalten las celdas al darles click.
        self.spinBox_2.valueChanged.connect(self.actualizar_tabla) #Asociamos los spinboxes del número de columnas y filas a la función que actualiza el tamaño de la tabla.
        self.spinBox_3.valueChanged.connect(self.actualizar_tabla)
        self.spinBox.valueChanged.connect(self.actualizar_timer) #Y el spinbox que determina la velocidad de actualización de las serpientes también lo asociamos con la función que actualiza el intervalo del timer.
        self.pushButton_2.clicked.connect(self.comenzar_juego) #Finalmente, los botones de la parte inferior se asocian con las funciones que modifican el estado del juego.
        self.pushButton_3.clicked.connect(self.terminar_juego)
        self.show() #Se muestra la ventana.

    def comenzar_juego(self):
        '''
        Marca el estado del juego como iniciado; crea una serpiente
        '''
        if not self.juego_empezado:
            self.pushButton_3.show() #Se muestra el botón que permitirá terminar el juego después.
            serpiente_1 = Serpiente(181,201,70)  #Se crea la serpiente y se añade a las del juego.
            self.serpientes_juego.append(serpiente_1)
            self.pushButton_2.setText("Pausar el Juego") #Cambia el texto del botón de inicio.
            self.dibujar_serpientes()
            self.timer = QtCore.QTimer(self) #Se crean los tres contadores. El primero es de la actualización de las serpientes, el segundo de la aparición de la comida, y el tercero de la verificación de si la serpiente choca.
            self.timer_guisantes = QtCore.QTimer(self)
            self.timer_comida = QtCore.QTimer(self)
            self.timer.timeout.connect(self.mover_serpientes) #Para cada contador se le asocia la función correspondiente.
            self.timer.start(200) #y se especifica su intervalo.
            self.timer_comida.timeout.connect(self.serpiente_come)
            self.timer_comida.start(200)
            self.timer_guisantes.timeout.connect(self.crear_guisante) 
            self.timer_guisantes.start(5000) 
            self.tableWidget.installEventFilter(self) #Por medio de esta asociación de un escucha a la tabla, ya no es necesario hacer sublassing del QTableWidget y promoción en QtDesigner.
            self.juego_empezado = True #E indicamos que el juego ha comenzado para futuras modificaciones del estado.
        elif self.juego_empezado and not self.juego_pausado: #Si volvemos a presionar el botón:
            self.timer.stop() #Se tiene que pausar el juego, por lo que paramos los contadores.
            self.timer_guisantes.stop()
            self.timer_comida.stop()
            self.juego_pausado = True #Decimos que el juego está en pausa.
            self.pushButton_2.setText("Reanudar el Juego") #Y se moficia el texto del botón para indicar que si se clickea de nuevo, el juego puede reanudarse.
        elif self.juego_pausado: #Si se clickea por tercera ocasión:
            self.timer.start() #Se reanuda el juego, por lo que se reanudan los contadores del juego.
            self.timer_guisantes.start()
            self.timer_comida.start()
            self.juego_pausado = False #Decimos que el juego ya no está pausado.
            self.pushButton_2.setText("Pausar el Juego") #Y nuevamente se modifica el texto del botón para indicar que luego podrá ser pausado de nuevo cuando así de quiera.

    def terminar_juego(self):
        '''
        Función asociada al botón 'Terminar el Juego' que permite
        terminar aparentemente la ejecución del programa al borrar a todas
        las serpientes y colorear uniformemente el tablero.
        '''
        self.serpientes_juego = [] #Las listas del juego se vacían.
        self.guisantes = []
        self.highscore = 0
        self.lcdNumber.display(0)
        self.timer_comida.stop() #Los contadores son detenidos.
        self.timer_guisantes.stop()
        self.timer.stop()
        self.juego_empezado = False #Decimos que el juego no ha empezado, para dar la libertad de comenzarlo de nuevo si se desea.
        self.pushButton_3.hide() #Luego de ser picado, este botón desaparece de nuevo, pues no se puede terminar lo que ya terminó.
        self.pushButton_2.setText("Inicia Juego") #Y de nuevo el texto del otro botón cambia para dar una pista al usuario de lo que pasa si se clickea de nuevo.
        self.llenar_tabla() #Coloreando la tabla uniformemente: borra rastros de las serpientes y guisantes.

    def actualizar_timer(self):
        '''
        En caso de que el valor del spinbox se vea modificado, esta función 
        se encarga de actualizar el intervalo del timer princial del juego, 
        aquél que está encargado de qué tan seguido se actualiza el movimiento de 
        las serpientes.
        '''
        valor = self.spinBox.value()
        self.timer.setInterval(valor)

    def eventFilter(self, source, event):
        '''
        Nos permite añadir una nueva funcionalidad del QTableWidget para poder
        escuchar eventos relacionados con que el usuario presiona las teclas de flechas, 
        sin necesidad de tener que definir una subclase que herede de QTableWidget para no 
        tener que hacer promociones en QtDesigner y crear instancias de clases hijas 
        en el programa.
        '''
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.tableWidget): #Verificamos que el evento sea de presionado de tecla y el llamado provenga de la tabla.
                key = event.key() #Vemos qué tecla fue.
                '''
                En cada caso, se verifica de qué tecla se trata. Luego se procede a verificar
                que el movimiento sea válido, e.g., que el usuario no pretenda mover a la 
                serpiente hacia arriba si actualmente va hacia abajo (se comería: Ouroboros).
                En caso de que sea válido el movimiento, solamente se cambia el atributo movmiento de 
                las serpientes del juego. Otra función es la encargada de efectual el mismo.
                '''
                if (key == QtCore.Qt.Key_Up and
                    source is self.tableWidget):
                    for serpiente in self.serpientes_juego:
                        if serpiente.direccion is not "Abajo":
                            serpiente.direccion = "Arriba"
                elif (key == QtCore.Qt.Key_Down and
                    source is self.tableWidget):
                    for serpiente in self.serpientes_juego:
                        if serpiente.direccion is not "Arriba":
                            serpiente.direccion = "Abajo"
                elif (key == QtCore.Qt.Key_Right and
                    source is self.tableWidget):
                    for serpiente in self.serpientes_juego:
                        if serpiente.direccion is not "Izquierda":
                            serpiente.direccion = "Derecha"
                elif (key == QtCore.Qt.Key_Left and
                    source is self.tableWidget):
                    for serpiente in self.serpientes_juego:
                        if serpiente.direccion is not "Derecha":
                            serpiente.direccion = "Izquierda"
        return QtGui.QMainWindow.eventFilter(self, source, event) #Requiere un regreso la función.

    def dibujar_serpientes(self):
        '''
        Dibuja las serpientes en el tablero. Lo que se hace es iterar por cada sublista en el cuerpo de la serpiente
        para poder colorar los items de la tabla del color de la serpiente. 
        '''
        for serpiente in self.serpientes_juego:
            for seccion_corporal in serpiente.casillas:
                self.tableWidget.item(seccion_corporal[0], seccion_corporal[1]).setBackground(QtGui.QColor(serpiente.color[0], serpiente.color[1], serpiente.color[2]))
    
    def crear_guisante(self):
        '''
        Extra: 'Deposita' la comida de las serpientes en la tabla, verificando que la celda
        que va a simular la comida al ser pientad de un color distinto, sea válida, es decir, no
        se crear comida sobre las serpientes porque no sería justo.
        '''
        en_buena_posicion = False
        while not en_buena_posicion: #Se crean números aleatorios en tanto que no se halle una posición óptima.
            i = randint(0, self.tableWidget.rowCount()-1) 
            j = randint(0, self.tableWidget.columnCount()-1)
            for serpiente in self.serpientes_juego:
                if [i,j] in serpiente.casillas: #Si coincide con alguna parte de alguna serpiente, la posición no es válida.
                    break
            en_buena_posicion = True #Si sí, se saldrá del ciclo.
            self.guisantes.append([i,j]) #Y se añade la posición de esta comida a la lista de la comida del juego.
            self.tableWidget.item(i,j).setBackground(QtGui.QColor(66,244,167)) #Finalmente, esta celda se pinta de un color distinto.

    def serpiente_come(self):
        '''
        Verifica si la serpiente ha comido.
        '''
        for serpiente in self.serpientes_juego:
            for guisante in self.guisantes:
                #Si la cabeza de la serpiente coincide con la celda de comnida:
                if serpiente.casillas[-1][0] == guisante[0] and serpiente.casillas[-1][1] == guisante[1]:
                    self.label_7.setText("¡Yum!") #Se notifica al usuario que comión cambiando el texto de un label de la interfaz.
                    serpiente.veces_ha_comido += 1
                    if serpiente.veces_ha_comido > self.highscore:
                        self.highscore = serpiente.veces_ha_comido
                        self.lcdNumber.display(self.highscore)
                    self.label_7.setStyleSheet("QLabel { color : #42bcf4; }")
                    QtCore.QTimer.singleShot(2000, lambda: self.label_7.setText('')) #Después, el label retoma su valor de cadena vacía.
                    serpiente.casillas.append([guisante[0],guisante[1]]) #Se añade una nueva celda al cuerpo de la serpiente que comió.
                    self.guisantes.remove(guisante) #Y se borra el guisante de la lista de la comida disponible en tablero.
                    self.dibujar_serpientes() #Se vuelven a dubujar las serpientes en la tabla para actualizar su tamaño.
                    return True
        return False

    def ha_chocado_consigo(self, serpiente):
        '''
        Verifica constantemente --con ayuda del timer-- que la serpiente no choque con 
        partes de su propio cuerpo. La cebeza de la serpiente no se verifica, pues no puede
        chocar con esta parte.
        '''
        for seccion_corporal in serpiente.casillas[0:len(serpiente.casillas)-2]: 
            #Si la posición de la cabeza coincide con la de alguna otra parte de su cuerpo, quiere decir que al serpiente ha chocado.
            if serpiente.casillas[-1][0] == seccion_corporal[0] and serpiente.casillas[-1][1] == seccion_corporal[1]:
                self.label_7.setText("¡Moriste!") #Se indica al usuario que la serpiente murió, cambiando del texto del label.
                self.label_7.setStyleSheet("QLabel { color : #fc360a; }")
                QtCore.QTimer.singleShot(2000, lambda: self.label_7.setText('')) #Después, el label retoma su valor de cadena vacía.
                return True
        return False

    def mover_serpientes(self):
        '''
        Simula el movimiento de las serpientes del juego al ir pintando las celdas de acuerdo a la dirección
        actual de cada una de ellas. Las celdas que preceden a la cabeza constantemente están tomando la posición 
        que les seguía. En sí, la única parte de la serpiente que tiene que verificar a dónde tiene que moverse es 
        la cebza de la sepiente.
        '''
        for serpiente in self.serpientes_juego: #Tiene que mover a todas las serpientes.
            if self.ha_chocado_consigo(serpiente): #Si chocó la serpiente,
                self.serpientes_juego.remove(serpiente) #Se borra de la lista.
                self.llenar_tabla() #Se tiene que rellenar la tabla.
                r,g,b = randint(0,255),randint(0,255),randint(0,255) #Y se crea una nueva serpiente de un color generado aleatoriamente.
                serpiente_1 = Serpiente(r,g,b)
                self.serpientes_juego = [serpiente_1]
            self.tableWidget.item(serpiente.casillas[0][0],serpiente.casillas[0][1]).setBackground(QtGui.QColor(82,135,135))
            x = 0 #Variable que permite acceder a la siguiente sección coportal de la iteración actual.
            #Cada sección corporal de la serpiente adopta la posición previa de la parte corporal que le sigue, exceptuando su cabeza.
            for tupla in serpiente.casillas[0: len(serpiente.casillas)-1]:
                x += 1
                tupla[0] = serpiente.casillas[x][0]
                tupla[1] = serpiente.casillas[x][1]
            '''
            En cada posible movimiento se checa que la siguiente posición de la cabeza de la serpiente en la dirección en que 
            se está moviendo esté dentro del tablero; en caso de que no, únicamente se tiene que indicar que la cabeza de la serpiente
            tiene que 'salir' por el otro lado de la tabla y sus otras partes del cuerpo le seguirán.
            '''
            if serpiente.direccion is "Abajo":
                if serpiente.casillas[-1][0] + 1 < self.tableWidget.rowCount():
                    serpiente.casillas[-1][0] += 1
                else:
                    serpiente.casillas[-1][0] = 0
            if serpiente.direccion is "Derecha":
                if serpiente.casillas[-1][1] + 1 < self.tableWidget.columnCount():
                    serpiente.casillas[-1][1] += 1
                else:
                    serpiente.casillas[-1][1] = 0
            if serpiente.direccion is "Arriba":
                if serpiente.casillas[-1][0] != 0:
                    serpiente.casillas[-1][0] -= 1
                else:
                    serpiente.casillas[-1][0] = self.tableWidget.rowCount()-1
            if serpiente.direccion is "Izquierda":
                if serpiente.casillas[-1][1] != 0:
                    serpiente.casillas[-1][1] -= 1
                else:
                    serpiente.casillas[-1][1] = self.tableWidget.columnCount()-1
        self.dibujar_serpientes() #Se vuelven a dibujar las serpientes del juego.

    def llenar_tabla(self):
        '''
        Se encarga de crear un Item en cada celda de la tabla para que luego podamos 
        colorear las celdas de distinto color simulando el movimiento de las serpientes. 
        Inicialmente cada celda se pinta del mismo color.
        '''
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QtGui.QTableWidgetItem())
                self.tableWidget.item(i,j).setBackground(QtGui.QColor(82,135,135))

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

    def actualizar_tabla(self):
        '''
        Función que permite incrementar el número de filas y columnas de la tabla.
        '''
        num_filas = self.spinBox_3.value() #Extraemos los valores de los spinboxes.
        num_columnas = self.spinBox_2.value()
        self.tableWidget.setRowCount(num_filas)  #Y fijamos el número de columnas/celdas para adaptarse al ńuevo número.
        self.tableWidget.setColumnCount(num_columnas)
        self.llenar_tabla() #Cada vez que hacemos lo anterior, la nueva tabla se llena por completo del color adecuado para que sea uniforme.

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv) #Creando la aplicación.
    ventana = VentanaServidor() #Ya con la aplicación creada, podemos crear un objeto del tipo ventana principal de tipo cliente.
    sys.exit(app.exec_()) #Y continúa la ejecución en tanto que no se considere lo contrario.

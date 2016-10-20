# -*- coding: utf-8 -*-
import sys
from xmlrpc.server import SimpleXMLRPCServer #Implementar el servidor.
from PyQt4 import QtGui, QtCore, uic
from random import randint #Para poder generar la celda en donde aparece la comida.
import uuid #Crear un id único para cada víbora.

class Serpiente():
    '''
    Permite modelar objetos que serán controlados por los usuarios del programa. 
    Se crea una serpiente con un color definido a partir de los valores que son pasados
    como parámetros. Falta todavía implementar que la serpiente se cree en un lugar donde
    no haya ya otra, pero por ahora no nos preocupa porque es un juego de un solo jugador.
    '''
    def __init__(self):
        self.id = str(uuid.uuid4())[:8] #Solamente nos tomamos la primer partd del id porque son muy largos.
        red, green, blue = randint(0,255), randint(0,255), randint(0,255)
        self.color = {"r": red, "g": green, "b": blue} #El diccionario que necesitaremos más adelante.
        self.camino = [] #Esta será una lista de tuplas; como las tuplas no son mutables, tendremos que estar construyéndola siempre.
        self.casillas = [] #Esta será la lista de las partes del cuerpo de la serpiente.
        self.camino = []
        self.tam = len(self.casillas)
        self.direccion = "Abajo" #Bandera que servirá para poder dibujar correctamente a la serpiente y validar ciertos movimientos del usuario.
        self.veces_ha_comido = 0 #Se necesita para poder tener el highscore.

    def obtener_diccionario(self):
        '''
        Función que permite visualizar a una serpiente del juego
        a partir de sus características principales: color, identificador y 
        las casillas que ocupa.
        '''
        diccionario = dict()
        diccionario = {
            'id': self.id,
            'camino': self.camino, 
            'color': self.color
        }
        return diccionario #Será necesario para poder implementar la función que será llamada por el cliente.

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
        self.pushButton.clicked.connect(self.inicializar_servidor) #Se inicializa el servidor hasta que se oprime el botón.
        self.juego_empezado = False #Un par de banderas para conocer el estado del juego.
        self.juego_pausado = False
        self.timer = None #Se especifica que la ventana tendrá contadores asociados; por ahora no han sido creados.
        self.timer_comida = None
        self.timer_guisantes = None 
        self.timer_s = None
        self.timer_camino = None #Este timer estará actualizando la lista de tuplas de las serpientes del juego.
        self.highscore = 0
        self.serpientes_juego = [] #Lista que contendrá todas las serpientes.
        self.guisantes = [] #Lista que contiene las posiciones de la comida de las serpientes.
        self.expandir_cuadros_tabla() #Especificando que las celdas tienen que cubrir el tamaño del QTableWidget.
        self.llenar_tabla() #Se crean Items en todas las celdas de la tabla para poder pintarlos a nuestra conveniencia; inicialmente se pintado del mismo color.
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection) #Para que no se resalten las celdas al darles click.
        self.spinBox_2.valueChanged.connect(self.actualizar_tabla) #Asociamos los spinboxes del número de columnas y filas a la función que actualiza el tamaño de la tabla.
        self.spinBox_3.valueChanged.connect(self.actualizar_tabla)
        self.spinBox.valueChanged.connect(self.actualizar_timer) #Y el spinbox que determina la velocidad de actualización de las serpientes también lo asociamos con la función que actualiza el intervalo del timer.
        self.time.valueChanged.connect(self.actualizar_timeout)
        self.pushButton_2.clicked.connect(self.comenzar_juego) #Finalmente, los botones de la parte inferior se asocian con las funciones que modifican el estado del juego.
        self.pushButton_3.clicked.connect(self.terminar_juego)
        self.show() #Se muestra la ventana.

    def hacer(self):
        '''
        No se hace el serve_forever() del servidor
        para poder regresar a la ejecución del loop principal del juego. 
        El servidor entonces solamente ejectuta las peticiones que hay en la cola y 
        esto a partir de su timeout. Después se regresa al loop del juego.
        '''
        self.servidor.handle_request()

    def actualizar_camino(self):
        '''
        Función que se encarga de formar la lista de tuplas
        que representa las celdas de la tabla que ocupan todas las 
        serpientes. Se tiene que asociar con un QTimer dado que las tuplas no 
        son mutables y entonces esta lista se tendrá que ir reconstruyendo cada
        cierto lapso.
        '''
        for serpiente in self.serpientes_juego:
            serpiente.camino = []
            for casilla in serpiente.casillas:
                #Se construye a partir de la lista de listas, mismas que sí son mutables.
                serpiente.camino.append((casilla[0], casilla[1]))
    
    def inicializar_servidor(self):
        '''
        Función encargada de crear al servidor xmlrpc. Se le asigna una dirección
        y un puerto, además de registrar las funciones a las que tendrán acceso los clientes.
        '''
        puerto = self.spinBox_4.value()
        direccion = self.lineEdit.text()
        #print(direccion)
        self.servidor = SimpleXMLRPCServer((direccion, 0)) #El puerto 0 hace que el sistema le asigne un puerto disponible.
        puerto = self.servidor.server_address[1] 
        self.spinBox_4.setValue(puerto) #Ponemos en la interfaz el puerto que le fue asignado.
        self.spinBox_4.setReadOnly(True) #Bloqueamos los spinboxes y botones para no modificar la configuración que ya se le dio.
        self.lineEdit.setReadOnly(True) #Bloqueamos los spinboxes y botones para no modificar la configuración que ya se le dio.
        self.pushButton.setEnabled(False)
        #Se registran las cuatro funciones del servidor.
        self.servidor.register_function(self.ping)
        self.servidor.register_function(self.yo_juego)
        self.servidor.register_function(self.cambia_direccion)
        self.servidor.register_function(self.estado_del_juego)
        self.servidor.timeout = 0 #Inicialmente, esta es la espera del servidor (tiempo para ejecutar las peticiones antes de volver al loop del juego).
        self.timer_s = QtCore.QTimer(self)
        self.timer_s.timeout.connect(self.hacer) #Para cada contador se le asocia la función correspondiente.
        self.timer_s.start(self.servidor.timeout) #y se especifica su intervalo.

    
    def lista_viboras(self):
        '''
        Función que regresa una lista con las representaciones de todas las víboras
        del juego a partir de su representación a partir de un diccionario. 
        Será usada esta lista en la función asociada al servidor "yo_juego()".
        '''
        lista = list()
        for serpiente in self.serpientes_juego:
            lista.append(serpiente.obtener_diccionario())
        return lista


    '''Funciones del cliente'''
    '''''''''''''''''''''''''''
    '''''''''''''''''''''''''''

    def ping(self):
        return "¡Pong!"

    def yo_juego(self):
        '''
        Permite registrar una nueva serpiente en el juego.
        Se le asigna en su constructor un color aleatorio, un id único, etc.
        Posteriormente, también se tiene que regresar la información de la serpiente 
        que fue creada.
        '''
        serpiente_nueva = self.crear_serpiente()
        diccionario = {"id": serpiente_nueva.id, "color": serpiente_nueva.color}
        return diccionario

    def cambia_direccion(self, identificador, numero):
        '''
        Permite que el cliente pueda modificar la dirección en la que se mueve 
        una serpiente. Para ésto le tendrá que pasar como parámetros a la función 
        el identificador de la serpiente cuya dirección será modificada y la dirección 
        (dado por 0, 1, 2, 3).
        '''
        for s in self.serpientes_juego:
            #Busca que el id dado concuerde con el de una serpiente del juego.
            if s.id == identificador:
                #Y de ser posible, modifica la dirección de la serpiente encontrada.
                if numero == 0:
                    if s.direccion is not "Abajo": 
                        s.direccion = "Arriba"
                if numero == 1:
                    if s.direccion is not "Izquierda":
                        s.direccion = "Derecha"
                if numero == 2: 
                    if s.direccion is not "Arriba":
                        s.direccion = "Abajo"
                if numero == 3: 
                    if s.direccion is not "Derecha":
                        s.direccion = "Izquierda"
        return True #Tienen que forzosamente regresar algo las funciones del servidor.

    def estado_del_juego(self):
        '''
        Función del servidor que regresa un diccionario
        con la información clave del juego al cliente.
        '''
        diccionario = dict()
        diccionario = {
            'espera': self.servidor.timeout, 
            'tamX': self.tableWidget.columnCount(),
            'tamY': self.tableWidget.rowCount(),
            'viboras': self.lista_viboras() #Esta lista ya fue construída con otra función.
        }
        return diccionario



    def crear_serpiente(self):
        '''
        Función para meter una nueva serpiente al juego. 
        La crea de un tamaño de tres celdas y verifica que estas celdas no estén ocupadas.
        '''
        serpiente_nueva = Serpiente()
        creada = False
        while not creada:
            #Crea número aleatorios sin excederse de las dimensiones de la tabla.
            creada = True
            uno = randint(1, self.tableWidget.rowCount()/2)
            dos = uno + 1
            tres = dos +1 
            ancho = randint(1, self.tableWidget.columnCount()-1)
            achecar_1, achecar_2, achecar_3 = [uno, ancho], [dos, ancho], [tres, ancho]
            for s in self.serpientes_juego:
                #Si las casillas ya han sido ocupadas, tiene que volver a generar los números.
                if achecar_1 in s.casillas or achecar_2 in s.casillas or achecar_3 in s.casillas:
                    creada = False
                    break
            #Cuando ya sean válidas, especificamos qué celdas ocupa la víbora.
            serpiente_nueva.casillas = [achecar_1, achecar_2, achecar_3]
            self.serpientes_juego.append(serpiente_nueva) #Y la metemos a la lista de las serpientes en el juego.
            return serpiente_nueva

    def actualizar_timeout(self):
        '''
        Función que permite modificar el tiempo que tiene el servidor
        para llevar a cabo las peticiones de los clientes.
        '''
        self.servidor.timeout = self.time.value() #Se moficia el valor del timer asociado a partir del valor del doublespinbox.
        self.timer_s.setInterval(self.time.value())

    def comenzar_juego(self):
        '''
        Marca el estado del juego como iniciado; crea una serpiente
        '''
        if not self.juego_empezado:
            self.pushButton_3.show() #Se muestra el botón que permitirá terminar el juego después.
            self.crear_serpiente() #Por default crearemos una serpiente sin que se pida, para debuggear.
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
            self.timer_camino = QtCore.QTimer(self)
            self.timer_camino.timeout.connect(self.actualizar_camino)
            self.timer_camino.start(100)
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
                self.tableWidget.item(seccion_corporal[0], seccion_corporal[1]).setBackground(QtGui.QColor(serpiente.color['r'], serpiente.color['g'], serpiente.color['b']))
    
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

    def ha_chocado_con_otra_serpiente(self, serpiente_a_checar):
        '''
        Verifica si la serpiente chocó con una serpiente.
        '''
        for serpiente in self.serpientes_juego:
            #Solamente tenemos que checar que choque con las OTRAS, no consigo misma.
            if serpiente.id != serpiente_a_checar.id:
                for seccion_corporal in serpiente.casillas[:]: 
                    #Si chocó, con la cabeza, con otra serpiente...
                    if serpiente_a_checar.casillas[-1][0] == seccion_corporal[0] and serpiente_a_checar.casillas[-1][1] == seccion_corporal[1]:
                        self.label_7.setText("¡Chocaste!") #Se indica al usuario que la serpiente murió, cambiando del texto del label.
                        self.label_7.setStyleSheet("QLabel { color : #fc360a; }")
                        QtCore.QTimer.singleShot(2000, lambda: self.label_7.setText('')) #Después, el label retoma su valor de cadena vacía.
                        self.serpientes_juego.remove(serpiente_a_checar) #Como la serpiente murió, sale del juego.

    def mover_serpientes(self):
        '''
        Simula el movimiento de las serpientes del juego al ir pintando las celdas de acuerdo a la dirección
        actual de cada una de ellas. Las celdas que preceden a la cabeza constantemente están tomando la posición 
        que les seguía. En sí, la única parte de la serpiente que tiene que verificar a dónde tiene que moverse es 
        la cebza de la sepiente.
        '''
        for serpiente in self.serpientes_juego: #Tiene que mover a todas las serpientes.
            if self.ha_chocado_consigo(serpiente) or self.ha_chocado_con_otra_serpiente(serpiente): #Si chocó la serpiente,
                self.serpientes_juego.remove(serpiente) #Se borra de la lista.
                self.llenar_tabla() #Se tiene que rellenar la tabla.
                serpiente_1 = self.crear_serpiente()
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

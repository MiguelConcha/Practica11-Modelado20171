# Practica10-Modelado20171

__Clásico juego de Snake implementado con Pyqt4.__ 


El juego ahora permite comunicarse con con XMLRPCServer y hacer ciertas peticiones a funciones que fueron registradas en el servidor, a saber: 

* ping: Regresa la cadena __¡Pong!__
* yo_juego: Crea una nueva serpiente que mete al juego, además de que se le asigna un identificador único (UUID) y un color en formato RGB aleatorio. Regresa un diccionario con esta información.
* cambia_dirección: Permite modificar la dirección de una serpiente que se encuentea en el juego a partir de su identificador único dado como parámetro y un número que reprsenta la dirección (tiene que ser un movimiento válido de acuerdo con la dirección actual de la víbora, e.g, no puede moverse para arriba si se está moviento hacia abajo): 
 * 0: Arriba
 * 1: Derecha
 * 2: Abajo
 * 3: Izquierda
* estado_del_juego: Regresa un diccionario que permite conocer la información más importante del juego, como es: 
 * La espera del servidor (timeout).
 * El número de columnas en la tabla.
 * El número de filas/renglones en la tabla.
 * Una lista de las víboras, en donde cada víbora a su vez se puede ver como un diccionario que contiene: 
  * Su identificador único.
  * Su diccionario de colores RGB
  * Una lisa de tuplas que representan el camino de la serpiente, i.e., la lista de las posiciones (x,y) que ocupa la serpiente en la tabla.


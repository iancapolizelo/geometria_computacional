import math as m
from cmath import pi, sqrt
import sys
import ctypes
from tracemalloc import start
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import math
sys.path.append('lib/')
import utils as ut
import time

pontos = []

#------------------------------------
# Funções auxiliares
#------------------------------------

def area(p1, p2, p3):

    v1 = np.empty((0,1),dtype="float32")
    v2 = np.empty((0,1),dtype="float32")

    v1 = np.append(v1,p2[0] - p1[0])
    v1 = np.append(v1,p2[1] - p1[1])

    v2 = np.append(v2,p3[0] - p1[0])
    v2 = np.append(v2,p3[1] - p1[1])


    A = np.cross(v1,v2)

    return A/2

def left(a,b,c):
    if (area(a,b,c) >= 0):
        return True
    return False


## Classe da estrutura do vértice
class Vertice:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.incidente = None

    def distancia(x, y):
        return m.sqrt((x-self.x)**2 + (y-self.y)**2)

    def orbidaAresta():
        while(not self.aresta.twin.origin is self ):
            self.aresta = self.aresta.next
        
        self.aresta = self.aresta.twin



## Classe da estrutura da aresta
class Aresta:

    def __init__(self, v):
        self.origin = v
        self.twin = None
        self.next = None
        self.prev = None
        self.face = None
        self.origin.incidente = self
    
    def setTwin(v):
        self.twin = v
        v.twin = self
    
    def setNext(v):
        self.next = v
        v.prev = self
        v.face = self.face
    
    def distancia(x, y):
        x_origin = self.origin.x
        y_origin = self.origin.y

        x_twin = self.twin.origin.x
        y_twin = self.twin.origin.y

        return abs((y_twin-y_origin)*x-(x_twin-x_origin)*y+x_twin*y_origin-y_twin*x_origin)/m.sqrt(pow(y_twin-y_origin,2)+pow(x_twin-x_origin,2))

    def intercepta(aresta):
        return (left(self.origin, self.twin.origin, aresta.origin) 
                != left(self.origin, self.twin.origin, aresta.twin.origin) 
            and left(aresta.origin, aresta.twin.origin, self.origin) 
                != left(aresta.origin, aresta.twin.origin, self.twin.origin))


## Classe da estrutura da face
class Face:
    def __init__(self, aresta):
        self.aresta = aresta

        atual = aresta
        while(atual is not aresta):
            atual.face = self
            atual = atual.next

    def getArestas(self):
        h = self.aresta
        pl = [h.origin]
        while(not h.next is self.arest):
            h = h.next
            pl.append(h.origin)
        return pl
    
    def nextAresta():
        self.aresta = self.aresta.next


## Classe da estrutura do DCEL
class DCEL:
    def __init__(self):
        self.vertices = []
        self.arestas = []
        self.faces = []

    def build(self, pontos):

        anti_horario = left(pontos[0], pontos[1], pontos[2])
        inicio = 0
        fim = 0

        ## Adicionando os pontos como vértices da DCEL
        if anti_horario:
            inicio = 0
            fim = len(pontos)

            while(inicio is not fim ):
                novo_vertice = Vertice(pontos[i][0], pontos)
                self.vertices.append(novo_vertice)
                inicio = inicio + 1
        else:
            inicio = len(pontos) - 1
            fim = -1

            while(inicio is not fim):
                novo_vertice = Vertice(pontos[i][0], pontos)
                self.vertices.append(novo_vertice)
                inicio = inicio - 1

            
        ## Criando as arestas a partir dos vértices do DCEL
        nova_aresta = None
        nova_twin = None

        ultima_aresta = None
        ultima_twin = None

        primeira_aresta = None
        primeira_twin = None

        for i in range(len(self.vertices)):
            nova_aresta = Aresta(self.vertices[i])
            nova_twin = Aresta(self.vertices[(i+1)%len(self.vertices)])

            nova_aresta.twin(nova_twin)
            if(ultima_aresta is not None):
                ultima_aresta.next = nova_aresta
                nova_twin.next = ultima_twin
            else:
                primeira_aresta = nova_aresta
                primeira_twin = nova_twin
            
            self.arestas.append(nova_aresta)
            self.aresta.append(nova_twin)

            ultima_aresta = nova_aresta
            ultima_twin = nova_twin
        
        ultima_aresta.next = primeira_aresta
        primeira_twin.next = ultima_twin

        self.face.append(Face(primeira_aresta))
        self.face.append(Face(primeira_twin))

        """
        for i in range(len(self.vertices)):

            if i < (len(self.vertices)-1):
                aresta_origin = Aresta(self.vertices[i])
                aresta_twin = Aresta(self.vertices[i+1])

                aresta_origin.twin = aresta_twin
                aresta_twin.twin = aresta_origin

                self.vertices[1].incidente = aresta_origin

                self.arestas.append(aresta_origin)
                self.arestas.append(aresta_twin)
            else:
                aresta_origin = Aresta(self.vertices[i])
                aresta_twin = Aresta(self.vertices[0])

                aresta_origin.twin = aresta_twin
                aresta_twin.twin = aresta_origin

                self.vertices[i].incidente = aresta_origin

                self.arestas.append(aresta_origin)
                self.arestas.append(aresta_twin)
        
        for i in range(len(self.arestas)):

            if(i < (len(self.arestas)-2)):
                self.arestas[i].next = self.arestas[i+2]
                self.arestas[i+2].prev = self.arestas[i]
            else:
                self.arestas[i].next = self.arestas[(i%2)]
                self.arestas[(i%2)].prev = self.arestas[i]
        """



    def getArestaProxima(x, y, distancia_limite):

        aresta_proxima = None

        for aresta in self.arestas:
            distancia = aresta.distancia(x, y)

            if distancia < distancia_limite:
                distancia_limite = distancia
                aresta_proxima = aresta
            
        return aresta_proxima


    def getFaceProxima(x, y):
        aresta_proxima = self.getArestaProxima(x, y)
        vertice = Vertice(x, y)

        if(left(aresta_proxima.origin, aresta_proxima.twin.origin, vertice)):
            return aresta_proxima.face
        return aresta_proxima.twin.face

    def getVerticeCoordenadas():
        coordenadas = []

        for vertice in self.vetices:
            coordenadas.append(vertice.x)
            coordenadas.append(vertice.y)
        
        return coordenadas
    
    def getArestasCoordenadas():
        coordenadas = []

        for aresta in self.arestas:
            coordenadas.append(aresta.origin.x)
            coordenadas.append(aresta.origin.y)

            coordenadas.append(aresta.twin.origin.x)
            coordenadas.append(aresta.twin.origin.y)

        return coordenadas
import cv2
import numpy as np

def mostrar_coordenadas(event, x, y, flags, param):
    # Esta función se ejecuta cada vez que hay un evento del mouse
    if event == cv2.EVENT_MOUSEMOVE:  # Cuando el mouse se mueve
        # Obtener el color del píxel en formato BGR
        pixel = imagen[y, x]
        # Crear una copia de la imagen para no modificar la original
        img_mostrar = imagen.copy()
        # Mostrar las coordenadas y el color en la imagen
        texto = f"x: {x}, y: {y}, Color BGR: {pixel}"
        cv2.putText(img_mostrar, texto, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img_mostrar, texto, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
        cv2.imshow('Imagen', img_mostrar)

# Cargar la imagen
# Reemplaza 'ruta_de_tu_imagen.jpg' con la ruta de tu imagen
imagen = cv2.imread('imagen_coord/minecraft1.jpg')

# Verificar si la imagen se cargó correctamente
if imagen is None:
    print("Error al cargar la imagen")
    exit()

# Crear una ventana y asignar la función de callback para el mouse
cv2.namedWindow('Imagen')
cv2.setMouseCallback('Imagen', mostrar_coordenadas)

# Mostrar la imagen inicial
cv2.imshow('Imagen', imagen)

# Mantener la ventana abierta hasta que se presione 'q'
while True:
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('q'):
        break

# Cerrar todas las ventanas
cv2.destroyAllWindows()
"""Plantilla del juego Arkanoid para el hito M2
Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""

from pathlib import Path
from arkanoid_core import *
from pygame import Vector2
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method
def cargar_nivel(self) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""
    
    if not self.level_path:
        raise FileNotFoundError("No se ha proporcionado ruta de nivel.")

    if not self.level_path.is_file():
        raise FileNotFoundError(f"El fichero de nivel no existe: {self.level_path}")
    
    with open(self.level_path, 'r') as file:
        lineas = file.read().splitlines()

        for linea in lineas:
            if linea.strip() == "":
                lineas.remove(linea)
            if len(lineas[0]) != len(linea.strip()) and linea.strip() != "":
                raise ValueError("Las líneas del nivel no tienen el mismo ancho.")
    layout = [linea.strip() for linea in lineas]
    self.layout = layout
    return layout
    # - Comprueba que `self.level_path` existe y es fichero.
    # - Lee su contenido, filtra líneas vacías y valida que todas tienen el mismo ancho.
    # - Guarda el resultado en `self.layout` y devuélvelo.


@arkanoid_method
def preparar_entidades(self) -> None:
    self.paddle = self.crear_rect(0,0, *self.PADDLE_SIZE)
    self.paddle.midbottom = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - self.PADDLE_Y_OFFSET)
    self.score = 0
    self.lives = 3
    self.end_message = "Has perdido"
    self.reiniciar_bola()
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.


@arkanoid_method
def crear_bloques(self) -> None:
    self.blocks.clear()
    self.blocks_colors.clear()
    self.block_symbols
    
    for fila_idx, fila in enumerate(self.layout):
        for col_idx, simbolo in enumerate(fila):
            if simbolo not in self.BLOCK_COLORS:
                continue
            rect= self.calcular_posicion_bloque(fila_idx, col_idx)
            self.blocks.append(rect)
            self.block_colors.append(self.BLOCK_COLORS[simbolo])
            self.block_symbols.append(simbolo)
    

    """Genera los rectángulos de los bloques en base a la cuadrícula."""
    # - Limpia `self.blocks`, `self.block_colors` y `self.block_symbols`.
    # - Recorre `self.layout` para detectar símbolos de bloque.
    # - Usa `self.calcular_posicion_bloque` y rellena las listas paralelas.

@arkanoid_method
def procesar_input(self) -> None:
    self.obtener_estado_teclas()
    if self.teclas_presionadas[self.KEY_LEFT] or self.teclas_presionadas[self.KEY_A]:
        if self.paddle.x > self.paddle.width/2:
            self.paddle.x -= self.PADDLE_SPEED
            self.paddle.x = max(self.paddle.x, 0)
        else:
            self.paddle.x = self.paddle.width/2

    if self.teclas_presionadas[self.KEY_RIGHT] or self.teclas_presionadas[self.KEY_D]: 
        if self.paddle.x < self.SCREEN_WIDTH - self.paddle.width/2:
            self.paddle.x += self.PADDLE_SPEED
            self.paddle.x = min(self.paddle.x, self.SCREEN_WIDTH - self.paddle.width)
        else:
            self.paddle.x = self.SCREEN_WIDTH - self.paddle.width/2
            
    """Gestiona la entrada de teclado para mover la paleta."""
    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha.
    # - Limita la posición para que no salga de la pantalla.
    

@arkanoid_method
def actualizar_bola(self) -> None:
    """Actualiza la posición de la bola y resuelve colisiones."""
    self.ball_pos += self.ball_velocity
    ball_rect = self.obtener_rect_bola()
    if ball_rect.left <= 0 or ball_rect.right >= self.SCREEN_WIDTH:
        self.ball_velocity.x *= -1
    if ball_rect.top <= 0:
        self.ball_velocity.y *= -1
    if ball_rect.colliderect(self.paddle):
        self.ball_velocity.y *= -1
        offset = (ball_rect.centerx - self.paddle.centerx) / (self.paddle.width / 2)
        self.ball_velocity.x += offset * self.BALL_SPEED * 0.5
        self.ball_velocity = self.ball_velocity.normalize() * self.BALL_SPEED
        
    if not self.blocks or self.blocks == []:
        self.end_message = "Nivel completado"
    elif self.lives <= 0:
        self.end_message = "Game Over"
    
    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.

@arkanoid_method
def dibujar_escena(self) -> None:
    self.screen.fill(self.BACKGROUND_COLOR)
    for rect,color in zip (self.blocks, self.block_colors):
        self.dibujar_rectangulo(rect,color)

    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    self.dibujar_circulo((int(self.ball_pos.x),int(self.ball_pos.y)), self.BALL_RADIUS, self.BALL_COLOR)
    self.dibujar_texto(f"Puntos:{self.score}", (20,20))
    self.dibujar_texto(f"Vidas:{self.lives}", (20,50))
    self.dibujar_texto(self.end_message, (self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2), center=True)

        
    """Renderiza fondo, bloques, paleta, bola y HUD."""
    # - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    # - Pinta la paleta y la bola con las utilidades proporcionadas.
    # - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.

@arkanoid_method
def run(self) -> None:
    """Ejecuta el bucle principal del juego."""
    self.inicializar_pygame()
    self.cargar_nivel()
    self.preparar_entidades()
    self.crear_bloques()

    running = True
    while running == True:
        for event in self.iterar_eventos():
            if event.type == pygame.QUIT:
                running = False
        self.procesar_input()
        self.actualizar_bola()
        self.dibujar_escena()
        self.actualizar_pantalla()

        if self.teclas_presionadas[self.KEY_ESCAPE]:
            running = False

        if self.clock:
            self.clock.tick(self.FPS)

        if self.end_message:
            self.dibujar_escena()
            self.actualizar_pantalla()
            self.esperar(2000)
            running = False

    self.finalizar_pygame()
    # - Inicializa recursos (`self.inicializar_pygame`, `self.cargar_nivel`, etc.).
    # - Procesa eventos de `self.iterar_eventos()` y llama a los métodos de actualización/dibujo.
    # - Refresca la pantalla con `self.actualizar_pantalla()` y cierra con `self.finalizar_pygame()`.


def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        help="Ruta al fichero de nivel (texto con # para bloques y . para huecos).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()


if __name__ == "__main__":
    main()
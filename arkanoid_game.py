v"""Plantilla del juego Arkanoid para el hito M2
Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""

from pathlib import Path
from arkanoid_core import *
from pygame import Vector2
import sys
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method
def cargar_nivel(self) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""
    
    if not self.level_path.exists() or not self.level_path.is_file():
        raise FileNotFoundError(f"No se ha encontrado el nivel: {self.level_path}")

    contenido = self.level_path.read_text(encoding="utf-8")
    lineas = [linea.rstrip("\r") for linea in contenido.splitlines()]
    cuadricula = [linea for linea in lineas if linea.strip()]

    if not cuadricula:
        raise ValueError("El fichero de nivel no contiene filas válidas.")

    ancho = len(cuadricula[0])
    if ancho == 0:
        raise ValueError("Las filas del nivel no pueden estar vacías.")

    for fila in cuadricula:
        if len(fila) != ancho:
            raise ValueError("Todas las filas del nivel deben tener el mismo ancho.")

    self.layout = cuadricula
    return self.layout
    # - Comprueba que `self.level_path` existe y es fichero.
    # - Lee su contenido, filtra líneas vacías y valida que todas tienen el mismo ancho.
    # - Guarda el resultado en `self.layout` y devuélvelo.


@arkanoid_method
def preparar_entidades(self) -> None:
    self.paddle = self.crear_rect(0,0, *self.PADDLE_SIZE)
    self.paddle.midbottom = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - self.PADDLE_OFFSET)
    self.score = 0
    self.lives = 3
    self.end_message = ""
    self.reiniciar_bola()
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.


@arkanoid_method
def crear_bloques(self) -> None:
    self.blocks.clear()
    self.block_colors.clear()
    self.block_symbols.clear()
    
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
    teclas = self.obtener_estado_teclas()
    if teclas[self.KEY_LEFT] or teclas[self.KEY_A]:
        if self.paddle.x < self.SCREEN_WIDTH:
            self.paddle.x -= self.PADDLE_SPEED
            self.paddle.x = max(self.paddle.x, 0)
        else:
            self.paddle.x = self.SCREEN_WIDTH - self.paddle.width/2

    if teclas[self.KEY_RIGHT] or teclas[self.KEY_D]: 
        if self.paddle.x < self.SCREEN_WIDTH:
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
    posicion_anterior = Vector2(self.ball_pos)
    self.ball_pos = self.ball_pos + self.ball_velocity
    ball_rect = self.obtener_rect_bola()

    # Rebotes contra paredes laterales
    if self.ball_pos.x - self.BALL_RADIUS <= 0:
        self.ball_pos.x = self.BALL_RADIUS
        self.ball_velocity.x *= -1
    elif self.ball_pos.x + self.BALL_RADIUS >= self.SCREEN_WIDTH:
        self.ball_pos.x = self.SCREEN_WIDTH - self.BALL_RADIUS
        self.ball_velocity.x *= -1

    # Rebote contra la parte superior
    if self.ball_pos.y - self.BALL_RADIUS <= 0:
        self.ball_pos.y = self.BALL_RADIUS
        self.ball_velocity.y *= -1

    ball_rect = self.obtener_rect_bola()

    # Colisión con la paleta
    if ball_rect.colliderect(self.paddle) and self.ball_velocity.y > 0:
        distancia = (self.ball_pos.x - self.paddle.centerx) / (self.paddle.width / 2)
        self.ball_velocity.y *= -1
        self.ball_velocity.x += distancia * self.BALL_SPEED * 0.5
        if self.ball_velocity.length_squared() == 0:
            self.ball_velocity.update(0, -self.BALL_SPEED)
        else:
            self.ball_velocity = self.ball_velocity.normalize() * self.BALL_SPEED
        self.ball_pos.y = self.paddle.top - self.BALL_RADIUS - 1
        ball_rect = self.obtener_rect_bola()

    # Colisión con bloques
    bloque_golpeado = -1
    for idx, rect in enumerate(self.blocks):
        if ball_rect.colliderect(rect):
            bloque_golpeado = idx
            break

    if bloque_golpeado >= 0:
        rect_bloque = self.blocks.pop(bloque_golpeado)
        simbolo = self.block_symbols.pop(bloque_golpeado)
        self.block_colors.pop(bloque_golpeado)
        self.score += self.BLOCK_POINTS.get(simbolo, 0)

        rect_prev = self.crear_rect(
            int(posicion_anterior.x - self.BALL_RADIUS),
            int(posicion_anterior.y - self.BALL_RADIUS),
            self.BALL_RADIUS * 2,
            self.BALL_RADIUS * 2,
        )
        # Determina si el impacto fue horizontal o vertical para invertir el eje adecuado
        if rect_prev.right <= rect_bloque.left or rect_prev.left >= rect_bloque.right:
            self.ball_velocity.x *= -1
        else:
            self.ball_velocity.y *= -1

        if not self.blocks:
            self.end_message = "Nivel completado"
            self.running = False

    # La bola cae por la parte inferior
    if self.ball_pos.y - self.BALL_RADIUS > self.SCREEN_HEIGHT:
        self.lives -= 1
        if self.lives <= 0:
            self.end_message = "Fin del juego"
            self.running = False
        else:
            self.reiniciar_bola((0, -1))
    
    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.

@arkanoid_method
def dibujar_escena(self) -> None:
    if not self.screen:
        return


    self.screen.fill(self.BACKGROUND_COLOR)
    for rect,color in zip (self.blocks, self.block_colors):
        self.dibujar_rectangulo(rect,color)

    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    self.dibujar_circulo((int(self.ball_pos.x),int(self.ball_pos.y)), self.BALL_RADIUS, self.BALL_COLOR)
    self.dibujar_texto(f"Puntos:{self.score}", (20,20))
    self.dibujar_texto(f"Vidas:{self.lives}", (20,50))
    
    if self.end_message:
        texto_x = self.SCREEN_WIDTH // 2 - 110
        texto_y = self.SCREEN_HEIGHT // 2 - 20
        self.dibujar_texto(self.end_message, (texto_x, texto_y), grande=True)

        
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

    self.running = True
    while self.running:
        for evento in self.iterar_eventos():
            if evento.type == self.EVENT_QUIT:
                self.running = False
            elif evento.type == self.EVENT_KEYDOWN and evento.key == self.KEY_ESCAPE:
                    self.running = False

            if not self.running:
                break
        self.procesar_input()
        self.actualizar_bola()
        self.dibujar_escena()
        self.actualizar_pantalla()


        if self.clock:
            self.clock.tick(self.FPS)

        if self.end_message:
            self.dibujar_escena()
            self.actualizar_pantalla()
            self.esperar(2000)
    
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

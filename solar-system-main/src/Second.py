import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import events
import texture

# Гравитационная постоянная (в условных единицах)
G = 0.1

# Масса Солнца
M_sun = 1000

# Эксцентриситет орбит и радиусы для планет
planet_data = {
    "mercury": {"mass": 0.0553, "a": 45, "radius": 1.383, "e": 0.2056,"rotation":0,"speed":0.3},
    "venus": {"mass": 0.815, "a": 65, "radius": 1.949, "e": 0.0068,"rotation":0,"speed":0.2},
    "earth": {"mass": 1.0, "a": 85, "radius": 2.0, "e": 0.0167,"rotation":0,"speed":1},
    "mars": {"mass": 0.107, "a": 125, "radius": 1.532, "e": 0.0934,"rotation":0,"speed":0.96},
    "jupiter": {"mass": 317.8, "a": 175, "radius": 11.209, "e": 0.0489,"rotation":0,"speed":2.1},
    "saturn": {"mass": 95.2, "a": 235, "radius": 9.449, "e": 0.0565,"rotation":0,"speed":2.7},
    "uranus": {"mass": 14.5, "a": 275, "radius": 4.007, "e": 0.0463,"rotation":0,"speed":1.4},
    "neptune": {"mass": 17.1, "a": 335, "radius": 3.883, "e": 0.0100,"rotation":0,"speed":0.4},
}
dt = 1

# Класс для Солнца
class Sun:
    def __init__(self, position=np.array([0.0, 0.0, 0.0]), radius=10):
        self.position = position
        self.radius = radius
        self.texture_id = texture.read(f"sun.jpg")

    def draw(self):
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glDisable(GL_LIGHTING)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 10, 360, 180)
        gluDeleteQuadric(quadric)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        glEnable(GL_LIGHTING)

def enable_texturing():
    glEnable(GL_TEXTURE_2D)  # Enable 2D texturing
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)  # Set the texture blending mode


class Orbits:
    def __init__(self, planet_data):
        self.planet_data = planet_data
        self.trajectory = {planet: [] for planet in planet_data}
        self.position = {
            planet: np.array([data['a'] * (1 - data['e']), 0.0, 0.0]) for planet, data in planet_data.items()
        }
        self.velocity = {planet: np.array([0.0, 0.0, 0.0]) for planet in planet_data}
        self.textures = {planet: texture.read(f"{planet}.jpg") for planet in planet_data}
        self.time = 0  # Начальное время

    # Function to calculate orbital period
    def orbital_period(self, a):
        return 2 * np.pi * np.sqrt(a**3 / (G * M_sun))

    # Function to solve Kepler's equation for eccentric anomaly E
    def solve_kepler(self, M, e):
      

        E = M  # Initial approximation for E
        for _ in range(100):  # Iterating with Newton's method (a fixed number of iterations)
            # Kepler's equation: E - e * sin(E) = M
            delta_E = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
            E -= delta_E  # Update E
            if abs(delta_E) < 1e-6:  # Convergence criterion
                break
        return E

    # Function to update position and velocity
    def update_position_velocity(self, position, velocity, time, a, e):
        # Mean anomaly M
        M = 2 * np.pi * time / self.orbital_period(a)

        # Solve for eccentric anomaly E
        E = self.solve_kepler(M, e)

        # Calculate distance r from the Sun
        r = a * (1 - e ** 2) / (1 + e * np.cos(E))


        position[0] = r * np.cos(E)
        position[1] = r * np.sin(E)

        # Calculate the tangential velocity (orbital speed)
        v_magnitude = np.sqrt(G * M_sun * (2 / r - 1 / a))

        # Update velocity (using the correct direction based on E)
        velocity[0] = -v_magnitude * np.sin(E)
        velocity[1] = v_magnitude * np.cos(E)

        return position, velocity
    
    def set_material_properties(self, planet):
        # Set material properties for each planet based on its size
        data = self.planet_data[planet]
        # Smaller planets could use higher ambient lighting
        if data['radius'] < 2.0:
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])  # More ambient light for smaller planets
        else:
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])  # Less ambient light for larger planets
        
        # Diffuse lighting can also vary by size
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])

    # Function to draw planets and their trajectories
    def draw_planets_and_trajectories(self, sun_pos):
        for planet, data in self.planet_data.items():
            print("\t", data)
            # Обновление позиции и скорости планеты
            self.position[planet], self.velocity[planet] = self.update_position_velocity(
                self.position[planet], self.velocity[planet], self.time, data['a'], data['e']
            )
            
            # Push matrix to preserve transformations
            glPushMatrix()
            
            # Apply transformation to position the planet
            glTranslatef(self.position[planet][0], self.position[planet][1], self.position[planet][2])
            
            # Rotate the planet around its own axis
            glRotatef(data['rotation'], 0, 0,1)
            
            # Update rotation for the next frame
            data['rotation'] += data['speed']
            if data['rotation'] >= 360:
                data['rotation'] = 0
            
            # Рисуем траекторию
            self.trajectory[planet].append(self.position[planet].copy())
            glDisable(GL_LIGHTING)
            
            glEnable(GL_LIGHTING)
            
            # Set the material properties based on the planet size
            self.set_material_properties(planet)

            # Рисуем планету
            texture = self.textures[planet]

    
            glPushMatrix()

          
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)  
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture)


            quadric = gluNewQuadric()
            gluQuadricTexture(quadric, GL_TRUE)
            gluSphere(quadric, data['radius'], 60, 50)
            gluDeleteQuadric(quadric)

        
            glDisable(GL_TEXTURE_2D)

       
            glPopMatrix()
            glPopMatrix()
            # Restore the previous transformations
            glColor3f(0.1, 0.1, 0.2)
            glBegin(GL_LINE_STRIP)
            for pos in self.trajectory[planet]:
                glVertex3f(pos[0], pos[1], 0)  # Отображаем точки траектории
            glEnd()

        self.time += 0.1 * dt  # Увеличиваем время


            
        


# Класс для Солнечной системы
class SolarSystem:
    def __init__(self, planet_data):
        self.start_light()
        self.sun = Sun()  # Солнце
        self.orbits = Orbits(planet_data)  # Орбиты планет

    def draw(self):
        # Рисуем Солнце
        self.sun.draw()

        # Рисуем планеты и их траектории
        self.orbits.draw_planets_and_trajectories(self.sun.position)
    
    def start_light(self):
        """
        Настройка освещения (солнце и окружающий свет)
        """
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])  # Increased ambient light
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])  # Set ambient light for the light source
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # Diffuse light for better illumination
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])  # Light from the Sun
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [0.0, 0.0, 1.0])
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 0.0)
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 180.0)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)



# Инициализация OpenGL и Pygame
def init_openGL():
    pygame.init()
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, display[0] / display[1], 20, 1000)
    glTranslatef(0.0, 0.0, -300)  


# Главная функция симуляции
def main():
    global dt
    # Инициализация OpenGL
    init_openGL()
    pygame.key.set_repeat(1, 10)
    # Создание солнечной системы
    solar_system = SolarSystem(planet_data)

    glClearColor(0.0, 0.0, 0.0, 1.0)  # Устанавливаем цвет фона
    glEnable(GL_DEPTH_TEST)  # Включаем проверку глубины

    last_mouse_position = {"x": 0, "y": 0}
    draw_rotating_enable = True

    while True:
        last_mouse_position, draw_rotating_enable, dt = events.handle(
            last_mouse_position, draw_rotating_enable, dt
        )

        # Очистка экрана и рисование солнечной системы
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        solar_system.draw()

        # Обновляем экран
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

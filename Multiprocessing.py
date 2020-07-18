import pygame
import multiprocessing
import time
import mysql.connector
import random
import math

#Class for initializing pygame and drawing the Main Window
class Window:
    pygame.init()
    pygame.font.init()
    def __init__(self, Dimensions, Title, Color):
        self.dimensions = Dimensions
        self.color = Color
        self.title = pygame.display.set_caption(Title)
        self.window = pygame.display.set_mode(self.dimensions)
        self.clock = pygame.time.Clock()
        self.icon = pygame.display.set_icon(pygame.image.load('ICON.png'))
        self.text_font = pygame.font.Font(None, 26)
        self.number_font = pygame.font.Font(None, 20)

    #Sets background color for Window
    def draw(self):
        self.window.fill(self.color)

    #Gets user input regarding the program
    def get_user_actions(self):
        for Event in pygame.event.get():
            if Event.type == pygame.QUIT:
                return True

class Element:
    def __init__(self, Name, Protons, Neutrons, ElectronConfig):
        self.name = Name
        self.protons = Protons
        self.neutrons = Neutrons
        self.core_color = (100, 0, 255)
        self.electron_color = (150, 0, 100)
        self.electron_config = ElectronConfig
        self.center_position = [480, 480]

    #Generates & Draws the Atom
    def generate_atom(self, Window):
        #Draws the Atom Core
        for i in range(self.protons + self.neutrons):
            print(self.protons + self.neutrons)
            pygame.draw.circle(Window, self.core_color,
                               [self.center_position[0] + random_position(0, 10),
                                self.center_position[1] + random_position(0, 10)], 20)

        #Draws the number of Electron Shells
        for i in range(len(self.electron_config.split(","))):
            radius = [100, 150, 200, 250, 300, 350, 400]
            pygame.draw.circle(Window, (211, 211, 211), self.center_position, radius[i], 2)

            #Draws each Electron on the correct Electron Shell
            for j in range(int(self.electron_config.split(",")[i])):
                angle = random.randint(0, int((10 - 1) / 0.1)) * 0.1 + 1
                pygame.draw.circle(Window, self.electron_color, [round(radius[i] * math.cos(angle) + self.center_position[0]),
                                              round(radius[i] * math.sin(angle) + self.center_position[1])], 8)

def random_position(start, end):
    return random.randint(start, end)

#Fetch data from MYSQL Database (Element properties, Periodic Table layout etc.)
def fetch_from_database(command):
    DBLOGIN = {"host": "localhost", "database": "OlijonDB", "user": "root", "passwd": "eBA1D56903!"}
    DB = mysql.connector.connect(host=DBLOGIN["host"], database=DBLOGIN["database"], user=DBLOGIN["user"],
                                 passwd=DBLOGIN["passwd"])
    DBCursor = DB.cursor(prepared=True)
    DBCursor.execute(command)
    return DBCursor.fetchall()

#----------------------------------------------------------------------------------------------------------

def P1():
    #Periodic Table Class
    class Table:
        def __init__(self, CellDimensions, GridSize):
            self.cell_dimensions = CellDimensions
            self.colors = [(255, 255, 255), (253, 253, 150), (255, 105, 97), (119, 158, 203), (119, 221, 119),
                           (218, 191, 222), (174, 198, 207)]
            self.grid_size = GridSize
            self.grid = []
            self.layout = []
            self.element_texts = []
            self.element_colors = []

        #Generates a Grid
        def generate_grid(self):
            for Row in range(self.grid_size):
                self.grid.append([])
                for Column in range(self.grid_size):
                    self.grid[Row].append(0)

            # Generate Periodic Table Layout & Colors
            for i in range(len(self.layout)):
                self.grid[self.layout[i][0]][self.layout[i][1]] = self.element_colors[i]

        #Gets mouse action and if pressed, launches another process with an animation of the selected Element
        def lanuch_simulation(self):
            if pygame.mouse.get_pressed()[0]:
                mouse_position = pygame.mouse.get_pos()
                Column = mouse_position[0] // (self.cell_dimensions[0] + self.cell_dimensions[2])
                Row = mouse_position[1] // (self.cell_dimensions[1] + self.cell_dimensions[2])
                if self.grid[Row][Column] in self.element_colors:
                    multiprocessing.Process(target=P2, args=(int(self.layout.index([Row, Column]) + 1),)).start()
                    time.sleep(1)

        #Draws the Grid onto the Window
        def draw(self, Window):
            for Row in range(self.grid_size):
                for Column in range(self.grid_size):

                    # Selects each cells color
                    CellColor = self.grid[Row][Column]
                    Color = self.colors[CellColor]

                    # Draws each cell with color
                    pygame.draw.rect(Window, Color,
                                     [(self.cell_dimensions[2] + self.cell_dimensions[0]) * Column +
                                      self.cell_dimensions[2],
                                      (self.cell_dimensions[2] + self.cell_dimensions[1]) * Row + self.cell_dimensions[
                                          2],
                                      self.cell_dimensions[0], self.cell_dimensions[1]])

                    #Draws the Symbol and Atomic Number for each Element in each Cell
                    if self.grid[Row][Column] in self.element_colors:
                        Text = W.text_font.render(self.element_texts[self.layout.index([Row, Column])], True, (0, 0, 0))
                        Window.blit(Text, [
                            (self.cell_dimensions[2] + self.cell_dimensions[0]) * Column + self.cell_dimensions[2] + 16,
                            (self.cell_dimensions[2] + self.cell_dimensions[1]) * Row + self.cell_dimensions[2] + 20,
                            self.cell_dimensions[0], self.cell_dimensions[1]])
                        Numerics = W.number_font.render(str(self.layout.index([Row, Column]) + 1), True,
                                                        (0, 0, 0))
                        Window.blit(Numerics,
                                    [(self.cell_dimensions[2] + self.cell_dimensions[0]) * Column +
                                     self.cell_dimensions[2] + 2,
                                     (self.cell_dimensions[2] + self.cell_dimensions[1]) * Row + self.cell_dimensions[
                                         2] + 4,
                                     self.cell_dimensions[0], self.cell_dimensions[1]])

    #Function for refreshing the screen
    def refresh_screen():
        W.draw()
        T.draw(W.window)
        pygame.display.update()

    #Object Initialization
    W = Window([919, 919], "The Periodic Table", (255, 255, 255))
    T = Table([50, 50, 1], 18)

    #Fetch from database
    for Element in fetch_from_database("SELECT tablerow, tablecolumn, symbol, color FROM periodictable"):
        T.layout.append([Element[0], Element[1]])
        T.element_texts.append(Element[2])
        T.element_colors.append(Element[3])

    #Main Loop
    run = True
    while run:
        # FPS Limiter
        W.clock.tick(30)

        if W.get_user_actions(): run = False

        T.generate_grid()
        T.lanuch_simulation()

        refresh_screen()
    pygame.quit()

#--------------------------------------------------------------------------------------------------------

def P2(AtomicNumber):
    def render_screen():
        W.draw()
        E.generate_atom(W.window)
        pygame.display.update()

    #Object Definition
    W = Window([1000, 1000], "Process 2", (255,255,255))
    for Properties in fetch_from_database("SELECT atomicnumber, name, atomicmass, electronconfig FROM periodictable WHERE atomicnumber = " + str(AtomicNumber)):
        E = Element(Properties[1], Properties[0], Properties[2] - Properties[0], Properties[3])

    #Main Loop
    Run = True
    while Run:
        #FPS Limiter
        W.clock.tick(5)

        #Checks if User has pressed "Close" Button and thereafter exits while loop
        if W.get_user_actions(): Run = False

        render_screen()
    pygame.quit()

#---------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    P1()
from random import randint
from sys import exit
import os

class BoardException(Exception): # родительский класс собственных исключений
    pass

class BoardOutException(BoardException):
    def __str__(self): # чтобы не писать BoardOutException.method()
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y): # координаты точек
        self.x = x
        self.y = y
    # будем сравнивать все точки (в том числе и в списках)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    # будем корректно печатать списки
    def __repr__(self):
        return f"({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow # координаты начала корабля
        self.l = l # длина корабля
        self.o = o # ориентация корабля
        self.lives = l # жизни корабля (не подбитые точки)
    
    @property
    def dots(self):
        ship_dots = [] # создаем список точек корабля
        for i in range(self.l): # к-во повторов = длине корабля
            cur_x = self.bow.x # на каждом проходе присваиваем текущей точке
            cur_y = self.bow.y # корабля координаты начальной точки
            # в зависимости от ориентации увеличиваем ту или иную координату
            # на номер текущей итерации
            if self.o == 0:
                cur_x += i
            
            elif self.o == 1:
                cur_y += i
            # добавляем текущую точку в список точек корабля
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot): # проверка попадания: с помощью метода __eq__
        return shot in self.dots # проверяем присутствует ли точка shot в списке
    # self.dots (кторорый формируется в методе dots)

class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid # скрывать ли расставленные корабли
        
        self.count = 0 # к-во подбитых кораблей

        # поле размером size на size - двумерная матрица
        self.field = [ ["O"]*size for _ in range(size) ]
        
        self.busy = [] # список занятых точек (кораблями или выстрелами)
        self.ships = [] # список кораблей (состящих из списков точек)
    
    def add_ship(self, ship): # добавление
        
        for d in ship.dots: # проверяем все точки корабля
            # что они не выходят за границу поля или не заняты
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots: # снова проходим по точкам корабля
            self.field[d.x][d.y] = "■" # записываем в поле во все точки символ
            self.busy.append(d) # и занисим эти точки в список занятиых
        
        self.ships.append(ship) # добавляем в список кораблей
        self.contour(ship) # добавляем точки контура
            
    def contour(self, ship, verb = False):
        # список координат самой точки и окружающих ее точек
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        # проходим по точкам корабля
        for d in ship.dots:
            # проходим по списку точек
            for dx, dy in near:
                # записываем смещенную точку
                cur = Dot(d.x + dx, d.y + dy)
                # Если не мимо поля и не в занятую точку
                if not(self.out(cur)) and cur not in self.busy:
                    # если нужно визуализировать (в режиме боя)
                    if verb:
                        # в эти координаты записываем символ точки
                        self.field[cur.x][cur.y] = "."
                    # то добавляем ее в список занятых точек
                    self.busy.append(cur)
    
    def __str__(self): # отрисовка поля
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |" # заголовки столбцов
        # один проход - одна строка (field - матрица из __init__)
        # row - i-тый список символов
        for i, row in enumerate(self.field):
            #       № строки        собираем строку поля
            #                       из подсписка поля
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hid:  # если невидимость - истина
            res = res.replace("■", "O")  # меряем символы кораблей на символы пустых клеток
        return res
    
    def out(self, d): # проверяем, вышла ли точка за пределы поля
        # истина если не выполняется данное условие
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def shot(self, d):
        # проверяем на выстрел за границу поля и в занятую точку
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        # добавляем в список занятых
        self.busy.append(d)
        
        for ship in self.ships: # проходим по списку кораблей
            # если точка выстрела совпадает с одной из точек корабля (попадание)
            # if d in ship.dots:
            if ship.shooten(d):
                ship.lives -= 1 # уменьшаем жизни корабля
                self.field[d.x][d.y] = "X" # перерисовываем точку на символ ранения
                if ship.lives == 0: # если ни одной жизни не осталось (корабль потоплен)
                    self.count += 1 # увеличиваем счет
                    self.contour(ship, verb = True) # делаем контур видимым
                    print("Корабль уничтожен!")
                    return False # передаем ход
                else:
                    print("Корабль ранен!")
                    return True # продолжаем ходить
        # если попадания не было
        self.field[d.x][d.y] = "." # отрисовываем точку
        print("Мимо!")
        return False # передаем ход
    
    def begin(self):
        # в начале режима боя обнуляем список занятых точек
        # будем хранить выстрелы, убитые корабли с контурами
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if cords == ['q']:
                exit()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            # в мозгах с координаты начинаем с 0, а показываем с 1
            return Dot(x-1, y-1)

class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_place(self):
        # список длин кораблей
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        # попытки
        attempts = 0
        # проходим по списку длин кораблей
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                # пытаемся поставить на доску корабль со всеми рандомными характеристиками
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                # проверяем, поставился ли кораболь
                # ели да, выходим из уикла, переходим к след. кораблю
                try:
                    board.add_ship(ship)
                    break
                # если нет, выбрасываем исключение, переходим на след. итерацию вечника
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # для 100% расстановки кораблей
    def random_board(self):
        board = None
        # пока доска не создана, будет выполняться метод random_place
        while board is None:
            board = self.random_place()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
        print(" для дострочного выхода нажмите q ")

    
    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.board.defeat():
                print("-"*20)
                print("Пользователь выиграл!")
                input('Нажмите Enter.')
                break
            
            if self.us.board.defeat():
                print("-"*20)
                print("Компьютер выиграл!")
                input('Нажмите Enter.')
                break
            num += 1
            os.system('cls' if os.name == 'nt' else 'clear')
            
    def start(self):
        self.greet()
        self.loop()

            
g = Game()
g.start()

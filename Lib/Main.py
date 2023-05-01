from random import randint

# описание исключений

class BoardEx(Exception): # общий класс исключений для доски
    ...

class BoardUotEx(BoardEx): # выход за пределы доски
    def __str__(self):
        return "Вы вышли за пределы заданной доски"

class BoardSizeUotEx(BoardEx):
    def __str__(self):
        return "Вы задали неверный размер доски"

class BoardDoubleShotEx(BoardEx): # повтор выстрела в ту же клетку
    def __str__(self):
        return "Это поле уже битое :)"

class BoardWrongShipEx(BoardEx):
    def __str__(self):
        return "Ошибка при установке корабля"

# класс точка, для доски
class Dot():
    def __init__(self,x,y): # конструктор
        self.x=x
        self.y=y

    def __eq__(self, other): # перегрузка сравнения классов
        return self.x==other.x and self.y==other.y  # когда равны координаты

    def __repr__(self): # строковое представление объекта
        return f"( {self.x} ,  {self.y} )"

# класс корабля
class Ship:
    def __init__(self,l,p,direction): # строим корабль
        self.l=l # длина корабля
        self.p=p # точка носа корабля
        self.direction=direction # направление корабля (вертикальное 0/горизонтальное 1)
        self.lives=l # количество жизней корабля равно длине

    @property # делаем метод как свойство
    def dots(self): # все точки корабля
            ship_dots = [] # список точек корабля
            # вычисляем и заносим в список все точки корабля
            for j in range(self.l):
                x1=self.p.x # начинаем с точки вершины корабля
                y1=self.p.y
                if self.direction==0: # корабль расположен вертикально
                    x1+=j  # двигаемся по строкам вниз
                else: # корабль расположен горизонтально
                    y1+=j  # двигаемся по столбцам
                ship_dots.append(Dot(x1,y1)) # добавляем точку к списку точек корабля
            return ship_dots
    def shooten(self,shot):  # выстрел в корабль
        return shot in self.dots # true, если попали, точка находится в списке точек корабля

# класс доски
class Board:
    def __init__(self, size, hide=False):
        self.size=size # размер доски
        self.hide=hide # параметр отображения кораблей на доске
        self.ship_lives=0 # кол-во "живых" кораблей на доске
        # Двумерный список, в котором хранятся состояния каждой из клеток
        self.fields = [ ["O"]*size for _ in range(size)] # заполняем O при создании доски по размеру
        self.busy = []  # занятые клетки (кораблями и рядом с ними клетки), значения ■ X ., класс Dot
        self.shots = [] # клетки с выстрелами пользователя или отображаемое поле *, класс Dot
        self.ships= []  # список кораблей, класс Ship

    def add_ship(self, ship): # установка корабля на доску
        # проверяем, может ли этот корабль стать на доску, свободное ли место

        for k in ship.dots: # идем по точкам корабля
            if self.out(k) or k in self.busy: # если точка за пределами доски или занята
                raise BoardWrongShipEx()
        # можно устанавливать корабль, исключения нет
        for k in ship.dots:  # идем по точкам корабля
            self.fields[k.x][k.y]="■"  # заполняем точки корабля на доске
            #print('x='+str(k.x)+'  y='+str(k.y)+'   fields[k.x][k.y]='+self.fields[k.x][k.y])
            self.busy.append(k)         # данные точки делаем занятыми
        self.ships.append(ship)         # добавлям корабль к списку кораблей доски
        self.contour(ship)              # обводим контуром установленный корабль, что данные клетки заняты
        self.ship_lives += 1  # кол-во "живых" кораблей на доске, добавляем один


    # метод, который для точки (объекта класса Dot) возвращает True, если точка выходит за пределы поля, и False, если не выходит
    def out(self,p):
        return p.x<0 or p.x>=self.size or p.y<0 or p.y>=self.size

    # контур занятых клеток вокруг корабля, на них нельзя ставить другой корабль, но можно стрелять
    def contour(self, ship): # обводим корабль по контуру
        # опишем множество отступов координат точек вокруг корабля
        neighbor= [(-1, -1), (-1, 0) , (-1, 1),(0, -1) , (0 , 1),(1, -1), (1, 0) , (1, 1), (0,0)]
        # идем по точкам корабля
        for p in ship.dots:
            for px, py in neighbor: # бежим по соседним клеткам корабля
                p_current=Dot(p.x+px, p.y+py) # вычисление соседней точки
                # если точка не за пределами доски
                if not (self.out(p_current)):
                    self.busy.append(p_current) # вносим точку в мн-во занятых

    # прорисовка контура корабля для отображения
    def contour_print(self, ship, mark=True): # обводим корабль по контуру
        # опишем множество отступов координат точек вокруг корабля
        neighbor= [(-1, -1), (-1, 0) , (-1, 1),(0, -1) , (0 , 1),(1, -1), (1, 0) , (1, 1)]
        # идем по точкам корабля
        for p in ship.dots:
            for px, py in neighbor: # бежим по соседним клеткам корабля
                p_current=Dot(p.x+px, p.y+py) # вычисление соседней точки
                # если точка не за пределами доски и не в точках корабля
                if not (self.out(p_current)) and not (p_current in ship.dots):
                        #and p_current not in self.busy:
                    if self.fields[p_current.x][p_current.y]!="*": # если поле не стреляное
                        self.fields[p_current.x][p_current.y] = "." # помечаем соседние точки

    def __str__(self): # определяем вывод объекта в консоль
        if self.size>=10:
            s='   |'
        else:
            s="  |"
        for i in range(self.size): # отображение первой строки с цифрами
            if self.size >= 10 and i+1>=10:
                s+=" "+str(i+1)+"|"
            else:
                s+=" "+str(i+1)+" |"
        for i in range(self.size): # бежим по полям доски
            if self.size >= 10 and i+1<10:
                s+=f"\n {i+1} |"
            else:
                s+=f"\n{i+1} |"
            for j in range(self.size):
                s+=f" {self.fields[i][j]} |"
        if self.hide: # прячем корабли на доске
            s = s.replace("■", "O")
        return s

    def shot(self, p): # выстрел в доску, если выход за пределы, исключение
        if self.out(p): # если выстел за пределы доски
            raise BoardOutEx()
        if p in self.shots: # если в поле уже стреляли
            raise BoardDoubleShotEx()
        # помечаем поле, что мы сюда уже стреляли
        self.shots.append(p)
        for sh in self.ships: # перебираем все корабли на доске
            if p in sh.dots: # выстрел попал в корабль
                self.fields[p.x][p.y]='X' # рисуем подбитое поле корабля
                sh.lives-=1 # уменьшаем количество жизней корабля
                if sh.lives==0:  # если у корабля больше нет жизней
                    self.ship_lives-=1 # уменьшаем счетчик живых кораблей на доске на 1
                    self.contour_print(sh, mark=True) # обводим подбитый корабль, что в эти клетки стрелять смысла нет
                    print("Корабль уничтожен!")
                    if self.ship_lives!=0:
                        print(f"   (всего осталось) {self.ship_lives} кораблей")
                    return True # повторный ход
                else:
                    print("Корабль ранен!")
                    return True # повторный ход
        # помечаем клетку выстрела
        if self.fields[p.x][p.y] == ".":
            print("Не было смысла стрелять в эту клетку!")
        self.fields[p.x][p.y] = "*"  # помечаем клетку выстрела
        print("Мимо!")

        return False # нет повторного хода


    def start(self):    # начало действия доски
        busy=[]         # нет занятых клеток


class Player:
    def __init__(self, board, enemy):
        self.board = board # своя доска
        self.enemy = enemy # доска противника

    def ask(self):
        raise NotImplementedError()

    def move(self): # ход игрока
        while True:
            try:
                target = self.ask()                 # опрашиваем игрока, куда будет стрелять
                repeat = self.enemy.shot(target)    # выстрел по вражеской доске
                return repeat
            except BoardException as e:  # если что-то пошло не так, генерируем исключение
                print(e)

class AI(Player):
    def ask(self):
        # формируем случайную точку выстрела, с учетом размера доски
        p = Dot(randint(0,self.board.size-1), randint(0, self.board.size-1))
        # стреляем наугад, но проверяем, чтобы не стрелять туда, где уже стреляли
        while True:
            if p not in self.enemy.shots:
                print(f"Ход компьютера: {p.x + 1} {p.y + 1}")
                return p
            else:
                p = Dot(randint(0, self.board.size - 1), randint(0, self.board.size - 1))

    def move(self):
        while True:
            try:
                target = self.ask() # опрашиваем комп, куда будет стрелять
                repeat = self.enemy.shot(target) # выстрел по вражеской доске
                return repeat
            except BoardException as e:
                print(e)

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1) # координаты уменьшаем на 1, чтобы работать потом как с координатами массива fields

class Game:
    def __init__(self, size = 6, lens=[]): # минимальный размер поля для игры 6*6, набор кораблей пустой
        self.size = size
        self.lens = lens # набор кораблей, только их длины

    def generate(self):
        if len(self.lens)==0: # если спосок кораблей пуст, то генерируем
            self.lens = self.calc_len()
        print(f"Генерирую доски со случайной расстановкой кораблей {len(self.lens)} шт.")
        print("длины кораблей:")
        print(self.lens)
        players_board = self.random_board()  # генерация случайных досок
        comps_board = self.random_board()
        comps_board.hide = True  # прячем доску компьютера

        self.ai = AI(comps_board, players_board)  # игрок комп
        self.us = User(players_board, comps_board)  # игрок пользователь

    def random_board(self): # стабильная генерация случайной доски
        board = None
        while board is None:
            board = self.random_place()
        return board

    # расчет размеров и кол-ва кораблей на выбранной доске
    def calc_len(self):
        len=[]
        # процент поля заполенный кораблями 1/size*100 + (20-size) -1
        pr=round((1 / self.size * 100 + (20 - self.size)))
        s= round(self.size*self.size * pr/100)  # площадь заполнения кораблями
        while s!=0:
            # самый большой корабль должен быть меньше половины поля, при увеличении поля еще меньше
            r=round(self.size-self.size/2)
            if self.size>10:
                r-=1
            if self.size>15:
                r -= 2
            len.append(r)
            s=s-r
            # меньших корабля 2 шт
            r=r-1
            len.append(r)
            len.append(r)
            r = r - 1
            # ставим корабли, пока размер не равен 1 и площадь кораблей позволяет разместить 4 корабля одиночки
            while r!=1 and s>=6:
                # по 3 шт
                len.append(r)
                len.append(r)
                len.append(r)
                r = r - 1
            # в конце ставим 4 шт одиночки
            for i in range(4):
                len.append(r)
            s=0
        len.sort(reverse=True)  # сортрировка кораблей в обратном порядке, чтобы потом ставить с большего
        return len

    def random_place(self):
        board = Board(size = self.size)
        attempts = 0 # кол-во попыток установки корабля
        for l in self.lens:
            while True:
                attempts += 1 # увеличиваем счетчик попыток
                if attempts > 2000:
                    return None
                ship = Ship(l,Dot(randint(0, self.size), randint(0, self.size)), randint(0,1))
                #print('ship: l='+str(l)+' ('+str(ship.p.x)+','+str(ship.p.y)+'),'+str(ship.direction)  )
                # задаем случайную вершину для установки корабля и случайно ориентир, но заданной длинны
                try:
                    board.add_ship(ship)  # добавляем корабль на доску
                    break
                except BoardWrongShipEx: # ошибка установки корабля
                    pass
        board.start()
        return board

    def greet(self): # привествие
        print("Это игра Морской бой !")
        print(" формат ввода координат выстрела: x y (x - номер строки, y - номер столбца)")
        print("О - неизвестное (скрытое) поле")
        print("■ - неподбитый корабль на доске")
        print("X - подбитый корабль на доске")
        print(". - поле рядом с кораблем, куда стрелять не стоит")
        print("* - поле с выстрелом игрока")
        print("размер игровой доски "+str(self.size))
        print("-"*20)


    def loop(self): # игровой цикл
        num = 0 # номер хода
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0: # четный ход пользователя
                print("-"*20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else: # нечетный компа
                print("-"*20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat: # если повтор хода, то просто уменьшаем счетчик хода на 1, чтобы соблюдалась четность
                num -= 1

            if self.ai.board.ship_lives == 0: # нет живых кораблей на доске
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.us.board.ship_lives == 0: # нет живых кораблей на доске
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.generate()
        self.loop()


# тело программыы
s1=input('Задайте размер поля игры от 6 до 20:')
if (6<=int(s1)<=20):
    g = Game(int(s1))
else:
    raise BoardSizeUotEx

g.start()

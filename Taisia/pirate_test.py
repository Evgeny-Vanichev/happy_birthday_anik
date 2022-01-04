import thorpy, pygame, random
from questions import *
from level_completed import *
from game_over import *


class PirateTest(object):
    def __init__(self, count):
        self.count = count
        self.label = thorpy.make_text(text=f'Вопрос №{self.count + 1}',
                                      font_color=(0, 0, 255))
        self.radioButton1 = thorpy.Checker(questions[self.count + 1][1][0], type_="radio")
        self.radioButton2 = thorpy.Checker(questions[self.count + 1][2][0], type_="radio")
        self.radioButton3 = thorpy.Checker(questions[self.count + 1][3][0], type_="radio")
        self.radioButton4 = thorpy.Checker(questions[self.count + 1][4][0], type_="radio")
        self.checkButton = thorpy.make_button("Проверить", func=self.check)
        self.e_group_menu = thorpy.make_group([self.radioButton1, self.radioButton2,
                                               self.radioButton3, self.radioButton4])
        self.questionText = thorpy.make_text(text=questions[self.count + 1][0],
                                             font_color=(0, 0, 255))
        self.e_background = thorpy.Background(color=(200, 200, 255),
                                              elements=[self.questionText,
                                                        self.e_group_menu,
                                                        self.checkButton])
        thorpy.store(self.e_background, gap=20)

    def check(self):
        if (self.radioButton1.get_value() and questions[self.count + 1][1][1]) \
                or (self.radioButton2.get_value() and questions[self.count + 1][2][1]) \
                or (self.radioButton3.get_value() and questions[self.count + 1][3][1]) \
                or (self.radioButton4.get_value() and questions[self.count + 1][4][1]):
            self.count += 1
            if self.count >= 5:
                thorpy.functions.quit_menu_func()
                level_completed()
            else:
                self.e_background.update()
                self.e_background.blit()
                self.__init__(self.count)
                thorpy.functions.quit_menu_func()
                self.launch_game()
        else:
            thorpy.functions.quit_menu_func()
            game_over()

    def launch_game(self):
        menu = thorpy.Menu(self.e_background)
        menu.play()
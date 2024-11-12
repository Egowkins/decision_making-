from os import get_terminal_size
from sys import exception

import numpy as np
import pandas as pd
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class R_Matrix():

    def __init__(self, names=None, data=None) -> None:
        self.__matrix = pd.DataFrame()
        self.__names = None
        self.__data = None
        self.set_names(names)
        self.set_data(data)


    def get_data(self):
        return self.__data

    def set_data(self, data=None):
        self.__data = data

    def set_names(self, names=None):
        self.__names = names

    def get_names(self):
        return self.__names


    def get_matrix(self):
        return self.__matrix

    def get_length(self):
        return self.__matrix.shape[1]

    def get_width(self):
        return self.__matrix.shape[0]


    def fill_matrix(self, data=None, names=True, excel=True) -> pd.DataFrame:

        self.__data = data
        self.__names = names

        match self.__data,self.__names,excel:
            case (None, False, False):
                return self.__matrix

            case (self.__data, False, True):
                self.__matrix = pd.read_excel(self.__data, header=None, names=None, index_col=None)


            case (self.__data, True, True):
                self.__matrix = pd.read_excel(self.__data, index_col=0, header=0)


            case (self.__data, False, False):
                self.__matrix = pd.DataFrame(self.__data, index=None, columns=None)


    def get_matrix(self):
        return self.__matrix


    def risk_matrix(self) -> np.array:
        np_matrix = self.__matrix.to_numpy()

        w = self.get_width()
        n = self.get_length()


        risk_mx = np.zeros((w, n))
        for i in range(0, n, 1):

            b = max(np_matrix[:,i])
            risk_mx[:,i] = b

        #print(risk_mx)
        risk_mx -= np_matrix

        return risk_mx #valid

    def risk_mx_to_df(self):
        return pd.DataFrame(self.risk_matrix(), index=None, columns=None)


    def vald_cr(self)-> set:
        """
        Критерий Вальда:
        Работаем с матрицей исходов
        Ищем минимум по каждой строке и записываем в массив. Берем максимальное из полученных значений
        :return:Массив значений; Значение, соответствующие условию метода (type: set)
        """
        ans = self.get_matrix()
        answ = np.zeros(self.get_width())

        for i in range(self.get_width()):

            answ[i] = ans.iloc[i].min()

        i_win = np.where(answ == answ.max())
        win = answ[i_win]

        return  answ, win

    def maximax(self)-> set:
        """
        Критерий максимакса:
        Аналогично критерию Вальда, но в строках берем максимальное значение
        :return: Массив значений; Значение, соответствующие условию метода (type: set)
        """
        ans = self.get_matrix()
        answ = np.zeros(self.get_width())

        for i in range(self.get_width()):

            answ[i] = ans.iloc[i].max()

        i_win = np.where(answ == answ.max())
        win = answ[i_win]

        return answ, win



    def laplas(self)->pd.DataFrame:
        """
        Критерий Лапласа:
        Ищем средний выйгрыш по каждой из стратегий (по строкам) и записываем в массив.
        Из полученного массива выбираем наибольшее значение
        :return: Массив значений; Значение, соответствующие условию метода (type: set)
        """
        #
        ans = self.get_matrix()
        answ = np.zeros(self.get_width())

        for i in range(self.get_width()):
            #print(self.get_length())
            answ[i] = round(sum(ans.iloc[i]) / self.get_length(),2)

        i_win = np.where(answ == answ.max())
        win = answ[i_win]

        return answ, win

    def sevidg(self) -> set:
        """
        Критерий Сэвиджа
        Строим матрицу рисков
        Берем максимальное значение по строке, записываем в массив. Далее берем минимальное из полученного массива
        :return: Массив значений; Значение, соответствующие условию метода (type: set)
        """
        ans = self.risk_mx_to_df()
        answ = np.zeros(self.get_width())

        for i in range(self.get_width()):

            answ[i] = ans.iloc[i].max()

        i_win = np.where(answ == answ.min())
        win = answ[i_win]

        return answ, win


    def gurvic(self, alpha=0.5)->pd.DataFrame:
        if  0 > alpha > 1:
            print('Некорректное значение альфа, должно лежать в пределах [0;1]')
        ans = self.get_matrix()
        answ = np.zeros(self.get_width())

        for i in range(self.get_width()):

            answ[i] = alpha * ans.iloc[i].max() + (1-alpha) * ans.iloc[i].min()

        i_win = np.where(answ == answ.max())
        win = answ[i_win]

        return answ, win


    def baies(self, p:(list, np.array))->set:

        if sum(p) != 1:
            raise ValueError('Сумма вероятностей не равна 0')

        ans = self.get_matrix()
        answ = np.zeros(self.get_width())

        for i in range(self.get_width()):

            answ[i] = sum(ans.iloc[i] *p[i])
            #ans.iloc[i] = ans.iloc[i] * p[i]
        i_win = np.where(answ == answ.max())
        win = answ[i_win]
        #print(ans)

        return answ, win



if __name__ == '__main__':
    a = R_Matrix()
    a.fill_matrix('risk/risk.xlsx', True, True)
    print(f'{'-' * 70}')
    print(f'{'-' * 70}')
    print('Исходная матрица:')
    print(a.get_matrix())
    print(f'{'-' * 70}')
    print(f'{'-' * 70}')
    print('Матрица рисков:')
    print(a.risk_matrix())
    print(f'{'-' * 70}')
    print(f'{'-' * 70}')
    print('Критерий Вальда')
    #print(a.__names)
    abob = a.vald_cr()
    print(f'\nМассив полученных значений :{abob[0].tolist()} \nЗначение, подходящее под критерии: {int(abob[1])}'
          f'\nНомер выйгрышной стратегии: {int(np.where(abob[0] == abob[1])[0])+1}')
    #print(a.vald_cr())
    print(f'{'-' * 70}')
    print('Критерий Максимакса')
    abob = a.maximax()
    print(f'\nМассив полученных значений :{abob[0].tolist()} \nЗначение, подходящее под критерии: {int(abob[1])}'
          f'\nНомер выйгрышной стратегии: {int(np.where(abob[0] == abob[1])[0])+1}')
   # print(a.maximax())
    print(f'{'-' * 70}')
    print('Критерий Лапласа')
    abob = a.laplas()
    print(f'\nМассив полученных значений :{abob[0].tolist()} \nЗначение, подходящее под критерии: {int(abob[1])}'
          f'\nНомер выйгрышной стратегии: {int(np.where(abob[0] == abob[1])[0])+1}')
    #print(a.laplas())
    print(f'{'-' * 70}')
    print('Критерий Севиджа')
    abob = a.sevidg()
    print(f'\nМассив полученных значений :{abob[0].tolist()} \nЗначение, подходящее под критерии: {int(abob[1])}'
          f'\nНомер выйгрышной стратегии: {int(np.where(abob[0] == abob[1])[0])+1}')
    #print(a.sevidg())
    print(f'{'-' * 70}')
    print('Критерий Гурвица')
    abob = a.gurvic(0.5)
    print(f'\nМассив полученных значений :{abob[0].tolist()} \nЗначение, подходящее под критерии: {int(abob[1])}'
          f'\nНомер выйгрышной стратегии: {int(np.where(abob[0] == abob[1])[0])+1}')
    #print(a.gurvic(0.5))
    print(f'{'-' * 70}')
    print('Критерий Байеса')
    abob = a.baies([0.5, 0.3, 0.1, 0.1])
    print(f'\nМассив полученных значений :{abob[0].tolist()} \nЗначение, подходящее под критерии: {int(abob[1])}'
          f'\nНомер выйгрышной стратегии: {int(np.where(abob[0] == abob[1])[0])+1}')
    #print(a.baies([0.5, 0.3, 0.1, 0.1]))


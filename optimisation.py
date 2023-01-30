import pandas as pd
import math
import random
import time
import matplotlib.pyplot as plt


def time_of_work(func):
    def wrapper(self):
        start = time.time()
        func(self)
        end = time.time()
        print("[Function time]", func.__name__, "[time]:", end - start)
    return wrapper


class Matrices:

    def __init__(self, data_file_csv='Circle_coord.csv'):
        self.data = None
        self.__distance_matrix = None
        self.data_file_csv = data_file_csv

    def __init_data_table(self):
        self.data = pd.read_csv(self.data_file_csv)
        self.data.style.format({
             'x_coordinate': '{:,.2f}'.format,
             'y_coordinate': '{:,.2f}'.format,
        })

    def __process_table(self):
        self.data.sort_values(by='name')

    def print_data_table(self):
        print(self.data)

    @time_of_work
    def init_distance_matrix(self):
        self.__init_data_table()
        self.__process_table()
        # self.print_data_table()
        self.__distance_matrix = pd.DataFrame()
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                if i == j:
                    self.__distance_matrix.at[i, j] = 0
                    continue
                self.__distance_matrix.at[i, j] = math.sqrt(abs(self.data.loc[i, 'x_coordinate'] -
                                                                self.data.loc[j, 'x_coordinate']) ** 2 +
                                                            abs(self.data.loc[i, 'y_coordinate'] -
                                                                self.data.loc[j, 'y_coordinate']) ** 2)

    def print_distance_matrix(self):
        print(self.__distance_matrix.to_string())

    def get_index(self, point_name):
        return self.data.set_index('name').index.get_loc(point_name)

    def get_distance(self, first_point, second_point):
        # print(self.__get_index(first_point))
        # print(self.__get_index(second_point))
        # print(self.__distance_matrix.at[self.__get_index(first_point), self.__get_index(second_point)])
        return self.__distance_matrix.at[first_point, second_point]

    def get_inverse_distance(self, first_point, second_point):
        if first_point == second_point:
            return 0
        else:
            return 1 / self.__distance_matrix.at[first_point, second_point]

    def get_points_count(self):
        return len(self.data)

    """
    def get_path_length(self):
        p_length = 0
        for i in range(len(self.__best_path) - 1):
            p_length = p_length + self.get_distance(self.__best_path[i], self.__best_path[i + 1])
        return p_length
    """


class ACO(Matrices):
    def __init__(self):
        Matrices.__init__(self)

        # ==========================================SETTINGS==========================================
        # Count of ants in each generation
        self.ant_count = 1
        # Count of generation(iteration)
        self.generations_count = 8
        # Alpha
        self.alfa = 1
        # Beta
        self.beta = 2
        # Initial pheromone [tau]
        self.initial_pheromone = 0.1
        # Pheromone quantity
        self.pheromone_quantity = 1
        # Pheromone evaporation coefficient [p]
        self.evaporation_coefficient = 0.1
        # =============================================================================================
        self.__pheromone_matrix = None
        self.__ant_path_matrix = None
        self.__best_path = 1000000000000000
        self.__best_order = []

    # @time_of_work
    def __init_pheromone_matrix(self):
        self.__pheromone_matrix = pd.DataFrame()
        for i in range(self.get_points_count()):
            for j in range(self.get_points_count()):
                # self.__pheromone_matrix.at[i, j] = self.initial_pheromone
                # self.__pheromone_matrix._set_value(i, j, self.initial_pheromone)

    # @time_of_work
    def __init_ant_path_matrix(self):
        self.__ant_path_matrix = pd.DataFrame()

    def print_pheromone_matrix(self):
        print(self.__pheromone_matrix.to_string())

   #  @time_of_work
    def __get_pheromone_value(self, current_position, perspective_position):
        return self.__pheromone_matrix.loc[current_position, perspective_position]

    def __set_rand_points(self):
        for i in range(self.ant_count):
            # self.__ant_path_matrix.at[0, i] = random.randint(0, self.get_points_count() - 1)
            self.__ant_path_matrix._set_value(0, i, (random.randint(0, self.get_points_count() - 1)))
        """
        for i in range(1, self.get_points_count()):
            for j in range(self.ant_count):
                self.__ant_path_matrix.at[i, j] = None
        """

    def print_ant_path_matrix(self):
        # self.__set_rand_points()
        print(self.__ant_path_matrix.to_string())

    def __get_probability_of_transition(self, current_position, perspective_position, ant_number, count_of_iter):
        if self.__is_tabu(ant_number, count_of_iter, perspective_position):
            return 0.0
        else:
            return (self.__get_pheromone_value(current_position, perspective_position) ** self.alfa) * \
                   (self.get_inverse_distance(current_position, perspective_position) ** self.beta)

    def __is_tabu(self, ant_number, count_of_iter, current_value):
        for i in range(0, count_of_iter):
            if self.__ant_path_matrix.at[i, ant_number] == current_value:
                return True
        return False

    def __get_new_point(self, current_position, ant_number, count_of_iter):
        probability_sum = 0
        max_probability = 0
        max_probability_city = 0

        # print("[Find new point] \ncurrent_position: {} \nant_number: {} \ncount_of_iter: {}".format(current_position,
        # ant_number,
        # count_of_iter))

        for i in range(self.get_points_count()):
            probability_sum += self.__get_probability_of_transition(current_position, i, ant_number, count_of_iter)

        for i in range(self.get_points_count()):
            prob = self.__get_probability_of_transition(current_position, i, ant_number,
                                                        count_of_iter) / probability_sum
            if prob > max_probability:
                max_probability = prob
                max_probability_city = i
            # print("Current pos: {}; Perspective pos: {}; Probability: {}".format(current_position, i, prob))
        # print("max_probability: {} \nmax_probability_city: {}".format(max_probability, max_probability_city))
        return max_probability_city

    def __add_point(self, ant_number, iteration):
        value = self.__get_new_point(self.__ant_path_matrix.at[iteration, ant_number], ant_number, iteration + 1)
        self.__ant_path_matrix.at[iteration + 1, ant_number] = value
        # self.__ant_path_matrix._set_value(iteration + 1, ant_number,  value)

    def __create_ant_path_matrix(self):
        self.__set_rand_points()
        for point in range(0, (self.get_points_count() - 1)):
            for ant in range(0, self.ant_count):
                self.__add_point(ant, point)

    def __get_path_length(self, input_list):
        p_length = 0
        for i in range(len(input_list) - 1):
            p_length = p_length + self.get_distance(input_list[i], input_list[i + 1])
        return p_length

    def __select_best_local_path(self):
        best_path = self.__get_path_length(self.__ant_path_matrix[0].to_list())
        best_order = self.__ant_path_matrix[0].to_list()
        for i in range(self.ant_count):
            # print(i, ":", self.__get_path_length(self.__ant_path_matrix[i].to_list()))
            if self.__get_path_length(self.__ant_path_matrix[i].to_list()) < best_path:
                best_path = self.__get_path_length(self.__ant_path_matrix[i].to_list())
                best_order = self.__ant_path_matrix[i].to_list()
        if best_path < self.__best_path:
            self.__best_path = best_path
            self.__best_order = best_order
        # print(best_path)
        # print(best_order)

    def __set_pheromone(self):
        for ant in range(self.ant_count):
            pheromone = self.pheromone_quantity / self.__get_path_length(self.__ant_path_matrix[ant].to_list())
            for i in range(0, self.get_points_count() - 1):
                self.__pheromone_matrix.at[
                    self.__ant_path_matrix.iloc[i, ant], self.__ant_path_matrix.iloc[i + 1, ant]] += pheromone
                self.__pheromone_matrix.at[
                    self.__ant_path_matrix.iloc[i + 1, ant], self.__ant_path_matrix.iloc[i, ant]] += pheromone

    # def __pheromone_evaporation(self):

    def plot_path(self):
        x = []
        y = []
        for i in range(len(self.__best_order)):
            x.append(self.data.loc[self.__best_order[i], 'x_coordinate'])
            y.append(self.data.loc[self.__best_order[i], 'y_coordinate'])
            plt.plot(self.data.loc[self.__best_order[i], 'x_coordinate'],
                     self.data.loc[self.__best_order[i], 'y_coordinate'], 'bo', linewidth=2)
        plt.plot(x, y, linewidth=0.5)
        # plt.show(block=False)
        plt.show()
        # time.sleep(2)
        # plt.cla()

    def aco_solve(self):

        start = time.time()

        self.__init_pheromone_matrix()
        end = time.time()
        print("[__init_pheromone_matrix]:", end - start)
        self.__init_ant_path_matrix()

        start = time.time()
        for i in range(self.generations_count):
            print("[Iteration]: {}".format(i))

            st1 = time.time()
            self.__create_ant_path_matrix()
            end1 = time.time()
            print("__create_ant_path_matrix:", end1 - st1)

            st2 = time.time()
            self.__select_best_local_path()
            end2 = time.time()
            print("__select_best_local_path:", end2 - st2)

            st3 = time.time()
            self.__set_pheromone()
            end3 = time.time()
            print("__set_pheromone:", end3 - st3)


        end = time.time()

        self.print_pheromone_matrix()
        self.print_ant_path_matrix()
        
        
        print("[Best path]:", self.__best_path)
        print("[Best order]:", self.__best_order)

        self.plot_path()





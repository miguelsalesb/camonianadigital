import os
import csv


def read_csv(filename):

    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=';')
            # necessário remover elementos vazios
            filtered_list = [x for x in csv_reader if x]
    return filtered_list
import csv
import os


class BlankObj:
    def __init__(self, blank=None, is_exception=False):
        self.blank = blank if not (is_exception and not issubclass(type(blank), BaseException)) else BaseException(blank)
        self.is_exception = issubclass(type(blank), BaseException) or is_exception

    def __repr__(self):
        return repr(self.blank)

    def __str__(self):
        return str(self.blank)

    def release(self):
        if self.is_exception:
            raise self.blank

        return self.blank


class FileReader:
    def __init__(self, file_path, blank=BlankObj()):
        self.path = file_path
        if isinstance(blank, BlankObj):
            self.blank = blank
        else:
            self.blank = BlankObj(blank)

    def __read__(self):
        pass

    def __re_alert__(self, reader, blank):
        try:
            return reader()
        except IOError:
            return blank.release()
        else:
            raise BaseException('unknown error')

    def read(self):
        return self.__re_alert__(self.__read__, self.blank)

    def simple_read(self):
        return self.__read__()


class TxtFileReader(FileReader):
    def __init__(self, path, blank=BlankObj('')):
        super().__init__(path, blank)

    def __read__(self):
        result = ''
        with open(self.path) as file:
            result = file.read()
        return result


class CsvReader(FileReader):
    def __init__(self, path, blank=BlankObj([]), delimiter=';'):
        super().__init__(path, blank)
        self.delimiter = delimiter

    def __read__(self):
        res = []
        with open(self.path) as f_csv:
            reader = csv.reader(f_csv, delimiter=self.delimiter)
            next(reader)
            for row in reader:
                res.append(row)
        return res


class BaseCar:
    def __init__(self, photo, brand, carry):
        self.photo_file_name = photo
        self.brand = brand
        self.carrying = float(carry)
        if self.get_photo_file_ext() == '':
            raise ValueError('Bad Photo Extension')

    def get_photo_file_ext(self):
        res = os.path.splitext(self.photo_file_name)
        return res[1]


class Car(BaseCar):
    def __init__(self, photo, brand, carry, passengers):
        super().__init__(photo, brand, carry)
        self.passenger_seats_count = int(passengers)


class Truck(BaseCar):
    def __init__(self, photo, brand, carry, body_whl):
        super().__init__(photo, brand, carry)
        self.body_width = 0.0
        self.body_height = 0.0
        self.body_length = 0.0
        self.get_body_volume(body_whl)

    def get_body_volume(self, body_whl):
        if body_whl != '':
            whl_list = str(body_whl).split('x')
            if len(whl_list) != 3:
                raise ValueError('Bad whl')
            self.body_length = float(whl_list[0])
            self.body_width = float(whl_list[1])
            self.body_height = float(whl_list[2])


class SpecCar(BaseCar):
    def __init__(self, photo, brand, carry, extra):
        super().__init__(photo, brand, carry)
        self.extra = extra


class CsvRow:
    def __init__(self, type, brand, passengers, photo, whl, carry, extra):
        self.type = type
        self.brand = brand
        self.passengers = passengers
        self.photo = photo
        self.whl = whl
        self.carry = carry
        self.extra = extra

    def create_car(self):
        if self.type == 'car':
            return Car(self.photo, self.brand, self.carry, self.passengers)
        elif self.type == 'truck':
            return Truck(self.photo, self.brand, self.carry, self.whl)
        elif self.type == 'spec_machine':
            return SpecCar(self.photo, self.brand, self.carry, self.extra)


def get_car_list(csv_filename):
    file = CsvReader(csv_filename)
    csv_ = file.read()
    result = []
    for row in csv_:
        try:
            tmp = CsvRow(*row)
            result.append(tmp.create_car())
        except (ValueError, TypeError) as d:
            print(f'Incorret file row: {row}. Exception: {d.args[0]}')

    return result


if __name__ == '__main__':
    total = get_car_list(r'D:\Users\HardCorn\Desktop\python\coursera_week3_cars.csv')
    print(total)
    for each in total:
        print (each.__dict__)
    # a = ValueError('некий текст')
    # b = BlankObj(None, True)
    # f = CsvReader(r'D:\Users\HardCorn\Desktop\python\coursera_week3_cars.csv',b)
    # res = f.read()
    # print(res)
    # f2 = TxtFileReader(r'D:\Users\HardCorn\Desktop\python\coursera_week3_cars.csv',a)
    # res2 = f2.read()
    # print(res2)
    # print(repr(b))

    # get_car_list(r'D:\Users\HardCorn\Desktop\python\coursera_week3_cars.csv')
    # a = BaseCar(r'sdf/sdfasdf/sdfo/sd.ffx', 'honda', '20')
    # print(a.get_photo_file_ext())
    #
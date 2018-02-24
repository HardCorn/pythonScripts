import expressions as exp


class Filter:
    def __init__(self, logic_clause):
        self.data = self.parse(logic_clause)

    def parse(self, logic_clause):
        res_dict = dict()

        return res_dict

    def logic_refactor(self, logic_clause):
        pass


if __name__ == '__main__':
    str = "1 = 0 and 1 not in '' or ('2018-01-01' < '2018-01-02') and self_name is none ('22', '33', '44')"

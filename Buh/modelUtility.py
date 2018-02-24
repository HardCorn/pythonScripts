import expressions as exp
import modelExceptions as me


class Filter:
    def __init__(self):
        self.parser = exp.ExpressionParser()
        self.expr = None
        self.dictionary = dict()

    def set_clause(self, str_):
        self.expr = self.parser.parse(str_)

    def set_str(self, row_, row_head):
        tmp_dic = dict()
        for num in range(len(row_head)):
            tmp_dic[row_head[num]] = row_[num]
        self.dictionary = tmp_dic

    def get_result(self):
        if type(self.expr) == bool:
            return self.expr
        elif isinstance(self.expr, exp.Expression):
            self.expr.reset(self.dictionary)
            return self.expr.evaluate()
        elif self.expr is None:
            raise me.FilterException('Expression is None! Can\'t filter with it!')
        else:
            raise me.FilterException('Unknow expression type {}. Can\'t filter with it!'.format(type(self.expr)))


if __name__ == '__main__':
    str = "1 = 0 and 1 not in '' or ('2018-01-01' < '2018-01-02') and self_name is none ('22', '33', '44')"

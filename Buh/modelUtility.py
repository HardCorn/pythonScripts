import expressions as exp
import modelExceptions as me


class Filter:
    def __init__(self):
        self.expr = None
        self.dictionary = dict()
        self.row_head = None

    def set_clause(self, str_):
        self.expr = exp.parse(str_)

    def set_row_head(self, row_head):
        self.row_head = row_head

    def set_row(self, row_):
        if len(self.row_head) != len(row_):
            raise me.FilterException('Set row', 'desync row with it\'s metadata: row_head: {0}, row: {1}'.format(
                self.row_head, row_
            ))
        self._set_str(row_, self.row_head)

    def _set_str(self, row_, row_head):
        tmp_dic = dict()
        for num in range(len(row_head)):
            tmp_dic[row_head[num]] = row_[num]
        self.dictionary = tmp_dic

    def try_resolve(self):
        if type(self.expr) == bool:
            return self.expr
        try:
            return self.expr.evaluate()
        except:
            return None

    def resolve(self, row_):
        self.set_row(row_)
        return self.get_result()

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
    a = Filter()
    a.set_clause("date_field = '2018-04-01'")
    n = a.try_resolve()
    a.set_row_head(['date_field'])
    b = a.resolve(['2018-04-01'])
    print(n)
    print(b)

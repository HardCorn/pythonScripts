import dates as dt
import expressions as exp
import operations as op
import smartSplit as ss
import utility as ut





class ExpressionParser:
    def __init__(self, str_):
        self.str_ = str_.lower()

    def _try_build(self):


    def parse(self):
        str_stack = ut.Stack(ss.smart_split(self.str_, exp.OPERATOR_LIST, ' \t\n'))
        operand_stack = ut.Stack()
        bool_stack = ut.Stack()
        compare_stack = ut.Stack()
        control_stack = ut.Stack()
        arithmetic_stack = ut.Stack()
        while not str_stack.is_empty():
            val = str_stack.next()
            if val not in op.OPERATIONS:
                pass


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
    print(str)
    print(ss.smart_split(str, exp.OPERATOR_LIST))

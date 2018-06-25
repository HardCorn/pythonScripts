import modelManager as mm
import dates as dt
import buhExceptions as be
# Accounting_plan
# Accounts
# Entry
# Balance
# Advanced_quota


class BuhData:
    def __init__(self): #, plan, accounts, entry, balance, month_quota, cumulative_quota, year_quota):
        self.plan = None # plan
        self.accounts = None # accounts
        self.entry = None # entry
        self.balance = None # balance
        self.month_quota = None # month_quota
        self.cumulate_quota = None # cumulative_quota
        self.year_quota = None # year_quota
        self.base = None
        self.initialized = False

    def read(self, manager : mm.ModelManager, entry_depth=1, base_name=None):
        if self.initialized:
            raise be.BuhDataError('Data container already initialized!')
        self.plan = manager.read_model_data('Accounting_plan', worker_name=base_name, build_view_flg=True)
        self.accounts = manager.read_model_data('Accounts', worker_name=base_name, build_view_flg=True)
        cur_date = dt.current_date()
        date = cur_date - dt.timedelta(entry_depth)
        self.entry = manager.read_model_data('Entry', partition_filter='entry_date >= ' + dt.date_to_str(date),
                                        worker_name=base_name, build_view_flg=False)
        self.balance = manager.read_model_data('Balance', worker_name=base_name, build_view_flg=True)
        self.month_quota = manager.read_model_data('Advanced_quota', partition_filter='quota_type = \'month\' '+
                                                   ' and month = {0} and year = {1}'.format(str(cur_date.month), str(cur_date.year)), build_view_flg=False)
        self.year_quota = manager.read_model_data('Advanced_quota', partition_filter='quota_type = \'year\' ' +
                                                  ' and year = {}'.format(str(cur_date.year)), build_view_flg=False)
        self.cumulate_quota = manager.read_model_data('Advanced_quota', partition_filter='quota_type = \'cumulative\' '+
                                                      ' and month = {0} and year = {1}'.format(str(cur_date.month), str(cur_date.year)), build_view_flg=False)
        self.initialized = True
        self.base = base_name

    def write(self, manager : mm.ModelManager):
        manager.write_model_data('Accounting_plan', self.plan)
        manager.write_model_data('Accounts', self.accounts)
        manager.write_model_data('Entry', self.entry)
        manager.write_model_data('Balance', self.balance)
        curr = dt.current_date()
        drop_clause = 'year = {0} and (month = {1} or quota_type = \'year\')'.format(str(curr.year), str(curr.month))
        manager.drop_model_partition('Advanced_quota', drop_clause, self.base)
        manager.write_model_data('Advanced_quota', self.month_quota)
        manager.write_model_data('Advanced_quota', self.year_quota)
        manager.write_model_data('Advanced_quota', self.cumulate_quota)

    def add_entry(self, entry_data):
        if not isinstance(entry_data, list) and not isinstance(entry_data, tuple):
            raise be.BuhDataError('Incorrect entry_data data type: {}!'.format(type(entry_data)))


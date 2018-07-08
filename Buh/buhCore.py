import modelManager as mm
import dates as dt
import buhExceptions as be
# Accounting_plan
# Accounts
# Entry
# Balance
# Advanced_quota

# Используется упрощенная схема:
#     дебет - счет списания (источник)
#     кредит - счет зачисления (некое благо)


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
        self.date = None
        self.buffer = None
        self.initialized = False

    def _get_balance_date(self, manager : mm.ModelManager, base_name=None, filter='1=1'):
        parts = manager.get_model_parts_list('Balance', base_name, filter)
        if len(parts) > 0:
            parts = max(parts)
            pre_date = dt.dateRange(parts)
            month = pre_date.month if not isinstance(pre_date.month, range) else 1
            pre_date = dt.date(pre_date.year, month, 1)
            pre_date = dt.date_to_str(pre_date)
            bal_date = manager.read_model_data('Balance', partition_filter='balance_date >= {}'.format(pre_date), data_filter=filter,
                                               selected_attrs=['balance_date'], worker_name=base_name,
                                               build_view_flg=False)
            bal_date = max([each[0] for each in bal_date])
            return bal_date
        else:
            return None

    def read(self, manager : mm.ModelManager, entry_depth=1, balance_date=None, base_name=None):
        if self.initialized:
            raise be.BuhDataError('Data container already initialized!')
        self.plan = manager.read_model_data('Accounting_plan', worker_name=base_name, build_view_flg=True)
        self.accounts = manager.read_model_data('Accounts', data_filter='actual_account_flg = 1', worker_name=base_name,
                                                build_view_flg=True)
        if balance_date is None:
            bal_dt = self._get_balance_date(manager, base_name)
            if bal_dt is not None:
                balance_filter = 'balance_date = ' + dt.date_to_str(bal_dt)
            else:
                balance_filter = '1=0'
        elif isinstance(balance_date, str):
            balance_filter = 'balance_date = {}'.format(balance_date)
        elif isinstance(balance_date, dt.dt.date):
            balance_filter = 'balance_date = ' + dt.date_to_str(balance_date)
        elif isinstance(balance_date, dt.dt.datetime):
            balance_filter = 'balance_date = ' + dt.date_to_str(balance_date.date())
        else:
            raise be.BuhDataError('Incorrect input: balance_date = {0} (type: {1})'.format(balance_date, type(balance_date)))
        cur_date = dt.current_date()
        date = cur_date - dt.timedelta(entry_depth)
        self.entry = manager.read_model_data('Entry', partition_filter='entry_date >= ' + dt.date_to_str(date),
                                             data_filter='entry_date >= ' + dt.date_to_str(date), worker_name=base_name, build_view_flg=False)
        self.balance = manager.read_model_data('Balance', partition_filter=balance_filter, data_filter=balance_filter,
                                               worker_name=base_name, build_view_flg=True)
        for each in self.balance:
            self.balance[each]['balance_date'] = cur_date
        self.date = cur_date
        self.month_quota = manager.read_model_data('Advanced_quota', partition_filter='quota_type = \'month\' '+
                                                   ' and month = {0} and year = {1}'.format(str(cur_date.month), str(cur_date.year)), build_view_flg=False)
        self.year_quota = manager.read_model_data('Advanced_quota', partition_filter='quota_type = \'year\' ' +
                                                  ' and year = {}'.format(str(cur_date.year)), build_view_flg=False)
        self.cumulate_quota = manager.read_model_data('Advanced_quota', partition_filter='quota_type = \'cumulative\' ' +
                                                      ' and month = {0} and year = {1}'.format(str(cur_date.month), str(cur_date.year)), build_view_flg=False)
        self.initialized = True
        self.base = base_name

    def write(self, manager : mm.ModelManager):
        if self.plan is not None:
            manager.write_model_data('Accounting_plan', self.plan)
        if self.accounts is not None:
            manager.write_model_data('Accounts', self.accounts)
        if self.entry is not None:
            manager.write_model_data('Entry', self.entry)
        if self.balance is not None:
            manager.write_model_data('Balance', self.balance)
        curr = dt.current_date()
        drop_clause = 'year = {0} and (month = {1} or quota_type = \'year\')'.format(str(curr.year), str(curr.month))
        manager.drop_model_partition('Advanced_quota', drop_clause, self.base)
        manager.write_model_data('Advanced_quota', self.month_quota)
        manager.write_model_data('Advanced_quota', self.year_quota)
        manager.write_model_data('Advanced_quota', self.cumulate_quota)

    def add_entry(self, entry_data, manager : mm.ModelManager):
        if not isinstance(entry_data, list) and not isinstance(entry_data, tuple):
            raise be.BuhDataError('Incorrect entry_data data type: {}!'.format(type(entry_data)))
        data = list(entry_data)
        self.entry.append(data)
        for num in (1,2):   # 1 - счет списания, 2 - счет зачисления, 3 - сумма проводки
            acct_list = list()
            curr_acct = data[num]
            consolid_acct = self.accounts[curr_acct]['consolid_account_num']
            acct_list.append(curr_acct)
            while consolid_acct != -1:
                acct_list.append(consolid_acct)
                consolid_acct = self.accounts[consolid_acct]['consolid_account_num']
            if data[4] != self.date:
                bal_dt = self._get_balance_date(manager, self.base, 'balance_date <= {}'.format(dt.date_to_str(data[4])))
                if bal_dt is not None:
                    if bal_dt == data[4]:
                        data_filt = 'balance_date >= {0} and account_num in {1}'.format(dt.date_to_str(bal_dt), tuple(acct_list))
                    else:
                        data_filt = 'balance_date = {0} or (balance_date > {0} and account_num in {1})'.format(dt.date_to_str(bal_dt), tuple(acct_list))
                    balance_data = manager.read_model_data('Balance', 'balance_date >= {}'.format(dt.date_to_str(bal_dt)),
                                                       data_filt, worker_name=self.base, build_view_flg=False)
                    for each in balance_data:
                        bal_amount = each[1]
                        if num == 1:
                            bal_amount -= data[3]
                        else:
                            bal_amount += data[3]
                        each[1] = bal_amount
                        if each[2] == bal_dt and bal_dt != data[4]:
                            each[2] = data[4]
                else:
                    balance_data = list()
            for each in acct_list:
                mnt = self.balance[each]['balance_amount']
                if num == 1:
                    mnt -= data[3]
                else:
                    mnt += data[3]
                self.balance[each]['balance_amount'] = mnt
        if data[6] == 0:
            gl_acc = self.accounts[data[2]]['gl_account_num']
            self.plan





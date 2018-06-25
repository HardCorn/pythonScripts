worker Main
name Accounting_plan
attrs (
    gl_account_num int key,
    account_description str,
    basic_quota_amount int,
    basic_qouta_type str
    )
loading mode r;

worker Main
name Accounts
attrs (
    account_num int key,
    gl_account_num int,
    account_description str
    )
loading mode a;

worker Main
name Entry
attrs (
    entry_num int key,
    debet_account_num int,
    credit_account_num int,
    entry_amount int,
    entry_date date partition 'YYYYMM',
    entry_desctiption str
    )
loading mode a;

worker Main
name Balance
attrs (
    account_num int key,
    balance_amount int,
    balance_date date partition 'YYYYMM'
    )
loading mode a;

worker Main
name Advanced_quota
attrs (
    quota_id int key,
    gl_account_num int,
    quota_amount int,
    quota_type str,
    year int,
    month int
    )
partition (year None, month None, quota_type None)
loading mode a;
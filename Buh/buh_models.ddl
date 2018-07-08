worker Main
name Accounting_plan
attrs (
    gl_account_num int key,
    gl_account_group str,
    account_description str,
    basic_quota_amount int,
    basic_qouta_type str,
    technical_account_flg int default 0,
    month_regeneration_flg int default 0,
    actual_account_num int
    )
loading mode r;

worker Main
name Accounts
attrs (
    account_num int key,
    gl_account_num int,
    account_description str,
    consolid_account_num int,
    account_holder str,
    actual_account_flg int default 1,
    account_year int,
    account_month int
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
    owner_name str,
    profit_flg int,
    entry_description str
    )
loading mode a;

worker Main
name Balance
attrs (
    account_num int,
    balance_amount int,
    balance_date date partition 'YYYYMM',
    row_id int key
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

worker Main
name id_mapper
attrs (
    model_name str key,
    real_key_value str
    
)
loading mode r;
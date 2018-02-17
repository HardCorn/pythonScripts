
call base.drop_table('a');
create table a as (
select 
proto.pk1
 , proto.pk2
 , proto.info1 
 , proto.info2
 , proto.info3
from P_TECH_PLAN_FACT_IS;SUE_DETAIL; as proto left join TECH_PLAN_FACT_ISSUE_DETAIL as etl on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where 
etl.pk1 is null
 or etl.pk2 is null
union
select 
etl.pk1
 , etl.pk2
 , etl.info1
 , etl.info2
 , etl.info3
from TECH_PLAN_FACT_ISSUE_DETAIL as etl left join P_TECH_PLAN_FACT_ISSUE_DETAIL as proto on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where proto.pk1 is null
) with data primary index (pk1,pk2);
call base.drop_table('b');
create table b as (
select 
proto.pk1
 , proto.pk2
 , proto.info1
 , proto.info2
 , proto.info3
from P_TECH_PLAN_FACT_ISSUE_DETAIL as proto left join TECH_PLAN_FACT_ISSUE_DETAIL as etl on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where 
etl.pk1 is null
 or etl.pk2 is null
union
select 
etl.pk1
 , etl.pk2
 , etl.info1
 , etl.info2
 , etl.info3
from TECH_PLAN_FACT_ISSUE_DETAIL as etl left join P_TECH_PLAN_FACT_ISSUE_DETAIL as proto on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where proto.pk1 is null
) with data primary index (pk1,pk2);
call base.drop_table('c');
create table c as (
select 
proto.pk1
 , proto.pk2
 , proto.info1
 , proto.info2
 , proto.info3
from P_TECH_PLAN_FACT_ISSUE_DETAIL as proto left join TECH_PLAN_FACT_ISSUE_DETAIL as etl on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where 
etl.pk1 is null
 or etl.pk2 is null
union
select 
etl.pk1
 , etl.pk2
 , etl.info1
 , etl.info2
 , etl.info3
from TECH_PLAN_FACT_ISSUE_DETAIL as etl left join P_TECH_PLAN_FACT_ISSUE_DETAIL as proto on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where proto.pk1 is null
) with data primary index (pk1,pk2);
call base.drop_table('d');
create table d as (
select 
proto.pk1
 , proto.pk2
 , proto.info1
 , proto.info2
 , proto.info3
from P_TECH_PLAN_FACT_ISSUE_DETAIL as proto left join TECH_PLAN_FACT_ISSUE_DETAIL as etl on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where 
etl.pk1 is null
 or etl.pk2 is null
union
select 
etl.pk1
 , etl.pk2
 , etl.info1
 , etl.info2
 , etl.info3
from TECH_PLAN_FACT_ISSUE_DETAIL as etl left join P_TECH_PLAN_FACT_ISSUE_DETAIL as proto on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where proto.pk1 is null
) with data primary index (pk1,pk2);
call base.drop_table('trp');
create table trp as (
select 
proto.pk1
 , proto.pk2
 , proto.info1
 , proto.info2
 , proto.info3
from P_TECH_PLAN_FACT_ISSUE_DETAIL as proto left join TECH_PLAN_FACT_ISSUE_DETAIL as etl on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where 
etl.pk1 is null
 or etl.pk2 is null
union
select 
etl.pk1
 , etl.pk2
 , etl.info1
 , etl.info2
 , etl.info3
from TECH_PLAN_FACT_ISSUE_DETAIL as etl left join P_TECH_PLAN_FACT_ISSUE_DETAIL as proto on
proto.pk1 = etl.pk1
 and proto.pk2 = etl.pk2
 and proto.info1 = etl.info1 or (proto.info1 is null and etl.info1 is null)
 and proto.info2 = etl.info2 or (proto.info2 is null and etl.info2 is null)
 and proto.info3 = etl.info3 or (proto.info3 is null and etl.info3 is null)
where proto.pk1 is null
) with data primary index (pk1,pk2);

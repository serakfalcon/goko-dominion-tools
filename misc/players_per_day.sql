select date, count(pname)
  from (select distinct date_trunc('day', time) as date, pname 
          from game join presult using(logfile)
         where not guest) as x
 group by date
 order by date asc;

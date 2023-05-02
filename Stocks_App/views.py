from django.shortcuts import render
from django.db import connection
from .models import Buying, Company, Investor, Stock, Transactions
from datetime import datetime


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def home(request):
    return render(request, 'home.html')


def query_results(request):
    # que1
    with connection.cursor() as cursor:
        cursor.execute("""
        with investors_ID as (
        select distinct s1.ID
        from (
            select distinct Buying.ID, Buying.tDate, Company.Sector
            from Buying
             inner join Company
             on Company.Symbol = Buying.Symbol
             ) as s1
        group by s1.ID, s1.tDate
        having count(s1.tDate) >= 8
        ),

    investors_names as(
        select Investor.ID, Investor.Name
        from investors_ID
        inner join Investor
         on Investor.id = investors_ID.ID
),

    Total_sum as (
    select s2.ID, round(sum(s2.sum), 3) as Total_Sum
    from (
             select s1.ID, s1.Symbol, s1.tDate, (s1.BQuantity * Stock.price) as sum
             from Stock
             inner join (
                 select Buying.ID, Buying.tDate, Buying.Symbol, Buying.BQuantity
                 from investors_Id
                          inner join Buying
                                     on Buying.id = investors_Id.ID
             ) as s1
             on Stock.tDate = s1.tDate and Stock.Symbol = s1.Symbol
         ) as s2
    group by s2.ID
)

    select investors_names.Name, Total_Sum.Total_Sum
    from investors_names
    inner join Total_sum
    on Total_Sum.ID = investors_names.ID
    order by Total_Sum desc
        """)
        sql_res1 = dictfetchall(cursor)

    # que2
    with connection.cursor() as cursor:
        cursor.execute("""
        with Total_Trade_Dates as (
        select count(b1.tDate) as total_trade_dates
        from (
             select distinct Buying.tDate
             from Buying
         ) as b1
        ),

        popular_company as(
        select b3.Symbol
        from (
              select b2.Symbol, b2.trade_dates_num, Total_Trade_Dates.total_trade_dates
              from Total_Trade_Dates
                  cross join
              (
                  select b1.Symbol, count(b1.tDate) as trade_dates_num
                  from (
                           select distinct Buying.Symbol, Buying.tDate
                           from Buying
                       ) as b1
                  group by Symbol
              ) as b2
             )as b3
         where b3.trade_dates_num > 0.5*b3.total_trade_dates
        ),

man_company_total_stock_amount as (
    select s2.id, s2.Symbol, s2.stocks_amount
    from (
             select s1.id, s1.Symbol, sum(s1.BQuantity) as stocks_amount
             from (
                      select Buying.ID, Buying.Symbol, Buying.tDate, Buying.BQuantity
                      from Buying
                               inner join popular_company
                                          on popular_company.Symbol = Buying.Symbol
                  ) as s1
             group by s1.ID, s1.Symbol
         )as s2
    where s2.stocks_amount > 10
),

man_company_total_stock_max_amount as (
    select s2.Symbol, s2.ID, s1.max_stocks_amount
    from (
         select m2.Symbol, max(m2.stocks_amount) as max_stocks_amount
         from (
                  select m1.Symbol, m1.id, m1.stocks_amount
                  from man_company_total_stock_amount as m1
                           inner join popular_company
                                      on popular_company.Symbol = m1.Symbol
              ) as m2
         group by m2.Symbol
        ) s1
    inner join man_company_total_stock_amount as s2
    on s1.Symbol = s2.Symbol and s1.max_stocks_amount = s2.stocks_amount
    )

    select m1.Symbol, Investor.Name, m1.max_stocks_amount as quantity
    from man_company_total_stock_max_amount as m1
    inner join Investor
    on m1.ID = Investor.ID
    order by m1.Symbol,Investor.ID
        """)
        sql_res2 = dictfetchall(cursor)

    # que3
    with connection.cursor() as cursor:
        cursor.execute("""
        with  single_bought_companies as (
         select Buying.Symbol, Buying.tDate as buy_date, Buying.ID
         from (
             select s1.Symbol
             from (
                      select Buying.Symbol, id, tDate
                      from Buying
                  ) as s1
             group by s1.Symbol
             having count(s1.Symbol) = 1
         ) as s2
         inner join Buying
        on Buying.Symbol = s2.Symbol
        ),

        next_date_price as(
        select Stock.Symbol,Stock.Price as new_price
        from (
             select s1.Symbol, min(s1.tDate) as next_buy_date
             from (
                  select Stock.Symbol, Stock.tDate
                  from single_bought_companies as t1
                           inner join Stock
                                      on Stock.Symbol = t1.Symbol and Stock.tDate > t1.buy_date
                    ) as s1
                     group by s1.Symbol
            )as b1
        inner join Stock
        on Stock.Symbol = b1.Symbol and Stock.tDate = b1.next_buy_date
        ),

    current_date_price as (
    select s1.ID, Stock.Symbol, s1.buy_date, Stock.Price as old_price
    from single_bought_companies as s1
    inner join Stock
    on s1.Symbol = Stock.Symbol and s1.buy_date = Stock.tDate
    ),

    groisa_company as(
    select s1.Symbol, s1.buy_date, s1.ID
    from (
         select c1.Symbol, c1.ID, c1.old_price, c2.new_price, c1.buy_date
         from current_date_price as c1
                  inner join next_date_price as c2
                             on c2.Symbol = c1.Symbol
     ) as s1
    where ((s1.new_price*100)/s1.old_price) - 100 > 3
    )

    select g.buy_date, g.Symbol, Investor.Name
    from groisa_company as g
    inner join Investor
    on Investor.ID = g.ID
    order by g.buy_date, g.Symbol
        """)
        sql_res3 = dictfetchall(cursor)
    dic = {'sql_res1': sql_res1,
           'sql_res2': sql_res2,
           'sql_res3': sql_res3
           }
    return render(request, 'query_results.html', dic)


def add_transaction(request):
    id_flag = False
    if request.method == 'POST' and request.POST:
        input_id = request.POST["id"]
        id_flag = not (Investor.objects.filter(id=input_id).exists())
        if id_flag:
            return render(request, 'add_transaction.html', {'id_flag': flag})
        new_amount = int(request.POST["amount"])
        today = datetime.today().strftime('%Y-%m-%d')
        user_records = Investor.objects.filter(id=input_id)  # לקיחת הרשומה לפי הid
        old_avail_cash = int(user_records.values_list()[0][2])
        is_user_trans_today = Transactions.objects.filter(id=input_id, tdate=today).exists()
        if is_user_trans_today:
            today_tran_record = Transactions.objects.filter(id=input_id, tdate=today)
            old_amount = int(today_tran_record.values_list()[0][2])

            # deletes the previous transaction record that was made today from db
            with connection.cursor() as cursor:
                cursor.execute("""
                delete
                from Transactions
                where ID=%s and tDate=%s """, [input_id, today])

            # creates the new transaction record that was made today in db
            with connection.cursor() as cursor:
                cursor.execute("""
                insert into Transactions(tDate,ID,TQuantity)
                 values (%s, %s, %s)
                 """, [today, input_id, new_amount])
            # the amount that will be added to the user's available cash
            new_amount = new_amount - old_amount
        else:
            # creates the new transaction record that was made today in db
            with connection.cursor() as cursor:
                 cursor.execute("""
                 insert into Transactions (tDate,ID,TQuantity)
                 values (%s, %s, %s)
                 """,[today,input_id,new_amount])

        new_avail_cash = old_avail_cash + new_amount
        Investor.objects.filter(id=input_id).update(availablecash=new_avail_cash)

    with connection.cursor() as cursor:
        cursor.execute("""
         select top 10 t.tDate,t.ID,t.TQuantity
         from Transactions as t
         order by t.tDate desc ,t.ID desc
         """)
        sql_res = dictfetchall(cursor)

    dic = {'sql_res': sql_res,
           'id_flag': id_flag
           }
    return render(request, 'add_transaction.html', dic)


def buy_stocks(request):
    cash_flag = False
    id_flag = False
    symbol_flag = False
    buy_flag = False
    dic = {'id_flag': id_flag,
           'symbol_flag': symbol_flag,
           'buy_flag': buy_flag,
           'cash_flag': cash_flag,
           }

    if request.method == 'POST' and request.POST:
        input_id = request.POST["id"]
        input_symbol = request.POST["symbol"]
        input_stock_quantity = float(request.POST["quantity"])
        dic['id_flag'] = not (Investor.objects.filter(id=input_id).exists())
        dic['symbol_flag'] = not (Company.objects.filter(symbol=input_symbol).exists())

        if dic['id_flag'] or dic['symbol_flag']:
            return render(request, 'buy_stocks.html', dic)

        today = datetime.today().strftime('%Y-%m-%d')
        dic['buy_flag'] = Buying.objects.filter(tdate=today, id=input_id, symbol=input_symbol).exists()

        if dic['buy_flag']:
            return render(request, 'buy_stocks.html', dic)

        with connection.cursor() as cursor:
            cursor.execute("""
               select top 1 Stock.Price
               from Stock
               where Stock.Symbol= %s
               order by Stock.tDate DESC
               """, [input_symbol])
            last_stock_price = float(dictfetchall(cursor)[0]["Price"])

        total_price = input_stock_quantity * last_stock_price
        user_record = Investor.objects.filter(id=input_id)
        avail_cash = float(user_record.values_list()[0][2])

        if avail_cash < total_price:
            dic['cash_flag'] = True
            return render(request, 'buy_stocks.html', dic)

        is_today_stock_record=Stock.objects.filter(symbol=input_symbol,tdate=today).exists()
        if not(is_today_stock_record):
            with connection.cursor() as cursor:
                 cursor.execute("""
                 insert into Stock(symbol, tdate, price) 
                  values (%s, %s, %s)
                """, [input_symbol, today,last_stock_price])

        # Creates the stock buying record in db
        with connection.cursor() as cursor:
            cursor.execute("""
            insert into Buying(tDate,ID, Symbol,BQuantity)
            values (%s, %s, %s, %s)
            """, [today,input_id,input_symbol,input_stock_quantity])
        new_avail_cash = int(avail_cash - total_price)
        # update the user's cash amount
        Investor.objects.filter(id=input_id).update(availablecash=new_avail_cash)

    with connection.cursor() as cursor:
        cursor.execute("""
        select top 10 s1.tDate,s1.ID,s1.Symbol,s1.total_price
        from (
                select Buying.tDate, Buying.ID, Buying.Symbol, round((Buying.BQuantity * Stock.Price) ,3)as total_price
                from Buying
                inner join Stock
                on Stock.Symbol = Buying.Symbol and Stock.tDate = Buying.tDate
              ) as s1
        order by s1.total_price desc ,s1.ID desc
        """)
        sql_res = dictfetchall(cursor)

    dic['sql_res'] = sql_res
    return render(request, 'buy_stocks.html', dic)





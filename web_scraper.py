""" A web scraper for the retrieval of the following values:
    - BTC/USD rate
    - USD/HRK rate

    These values will be scraped once daily from the websites of:
    - Croatian National Bank, HNB
    - Coin Market Cap

    Finally, values will be stored into a SQL table running on MySQL RDBMS."""

import pandas as pd
import datetime as dt
import pymysql

usd_hrk_page = "http://api.hnb.hr/tecajn/v2?valuta=USD"
btc_usd_page = "https://coinmarketcap.com/currencies/bitcoin/#charts"

date_today = dt.date.today()

#Using pandas.read_html/json methods to read in the exchange rates,
# and converting them to floats.
try:
    print("-------> Fetching today's exchange rates...")
    usd_hrk = float(pd.read_json(usd_hrk_page)['srednji_tecaj'][0].replace(',', '.'))
    btc_usd = float(pd.read_html(btc_usd_page)[1].loc[0, 1].replace(' USD', ''))
    #New value, calculated by multiplying usd/hrk and btc/usd exchange rates.
    btc_hrk = round(usd_hrk * btc_usd, 2)

    create_table_query = """
                            CREATE TABLE IF NOT EXISTS `default_schema`.`exchange_rates` (
                            `date` DATE NOT NULL,
                            `btc/usd` DECIMAL(7,2) NOT NULL,
                            `usd/hrk` DECIMAL(7,6) NOT NULL,
                            `btc/hrk` DECIMAL(8,2) NOT NULL,
                            PRIMARY KEY (`date`),
                            UNIQUE INDEX `date_UNIQUE` (`date` ASC VISIBLE);"""

    insert_data_query = """INSERT INTO exchange_rates VALUES (%s, %s, %s, %s)"""

    #Storing the values into a table in MySQL.
    print("-------> Connecting to the database...")
    connection = pymysql.connect(host='127.0.0.1',
                             user='Leon',
                             password='password',
                             db='default_schema')

    cursor = connection.cursor()
    
    print("-------> Creating database and table (if it does not exist)...")
    cursor.execute(create_table_query)
    connection.commit()
    print("-------> Saving today's exchange rates into table...")
    cursor.execute(insert_data_query, (date_today, btc_usd, usd_hrk, btc_hrk))
    connection.commit()
    print("-------> Success! Date today: %s" % date_today)
except pymysql.err.IntegrityError:
    print("-------> Duplicate entry for today's date!")
except Exception as e:
    print("Error: ", str(e))
finally:
    print("-------> Exiting.")
    connection.close()

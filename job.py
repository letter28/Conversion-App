""" A web scraper for the retrieval of the following values:
    - BTC/USD rate
    - USD/HRK rate

    These values will be scraped every 10 minutes from the websites of:
    - Croatian National Bank, HNB
    - Coin Market Cap

    Finally, values will be stored into a Redis NoSQL db."""

import os
import pandas as pd
import datetime as dt
import redis
from apscheduler.schedulers.blocking import BlockingScheduler

usd_hrk_page = "http://api.hnb.hr/tecajn/v2?valuta=USD"
btc_usd_page = "https://coinmarketcap.com/currencies/bitcoin/#charts"

#Using pandas.read_html/json methods to read in the exchange rates,
# and converting them to floats.

def update_data():
    try:
        time_of_exec = int(dt.datetime.now().timestamp())
        print("-------> Fetching the exchange rates...")
        usd_hrk = float(pd.read_json(usd_hrk_page)['srednji_tecaj'][0].replace(',', '.'))
        btc_usd = float(pd.read_html(btc_usd_page)[1].loc[0, 1].replace(' USD', ''))
        #New value, calculated by multiplying usd/hrk and btc/usd exchange rates.
        btc_hrk = round(usd_hrk * btc_usd, 2)

        #Storing the values into the db.
        redis_db_conn = redis.Redis(host='localhost',
                                    port=6379,
                                    db=4,
                                    password=None)

        print("-------> Saving the exchange rates into db...")
        pipe = redis_db_conn.pipeline()
        temp_dict = {"btc_usd": btc_usd,
                    "usd_hrk": usd_hrk,
                    "btc_hrk": btc_hrk}
        pipe.hmset(time_of_exec, temp_dict)
        pipe.execute()
        pipe.close()
        print(f"-------> Success! Time: {time_of_exec}; Values: {temp_dict}")
    except Exception as e:
        print("Error: ", str(e))

scheduler = BlockingScheduler(daemon=True)
scheduler.add_job(update_data, 'interval', seconds=60)
update_data()
scheduler.start()
print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

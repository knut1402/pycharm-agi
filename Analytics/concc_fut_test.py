

import concurrent.futures
import datetime
from OIS_DC_BUILD import ois_dc_build, get_wirp
from Utilities import *

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()


# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %d bytes' % (url, len(data)))


DT = [[datetime.date(2024, 2, 7), datetime.date(2023, 10, 18)],
      [datetime.date(2024, 2, 7), datetime.date(2023, 10, 18)]]

[print(dt) for dt in DT]
#    ,
#      [datetime.date(2024, 2, 7), datetime.date(2024, 1, 4)],
#      [datetime.date(2024, 2, 7), datetime.date(2024, 2, 6)]]


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    future_to_func = {executor.submit(get_wirp('SOFR_DC', dt)): dt for dt in DT}
    for future in concurrent.futures.as_completed(future_to_func):
        y = future_to_func[future]
        print('future:',type(future))
        print('y:',y)
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (y, exc))
        else:
            print(data)




def add_func(a,b):
    return 3*a[0]**2 - 4*b*a[1]

DT = [ [10,2], [5,2], [3,3]]


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    future_to_func = {executor.submit(add_func, dt, 3): dt for dt in DT}
    for future in concurrent.futures.as_completed(future_to_func):
        y = future_to_func[future]
        print(y)
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (y, exc))
        else:
            print(data)



DT = ['SOFR_DC','ESTER_DC']


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    future_to_func = {executor.submit(ois_dc_build, dt, -1): dt for dt in DT}
    for future in concurrent.futures.as_completed(future_to_func):
        y = future_to_func[future]
        print(y)
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (y, exc))
        else:
            print(data.nodes)


future_to_func
for i in concurrent.futures.as_completed(future_to_func):
    print(i.result().ccy)



ql_date_str(   datetime.date(2024, 2, 7),  ql_date=0)


ois_dc_build('ESTER_DC',b=0)












def worker_function(x):
    return x ** 2

# multiprocessing.pool example:
from multiprocessing import Pool
with Pool() as pool:
    squares = pool.map(worker_function, (1, 2, 3, 4, 5, 6))

# concurrent.futures example:
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as executor:
    squares = list(executor.map(worker_function, (1, 2, 3, 4, 5, 6)))

































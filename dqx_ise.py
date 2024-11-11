from datetime import datetime as dt, timedelta as dt_td
from selenium import webdriver

def getTable() -> list[dt]:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    b = webdriver.Chrome(options=options)
    b.get('https://hiroba.dqx.jp/sc/tokoyami/')
    table = b.find_element('xpath', '//*[@id="raid-container"]/table/tbody')

    # print(len(tr)) # 24
    ll = []
    for tr in table.find_elements('tag name', 'tr')[1:]: # 先頭は日付
        l = []
        for td in tr.find_elements('tag name', 'td')[1:]: # 先頭は時間列
            l.append(td.find_element('xpath', 'img').get_attribute('src'))
        ll.append(l)
    b.quit()
    try: del(b)
    except Exception as e: print(e)
    
    n = dt.now()
    now = dt(n.year, n.month, n.day, 6, 0, 0, 0)
    if n.hour < 6:
        now -= dt_td(days=1)

    timelist = []
    for i in range(5):
        for j in range(24):
            if '19.png' in ll[j][i]:
                timelist.append(now)
            now += dt_td(hours=1)

    return timelist

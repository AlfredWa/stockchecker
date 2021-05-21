#!/usr/bin/env python3
import os, signal
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yeelight.transitions
from yeelight import *
from yeelight import discover_bulbs, Bulb
from yeelight import Flow, transitions
from yeelight.flow import Action
from multiprocessing import Process
import pandas as pd
import time
import requests
import sys
import re
import webbrowser

def setupStockAvailableFlow(bulbIp, durationFlowSeconds=60):
  try:
    bulb = Bulb(bulbIp)

    durationPulseInMs=200
    count = (durationFlowSeconds * 1000) / durationPulseInMs
    transitionsP = yeelight.transitions.pulse(0, 255, 0, durationPulseInMs, 100)
    flow = Flow(
        count=count,
        action=Action.recover,
        transitions=transitionsP
    )
    bulb.turn_on()
    bulb.start_flow(flow)
# except:
#   print("Error setting flow in bulb",file=sys.stderr)
  except Exception as ex:
    logging.exception("Something awful happened!")

# starts thread
def startStockAvailableAlert():
    bulbs = discover_bulbs()
    for b in bulbs:
      print("starting {}".format(b['ip']))
      bulbIp = b['ip']
      print(f"bulbIp:{bulbIp}")
      p = Process(target=setupStockAvailableFlow, args=(bulbIp,))
      p.start()
      p.join()

def checkForStock(page):
    # soup = BeautifulSoup(wd.page_source)
    soup = BeautifulSoup(page.content,features="html.parser")
    items = soup.find("div", {"class": "row pt-2 col-px-1"})

    items_processed = []

    for row in items.findAll("div",{"class":"col-12 py-1 px-1 bg-white mb-1 productTemplate gridViewToggle"}):
        row_processed = []
        itemTitle = row.find("a", {"class": "text-dark text-truncate_3"})
        itemPromoText = row.find("i", {"class": "fas fa-check text-success"})
        try:
          if 'href' in itemTitle.attrs:
            itemURL=itemTitle.get('href')
        except:
          pass

        status = "Available"

        if (not itemPromoText):
            status = "Sold Out"

        #else:
        #    itemAdd=row.find("div", {"class": "mt-auto"}).content[0]
            #itemAdd.get('href')
        #    print(itemAdd)

        if itemTitle:
            row_processed.append(itemTitle)
            row_processed.append(status)
            row_processed.append(itemURL)


        if row_processed:
            items_processed.append(row_processed)

    # cells[3].find("img"valid)["src"]
    # columns = ["ImageUrl","Origin"]

    df = pd.DataFrame.from_records(items_processed, columns=["Item Title","Status","URL"])

    return df



if __name__ == '__main__':
    print("Main line start")
    URL_RTX_3090 = 'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_3&mfr=&pr='
    URL_RTX_3080 = 'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_5&mfr=&pr='
    URL_RTX_3070 = 'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_7&mfr=&pr='
    URL_RTX_3060TI = 'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_8&mfr=&pr='
    URL_RTX_3060 = 'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_9&mfr=&pr='
    URL_1660TI = 'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_19&mfr=&pr='
    URL_1660S = 'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_20&mfr=&pr='
    URL_AMD = 'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_29,3_30&mfr=&pr='
    URL_TEST='https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_3,3_27&mfr=&pr='
    #STOCK_URLS=[URL_RTX_3090,URL_RTX_3080,URL_RTX_3070,URL_RTX_3060TI,URL_RTX_3060,URL_1660TI,URL_1660S,URL_AMD]
    STOCK_URLS=[URL_TEST]

    sig=True
    openedlink=[]
    while sig:
      for url in STOCK_URLS:
        page = requests.get(url)
        stock_df = checkForStock(page)
        print(stock_df)
        if "Available" in stock_df.Status.values:
          print("Stock Available!")
          prodAvailable=stock_df[stock_df.Status.values=="Available"].URL
          for link in prodAvailable:
            if (link not in openedlink):
                webbrowser.open(link)
                openedlink.append(link)
        # Switch on lighting to alert
          startStockAvailableAlert()
          sig=False
        else:
          print("Everything out of stock!")
        #time.sleep(1)
      print("Main line end")

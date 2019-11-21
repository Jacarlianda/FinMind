import pandas as pd
import requests

# class name，必須跟檔案名一致，例如 class MAXMINPERIODBAIS，檔名也是 MAXMINPERIODBAIS.py
class MAXMINPERIODBAIS:
    def __init__(self,
                 stock_price,
                 ma_days = 20,
                 bais_lower = -1.1,
                 bais_upper = 1.25,
                 period_days = 5,
                 **kwargs,):
        #-------------------------------------------------------------------
        # 此區塊請勿更動
        stock_price = stock_price.sort_values('date')
        # 股價
        self.stock_price = stock_price
        # 融資融券
        self.MarginPurchaseShortSale = kwargs.get("MarginPurchaseShortSale", pd.DataFrame())
        # 三大法人買賣
        self.InstitutionalInvestorsBuySell = kwargs.get("InstitutionalInvestorsBuySell", pd.DataFrame())
        # 外資持股
        self.Shareholding = kwargs.get("Shareholding", pd.DataFrame())
        # 此區塊請勿更動
        #-------------------------------------------------------------------
        self.ma_days = ma_days
        self.bais_lower = bais_lower
        self.bais_upper = bais_upper
        self.period_days = period_days

        self.create_feature()

    def create_feature(self):
        self.stock_price['ma{}'.format(self.ma_days)] = self.stock_price['close'].rolling(window=self.ma_days).mean()
        self.stock_price['bais'] = ((self.stock_price['close'] - self.stock_price['ma{}'.format(self.ma_days)]) / self.stock_price['ma{}'.format(self.ma_days)]) * 100

        self.stock_price['max_period{}'.format(self.period_days)] = self.stock_price['close'].shift(1).rolling(window=self.period_days).max()
        self.stock_price['min_period{}'.format(self.period_days)] = self.stock_price['close'].shift(1).rolling(window=self.period_days).min()

        self.stock_price = self.stock_price.dropna()
        self.stock_price.index = range(len(self.stock_price))

    def trade(self,date):
        '''
        此區塊，可進行資料處理、做技術指標，寫自己的策略，
        寫你自己的策略, 必須 return : 1 (買) or -1 (賣) or 0 (不操作)
        根據時間date，回傳當下要進行什麼操作 ( 買/賣/不操作 )

        date : 昨天時間
        用昨天的資料，計算技術指標，判斷今天買/賣
        '''
        value = self.stock_price[ self.stock_price['date'] == date ]
        if len(value) == 0:
            return 0

        close = value['close'].values[0]
        bais = value['bais'].values[0]
        max_period = value['max_period{}'.format(self.period_days)].values[0]
        min_period = value['min_period{}'.format(self.period_days)].values[0]

        if bais < self.bais_lower and close > max_period:
            return 1
        elif bais > self.bais_upper and close < min_period:
            return -1
        else:
            return 0

def test():

    stock_id = '0056'
    date = '2015-01-01'

    url = 'http://finmindapi.servebeer.com/api/data'
    form_data = {'dataset':'TaiwanStockPrice',
                 'stock_id':stock_id,
                 'date':date}

    res = requests.post(url,verify = True,data = form_data)

    temp = res.json()
    stock_price = pd.DataFrame(temp['data'])

    form_data = {'dataset':'InstitutionalInvestorsBuySell',
  	   'stock_id':stock_id,
  	   'date':date}
    res = requests.post(
        url,verify = True,
        data = form_data)

    temp = res.json()
    InstitutionalInvestorsBuySell = pd.DataFrame(temp['data'])

    obj = MAXMINPERIODBAIS(
        stock_price=stock_price,
        InstitutionalInvestorsBuySell=InstitutionalInvestorsBuySell
    )
    obj.trade('2019-05-07')


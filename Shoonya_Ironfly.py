from NorenRestApiPy.NorenApi import  NorenApi
import pyotp

# Clients Credentials

userid    = 'User ID'
password =  'Passwd'
Totp = 'Auth QR Key'
Pin = pyotp.TOTP(Totp).now()
twoFA    =  f"{int(Pin):06d}" if len(Pin) <=5 else Pin
vendor_code = 'V_Code'
api_secret = 'Api_Secret'
imei = 'abc1234'

class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/', eodhost='https://api.shoonya.com/chartApi/getdata/')

# Login Function

def login():
     api = ShoonyaApiPy()
     login_status = api.login(userid=userid, password=password, twoFA=twoFA, vendor_code=vendor_code, api_secret=api_secret, imei=imei)
     print(login_status)
     return api

# Script Function

def GetToken(exchange,tradingsymbol):
    Token = api.searchscrip(exchange=exchange, searchtext=tradingsymbol).get('values')[0].get('token')
    return Token

# Last Traded Price Function

def GetLTP(exchange,token):
    ret = api.get_quotes(exchange, str(token))
    LTP = ret.get('lp')
    Message = "LTP =" + str(LTP)
    print(Message)
    return LTP

# Order Function

def order_place(tradingsymbol,exchange,buy_or_sell,quantity,variety='regular',price_type='MKT',product_type='M',price = 0):

    OrderId = api.place_order(buy_or_sell = buy_or_sell, 
                            product_type = product_type,
                            exchange = exchange,
                            tradingsymbol = tradingsymbol, 
                            quantity = quantity,
                            discloseqty=0,
                            price_type = price_type,
                            price = price,
                            trigger_price=None,
                            retention='DAY', 
                            remarks='my_order_001').get('norenordno')  
    Message = "Placed order id :" + OrderId
    print(Message)

    return OrderId

# IronFly Function (Strategy Function)

def createIronfly(exchange,symbol,expiry,strikedifference,strike = 100):
    index_tradingsymbol = str(symbol) + str(expiry) + 'F'
    Token = GetToken(exchange,index_tradingsymbol)
    LTP = GetLTP(exchange,Token)
 
    ATM_Strike = strike * round(float(LTP) / int(strike))
    print(f"ATM_Strike={ATM_Strike}")
    
    
    sellsymbol_1 = str(symbol) + str(expiry) + str('P') + str(ATM_Strike) 
    sellsymbol_2 = str(symbol) + str(expiry) + str('C') + str(ATM_Strike) 

    buysymbol_1 = str(symbol) + str(expiry) + str('C') + str(ATM_Strike + strikedifference *strike) 
    buysymbol_2 = str(symbol) + str(expiry) + str('P') + str(ATM_Strike - strikedifference *strike) 
    
    print(sellsymbol_1,sellsymbol_2,buysymbol_1,buysymbol_2)

    SellOrderId_1 = order_place(sellsymbol_1,exchange,buy_or_sell='S',quantity=100,variety='regular',price_type='MKT',product_type='M',price = 0)
    SellOrderId_2 = order_place(sellsymbol_2,exchange,buy_or_sell='S',quantity=100,variety='regular',price_type='MKT',product_type='M',price = 0)
    BuyOrderId_1 = order_place(buysymbol_1,exchange,buy_or_sell='B',quantity=100,variety='regular',price_type='MKT',product_type='M',price = 0)
    BuyOrderId_2 = order_place(buysymbol_2,exchange,buy_or_sell='B',quantity=100,variety='regular',price_type='MKT',product_type='M',price = 0)
    



if __name__ == "__main__":
    api = login()
    createIronfly(exchange='NFO',symbol='BANKNIFTY',expiry='26JUL23',strikedifference=4,strike = 100)
    

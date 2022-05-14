import requests as r
import json


def request_data(symbol):
    if "NIFTY" in symbol:
        api_endpoint = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    else:
        api_endpoint = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
    print(api_endpoint)
    headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9"

    }
    
    s = r.Session()
    response = s.get(api_endpoint, headers=headers)
    print(f"[REQUEST STATUS] {response.status_code}")
    
    try:
        data = json.loads(response.content)
        return data
    
    except json.JSONDecodeError:
        print("[NO DATA RETURNED]")
        return False



def get_data(expiryDate, symbol, _filter=False, strike_price=None):

    data = request_data(symbol)

    if not data:
        return False
    
    if not _filter:
        print("[UNFILTERED]")
        total_oi = {
        "CE_TOTAL" : 0,
        "PE_TOTAL" : 0
        }
        result = list()
        for i in data['records']['data']:
            keys = list(i.keys()) 
            if 'PE' in keys and 'CE' in keys:
                if i['expiryDate'] == expiryDate:
                    pe_oi = i.get('PE', {'openInterest' : 0})['openInterest']
                    total_oi["PE_TOTAL"] += pe_oi
                    ce_oi = i.get('CE', {'openInterest' : 0})['openInterest']
                    total_oi["CE_TOTAL"] += ce_oi
                    result.append({
                        'strikePrice' : i['strikePrice'],
                        'PE OI': pe_oi,
                        'CE OI': ce_oi
                    })
        return result, total_oi
    
    else:
        OI_data = {
            'PE OI': None,
            'CE OI': None,
        }
        for i in data['records']['data']:
            keys = list(i.keys()) 
            if 'PE' in keys and 'CE' in keys:
                if i['expiryDate'] == expiryDate:

                    if i['strikePrice'] == strike_price:
                        pe_oi = i.get('PE', {'openInterest' : 0})['openInterest']
                        OI_data['PE OI'] = pe_oi
                        ce_oi = i.get('CE', {'openInterest' : 0})['openInterest']
                        OI_data['CE OI'] = ce_oi
                        break
                        
        else:
            print(f'Couldn\'t find strike price [{strike_price}]')

        return OI_data


def validate_strike_price(expiryDate, symbol, strike_price):
    data = request_data(symbol)
    for i in data['records']['data']:
            keys = list(i.keys()) 
            if 'PE' in keys and 'CE' in keys:
                if i['expiryDate'] == expiryDate:

                    if i['strikePrice'] == strike_price:
                        return True
    return False



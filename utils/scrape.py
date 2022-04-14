import requests as r
import json


def get_data(expiryDate, symbol):
    if symbol == "NIFTY":
        api_endpoint = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
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
    except json.JSONDecodeError:
        print("[NO DATA RETURNED]")
        return
    total_oi = {
        "CE" : data['filtered']['CE']['totOI'],
        "PE" : data['filtered']['PE']['totOI']
    }
    result = list()
    for i in data['records']['data']:
        keys = list(i.keys())
        if 'PE' in keys or 'CE' in keys:
            if i['expiryDate'] == expiryDate:
                result.append({
                    'strikePrice' : i['strikePrice'],
                    'PE OI': i.get('PE', {'openInterest' : 0})['openInterest'],
                    'CE OI': i.get('CE', {'openInterest' : 0})['openInterest']
                })
    return result, total_oi
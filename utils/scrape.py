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
        "CE" : 0,
        "PE" : 0
    }
    result = list()
    for i in data['records']['data']:
        keys = list(i.keys())
        if 'PE' in keys and 'CE' in keys:
            if i['expiryDate'] == expiryDate:
                pe_oi = i.get('PE', {'openInterest' : 0})['openInterest']
                total_oi["PE"] += pe_oi
                ce_oi = i.get('CE', {'openInterest' : 0})['openInterest']
                total_oi["CE"] += ce_oi
                result.append({
                    'strikePrice' : i['strikePrice'],
                    'PE OI': pe_oi,
                    'CE OI': ce_oi
                })
    return result, total_oi
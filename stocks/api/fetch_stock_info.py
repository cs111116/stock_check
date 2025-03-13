# api/fetch_stock_info.py
import requests
from bs4 import BeautifulSoup
import pdb
from stocks.log_config import logging_info,logging_error
from stocks.models import StockInfo
def fetch_stock_info():
    """抓取台灣股市的股票基本資料"""
    # 設定所有可能的 market 和 issuetype 組合
    market_issuetype_combinations = [
        (1, 1),  # 上市 股票
        (1, 'I'),  # 上市 ETF
        (2, 3),  # 上櫃 股票
        (2, 4)   # 上櫃 ETF
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    logging_info(f"股票資訊抓取開始(上市-股票 AND 上市-ETF AND 上櫃-股票 AND 上櫃-ETF)")
    for market, issuetype in market_issuetype_combinations:
        url = f"https://isin.twse.com.tw/isin/class_main.jsp?market={market}&issuetype={issuetype}&chklike=Y"
        logging_info(f"抓取 URL: {url}")
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # 解析 HTML 並抓取資料
        stocks_info = []
        for row in soup.select('table tr')[1:]:  # 排除標題行
            cols = row.find_all('td')
            if len(cols) < 7:
                continue
            stock_code = cols[2].text.strip()
            stock_name = cols[3].text.strip()
            market_type = cols[4].text.strip()
            security_type = cols[5].text.strip()
            industry = cols[6].text.strip()

            # 根據市場類型設定 market_type 值
            if market_type == '上市':
                market_type = 1  # 1 = Listed
            elif market_type == '上櫃':
                market_type = 2  # 2 = OTC (Over-the-Counter)
            else:
                logging_error(f"{stock_name} market_type 不為上市或上櫃, market_type={market_type}")
                continue

            # 根據有價證券類型設定 security_type 值
            if security_type == '股票':
                security_type = 1  # 1 = Stock
            elif security_type == 'ETF':
                security_type = 2  # 2 = ETF
            else:
                logging_error(f"{stock_name} security_type 不為股票或ETF, security_type={security_type}")
                continue

            stocks_info.append({
                'stock_code': stock_code,
                'stock_name': stock_name,
                'market_type': market_type,
                'security_type': security_type,
                'industry': industry,
            })
        logging_info(f"股票資訊爬蟲完成,準備儲存中...")
        # 儲存抓取的資料
        save_stock_info(stocks_info)
    return True
def save_stock_info(stocks_info):
    for stock in stocks_info:
        try:
            stock_data, created = StockInfo.objects.get_or_create(
                stock_code=stock['stock_code'],
                defaults={
                    'stock_name': stock['stock_name'],
                    'market_type': stock['market_type'],
                    'security_type': stock['security_type'],
                    'industry': stock['industry']
                }
            )
            if not created:
                # 如果資料已經存在，你可以選擇更新資料
                stock_data.stock_name = stock['stock_name']
                stock_data.market_type = stock['market_type']
                stock_data.security_type = stock['security_type']
                stock_data.industry = stock['industry']
                stock_data.save()

        except Exception as e:
            logging_error(f"股票資訊新增有誤 {stock['stock_code']}:{stock['stock_name']}: {str(e)}")
            return False
    logging_info(f"股票資訊儲存成功")
    return True


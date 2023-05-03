import datetime

import requests

from configs.config import Config


def get_token():
    access_data = {
        'imp_key': Config().IAMPORT_KEY,
        'imp_secret': Config().IAMPORT_SECRET
    }
    url = "https://api.iamport.kr/users/getToken"
    req = requests.post(url, data=access_data)
    access_res = req.json()
    print('iamport.py의 get_token: access_res;;;;;;', access_res)
    if access_res['code'] == 0:
        return access_res['response']['access_token']
    else:
        return None


def payments_prepare(merchant_order_id, amount, *args, **kwargs):
    now = datetime.datetime.now()
    access_token = get_token()
    if access_token:
        access_data = {
            'merchant_uid': merchant_order_id,# + '@' + str(uuid.uuid4()) + NOW.microsecond,#
            'amount': amount
        }
        url = "https://api.iamport.kr/payments/prepare"
        print("api 통신 접속 ok::: access_data:::", access_data)
        headers = {
            'Authorization': access_token
        }
        req = requests.post(url, data=access_data, headers=headers)
        res = req.json()
        print("req.json 할당 완료 :::res = req.json()::::", res)
        if res['code'] != 0:
            raise ValueError("API 통신 오류")
    else:
        raise ValueError("토큰 오류")


def find_transaction(order_id, *args, **kwargs):
    print('def find_transaction(order_id, *args, **kwargs): order_id', order_id)
    access_token = get_token()
    print("find_transaction 시작:::access_token", access_token)
    if access_token:
        url = "https://api.iamport.kr/payments/find/"+order_id
        headers = {
            'Authorization': access_token
        }
        req = requests.post(url, headers=headers)
        print('def find_transaction:::req:::', req)
        res = req.json()
        print('def find_transaction:::res = req.json():::', res) ## 여기서 에러가 발생
        if res['code'] == 0:
            context = {
                'imp_id': res['response']['imp_uid'],
                'merchant_order_id': res['response']['merchant_uid'],
                'amount': res['response']['amount'],
                'status': res['response']['status'],
                'type': res['response']['pay_method'],
                'receipt_url': res['response']['receipt_url']
            }
            print('**********************context', context)
            return context
        else:
            ValueError("'NoneType' object is not subscriptable %%%%%")
            return None
    else:
        raise ValueError("토큰 오류")


def req_cancel_pay(reason, imp_uid, req_cancel_amount, cancelable_amount):
    access_token = get_token()
    print('req_cancel_pay access_token = get_token()', access_token)
    if access_token:
        access_data = {
            'reason': reason,
            'imp_uid': imp_uid,
            'amount': req_cancel_amount,
            'checksum': cancelable_amount
        }
        url = "https://api.iamport.kr/payments/cancel"
        headers = {
            'Authorization': access_token
        }

        req = requests.post(url, data=access_data, headers=headers)
        print('req_cancel_pay():::req:::', req)
        res = req.json()
        print('req_cancel_pay():::res = req.json():::', res)
        if res['code'] != 0:
            raise ValueError("API 통신 오류")
        return res
    else:
        raise ValueError("토큰 오류")


def req_billing_key(card_number, expiry, birth, pwd_2digit, customer_uid):
    access_token = get_token()
    print('req_billing_key access_token = get_token()', access_token)
    print("req_billing_key customer_uid", customer_uid)
    if access_token:
        access_data = {
            # 'pg': 'kcp_billing.BA001',
            'card_number': card_number,
            'expiry': expiry,
            'birth': birth,
            'pwd_2digit': pwd_2digit
        }
        url = "https://api.iamport.kr/subscribe/customers/" + customer_uid
        """
        access_data = {
            'card_number': "4899300000095976",
            'expiry': "202702",
            'birth': "691204",
            'pwd_2digit': "35"
        }
        url = "https://api.iamport.kr/subscribe/customers/moljin_10057_100118" #+ customer_uid
        """
        print("access_data", access_data)
        print("url", url)
        headers = {
            'Authorization': access_token
        }
        print("headers", headers)
        req = requests.post(url, data=access_data, headers=headers)
        print('req_billing_key():::req::: 여기를 넘어가야... ', req)
        res = req.json()
        print('req_billing_key():::res = req.json():::code==0 이어야 한다.', res)
        if res['code'] != 0:
            raise ValueError("API 통신 오류")
        return res
    else:
        raise ValueError("토큰 오류")


def onetime_pay_billing_key(card_number, expiry, birth, pwd_2digit, customer_uid, merchant_uid, amount):
    access_token = get_token()
    print('req_billing_key access_token = get_token()', access_token)
    if access_token:
        access_data = {
            # 'pg': 'kcp_billing.BA001',
            'customer_uid': customer_uid,
            'merchant_uid': merchant_uid,
            'card_number': card_number,
            'expiry': expiry,
            'birth': birth,
            'pwd_2digit': pwd_2digit,
            'amount': amount
        }
        url = "https://api.iamport.kr/subscribe/payments/onetime"
        print("access_data", access_data)
        print("url", url)
        headers = {
            'Authorization': access_token
        }
        print("headers", headers)
        req = requests.post(url, data=access_data, headers=headers)
        print('onetime_pay_billing_key():::req::: 여기를 넘어가야... ', req)
        res = req.json()
        print('onetime_pay_billing_key():::res = req.json():::code==0 이어야 한다.', res)
        if res['code'] != 0:
            raise ValueError("API 통신 오류")
        return res
    else:
        raise ValueError("토큰 오류")


def onetime_pay_without_key(card_number, expiry, birth, merchant_uid, amount):
    access_token = get_token()
    print('req_billing_key access_token = get_token()', access_token)
    if access_token:
        access_data = {
            # 'pg': 'kcp_billing.BA001',
            'merchant_uid': merchant_uid,
            'card_number': card_number,
            'expiry': expiry,
            'birth': birth,
            'amount': amount
        }
        url = "https://api.iamport.kr/subscribe/payments/onetime"
        print("access_data", access_data)
        print("url", url)
        headers = {
            'Authorization': access_token
        }
        print("headers", headers)
        req = requests.post(url, data=access_data, headers=headers)
        print('onetime_pay_without_key():::req::: 여기를 넘어가야... ', req)
        res = req.json()
        print('onetime_pay_without_key():::res = req.json():::code==0 이어야 한다.', res)
        if res['code'] != 0:
            raise ValueError("API 통신 오류")
        return res
    else:
        raise ValueError("토큰 오류")
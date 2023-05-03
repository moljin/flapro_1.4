import random
from lxml import etree
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import numpy as np
import pandas as pd

""" ################ 방법 1 ############### """
numberT = 45
numberL = 7


def sort_random_array(array_l):
    length = len(array_l) - 2
    for i in range(length):
        for j in range(length-i):
            if array_l[j] > array_l[j+1]:
                array_l[j], array_l[j+1] = array_l[j+1], array_l[j]


lengthy = ""


def set_random_array():
    global lengthy
    array_t = []
    array_l = []
    for i in range(1, numberT + 1):
        array_t.append(i)
        lengthy = array_t.__len__()
    for i in range(0, numberL):
        temp = random.randrange(0, lengthy)
        array_l.append(array_t[temp])
        array_t.pop(temp)
        lengthy = lengthy - 1
        sort_random_array(array_l)
    return array_l


""" ################ 다른 방법 2 ############### """


def lotto_pick(total, pick):
    from random import random, shuffle
    nums = list(range(1, total+1))
    picked_nums = []
    for i in range(pick):
        shuffle(nums)
        picked_index = int(random() * len(nums))
        picked_num = nums.pop(picked_index)
        picked_nums.append(picked_num)
    return picked_nums


"""
################ 방법 3 : 마지막회차까지 최다빈도 로또번호 추출하기 ################
GitHub(https://github.com/2dowon/Project-DOTTO) 참고
"""


def extract_latest_round():
    latest_url = f"https://dhlottery.co.kr/gameResult.do?method=byWin"
    latest_html = requests.get(latest_url).text
    soup = BeautifulSoup(latest_html, 'lxml')
    list_select = soup.find("select", id="dwrNoList")

    selected_soup = BeautifulSoup(f"""{list_select}""", 'lxml')
    latest_page = selected_soup.find_all('option', selected=True)[0].get_text()
    print("마지막 회차:: ", int(latest_page))

    select_html = etree.HTML(f"""{list_select}""")
    selected = select_html.xpath('//option[@selected]')
    # print(selected)  # 여기서 selected value 만 가져오는 방법을 못찾겠다.

    return latest_page


def extract_first_win_num():
    """1등번호 10개 추출하기"""
    latest_page = extract_latest_round()
    lotto_num = []  # 역대 로또 번호를 저장하는 리스트

    # 로또 사이트에서 역대 로또 당첨 번호를 크롤링해서 lotto_num 리스트에 추가하기
    for i in tqdm(range(1, int(latest_page))):
        url = f"https://dhlottery.co.kr/gameResult.do?method=byWin&drwNo={i}"

        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')

        soup_lottos = soup.select("span.ball_645")[:6]
        lotto_num_list = [int(soup_lotto.get_text()) for soup_lotto in soup_lottos]
        lotto_num.append(lotto_num_list)

    # 다차원 배열을 1차원 배열로 만들기 (개수를 세기 위해서)
    lotto_countlist = np.ravel(lotto_num, order='C').tolist()

    # 1~45까지 카운트한 횟수를 넣는 리스트
    lotto_count_value = []

    for i in range(1, 46):
        lotto_count_value.append(lotto_countlist.count(i))

    # 카운트한 값을 데이터프레임으로 만들기
    data = np.array(lotto_count_value)
    index_num = [i for i in range(1, 46)]
    columns_list = ["count"]
    df_lotto_count = pd.DataFrame(data, index=index_num, columns=columns_list)
    print(df_lotto_count)

    # 가장 많이 나온 로또 번호 10개 추출
    top10 = df_lotto_count.nlargest(10, 'count')
    print(top10)

    top10_list = top10.index.tolist()
    print(top10_list)

    return top10_list

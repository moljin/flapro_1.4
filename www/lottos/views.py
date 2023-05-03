import random

from flask import Blueprint, render_template, jsonify, request, flash, redirect

from configs import db
from www.lottos.models import LottoFirstWinNum, STATUS
from www.lottos.utils import set_random_array, lotto_pick, extract_latest_round, extract_first_win_num

NAME = 'lottos'
lotto = Blueprint(NAME, __name__, url_prefix='/')


@lotto.route("/lotto/create/test")
def lotto_create_test():
    return render_template("lottos/lotto_test.html", array=set_random_array())


@lotto.route("/lotto/get/random")
def lotto_return_random():
    """1번 방법"""
    array = set_random_array()
    """2번 방법"""
    pick = lotto_pick(45, 7)
    print('jsonify(_result=array, pick=pick)', jsonify(_result=array, pick=pick))
    return jsonify(_result=array, pick=pick)


"""GitHub 방법"""
"""# 랜덤으로 로또번호를 추출하는 함수"""

latest_round_num = ""
lotto_top10 = ""
top10_latest_round_num = ""


# @lotto.route("/")
@lotto.route("/random/lotto")
def random_lotto():
    global latest_round_num
    top10_latest_extract = LottoFirstWinNum.query.filter_by(status=STATUS[1]).first()
    if top10_latest_extract:
        latest_round_num = top10_latest_extract.latest_round_num
    lotto_random_num = sorted(random.sample(range(1, 46), 6))
    print(lotto_random_num)
    return render_template("lottos/lotto.html", variable=lotto_random_num, latest=int(latest_round_num))


"""# TOP10으로 로또번호를 추출하는 함수"""


# @lotto_bp.route("/lotto/create")
@lotto.route("/lotto/top10/lotto")
def top10_lotto():
    global lotto_top10, top10_latest_round_num
    top10_latest_extract = LottoFirstWinNum.query.filter_by(status=STATUS[1]).first()
    if top10_latest_extract:
        top10_latest_round_num = top10_latest_extract.latest_round_num
        top10_str_list = top10_latest_extract.extract_num.split(" ")
        """string 로 저장된 최다빈도 번호를 integer list 로 다시 변환"""
        top10_int_list = list(map(int, top10_str_list))
        # top10_int_list = [34, 18, 12, 27, 13, 17, 39, 14, 45, 1]
        lotto_top10 = sorted(random.sample(top10_int_list, 6))
    return render_template("lottos/lotto.html", variable=lotto_top10, latest=int(top10_latest_round_num))


full_int_list = ""


@lotto.route("/lotto/win/extract", methods=['GET'])
def win_extract_lotto():
    global full_int_list
    old_extract = LottoFirstWinNum.query.filter_by(status=STATUS[1]).first()
    if old_extract:
        full_str_list = old_extract.extract_num.split(" ")
        """string 로 저장된 최다빈도 번호를 integer list 로 다시 변환"""
        full_int_list = list(map(int, full_str_list))
        print(old_extract.extract_num.split(" "))
    return render_template("lottos/extract.html", old_extract=old_extract, old_extract_num=full_int_list)


@lotto.route("/lotto/win/extract/post", methods=['POST'])
def win_extract_lotto_post():
    old_extract = LottoFirstWinNum.query.filter_by(status=STATUS[1]).first()
    req_latest_round = request.form.get("latest_round")
    latest_page = extract_latest_round()

    if int(req_latest_round) == int(latest_page):
        extract_num = extract_first_win_num()
        """추출한 최다빈도 번호 리스트를 string 으로 변환해서 저장하기 위해"""
        map_str_extract_num = " ".join(map(str, extract_num))

        new_extract = LottoFirstWinNum()
        new_extract.title = latest_page + "회차"
        new_extract.latest_round_num = latest_page
        new_extract.extract_num = map_str_extract_num
        db.session.add(new_extract)

        if old_extract:
            old_extract.status = STATUS[0]
            db.session.add(old_extract)
        db.session.commit()

        """string 로 저장된 최다빈도 번호를 integer list 로 다시 변환"""
        _full_int_list = list(map(int, new_extract.extract_num.split(" ")))
        return render_template("lottos/extract.html", extract_num=_full_int_list, map_str_extract_num=map_str_extract_num)
    else:
        flash("입력하신 회차는 마지막 회차가 아니에요...")
        print("입력하신 회차는 마지막 회차가 아니에요...")
        return redirect(request.referrer)
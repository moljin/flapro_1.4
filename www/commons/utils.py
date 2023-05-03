import datetime
import os
import re
import shutil
import unicodedata
import uuid

from flask import g, abort, flash, session, render_template, make_response, jsonify, url_for
from flask_login import current_user
from flask_mail import Message

from configs import db, mail
from configs.config import BASE_DIR, Config
from www.accounts.models import User


def flash_form_errors(form):
    for _, errors in form.errors.items():
        for e in errors:
            flash(e)


def error_400_json_data():
    data = {"_err": "error",
            "res_msg": "유효하지 않은 요청(Error 400)",
            "redirect_url": url_for("commons.jsonify_error_400")}
    return data


def error_401_json_data():
    data = {"_err": "error",
            "res_msg": "자격없는 접근(Error 401)",
            "redirect_url": url_for("commons.jsonify_error_401")}
    return data


def error_404_json_data():
    data = {"_err": "error",
            "res_msg": "페이지가 없거나 유효하지 않은 접근(Error 404)",
            "redirect_url": url_for("commons.jsonify_error_404")}
    return data


def error_500_json_data():
    data = {"_err": "error",
            "res_msg": "서버 내부 에러(Error 500)",
            "redirect_url": url_for("commons.jsonify_error_500")}
    return data


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}


def random_word(length):  # 같은 이름의 파일을 다른 이름으로 랜덤하게 만든다.
    import random, string
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def filename_format(_filename):
    filename = "{random_word}-{user_id}-{username}-{date}{extension}".format(
        random_word=random_word(20),
        user_id=str(g.user.id),
        username=g.user.email.split('@')[0],
        date=datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
        extension=os.path.splitext(_filename)[1],
    )
    return filename


def base_file_path(_filename, request_path, user):
    base_relative_path = "static/media/user_images/{request_path}/{username}/{random_word}/{filename}".format(
        request_path=request_path,
        username=user.username,  # 해당 파일 owner
        random_word=random_word(20),
        filename=filename_format(_filename),
    )
    return base_relative_path


def save_file(file, request_path, user):
    if file.filename == '':
        abort(400)
    if file and allowed_file(file.filename):
        filename = filename_format(file.filename)
        relative_path = base_file_path(filename, request_path, user)
        upload_path = os.path.join(BASE_DIR, "www/" + relative_path)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        return relative_path, upload_path   # 템플릿단에서는 relative_path가 사용된다. static 폴더가 있어야 찾아간다.
    else:
        abort(400)


def base64_to_file(img_string, file_name, path, user):
    import base64
    from PIL import Image
    import io
    img_data = base64.b64decode(img_string)
    image_path = base_file_path(file_name, path, user)
    upload_path = os.path.join(BASE_DIR, "www/" + image_path)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)

    img = Image.open(io.BytesIO(img_data))
    img.save(upload_path)

    return image_path, file_name  # filename


def img_delete(img_path):
    old_image_abs_path = os.path.join(BASE_DIR, "www/"+img_path)
    if os.path.isfile(old_image_abs_path):
        shutil.rmtree(os.path.dirname(old_image_abs_path))


def img_update(img_path, req_img, req_path, user):
    if req_img:
        """기존 이미지 삭제"""
        img_delete(img_path)
        """신규 이미지 저장"""
        relative_path, upload_path = save_file(req_img, req_path, user)
        return relative_path


def single_img_save(obj, req_path, img, user, filename):
    existing_img_path = obj.img_path
    if img:
        if existing_img_path:
            relative_path = img_update(existing_img_path, img, req_path, user)
            obj.img_path = relative_path
            if filename:
                obj.original_filename = filename
        else:
            relative_path, _ = save_file(img, req_path, user)
            obj.img_path = relative_path
            if filename:
                obj.original_filename = filename
    # g.db.add(obj)
    # g.db.commit()


def slugify(value, allow_unicode=False):
    """Django 에서 가져옴(def slugify)"""
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


link = ""
img_link = ""


def any_send_mail(_subject, user, email, _token, msg_txt, msg_html, add_if):
    """통합: vendor update 알림메일 (회원등록 인증메일과 비밀번호 분실시 재설정 인증메일을 사용하지 않음) """
    global link, img_link
    msg = Message(_subject, sender=Config().MAIL_USERNAME, recipients=[email])
    if (add_if == "vendor_request") \
            or (add_if == "vendor_request_admin") \
            or (add_if == "vendor_pending") \
            or (add_if == "vendor_pending_admin") \
            or (add_if == "vendor_update") \
            or (add_if == "vendor_update_admin"):
        link = None
        img_link = None
    """
    elif (add_if == "register") or (add_if == "email_update") or (add_if == "not_verified"):
        link = url_for('accounts.confirm', token=_token, add_if=add_if, _external=True)
        img_link = url_for('static', filename='statics/images/product_1.jpg', _external=True)
    elif add_if == "forget_password":
        link = url_for('accounts.confirm_email', token=_token, add_if=add_if, _external=True)#, _anchor="here", _method="POST")
        img_link = url_for('static', filename='statics/images/product_1.jpg', _external=True)
    """
    msg.body = render_template(msg_txt)
    msg.html = render_template(msg_html, link=link, img_link=img_link, user=user, email=email, add_if=add_if)# , token=token
    mail.send(msg)


def existing_req_data_check(_type, req_data, existing_obj, target_obj, real_data):
    if req_data:
        if target_obj:
            if existing_obj and (req_data != real_data):
                flash_message = {"flash_message": f"동일한 {_type}이(가) 존재합니다.", }
            elif existing_obj and (req_data == real_data):
                flash_message = {"flash_message": f"{_type}이(가) 그전과 동일해요. (사용가능)", }
            else:
                flash_message = {"flash_message": f"사용가능한 {_type}입니다.", }
            return make_response(jsonify(flash_message))
        else:
            if existing_obj:
                flash_message = {"flash_message": f"동일한 {_type}이(가) 존재합니다.", }
            else:
                flash_message = {"flash_message": f"사용가능한 {_type}입니다.", }
            return make_response(jsonify(flash_message))
    else:
        flash_message = {"flash_message": f"{_type}을(를) 입력해주세요.", }
        return make_response(jsonify(flash_message))


def view_count_save(target_user, obj, obj_str):
    """세션에 객체의 디테일 뷰와 뷰를 열어본 이용자를 페어링 시켜 담아두었다가,
     뷰카운트 저장할때 체크하는 것으로 활용"""
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = "AnonymousUser"

    if target_user != current_user:
        if f'{obj_str}_{obj.id}_view_user_{username}' in session:
            if session[f'{obj_str}_{obj.id}_view_user_{username}'] != f'{obj_str}_{obj.id}:{username}':
                obj.view_count += 1
                db.session.commit()
        else:
            obj.view_count += 1
            db.session.commit()
        session[f'{obj_str}_{obj.id}_view_user_{username}'] = f'{obj_str}_{obj.id}:{username}'


content_text = "default"
"""이미지만 없로드 할때 내용이 있는것으로 체크되게 하기 위해 값을 주었다.
여기를 빈값으로 해버리면, 이미지업로드하고, if len(img_tags) == 0:를 bypass 해서 지나갈때, 빈값으로 인식되어 버린다."""


def editor_empty_check(content):
    print(content)
    global content_text
    import lxml.html
    html = lxml.html.fromstring(content)
    img_tags = html.xpath("//img")
    print("editor_empty_check:::len(img_tags):::", len(img_tags))
    if len(img_tags) == 0:
        """아무것도 입력하지 않거나, 텍스트만 입력하면 여기를 지나가서 텍스트 유무를 가려낸다.
        이미지만 올리면 여기를 bypass 해서, 지나가지 않는다."""
        html_tag_cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        content_text = re.sub(html_tag_cleaner, '', content)
        # html string 에서 태그 제거 content text::: https://calssess.tistory.com/88
    return content_text
    # content_text 글로벌 변수를 빈값 ""로 하지 않고, "default"라고 할당했음에 유의


def c_orm_id(objs_all, user):
    try:
        new_id = str(objs_all[-1].id + 1)  # 고유해지지만, model.id와 일치하지는 않는다. 삭제된 놈들이 있으면...
    except Exception as e:
        print("c_orm_id Exception error::: 임의로 1로... 할당  ", e)
        new_id = str(1)
    user_id = str(user.id)
    random_string = str(uuid.uuid4())
    username = user.email.split('@')[0]
    orm_id = user_id + ":~^:" + username + ";^~;" + new_id + ":" + random_string
    return orm_id


def decode_orm_id(orm_id):
    user_id = orm_id.split(':~^:')[0]
    decode_username = orm_id.split(':~^:')[1].split(';^~;')[0]
    orm_user = User.query.filter_by(id=user_id).first()
    orm_username = orm_user.email.split('@')[0]
    return orm_user, decode_username, orm_username


# def sun_image_save(obj, image_path, file_name):
#     if image_path:
#         obj.img_path = image_path
#         obj.original_filename = file_name
#     db.session.add(obj)
#     db.session.commit()


def sun_image_delete(sunimages):
    for sunimage in sunimages:
        try:
            img_delete(sunimage.img_path)
        except Exception as e:
            print("def sun_image_delete Exception Error::: ", e)
        db.session.delete(sunimage)
        db.session.commit()


def unused_sunimage_delete(db_img_objs_all, target_obj, sunimage_model):
    try:
        content_html = target_obj.content
        import lxml.html
        html = lxml.html.fromstring(content_html)
        img_tags = html.xpath("//img")
        content_img_objs_all = []
        for img_tag in img_tags:
            file_path = "static" + img_tag.attrib["src"].split("static")[1]
            content_img_obj = sunimage_model.query.filter_by(img_path=file_path).first()
            content_img_objs_all.append(content_img_obj)
        unused_db_img_objs = set(db_img_objs_all) - set(content_img_objs_all)
        """DB_image 와 content_image 들을 비교해서 필요없는 DB_image 모두 삭제하기"""
        if unused_db_img_objs:
            for unused_db_img_obj in unused_db_img_objs:
                try:
                    img_delete(unused_db_img_obj.img_path)
                except Exception as e:
                    print(e)
                db.session.delete(unused_db_img_obj)
                db.session.commit()

    except Exception as e:
        print('unused_sunimage_delete exception error::', e)


def unused_tag_delete(unused_tag_objs):
    for unused_tag in unused_tag_objs:
        try:
            db.session.delete(unused_tag)
            db.session.commit()
        except Exception as e:
            print(e)


def current_db_session_add(obj):
    current_db_sessions = db.session.object_session(obj)
    current_db_sessions.add(obj)
    db.session.commit()


def current_db_session_delete(obj):
    current_db_sessions = db.session.object_session(obj)
    current_db_sessions.delete(obj)
    db.session.commit()


def file_to_base64(file_path, file_name):
    import base64
    _format = file_name.split('.')[1]
    with open(file_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
        base64_src = "data:image/" + _format + ";base64," + base64_string

    return base64_src, file_name


def file_to_base64_src(file_path, file_name):
    import base64
    _format = file_name.split('.')[1]
    with open(file_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
        base64_src = "data:image/" + _format + ";base64," + base64_string

    return base64_src


def ajax_post_key():
    if 'ajax_post_key' in session:
        session['ajax_post_key'] = session.get('ajax_post_key')
    else:
        session["ajax_post_key"] = str(uuid.uuid4())
    return session['ajax_post_key']


def new_one_obj_multiple_image_save(obj, image, path, user, idx):
    init_path = "img_path_"
    if image:
        relative_path, _ = save_file(image, path, user)
        setattr(obj, init_path + str(idx), relative_path)


# cf. https://www.programiz.com/python-programming/methods/built-in/setattr
def existing_one_obj_multiple_image_save(obj, image, path, user, idx):
    init_path = "img_path_"
    if image:
        obj_img_path = getattr(obj, init_path + str(idx))
        if obj_img_path is not None:
            relative_path = img_update(obj_img_path, image, path, user)
            setattr(obj, init_path + str(idx), relative_path)
        else:
            relative_path, _ = save_file(image, path, user)
            setattr(obj, init_path + str(idx), relative_path)


# https://www.programiz.com/python-programming/methods/built-in/getattr
def one_obj_multiple_image_delete(obj, idx):
    init_path = "img_path_"
    for i in range(1, idx):
        obj_img_path = getattr(obj, init_path+str(i))
        if obj_img_path:
            img_delete(obj_img_path)


def new_three_image_save(user, new_obj, image1, image2, image3, path):
    if image1:
        relative_path1, _ = save_file(image1, path, user)
        new_obj.img_path_1 = relative_path1
    if image2:
        relative_path2, _ = save_file(image2, path, user)
        new_obj.img_path_2 = relative_path2
    if image3:
        relative_path3, _ = save_file(image3, path, user)
        new_obj.img_path_3 = relative_path3
    # db.session.add(new_obj)
    # db.session.commit()


def existing_three_image_save(existing_img_obj, image1, image2, image3, path, user):
    if image1:
        if existing_img_obj.img_path_1 is not None:
            existing_img_obj.img_path_1 = img_update(existing_img_obj.img_path_1, image1, path, user)
        else:
            relative_path1, _ = save_file(image1, path, user)
            existing_img_obj.img_path_1 = relative_path1
    if image2:
        if existing_img_obj.img_path_2 is not None:
            existing_img_obj.img_path_2 = img_update(existing_img_obj.img_path_2, image2, path, user)
        else:
            relative_path2, _ = save_file(image2, path, user)
            existing_img_obj.img_path_2 = relative_path2
    if image3:
        if existing_img_obj.img_path_3 is not None:
            existing_img_obj.img_path_3 = img_update(existing_img_obj.img_path_3, image3, path, user)
        else:
            relative_path3, _ = save_file(image3, path, user)
            existing_img_obj.img_path_3 = relative_path3
    db.session.add(existing_img_obj)
    db.session.commit()


def three_image_delete(obj):
    if obj.img_path_1:
        img_delete(obj.img_path_1)
    if obj.img_path_2:
        img_delete(obj.img_path_2)
    if obj.img_path_3:
        img_delete(obj.img_path_3)


def new_six_image_save(user, new_obj, image1, image2, image3, image4, image5, image6, path):
    if image1:
        relative_path1, _ = save_file(image1, path, user)
        new_obj.img_path_1 = relative_path1
    if image2:
        relative_path2, _ = save_file(image2, path, user)
        new_obj.img_path_2 = relative_path2
    if image3:
        relative_path3, _ = save_file(image3, path, user)
        new_obj.img_path_3 = relative_path3
    if image4:
        relative_path4, _ = save_file(image4, path, user)
        new_obj.img_path_4 = relative_path4
    if image5:
        relative_path5, _ = save_file(image5, path, user)
        new_obj.img_path_5 = relative_path5
    if image6:
        relative_path6, _ = save_file(image6, path, user)
        new_obj.img_path_6 = relative_path6
    # db.session.add(new_obj)
    # db.session.commit()


def existing_six_image_save(existing_img_obj, image1, image2, image3, image4, image5, image6, path, user):
    if image1:
        if existing_img_obj.img_path_1 is not None:
            existing_img_obj.img_path_1 = img_update(existing_img_obj.img_path_1, image1, path, user)
        else:
            relative_path1, _ = save_file(image1, path, user)
            existing_img_obj.img_path_1 = relative_path1
    if image2:
        if existing_img_obj.img_path_2 is not None:
            existing_img_obj.img_path_2 = img_update(existing_img_obj.img_path_2, image2, path, user)
        else:
            relative_path2, _ = save_file(image2, path, user)
            existing_img_obj.img_path_2 = relative_path2
    if image3:
        if existing_img_obj.img_path_3 is not None:
            existing_img_obj.img_path_3 = img_update(existing_img_obj.img_path_3, image3, path, user)
        else:
            relative_path3, _ = save_file(image3, path, user)
            existing_img_obj.img_path_3 = relative_path3
    if image4:
        if existing_img_obj.img_path_4 is not None:
            existing_img_obj.img_path_4 = img_update(existing_img_obj.img_path_4, image4, path, user)
        else:
            relative_path4, _ = save_file(image4, path, user)
            existing_img_obj.img_path_4 = relative_path4
    if image5:
        if existing_img_obj.img_path_5 is not None:
            existing_img_obj.img_path_5 = img_update(existing_img_obj.img_path_5, image5, path, user)
        else:
            relative_path5, _ = save_file(image5, path, user)
            existing_img_obj.img_path_5 = relative_path5
    if image6:
        if existing_img_obj.img_path_6 is not None:
            existing_img_obj.img_path_6 = img_update(existing_img_obj.img_path_6, image6, path, user)
        else:
            relative_path6, _ = save_file(image6, path, user)
            existing_img_obj.img_path_6 = relative_path6
    # db.session.add(existing_img_obj)
    # db.session.commit()


def elapsed_day(updated_at):
    from pytz import timezone
    # print("datetime.now(timezone('Asia/Seoul')).today()", datetime.now(timezone('Asia/Seoul')).today())
    # print("NOW", NOW)
    # print("updated_at", updated_at)
    diff_time = datetime.datetime.now() - updated_at
    # print("diff_time", diff_time)
    # diff_time_seconds = diff_time/86400
    # print("diff_time.days", diff_time.days)
    # print("diff_time 몇 시간 지난 건지", diff_time.seconds / 60 / 60)
    # print(f'{diff_time.days}일 {int(diff_time.seconds / 60 / 60)}시간 {int(diff_time.seconds / 60 - (int(diff_time.seconds / 60 / 60)) * 60)}분 지났어요')
    # print("diff_time_seconds = diff_time/86400(24시간) 머지", diff_time/86400)
    timestamp_now = datetime.datetime.now().timestamp()  # 타임스탬프(단위:초)
    # print("datetime.now()", datetime.now())
    # print("timestamp_now", timestamp_now)
    return diff_time.days

import json

from flask import Blueprint, request, g, redirect, url_for, render_template, make_response, jsonify, flash, session, abort
from flask_login import current_user
from sqlalchemy import desc

from configs import db
from www.accounts.models import User, Profile
from www.boards.articles.forms import ArticleForm
from www.boards.articles.models import ArticleCategory, Article, ArticleSunImage, ArticleTag, ArticleCategoryTag, ArticleComment, ArticleCommentSunImage
from www.commons.required import login_required
from www.commons.utils import img_delete, existing_req_data_check, single_img_save, view_count_save, c_orm_id, unused_sunimage_delete, editor_empty_check, decode_orm_id, sun_image_delete, \
    unused_tag_delete, slugify, error_401_json_data, error_400_json_data

NAME = 'articles'
articles = Blueprint(NAME, __name__, url_prefix='/boards/articles')


ARTICLE_PER_PAGE = 2


@articles.route('/existing/category/title/check/ajax', methods=['POST'])
@login_required
def existing_category_title_check_ajax():
    user_id = request.form.get("user_id")  # 이용자단 등록/수정, 어드민단의 change
    _user_email = request.form.get("user_email")  # 어드민단의 create

    req_title = request.form.get("title")
    ac_id = request.form.get("category_id")
    target_ac = db.session.query(ArticleCategory).filter_by(id=ac_id).first()
    existing_title_ac = ArticleCategory.query.filter_by(title=req_title).first()
    if ac_id == "create":
        if user_id:  # 이용자단의 create
            target_user = User.query.filter_by(id=user_id).first()
            if (current_user == target_user) or current_user.is_admin:
                _type = "타이틀"
                flash_message = existing_req_data_check(_type, req_title, existing_title_ac, None, None)
                return flash_message
            else:
                flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                return make_response(jsonify(flash_message))
        elif _user_email:  # 어드민단의 create
            _target_user = User.query.filter_by(email=_user_email).first()
            if _target_user:
                if current_user.is_admin:
                    _type = "타이틀"
                    flash_message = existing_req_data_check(_type, req_title, existing_title_ac, None, None)
                    return flash_message
                else:
                    flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                    return make_response(jsonify(flash_message))
            else:
                flash_message = {"flash_message": "유효하지 않은 요청(Error 400)", }
                return make_response(jsonify(flash_message))
        else:  # 어드민단의 create 시에 회원 선택하지 않은 경우
            flash_message = {"flash_message": "카테고리 등록을 위한 회원정보가 없네요!(Error 404)", }
            return make_response(jsonify(flash_message))
    else:
        if target_ac:
            target_user = User.query.filter_by(id=user_id).first()
            if target_user:  # 이용자단, 어드민단의 change
                if (current_user == target_user) or current_user.is_admin:
                    _type = "타이틀"
                    flash_message = existing_req_data_check(_type, req_title, existing_title_ac, target_ac, target_ac.title)
                    return flash_message
                else:
                    flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                    return make_response(jsonify(flash_message))
            else:
                flash_message = {"flash_message": "카테고리 등록을 위한 회원정보가 없네요!(Error 404)", }
                return make_response(jsonify(flash_message))
        else:
            flash_message = {"flash_message": "해당 카테고리가 없는 유효하지 않은 요청(Error 400)", }
            return make_response(jsonify(flash_message))


@articles.route('/category/save/ajax', methods=['POST'])
def ac_save_ajax():
    user_id = request.form.get("user_id")  # 이용자 단, 어드민단 change
    print(user_id)
    req_email = request.form.get("user_email")  # admin 단

    category_id = request.form.get("category_id")
    orm_id = request.form.get("orm_id")  # tag 저장에 필요 (ac 를 먼저 커밋하고 tag 를 저장하면 궅이 필요 없을수도...)
    title = request.form.get('title')
    content = request.form.get('content')
    tags_str = request.form.get('tagify')
    category_image = request.files.get('image')
    available_display = request.form.get("available_display")

    ac_img_request_path = "articlecategories/cover_images"
    existing_title_category = ArticleCategory.query.filter_by(title=title).first()
    target_category = ArticleCategory.query.filter_by(id=category_id).first()

    if current_user.is_admin and "admin" in request.referrer:
        req_user = User.query.filter_by(email=req_email).first()  # admin 단
        if category_id == "create":
            if not req_user:
                flash("카테고리 등록을 위한 회원정보가 없네요!(Error 404)")
                return redirect(request.referrer)
            if existing_title_category:
                flash("동일한 제목의 카테고리가 있습니다.")
                return redirect(request.referrer)
            new_category = ArticleCategory(user_id=req_user.id, title=title)
            new_ac_save_snippet(new_category, orm_id, content, tags_str, ac_img_request_path, category_image, req_user)
            if available_display is not None:
                new_category.available_display = True
            else:
                new_category.available_display = False
            g.db.add(new_category)
            g.db.commit()

            flash("카테고리 등록이 완료되었습니다.")
            return redirect(url_for("admin_articles.ac_change", _id=new_category.id, slug=new_category.slug))
        else:
            target_user = User.query.get_or_404(target_category.user_id)
            if str(target_category.user_id) == user_id:
                if existing_title_category:
                    if existing_title_category != target_category:
                        flash("동일한 제목의 카테고리가 있습니다.")
                        return redirect(request.referrer)
                target_ac_save_snippet(target_category, title, orm_id, content, tags_str, ac_img_request_path, category_image, target_user)
                if available_display is not None:
                    target_category.available_display = True
                else:
                    target_category.available_display = False
                g.db.add(target_category)
                g.db.commit()

                flash("카테고리 수정이 완료되었습니다.")
                return redirect(request.referrer)
            else:
                flash("자격없는 요청이거나 잘못된 접근(400)")
                return redirect(request.referrer)

    elif (current_user.is_admin and "admin" not in request.referrer) or user_id:
        if str(current_user.id) == user_id:
            if category_id == "create":
                _available_display = "True"
                if existing_title_category:
                    _response = {"flash_message": "동일한 제목의 카테고리가 있습니다."}
                    return make_response(jsonify(_response))
                new_category = ArticleCategory(user_id=user_id, title=title)
                new_ac_save_snippet(new_category, orm_id, content, tags_str, ac_img_request_path, category_image, g.user)
                if available_display == "true":
                    new_category.available_display = True
                else:
                    new_category.available_display = False
                g.db.add(new_category)
                g.db.commit()

                _type = "create"
                _response = ac_save_response(_type, new_category)
                return make_response(jsonify(_response))
            else:
                _available_display = "True"
                if existing_title_category:
                    if existing_title_category != target_category:
                        _response = {"flash_message": "동일한 제목의 카테고리가 있습니다."}
                        return make_response(jsonify(_response))
                target_ac_save_snippet(target_category, title, orm_id, content, tags_str, ac_img_request_path, category_image, g.user)
                if available_display == "true":
                    target_category.available_display = True
                else:
                    target_category.available_display = False
                g.db.add(target_category)
                g.db.commit()

                _type = "update"
                _response = ac_save_response(_type, target_category)
                return make_response(jsonify(_response))
        else:
            data = error_401_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


def new_ac_save_snippet(new_category, orm_id, content, tags_str, ac_img_request_path, category_image, user):
    new_category.orm_id = orm_id
    new_category.content = content

    if tags_str:
        tags_list = tags_str.split("[")[1].split("]")[0].split(",")
        for tag in tags_list:
            new_tag_obj = ArticleCategoryTag(user_id=user.id, orm_id=orm_id)
            tag_value = json.loads(tag)['value']
            new_tag_obj.tag = tag_value
            db.session.add(new_tag_obj)
            db.session.commit()

    single_img_save(new_category, ac_img_request_path, category_image, user, None)


def target_ac_save_snippet(category, title, orm_id, content, tags_str, ac_img_request_path, category_image, user):
    category.title = title
    category.slug = slugify(title, allow_unicode=True)
    category.content = content

    saved_tag_objs = list()
    if tags_str:
        """태그 저장"""
        tags_list = tags_str.split("[")[1].split("]")[0].split(",")
        for tag in tags_list:
            tag_obj = ArticleCategoryTag(user_id=user.id, orm_id=orm_id)
            tag_value = json.loads(tag)['value']
            tag_obj.tag = tag_value
            db.session.add(tag_obj)
            db.session.commit()
            saved_tag_objs.append(tag_obj)
    try:
        """사용하지 않는 태그 지우기"""
        db_tag_objs_all = category.tag_ac_set
        unused_db_tag_objs = set(db_tag_objs_all) - set(saved_tag_objs)
        if unused_db_tag_objs:
            unused_tag_delete(unused_db_tag_objs)
    except Exception as e:
        print('article_tag update exception error::', e)
    single_img_save(category, ac_img_request_path, category_image, user, None)


def articles_available_display(available_display, obj):
    if available_display is not None:
        obj.available_display = True
    else:
        obj.available_display = False


def ac_save_response(_type, category):
    _response = {
        "_save": _type,
        "_id": category.id,
        "slug": category.slug,
        "redirect_url": url_for("articles.ac_detail", _id=category.id, slug=category.slug),
        # 아래는 넘기더라도 사용하고 있지 않다. 아래 이유로...
        # /*tag_ac_set 이 serializable 되지 않아, AJAX 에서 그냥 리다이렉트로 변경했다.*/
        "ac_user_id": category.user_id,
        "ac_id": category.id,
        "ac_title": category.title,
        "ac_content": category.content,
        # "tag_ac_set": category.tag_ac_set,
        'nickname': category.user.profile_user_set[0].nickname,
        "ac_img_path": category.img_path
    }
    return _response


@articles.route('/category/detail/<_id>/<slug>', methods=['GET'])
def ac_detail(_id, slug):
    """카테고리 주인의 아티클 리스트를 담고 있다."""
    form = ArticleForm()
    if _id == "create":
        if current_user.is_authenticated:
            ac = None
            target_user = "create"
            acs_all = ArticleCategory.query.all()
            orm_id = c_orm_id(acs_all, g.user)  # tag 저장에 필요
            current_user_acs = ArticleCategory.query.filter_by(user_id=current_user.id, available_display=True).all()
            current_user_articles = Article.query.filter_by(user_id=current_user.id, available_display=True).all()
            return render_template('boards/articles/category/detail.html',
                                   form=form,
                                   current_user_acs=current_user_acs,
                                   current_user_articles=current_user_articles,
                                   target_category=ac,
                                   target_user=target_user,
                                   orm_id=orm_id)
        else:
            try:
                session['previous_url'] = request.path
            except Exception as e:
                print("login_required(function) Exception Error::: ", e)
                session['previous_url'] = None
            return redirect(url_for('accounts.login'))
    else:
        ac = ArticleCategory.query.filter_by(id=_id, slug=slug).first()
        target_user = User.query.filter_by(id=ac.user_id).first()
        obj_str = "ac"
        view_count_save(target_user, ac, obj_str)

        target_ac_tags = ArticleCategoryTag.query.filter_by(orm_id=ac.orm_id).all()

        tag_value_list = list()
        for tag in target_ac_tags:
            tag_value_list.append(tag.tag)
        tags_str = str(tag_value_list)
        new_tags_str = tags_str.replace("[", "").replace("'", "").replace("]", "")

        articles_query = Article.query.order_by(desc(Article.created_at)).filter_by(ac_id=ac.id, available_display=True)
        page = request.args.get('page', type=int, default=1)

        """######## 검색 ########"""
        kw = request.args.get('kw', type=str, default='')
        if kw:
            search = f'%%{kw}%%'  # '%%{}%%'.format(kw))
            sub_query = db.session.query(ArticleComment.article_id,
                                         ArticleComment.content,
                                         Profile.nickname).join(Profile, ArticleComment.user_id == Profile.user_id).subquery()
            articles_query = articles_query\
                .join(User, Profile)\
                .join(ArticleTag, ArticleTag.orm_id == Article.orm_id)\
                .outerjoin(sub_query, sub_query.c.article_id == Article.id) \
                .filter(Article.title.ilike(search) |  # 아티클 제목
                        Article.content.ilike(search) |  # 아티클 내용
                        Profile.nickname.ilike(search) |  # 아티클 작성자
                        ArticleTag.tag.ilike(search) |  # 해시태그
                        sub_query.c.content.ilike(search) |  # 코맨트 내용
                        sub_query.c.nickname.ilike(search)).distinct()  # 코멘트 작성자
        """######################"""

        """#### hash_tag 검색 ####"""
        """id=hashTag 클릭 ===> Ajax 로 받는다."""
        hash_tag = request.args.get("hash_tag")
        if hash_tag:
            response = {
                "_hash_tag": hash_tag,
                "_id": _id,
                "redirect_url": url_for("articles.ac_detail", _id=_id, slug=slug)
            }
            return make_response(jsonify(response))

        """Ajax 로 받은 response._hash_tag 를 res_tag 로 리다이렉트하면서 url 에 get request"""
        res_tag = request.args.get("res_tag")
        if res_tag:
            res_tag_articles = list()
            res_tag_objs = ArticleTag.query.filter_by(tag=res_tag).all()
            for tag_obj in res_tag_objs:
                article = tag_obj.article
                res_tag_articles.append(article)
            articles_query = articles_query \
                .join(ArticleTag, ArticleTag.orm_id == Article.orm_id) \
                .filter(ArticleTag.tag.ilike(res_tag)
                        ).distinct()
            pagination = articles_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
            article_objs = res_tag_articles
            """######################"""
        else:
            pagination = articles_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
            article_objs = pagination.items

        return render_template('boards/articles/category/detail.html',
                               form=form,
                               target_category=ac,
                               target_user=target_user,
                               articles=article_objs,
                               pagination=pagination,
                               tags_str=new_tags_str,
                               kw=kw,
                               res_tag=res_tag)


@articles.route('/all/category/list', methods=['GET'])
def all_ac_list():
    """모든 카테고리 리스트"""
    if current_user.is_authenticated:
        acs_query = ArticleCategory.query.filter_by(available_display=True).order_by(desc(ArticleCategory.created_at)).filter(ArticleCategory.user_id != current_user.id)
    else:
        acs_query = ArticleCategory.query.filter_by(available_display=True).order_by(desc(ArticleCategory.created_at))
    page = request.args.get('page', type=int, default=1)
    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        acs_query = acs_query.join(User, Profile).filter(ArticleCategory.title.ilike(search) |
                                                         ArticleCategory.content.ilike(search) |
                                                         User.username.ilike(search) |
                                                         User.email.ilike(search) |
                                                         Profile.nickname.ilike(search)).distinct()
    """######################"""
    pagination = acs_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
    ac_objs = pagination.items
    return render_template('boards/articles/category/list.html',
                           acs=ac_objs,
                           pagination=pagination,
                           kw=kw)


@articles.route('/user/category/list', methods=['GET'])
def user_ac_list():
    """작성자의 카테고리 리스트"""
    _id = request.args.get('_id')
    target_user = User.query.filter_by(id=_id).first()
    acs_query = ArticleCategory.query.filter_by(user_id=_id, available_display=True).order_by(desc(ArticleCategory.created_at))
    page = request.args.get('page', type=int, default=1)
    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        acs_query = acs_query.filter(ArticleCategory.title.ilike(search) |
                                     ArticleCategory.content.ilike(search)).distinct()
    """######################"""
    pagination = acs_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
    ac_objs = pagination.items
    return render_template('boards/articles/category/list.html',
                           acs=ac_objs,
                           target_user=target_user,
                           pagination=pagination,
                           kw=kw)


delete_response = ""


@articles.route('/category/delete/ajax', methods=['POST'])
def ac_delete_ajax():
    global delete_response
    ac_id = request.form.get("_id")
    related_all_delete = request.form.get("related_all_delete")
    if ac_id:
        target_ac = db.session.query(ArticleCategory).filter_by(id=ac_id).first()
        target_article_objs = db.session.query(Article).filter_by(ac_id=ac_id).all()
        if target_ac:
            target_user = User.query.filter_by(id=target_ac.user_id).first()
            if current_user.is_admin and "admin" in request.referrer:
                if related_all_delete != "undefined":
                    if related_all_delete == "true":
                        if target_ac.img_path:
                            img_delete(target_ac.img_path)
                        db.session.delete(target_ac)
                        for target_article in target_article_objs:
                            if target_article.img_path:
                                img_delete(target_article.img_path)
                            existing_articlesunimages = target_article.sunimage_article_set
                            if existing_articlesunimages:
                                sun_image_delete(existing_articlesunimages)

                            existing_article_comments = target_article.comment_article_set
                            if existing_article_comments:
                                for comment_obj in existing_article_comments:
                                    existing_articlecommentsunimages = comment_obj.sunimage_articlecomment_set
                                    if existing_articlecommentsunimages:
                                        sun_image_delete(existing_articlecommentsunimages)
                            db.session.delete(target_article)
                        db.session.commit()
                    else:
                        target_ac.available_display = False
                        for article in target_article_objs:
                            article.available_display = False
                            db.session.add(article)
                    db.session.commit()
                    delete_response = {
                        "_success": "success",
                        "_delete": "delete",
                        "redirect_url": url_for('admin_articles.ac_list')
                    }
                    return make_response(jsonify(delete_response))
                else:
                    data = error_400_json_data()
                    return make_response(jsonify(data))
            elif current_user == target_user:
                target_ac.available_display = False
                for article in target_article_objs:
                    article.available_display = False
                    db.session.add(article)
                db.session.commit()
                flash("카테고리가 삭제되었어요!")
                delete_response = {"_success": "success",
                                   "_delete": "delete",
                                   "redirect_url": url_for('articles.user_ac_list', _id=target_user.id)}
                return make_response(jsonify(delete_response))
            else:
                data = error_401_json_data()
                return make_response(jsonify(data))
        else:
            data = error_400_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@articles.route('/create', methods=['GET'])
@login_required
def article_create():
    form = ArticleForm()
    category_id = int(request.full_path.split("?")[1].split("&")[0].split("=")[1])
    target_category = ArticleCategory.query.filter_by(id=category_id).first()
    articles_all = Article.query.all()
    orm_id = c_orm_id(articles_all, g.user)
    return render_template("boards/articles/create.html",
                           form=form,
                           target_category=target_category,
                           orm_id=orm_id)


@articles.route('/save', methods=['POST'])
@login_required
def article_save():
    req_user_id = request.form.get("user_id")  # 이용자단 create, update, 어드민단 change
    article_id = request.form.get("article_id")  # 이용자단, 어드민단 change
    target_article = Article.query.filter_by(id=article_id).first()  # 어드민단 change 시 user_id 찾아낼때도 사용
    user_email = request.form.get("user_email")  # 어드민단 create
    ac_title = request.form.get("ac_title")  # 어드민단 create

    category_id = request.form.get("category_id")

    orm_id = request.form.get("orm_id")

    title = request.form.get("title")
    meta_description = request.form.get('meta_description')
    article_image = request.files.get("image")
    content = request.form.get('content')
    site_title = request.form.get('site_title')
    site_url = request.form.get('site_url')
    tags_str = request.form.get('tagify')
    available_display = request.form.get("available_display")

    request_path = "articles/thumbnail_images"

    orm_user, decode_username, orm_username = decode_orm_id(orm_id)
    content_text = editor_empty_check(content)
    """어드민이 작성한 것은 여기를 통과하지 못한다."""
    """
    if not target_ac or not orm_user or (decode_username != orm_username) or (current_user != orm_user):
        # abort(400)
        flash('처리가 불가능하거나, 유효하지 않은 접근입니다.')
        return redirect(request.referrer)
    """
    if content_text == "":
        flash('본문의 내용을 작성해주세요!')
        return redirect(request.referrer)

    if current_user.is_admin and "admin" in request.referrer:
        if article_id == "create":
            target_user = User.query.filter_by(email=user_email).first()
            target_ac = ArticleCategory.query.filter_by(title=ac_title).first()
            new_article = new_article_save_snippet(target_ac.id, title, meta_description, content, site_title, site_url, tags_str, orm_id, request_path, article_image, target_user, available_display)
            flash("아티클 등록이 완료되었습니다.")
            return redirect(url_for('admin_articles.article_change', _id=new_article.id))
        else:
            target_user = User.query.get_or_404(target_article.user_id)
            if str(target_article.user_id) == req_user_id:
                target_article_save_snippet(target_article, title, meta_description, content, site_title, site_url, tags_str, orm_id, request_path, article_image, target_user, available_display)

                flash("아티클 수정이 완료되었습니다.")
                return redirect(request.referrer)
            else:
                flash("자격없는 요청이거나 잘못된 접근(400)")
                return redirect(request.referrer)

    elif req_user_id:
        """이용자단"""
        if str(current_user.id) == req_user_id:
            if target_article:
                if g.user != target_article.user:  # or not g.user.is_admin:
                    flash('수정권한이 없습니다')
                    return redirect(url_for('articles.article_detail', _id=target_article.id, slug=target_article.slug))
                target_article_save_snippet(target_article, title, meta_description, content, site_title, site_url, tags_str, orm_id, request_path, article_image, current_user, available_display)
                if (not article_image) and (not target_article.img_path):
                    flash('대표이미지를 입력해주세요.')
                return redirect(url_for('articles.article_detail', _id=target_article.id, slug=target_article.slug))
            else:
                new_article = new_article_save_snippet(category_id, title, meta_description, content, site_title, site_url, tags_str, orm_id, request_path, article_image, g.user, available_display)
                if not article_image:
                    flash('대표이미지를 입력해주세요.')
                return redirect(url_for('articles.article_detail', _id=new_article.id, slug=new_article.slug))
        else:
            abort(401)
    else:
        abort(400)


def new_article_save_snippet(category_id, title, meta_description, content, site_title, site_url, tags_str, orm_id, request_path, article_image, user, available_display):
    new_article = Article(user_id=user.id,
                          title=title)
    new_article.meta_description = meta_description
    new_article.content = content
    new_article.ac_id = category_id
    new_article.site_title = site_title
    new_article.site_url = site_url
    new_article.orm_id = orm_id
    if (available_display == "true") or available_display is not None:
        new_article.available_display = True
    else:
        new_article.available_display = False

    if tags_str:
        tags_list = tags_str.split("[")[1].split("]")[0].split(",")
        for tag in tags_list:
            new_tag_obj = ArticleTag(user_id=user.id, orm_id=orm_id)
            tag_value = json.loads(tag)['value']
            new_tag_obj.tag = tag_value
            g.db.add(new_tag_obj)
            g.db.commit()
    if article_image:
        single_img_save(new_article, request_path, article_image, user, None)
    g.db.add(new_article)
    g.db.commit()
    return new_article


def target_article_save_snippet(article, title, meta_description, content, site_title, site_url, tags_str, orm_id, request_path, article_image, user, available_display):
    article.title = title
    article.slug = slugify(title, allow_unicode=True)
    article.meta_description = meta_description
    article.content = content
    article.site_title = site_title
    article.site_url = site_url
    if (available_display == "true") or available_display is not None:
        article.available_display = True
    else:
        article.available_display = False

    saved_tag_objs = list()
    if tags_str:
        """태그 저장"""
        tags_list = tags_str.split("[")[1].split("]")[0].split(",")
        for tag in tags_list:
            tag_obj = ArticleTag(user_id=g.user.id, orm_id=orm_id)
            tag_value = json.loads(tag)['value']
            tag_obj.tag = tag_value
            g.db.add(tag_obj)
            g.db.commit()
            saved_tag_objs.append(tag_obj)
    try:
        """사용하지 않는 태그 지우기"""
        db_tag_objs_all = article.tag_article_set
        unused_db_tag_objs = set(db_tag_objs_all) - set(saved_tag_objs)
        if unused_db_tag_objs:
            unused_tag_delete(unused_db_tag_objs)
    except Exception as e:
        print('article_tag update exception error::', e)

    if article_image:
        single_img_save(article, request_path, article_image, user, None)
    g.db.add(article)
    g.db.commit()

    """ # 저장후에 content 의 src 를, DB와 비교해서, DB 에 있으나 content 에는 없는 image(file, path)를 삭제"""
    db_img_objs_all = article.sunimage_article_set
    unused_sunimage_delete(db_img_objs_all, article, ArticleSunImage)


@articles.route('/detail/<int:_id>/<slug>', methods=['GET'])
@login_required
def article_detail(_id, slug):
    target_article = Article.query.filter_by(id=_id, slug=slug).first()
    target_category = ArticleCategory.query.filter_by(id=target_article.ac_id).first()
    target_user = User.query.filter_by(id=target_article.user_id).first()

    reply_com_objs = list()
    for comment_obj in target_article.comment_article_set:
        if comment_obj.paired_comment_id:
            reply_com_objs.append(comment_obj)
    print("reply_com_objs", reply_com_objs)

    obj_str = "article"
    view_count_save(target_user, target_article, obj_str)
    """ArticleComment SunImage 업로드 및 저장시 필요한 orm_id는 CommentEditor.js 파일내에서 생성시켰다."""
    return render_template("boards/articles/detail.html",
                           target_category=target_category,
                           target_article=target_article,
                           reply_com_objs=reply_com_objs,
                           target_user=target_user)


@articles.route('/update/<int:_id>/<slug>', methods=['GET'])
@login_required
def article_update(_id, slug):
    form = ArticleForm()
    target_article = Article.query.filter_by(id=_id, slug=slug).first()
    target_category = ArticleCategory.query.filter_by(id=target_article.ac_id).first()
    content = target_article.content.encode('ascii', 'xmlcharrefreplace')
    target_article_tags = ArticleTag.query.filter_by(orm_id=target_article.orm_id).all()

    tag_value_list = list()
    for tag in target_article_tags:
        tag_value_list.append(tag.tag)
    tags_str = str(tag_value_list)
    new_tags_str = tags_str.replace("[", "").replace("'", "").replace("]", "")
    return render_template("boards/articles/update.html",
                           form=form,
                           target_category=target_category,
                           target_article=target_article,
                           content=content,
                           tags_str=new_tags_str)


@articles.route('/delete/ajax', methods=['POST'])
def article_delete_ajax():
    _id = request.form.get("article_id")
    related_all_delete = request.form.get("related_all_delete")
    print(related_all_delete)
    target_article = Article.query.get_or_404(_id)
    target_ac = ArticleCategory.query.filter_by(id=target_article.ac_id).first()
    target_profile = db.session.query(Profile).filter_by(user_id=target_article.user_id).first()

    if target_article:
        """바로 target_profile.user_id 로 진입하면 에러 발생"""
        """admin 에서 주인 프로필이 삭제된 샵카테고리들 때문에...."""
        if current_user.is_admin and "admin" in request.referrer:
            if related_all_delete != "undefined":
                if related_all_delete == "true":
                    if target_article.img_path:
                        img_delete(target_article.img_path)
                    existing_articlesunimages = target_article.sunimage_article_set
                    if existing_articlesunimages:
                        sun_image_delete(existing_articlesunimages)

                    existing_article_comments = target_article.comment_article_set
                    if existing_article_comments:
                        for comment_obj in existing_article_comments:
                            existing_articlecommentsunimages = comment_obj.sunimage_articlecomment_set
                            if existing_articlecommentsunimages:
                                sun_image_delete(existing_articlecommentsunimages)
                    db.session.delete(target_article)
                    db.session.commit()
                    _response = {
                        "_success": "success",
                        "_delete": "delete",
                        "redirect_url": url_for('admin_articles.article_list')
                    }
                    return make_response(jsonify(_response))
                else:
                    target_article.available_display = False
                    db.session.add(target_article)
                    db.session.commit()
                    _response = {
                        "_success": "success",
                        "_delete": "delete",
                        "redirect_url": url_for('admin_articles.article_change', _id=target_article.id)
                    }
                    return make_response(jsonify(_response))
            else:
                data = error_400_json_data()
                return make_response(jsonify(data))
        elif current_user == target_article.user:
            target_article.available_display = False
            db.session.add(target_article)
            db.session.commit()
            if target_ac:
                _response = {
                    "_success": "success",
                    "_delete": "delete",
                    "redirect_url": url_for('articles.ac_detail', _id=target_ac.id, slug=target_ac.slug)
                    # "redirect_url": url_for('articles.user_article_list') + "?_id=" + str(current_user.id)
                    # "redirect_url": url_for('articles.user_article_list', _id=current_user.id)
                }
            else:  # # target_ac 가 먼저 삭제된 경우에 해당된다.
                _response = {
                    "_success": "success",
                    "_delete": "delete",
                    "redirect_url": url_for('articles.user_ac_list', _id=target_profile.user_id)
                    # "redirect_url": url_for('articles.user_article_list') + "?_id=" + str(current_user.id)
                    # "redirect_url": url_for('articles.user_article_list', _id=current_user.id)
                }
            return make_response(jsonify(_response))

        # if target_profile or current_user.is_admin:
        #     if (current_user.id == target_profile.user_id) or current_user.is_admin:
        #         try:
        #             """article_sunimage, article_tag, article_comment 들의 db table 은 삭제하지 않아도, 한꺼번에 삭제된다.
        #             (model 에 cascade='all, delete-orphan' 설정때문에) """
        #
        #             """그러나,db 에 저장된 실제 article cover_image 와 sunimage 들은 직접 삭제해줘야 한다."""
        #             if target_article.img_path:
        #                 img_delete(target_article.img_path)
        #             existing_articlesunimages = target_article.sunimage_article_set
        #             if existing_articlesunimages:
        #                 sun_image_delete(existing_articlesunimages)
        #
        #             existing_article_comments = target_article.comment_article_set
        #             if existing_article_comments:
        #                 for comment_obj in existing_article_comments:
        #                     existing_articlecommentsunimages = comment_obj.sunimage_articlecomment_set
        #                     if existing_articlecommentsunimages:
        #                         sun_image_delete(existing_articlecommentsunimages)
                            # comment_sun_image_delete(comment_obj)
        #         except Exception as e:
        #             print("article_delete_ajax() Exception Error::: ", e)
        #
        #         db.session.delete(target_article)
        #         db.session.commit()
        #
        #         if target_profile:
        #             if current_user.id == target_profile.user_id:
        #                 if "admin" not in request.referrer:
        #                     if target_ac:
        #                         _response = {
        #                             "_success": "success",
        #                             "_delete": "delete",
        #                             "redirect_url": url_for('articles.ac_detail', _id=target_ac.id, slug=target_ac.slug)
        #                             # "redirect_url": url_for('articles.user_article_list') + "?_id=" + str(current_user.id)
        #                             # "redirect_url": url_for('articles.user_article_list', _id=current_user.id)
        #                         }
        #                     else:  # # target_ac 가 먼저 삭제된 경우에 해당된다.
        #                         _response = {
        #                             "_success": "success",
        #                             "_delete": "delete",
        #                             "redirect_url": url_for('articles.user_ac_list', _id=target_profile.user_id)
        #                             # "redirect_url": url_for('articles.user_article_list') + "?_id=" + str(current_user.id)
        #                             # "redirect_url": url_for('articles.user_article_list', _id=current_user.id)
        #                         }
        #                     return make_response(jsonify(_response))
        #         if current_user.is_admin:
        #             # flash("아티클 삭제가 완료되었습니다.")  # 어드민 리스트에서 여러개 삭제시 메시지가 반복하므로 사용안함
        #             _response = {
        #                 "_success": "success",
        #                 "_delete": "delete",
        #                 "redirect_url": url_for('admin_articles.article_list')
        #             }
        #             return make_response(jsonify(_response))
        #     else:
        #         data = error_401_json_data()
        #         return make_response(jsonify(data))
        else:
            data = error_401_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@articles.route('/all/article/list', methods=['GET'])
def all_article_list():
    if current_user.is_authenticated:
        article_query = Article.query.filter_by(available_display=True).order_by(desc(Article.created_at)).filter(Article.user_id != current_user.id)
    else:
        article_query = Article.query.filter_by(available_display=True).order_by(desc(Article.created_at))

    page = request.args.get('page', type=int, default=1)
    pagination = article_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
    article_objs = pagination.items
    return render_template('boards/articles/list.html',
                           article_objs=article_objs,
                           pagination=pagination)


@articles.route('/user/article/list', methods=['GET'])
def user_article_list():
    """작성자의 아티클 리스트"""
    _id = request.args.get('_id')
    target_user = User.query.filter_by(id=_id).first()
    article_query = Article.query.order_by(desc(Article.created_at)).filter_by(user_id=_id, available_display=True)

    page = request.args.get('page', type=int, default=1)
    pagination = article_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
    article_objs = pagination.items
    return render_template('boards/articles/list.html',
                           article_objs=article_objs,
                           target_user=target_user,
                           pagination=pagination)


@articles.route('/not/available/display/article/list', methods=['GET'])
def no_display_article_list():
    article_query = Article.query.order_by(desc(Article.created_at)).filter_by(available_display=False)

    page = request.args.get('page', type=int, default=1)
    pagination = article_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
    article_objs = pagination.items
    return render_template('boards/articles/list.html',
                           article_objs=article_objs,
                           pagination=pagination)


subs_response = ""


@articles.route('/category/subscribe/ajax', methods=['POST'])
@login_required
def ac_subscribe_ajax():
    global subs_response
    _id = request.form.get("category_id")
    req_email = request.form.get("user_email")  # 어드민단
    target_ac = ArticleCategory.query.get_or_404(_id)
    if current_user.is_admin and "admin" in request.referrer:
        admin_req_user = User.query.filter_by(email=req_email).first()
        if target_ac.user == admin_req_user:
            flash("작성자는 구독할수 없습니다")
        else:
            target_ac.subscribers.append(admin_req_user)
            db.session.commit()
            flash("구독자가 추가 되었습니다.")
        subs_response = {"admin_success": "admin success",
                         "redirect_url": url_for('admin_articles.ac_subscriber_list', _id=target_ac.id)}
        return make_response(jsonify(subs_response))
    elif g.user == target_ac.user:
        subs_response = {"checked_message": "본인이 작성한 글은 구독할수 없습니다"}
        return make_response(jsonify(subs_response))
    else:
        if current_user in target_ac.subscribers:
            subs_response = {"checked_message": "이미 구독하고 계세요!"}
        else:
            target_ac.subscribers.append(g.user)
            db.session.commit()
            subscribe_count = len(target_ac.subscribers)
            subs_response = {"flash_message": '오! 구독하셨네요. 감사합니다!',
                             "subscribe_count": subscribe_count}
        return make_response(jsonify(subs_response))


@articles.route('/category/subscribe/cancel/ajax', methods=['POST'])
@login_required
def ac_subscribe_cancel_ajax():
    global subs_response
    category_id = request.form.get("category_id")
    user_id = request.form.get("user_id")  # 어드민단
    target_ac = ArticleCategory.query.get_or_404(category_id)
    if current_user.is_admin and "admin" in request.referrer:
        target_user = User.query.filter_by(id=user_id).first()
        target_ac.subscribers.remove(target_user)
        db.session.commit()
        subs_response = {
            "admin_success": "admin success",
            "redirect_url": url_for('admin_articles.ac_subscriber_list', _id=target_ac.id)
        }
    else:
        if current_user in target_ac.subscribers:
            target_ac.subscribers.remove(g.user)
            db.session.commit()
            subscribe_count = len(target_ac.subscribers)
            subs_response = {
                "flash_message": "그동안 구독해주셔서 감사해요!",
                "subscribe_count": subscribe_count
            }
        else:
            subs_response = {"no_auth_message": "구독했던 유저만 취소가 가능해요!"}
    return make_response(jsonify(subs_response))


vote_response = ""


@articles.route('/article/vote/ajax', methods=['POST'])
@login_required
def article_vote_ajax():
    global vote_response
    _id = request.form.get("article_id")
    req_email = request.form.get("user_email")  # 어드민단
    target_article = Article.query.get_or_404(_id)
    if current_user.is_admin and "admin" in request.referrer:
        admin_req_user = User.query.filter_by(email=req_email).first()
        if target_article.user == admin_req_user:
            flash("작성자는 추천할수 없습니다")
        else:
            target_article.voters.append(admin_req_user)
            db.session.commit()
            flash("추천인이 추가 되었습니다.")
        vote_response = {"admin_success": "admin success",
                         "redirect_url": url_for('admin_articles.article_voter_list', _id=target_article.id)}
        return make_response(jsonify(vote_response))
    elif g.user == target_article.user:
        vote_response = {"checked_message": "본인이 작성한 글은 추천할수 없습니다"}
        return make_response(jsonify(vote_response))
    else:
        if current_user in target_article.voters:
            vote_response = {"checked_message": "이미 추천하고 계세요!"}
        else:
            target_article.voters.append(g.user)
            db.session.commit()
            vote_count = len(target_article.voters)
            vote_response = {"flash_message": "오! 추천하셨군요. 감사합니다!",
                             "vote_count": vote_count}
        return make_response(jsonify(vote_response))


@articles.route('/article/vote/cancel/ajax', methods=['POST'])
@login_required
def article_vote_cancel_ajax():
    global vote_response
    article_id = request.form.get("article_id")
    user_id = request.form.get("user_id")  # 어드민단
    target_article = Article.query.get_or_404(article_id)
    if current_user.is_admin and "admin" in request.referrer:
        target_user = User.query.filter_by(id=user_id).first()
        target_article.voters.remove(target_user)
        db.session.commit()
        vote_response = {
            "admin_success": "admin success",
            "redirect_url": url_for('admin_articles.article_voter_list', _id=target_article.id)
        }
    else:
        if current_user in target_article.voters:
            target_article.voters.remove(g.user)
            db.session.commit()
            vote_count = len(target_article.voters)
            vote_response = {
                "flash_message": "그동안 추천해주셔서 감사해요!",
                "vote_count": vote_count
            }
        else:
            vote_response = {"checked_count": "추천했던 유저만 취소가 가능해요!"}
    return make_response(jsonify(vote_response))


@articles.route('/comment/is/secret/check/ajax', methods=['POST'])
@login_required
def article_comment_is_secret_check_ajax():
    comment_id = request.form.get("comment_id")
    target_comment = ArticleComment.query.filter_by(id=comment_id).first()

    paired_comment_id = request.form.get("paired_comment_id")
    paired_comment = ArticleComment.query.filter_by(id=paired_comment_id).first()
    if target_comment:
        response = {"is_secret": target_comment.is_secret}
        return make_response(jsonify(response))
    elif paired_comment:
        response = {"is_secret": paired_comment.is_secret}
        return make_response(jsonify(response))
    else:
        """new_comment"""
        response = {"is_secret": False}
        return make_response(jsonify(response))


@articles.route('/comment/save', methods=['POST'])
@login_required
def article_comment_save():
    """수정할 때"""
    comment_id = request.form.get("comment_id")
    target_comment = ArticleComment.query.filter_by(id=comment_id).first()

    user_email = request.form.get("user_email")  # only 어드민 comment create
    user_id = request.form.get("user_id")  # only 어드민 comment change

    paired_comment_id = request.form.get("paired_comment_id")
    paired_comment = ArticleComment.query.filter_by(id=paired_comment_id).first()

    article_id = request.form.get("article_id")
    target_article = Article.query.filter_by(id=article_id).first()

    orm_id = request.form.get("orm_id")

    content = request.form.get('content')
    is_secret = request.form.get("is_secret")

    content_text = editor_empty_check(content)
    """어드민이 작성한 것은 여기를 통과하지 못한다."""
    """
    if not target_article or not orm_user or (decode_username != orm_username) or (current_user != orm_user):
        response = {"flash_message": "처리가 불가능하거나, 유효하지 않은 접근입니다."}
        return make_response(jsonify(response))
    """
    if content_text == "":
        response = {"flash_message": "댓글의 내용을 작성해주세요!"}
        return make_response(jsonify(response))
    if current_user.is_admin and "admin" in request.referrer:
        if target_comment:
            if str(target_comment.user_id) == user_id:
                target_comment.content = content
                if is_secret is not None:
                    """체크되면 is_secret = 'on' """
                    target_comment.is_secret = True
                else:
                    target_comment.is_secret = False
                db.session.add(target_comment)
                db.session.commit()

                db_img_objs_all = target_comment.sunimage_articlecomment_set
                unused_sunimage_delete(db_img_objs_all, target_comment, ArticleCommentSunImage)

                flash("댓글 수정이 완료되었습니다.")
                return redirect(request.referrer)
            else:
                flash("자격없는 요청이거나 잘못된 접근(400)")
                return redirect(request.referrer)
        else:
            target_user = User.query.filter_by(email=user_email).first()
            new_article_comment = ArticleComment(user_id=target_user.id, orm_id=orm_id)
            new_article_comment.article_id = article_id
            new_article_comment.content = content
            if is_secret is not None:
                """체크되면 is_secret = 'on' """
                new_article_comment.is_secret = True
            else:
                new_article_comment.is_secret = False
            db.session.add(new_article_comment)
            db.session.commit()
            flash("댓글 등록이 완료되었습니다.")
            return redirect(url_for('admin_articles.comment_change', _id=new_article_comment.id))
    else:
        if target_comment:
            if g.user != target_comment.user:
                response = {"flash_message": "수정권한이 없습니다"}
                return make_response(jsonify(response))
            target_comment.content = content
            if is_secret == "true":
                """관리자에게 비밀글 등록되었슴을 알리는 메일 발송"""
                target_comment.is_secret = True
            else:
                target_comment.is_secret = False
            db.session.add(target_comment)
            db.session.commit()
            """ # 저장후에 content 의 src 를, DB와 비교해서, DB 에 있으나 content 에는 없는 image(file, path)를 삭제"""
            db_img_objs_all = target_comment.sunimage_articlecomment_set
            unused_sunimage_delete(db_img_objs_all, target_comment, ArticleCommentSunImage)
            response = {
                "_success": "_success",
                "comment_id": target_comment.id,
                "redirect_url": url_for('articles.article_detail', _id=target_article.id, slug=target_article.slug)
            }
            return make_response(jsonify(response))
        else:
            new_article_comment = ArticleComment(user_id=g.user.id, orm_id=orm_id)
            if paired_comment:
                new_article_comment.paired_comment_id = paired_comment_id
            new_article_comment.article_id = article_id
            new_article_comment.content = content

            if is_secret == "true":
                """관리자에게 비밀글 등록되었슴을 알리는 메일 발송"""
                new_article_comment.is_secret = True
            else:
                new_article_comment.is_secret = False
            db.session.add(new_article_comment)
            db.session.commit()
            response = {
                "_success": "_success",
                "comment_id": new_article_comment.id,
                "redirect_url": url_for('articles.article_detail', _id=target_article.id, slug=target_article.slug)
            }
            return make_response(jsonify(response))


@articles.route('/comment/delete/ajax', methods=['POST'])
def article_comment_delete_ajax():
    _id = request.form.get("comment_id")
    print(_id)
    target_comment = ArticleComment.query.get_or_404(_id)
    target_article = Article.query.get_or_404(target_comment.article_id)
    target_user = User.query.filter_by(id=target_comment.user_id).first()

    if target_comment:
        """바로 owner_profile.user_id 로 진입을 target_user 로 진입변경"""
        if current_user == target_user or current_user.is_admin:
            reply_comments = ArticleComment.query.filter_by(paired_comment_id=target_comment.id).all()
            for comment in reply_comments:
                comment_sunimages = comment.sunimage_articlecomment_set
                if comment_sunimages:
                    sun_image_delete(comment_sunimages)
                db.session.delete(comment)
            existing_articlecommentsunimages = target_comment.sunimage_articlecomment_set
            if existing_articlecommentsunimages:
                sun_image_delete(existing_articlecommentsunimages)

            db.session.delete(target_comment)
            db.session.commit()
            if current_user.is_admin and "admin" in request.referrer:
                # comment_sun_image_delete(target_comment)
                #
                # db.session.delete(target_comment)
                # db.session.commit()
                # # flash("댓글 삭제가 완료되었습니다.")  # 어드민 리스트에서 여러개 삭제시 메시지가 반복하므로 사용안함
                # if "admin" in request.referrer:
                _response = {
                    "_success": "success",
                    "_delete": "delete",
                    "redirect_url": url_for('admin_articles.comment_list')
                }
                return make_response(jsonify(_response))
            elif current_user == target_user:
                # comment_sun_image_delete(target_comment)
                #
                # db.session.delete(target_comment)
                # db.session.commit()
                #
                # if "admin" not in request.referrer:
                """admin 이 이용자단에서 답변 comment 를 삭제할때는 여기로 들어올 수 있게..."""
                _response = {
                    "_success": "success",
                    "_delete": "delete",
                    "redirect_url": url_for('articles.article_detail', _id=target_article.id, slug=target_article.slug)
                }
                return make_response(jsonify(_response))
            else:
                data = error_401_json_data()
                return make_response(jsonify(data))
        else:
            data = error_401_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))






from flask import Blueprint, request, render_template, g
from sqlalchemy import desc

from configs import db
from configs.config import ADMIN_PER_PAGE
from www.accounts.models import User, Profile
from www.boards.articles.forms import ArticleForm
from www.boards.articles.models import ArticleCategory, Article, ArticleCategoryTag, ArticleTag, ArticleComment, AcSubscriber, ArticleVoter
from www.boards.articles.views import ARTICLE_PER_PAGE
from www.commons.required import admin_required
from www.commons.utils import c_orm_id

NAME = 'admin_articles'
admin_article = Blueprint(NAME, __name__, url_prefix='/admin/articles')


@admin_article.route('/category/list', methods=['GET'])
@admin_required
def ac_list():
    ac_query = ArticleCategory.query.order_by(desc(ArticleCategory.id))  # .all()
    page = request.args.get('page', type=int, default=1)
    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        ac_query = ac_query.join(User, Profile).filter(ArticleCategory.title.ilike(search) |
                                                       ArticleCategory.content.ilike(search) |
                                                       User.username.ilike(search) |
                                                       User.email.ilike(search) |
                                                       Profile.nickname.ilike(search)).distinct()
    """######################"""
    pagination = ac_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    acs = pagination.items
    return render_template('boards/admin/articles/category/list.html',
                           acs=acs,
                           pagination=pagination,
                           kw=kw)


@admin_article.route('/category/<int:_id>/change', methods=['GET'])
@admin_required
def ac_change(_id):
    form = ArticleForm()
    user_objs = User.query.all()
    ac_obj = ArticleCategory.query.filter_by(id=_id).first()
    user_obj = User.query.filter_by(id=ac_obj.user_id).first()
    profile_obj = Profile.query.filter_by(user_id=ac_obj.user_id).first()

    target_ac_tags = ArticleCategoryTag.query.filter_by(orm_id=ac_obj.orm_id).all()

    tag_value_list = list()
    for tag in target_ac_tags:
        tag_value_list.append(tag.tag)
    tags_str = str(tag_value_list)
    new_tags_str = tags_str.replace("[", "").replace("'", "").replace("]", "")

    articles_query = Article.query.order_by(desc(Article.created_at)).filter_by(ac_id=ac_obj.id)
    page = request.args.get('page', type=int, default=1)
    pagination = articles_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
    article_objs = pagination.items
    return render_template('boards/admin/articles/category/change.html',
                           form=form,
                           users=user_objs,
                           target_category=ac_obj,
                           articles=article_objs,
                           target_user=user_obj,
                           target_profile=profile_obj,
                           tags_str=new_tags_str,
                           orm_id=ac_obj.orm_id,
                           pagination=pagination)


@admin_article.route('/category/create', methods=['GET'])
@admin_required
def ac_create():
    form = ArticleForm()
    user_objs = User.query.all()
    acs_all = ArticleCategory.query.all()
    orm_id = c_orm_id(acs_all, g.user)
    return render_template('boards/admin/articles/category/create.html',
                           form=form,
                           users=user_objs,
                           orm_id=orm_id)


@admin_article.route('/article/list', methods=['GET'])
@admin_required
def article_list():
    article_query = Article.query.order_by(desc(Article.id))  # .all()
    page = request.args.get('page', type=int, default=1)
    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        """.join(ArticleCategory, ArticleCategory.id == Article.ac_id) ::: 카테고리 검색을 위해 Article 을 중심으로 조인"""
        article_query = article_query\
            .join(User, Profile) \
            .join(ArticleCategory, ArticleCategory.id == Article.ac_id) \
            .filter(Profile.nickname.ilike(search) |
                    User.email.ilike(search) |
                    User.username.ilike(search) |

                    ArticleCategory.title.ilike(search) |
                    ArticleCategory.content.ilike(search) |

                    Article.title.ilike(search) |
                    Article.meta_description.ilike(search) |
                    Article.content.ilike(search)
                    ).distinct()
    """######################"""
    pagination = article_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    articles = pagination.items
    return render_template('boards/admin/articles/list.html',
                           articles=articles,
                           pagination=pagination,
                           kw=kw)


@admin_article.route('/article/<int:_id>/change', methods=['GET'])
@admin_required
def article_change(_id):
    form = ArticleForm()
    user_objs = User.query.all()
    ac_objs = ArticleCategory.query.all()
    article_obj = Article.query.filter_by(id=_id).first()
    user_obj = User.query.filter_by(id=article_obj.user_id).first()
    profile_obj = Profile.query.filter_by(user_id=article_obj.user_id).first()

    target_article_tags = ArticleTag.query.filter_by(orm_id=article_obj.orm_id).all()

    tag_value_list = list()
    for tag in target_article_tags:
        tag_value_list.append(tag.tag)
    tags_str = str(tag_value_list)
    new_tags_str = tags_str.replace("[", "").replace("'", "").replace("]", "")

    comments_query = ArticleComment.query.order_by(desc(ArticleComment.created_at)).filter_by(article_id=article_obj.id)
    page = request.args.get('page', type=int, default=1)
    pagination = comments_query.paginate(page=page, per_page=ARTICLE_PER_PAGE, error_out=False)
    comment_objs = pagination.items
    return render_template('boards/admin/articles/change.html',
                           form=form,
                           users=user_objs,
                           acs=ac_objs,
                           target_article=article_obj,
                           target_user=user_obj,
                           target_profile=profile_obj,
                           tags_str=new_tags_str,
                           orm_id=article_obj.orm_id,
                           target_comments=comment_objs,
                           pagination=pagination)


@admin_article.route('/article/create', methods=['GET'])
@admin_required
def article_create():
    form = ArticleForm()
    user_objs = User.query.all()
    acs_all = ArticleCategory.query.all()
    articles_all = Article.query.all()
    orm_id = c_orm_id(articles_all, g.user)
    return render_template('boards/admin/articles/create.html',
                           form=form,
                           users=user_objs,
                           acs=acs_all,
                           orm_id=orm_id)


@admin_article.route('/comments/list', methods=['GET'])
@admin_required
def comment_list():
    comment_query = ArticleComment.query.order_by(desc(ArticleComment.id))  # .all()
    page = request.args.get('page', type=int, default=1)
    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        """.join(ArticleCategory, ArticleCategory.id == Article.ac_id) ::: 카테고리 검색을 위해 Article 을 중심으로 조인"""
        comment_query = comment_query \
            .join(User, Profile) \
            .join(Article, Article.id == ArticleComment.article_id) \
            .filter(Profile.nickname.ilike(search) |
                    User.email.ilike(search) |
                    User.username.ilike(search) |

                    Article.title.ilike(search) |
                    Article.meta_description.ilike(search) |
                    Article.content.ilike(search) |

                    ArticleComment.content.ilike(search)
                    ).distinct()
    """######################"""
    pagination = comment_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    comments = pagination.items
    articles_all = Article.query.all()
    return render_template('boards/admin/articles/comments/list.html',
                           comments=comments,
                           articles=articles_all,
                           pagination=pagination,
                           kw=kw)


@admin_article.route('/comment/<int:_id>/change', methods=['GET'])
@admin_required
def comment_change(_id):
    user_objs = User.query.all()
    articles_all = Article.query.all()
    comment_obj = ArticleComment.query.filter_by(id=_id).first()
    target_article = Article.query.filter_by(id=comment_obj.article_id).first()
    user_obj = User.query.filter_by(id=comment_obj.user_id).first()
    profile_obj = Profile.query.filter_by(user_id=comment_obj.user_id).first()
    return render_template('boards/admin/articles/comments/change.html',
                           users=user_objs,
                           articles=articles_all,
                           target_comment=comment_obj,
                           target_article=target_article,
                           target_user=user_obj,
                           target_profile=profile_obj)


@admin_article.route('/comment/create', methods=['GET'])
@admin_required
def comment_create():
    form = ArticleForm()
    user_objs = User.query.all()
    articles_all = Article.query.all()
    comments_all = ArticleComment.query.all()
    orm_id = c_orm_id(comments_all, g.user)
    return render_template('boards/admin/articles/comments/create.html',
                           form=form,
                           users=user_objs,
                           articles=articles_all,
                           orm_id=orm_id)


@admin_article.route('/category/subscription/ac/list', methods=['GET'])
@admin_required
def subscription_ac_list():
    acs_query = ArticleCategory.query.order_by(desc(ArticleCategory.id))#.all()
    page = request.args.get('page', type=int, default=1)
    pagination = acs_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    acs = pagination.items
    return render_template('boards/admin/articles/category/subscription/categories.html',
                           acs=acs,
                           pagination=pagination)


@admin_article.route('/category/<_id>/subscriber/list', methods=['GET'])
@admin_required
def ac_subscriber_list(_id):
    users_all = User.query.all()
    target_ac = ArticleCategory.query.filter_by(id=_id).first()
    target_user = User.query.filter_by(id=target_ac.user_id).first()
    subscriber_query = AcSubscriber.query.order_by(desc(AcSubscriber.user_id)).filter_by(ac_id=target_ac.id)

    page = request.args.get('page', type=int, default=1)
    pagination = subscriber_query.paginate(page=page,
                                           per_page=ADMIN_PER_PAGE,
                                           error_out=False)
    _subscribers = pagination.items  # AcSubscriber
    subscribers = list()  # User
    for s in _subscribers:
        user = User.query.filter_by(id=s.user_id).first()
        subscribers.append(user)
    return render_template('boards/admin/articles/category/subscription/subscribers.html',
                           users=users_all,
                           target_user=target_user,
                           target_ac=target_ac,
                           _subscribers=_subscribers,
                           subscribers=subscribers,
                           pagination=pagination
                           )


@admin_article.route('/vote/article/list', methods=['GET'])
@admin_required
def vote_article_list():
    articles_query = Article.query.order_by(desc(Article.id))#.all()
    page = request.args.get('page', type=int, default=1)
    pagination = articles_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    articles = pagination.items
    return render_template('boards/admin/articles/vote/articles.html',
                           articles=articles,
                           pagination=pagination)


@admin_article.route('/article/<_id>/voter/list', methods=['GET'])
@admin_required
def article_voter_list(_id):
    users_all = User.query.all()
    target_article = Article.query.filter_by(id=_id).first()
    target_user = User.query.filter_by(id=target_article.user_id).first()
    voter_query = ArticleVoter.query.order_by(desc(ArticleVoter.user_id)).filter_by(article_id=target_article.id)

    page = request.args.get('page', type=int, default=1)
    pagination = voter_query.paginate(page=page,
                                      per_page=ADMIN_PER_PAGE,
                                      error_out=False)
    _voters = pagination.items  # ArticleVoter
    voters = list()  # User
    for v in _voters:
        user = User.query.filter_by(id=v.user_id).first()
        voters.append(user)
    return render_template('boards/admin/articles/vote/voters.html',
                           users=users_all,
                           target_user=target_user,
                           target_article=target_article,
                           _voters=_voters,
                           voters=voters,
                           pagination=pagination
                           )




from sqlalchemy import func

from www.commons.models import BaseModel
from www.commons.utils import slugify
from configs import db


# # https://stackoverflow.com/questions/46862900/why-i-am-getting-instrumentedlist-object-has-no-attribute-paginate-filter-by
# https://michaelcho.me/article/many-to-many-relationships-in-sqlalchemy-models-flask
class AcSubscriber(db.Model):
    __tablename__ = 'article_category_subscribers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    ac_id = db.Column(db.Integer, db.ForeignKey('article_categories.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


class ArticleCategory(BaseModel):
    __tablename__ = 'article_categories'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('ac_user_set'))

    title = db.Column(db.String(45), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    img_path = db.Column(db.String(200), nullable=True)

    available_display = db.Column(db.Boolean(), nullable=False, default=True)

    view_count = db.Column(db.Integer, default=0)

    subscribers = db.relationship('User', secondary='article_category_subscribers', backref=db.backref('ac_subscriber_set'))

    def __init__(self, title, user_id):
        self.user_id = user_id
        self.title = title
        self.slug = slugify(self.title, allow_unicode=True)

    def __repr__(self):
        return f"<ArticleCategory('{self.id}', '{self.title}')>"


class ArticleCategoryTag(BaseModel):
    __tablename__ = 'article_category_tags'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('actag_user_set'))

    tag = db.Column(db.String(350), nullable=False)

    ac = db.relationship('ArticleCategory', backref=db.backref('tag_ac_set', cascade='all, delete-orphan'),
                         primaryjoin='foreign(ArticleCategoryTag.orm_id) == remote(ArticleCategory.orm_id)')


class ArticleVoter(db.Model):
    __tablename__ = 'article_voters'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


class Article(BaseModel):
    __tablename__ = 'articles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('article_user_set'))

    ac_id = db.Column(db.Integer, db.ForeignKey('article_categories.id', ondelete='CASCADE'))
    ac = db.relationship('ArticleCategory', backref=db.backref('article_ac_set'))

    title = db.Column(db.String(45), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    meta_description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    img_path = db.Column(db.String(200), nullable=True)

    available_display = db.Column(db.Boolean(), nullable=False, default=True)

    site_title = db.Column(db.String(45), nullable=True)
    site_url = db.Column(db.Text, nullable=True)

    view_count = db.Column(db.Integer, default=0)

    voters = db.relationship('User', secondary="article_voters", backref=db.backref('article_voter_set'))

    def __init__(self, title, user_id):
        self.user_id = user_id
        self.title = title
        self.slug = slugify(self.title, allow_unicode=True)

    def __repr__(self):
        return f"<Article('{self.id}', '{self.title}')>"


class ArticleSunImage(BaseModel):
    __tablename__ = 'article_sun_images'
    """Please set confirm_deleted_row s=False within the mapper configuration to prevent this warning."""
    __mapper_args__ = {
        'confirm_deleted_rows': False
    }
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('articlesunimage_user_set'))

    img_path = db.Column(db.String(350), nullable=False)
    original_filename = db.Column(db.String(350), nullable=False)

    article = db.relationship('Article', backref=db.backref('sunimage_article_set', cascade='all, delete-orphan'),
                              primaryjoin='foreign(ArticleSunImage.orm_id) == remote(Article.orm_id)')


class ArticleTag(BaseModel):
    __tablename__ = 'article_tags'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('articletag_user_set'))

    tag = db.Column(db.String(350), nullable=False)

    article = db.relationship('Article', backref=db.backref('tag_article_set', cascade='all, delete-orphan'),
                              primaryjoin='foreign(ArticleTag.orm_id) == remote(Article.orm_id)')


class ArticleComment(BaseModel):
    __tablename__ = 'article_comments'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('articlecomments_user_set'))

    content = db.Column(db.Text(), nullable=False)
    is_secret = db.Column(db.Boolean(), nullable=False, default=False)

    available_display = db.Column(db.Boolean(), nullable=False, default=True)

    paired_comment_id = db.Column(db.Integer, nullable=True)

    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    article = db.relationship('Article', backref=db.backref('comment_article_set', cascade='all, delete-orphan'))


class ArticleCommentSunImage(BaseModel):
    __tablename__ = 'articlecomment_sun_images'
    """Please set confirm_deleted_row s=False within the mapper configuration to prevent this warning."""
    __mapper_args__ = {
        'confirm_deleted_rows': False
    }
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('articlecommentsunimage_user_set'))

    img_path = db.Column(db.String(350), nullable=False)  # 임시로 한번 저장하고 넘어가야 하기 때문에 nullable=True.
    original_filename = db.Column(db.String(350), nullable=False)

    article_id = db.Column(db.Integer, nullable=False)

    articlecomment = db.relationship('ArticleComment', backref=db.backref('sunimage_articlecomment_set', cascade='all, delete-orphan'),
                                     primaryjoin='foreign(ArticleCommentSunImage.orm_id) == remote(ArticleComment.orm_id)')



from functools import wraps

from www.boards.articles.models import Article, ArticleCategory
from www.commons.required import created_obj_ownership


def ac_ownership_required(function):
    @wraps(function)
    def decorator_function(_id, *args, **kwargs):
        ac = ArticleCategory.query.get_or_404(_id)
        created_obj_ownership(ac.user_id)
        return function(_id, *args, **kwargs)
    return decorator_function


def article_ownership_required(function):
    @wraps(function)
    def decorator_function(_id, *args, **kwargs):
        article = Article.query.get_or_404(_id)
        created_obj_ownership(article.user_id)
        return function(_id, *args, **kwargs)
    return decorator_function


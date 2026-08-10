# 10 aug 26
# Christiano Fernandes
# pagination.py
# page / search params shared by every list endpoint
#
# Offset paging rather than cursors: the lists are a few hundred rows, the
# frontend already keeps its filters in the URL, and scoped_key() already folds
# the query string into the cache key — so a paged, filtered response caches as
# its own entry with nothing extra to wire.


from flask import request
from sqlalchemy import or_

MAX_PER_PAGE = 100
DEFAULT_PER_PAGE = 25


def paginate(query):
    page = max(request.args.get("page", 1, type=int) or 1, 1)
    per_page = request.args.get("perPage", DEFAULT_PER_PAGE, type=int) or DEFAULT_PER_PAGE
    per_page = min(max(per_page, 1), MAX_PER_PAGE)

    # order_by(None) strips the ORDER BY, which a COUNT does not need and which
    # some backends reject inside the wrapping subquery.
    total = query.order_by(None).count()
    rows = query.limit(per_page).offset((page - 1) * per_page).all()

    return rows, {"page": page, "perPage": per_page, "total": total}


def search(query, columns):
    """Case-insensitive OR across `columns`, driven by ?search=."""
    term = (request.args.get("search") or "").strip()
    if not term:
        return query

    like = f"%{term}%"
    return query.filter(or_(*[column.ilike(like) for column in columns]))


def sort(query, allowed, default):
    """Ordering from ?sort= and ?dir=.

    `allowed` maps the client's column key to a real column. An unknown key
    falls back to the default rather than being interpolated into the query —
    the client never names a database column directly.

    `default` is appended as a tiebreaker so paging stays stable when the sort
    column has duplicates.
    """
    column = allowed.get(request.args.get("sort"))
    if column is None:
        return query.order_by(*default)

    descending = request.args.get("dir") == "desc"
    return query.order_by(column.desc() if descending else column.asc(), *default)


def enum_filter(query, column, enum_cls):
    """Applies ?status= if it names a real member; ignores it otherwise."""
    raw = (request.args.get("status") or "").strip()
    if not raw:
        return query
    try:
        return query.filter(column == enum_cls(raw))
    except ValueError:
        return query

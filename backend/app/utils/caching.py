# 9 aug 26
# Christiano Fernandes
# caching.py
# Redis cache keys, scoped so one user can never be served another's data
#
# Deliberately NOT @cache.cached. That decorator keys on request.path, and
# /api/drives returns a DIFFERENT list to every student (it is filtered by their
# own branch, CGPA and graduation year). A path-only key would hand student B
# student A's results — a data leak, not a stale-cache bug.
#
# So the key is built by hand and always carries:
#   namespace : version : path : role : userId : query-string
#
# The PATH is in there because two endpoints can legitimately share a namespace
# — /api/admin/companies and /api/companies both have to be dropped when a
# company is approved. Without the path they would also share a cache entry,
# and per_user=False drops the role too, so the admin's payload (account status,
# blacklist flags, moderation capabilities) could be served to a student.
#
# The version is a counter in Redis. Bumping it on a write orphans every old key
# at once, which is how you invalidate per-user keys without having to enumerate
# every user. Orphaned keys then expire on their own.


from flask import request

from app.extensions import cache
from app.utils.identity import current_role, current_user_id

# Every cached response also carries a TTL, so staleness is bounded even if an
# invalidation is ever missed. Expiry is the safety net; the version bump is the
# correctness mechanism.
DEFAULT_TTL = 60


def _version(namespace):
    key = f"ver:{namespace}"
    version = cache.get(key)
    if version is None:
        version = 1
        cache.set(key, version, timeout=0)  # 0 = never expires
    return version


def invalidate(namespace):
    """Call after any write that changes what this namespace returns."""
    cache.set(f"ver:{namespace}", _version(namespace) + 1, timeout=0)


def scoped_key(namespace, per_user=True):
    """per_user=False for lists that are identical for every caller who is
    allowed to see them at all — the admin registers, for instance."""
    parts = [namespace, str(_version(namespace)), request.path]

    if per_user:
        parts += [current_role() or "-", str(current_user_id())]

    query = request.query_string.decode()
    if query:
        parts.append(query)

    return ":".join(parts)


def cached_payload(key, build, ttl=DEFAULT_TTL):
    """Return the cached dict for `key`, or build it, store it and return it."""
    payload = cache.get(key)
    if payload is None:
        payload = build()
        cache.set(key, payload, timeout=ttl)
    return payload

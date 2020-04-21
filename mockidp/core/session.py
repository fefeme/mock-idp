# coding: utf-8
import time
import uuid
from datetime import datetime
from datetime import timedelta

_sessions = dict()
_next_session_id = 0


class Session:
    def __init__(self, user, request):
        self.user = user
        self.request_id = request.id
        self.sp_entity_id = request.sp_entity_id
        self.id = '_' + str(uuid.uuid4())
        self.assertion_id = '_' + str(uuid.uuid4())
        self.created = time.time()

    @property
    def not_on_or_after(self):
        return (datetime.now() + timedelta(days=365 * 2)).isoformat()

    def __str__(self) -> str:
        return f"Session(user: {self.user}, request_id: {self.request_id}, sp_entity_id: {self.sp_entity_id}, id: {self.id}, created: {self.created})"

    def __repr__(self):
        return str(self)


def get_session(user, request):
    username = user['username']
    if has_session(username):
        return _sessions[username]
    else:
        session = Session(user, request)
        _sessions[username] = session
        return session


def retrieve_session(username):
    if has_session(username):
        return _sessions[username]
    else:
        raise Exception(f'Failed to locate session for {username}')


def has_session(username):
    return username in _sessions


def _generate_session_id(username):
    global _next_session_id
    _next_session_id += 1
    return f"{username}_{_next_session_id}"

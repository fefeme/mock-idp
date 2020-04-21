# coding: utf-8
from mockidp.core.config import get_metadata

LOGIN_SUCCESS = 0
LOGIN_FAIL = 1


def login_user(config, username, password):
    """ Authenticate user """

    if password == get_metadata().get('password'):
        return LOGIN_SUCCESS, {
            'username': username,

        }

    return LOGIN_FAIL, None


def logout_user(config, username):
    """ Logout user """
    user = config['users'].get(username)
    user['username'] = username
    return LOGIN_SUCCESS, None

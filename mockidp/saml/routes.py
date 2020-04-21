import flask
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from mockidp import app

from mockidp.core.auth import login_user, logout_user, LOGIN_SUCCESS
from mockidp.core.session import get_session, retrieve_session

from .request import parse_request
from .response import create_auth_response, create_logout_response
from ..core.config import get_metadata

open_saml_requests = dict()
conf = None


def init(_conf):
    global conf
    conf = _conf


@app.route('/saml', methods=['POST'])
def begin_login():
    saml_request = flask.request.form['SAMLRequest']
    req = parse_request(saml_request)

    print(f"Storing request {req.id}")
    open_saml_requests[req.id] = req

    response = flask.make_response(flask.redirect("/saml/login", code=302))
    response.set_cookie('mockidp_request_id', value=req.id)
    return response


@app.route('/saml', methods=['GET'])
def begin_login_get():
    saml_request = flask.request.args['SAMLRequest']
    print(f"Got saml_request {saml_request}")

    req = parse_request(saml_request)

    print(f"Storing request {req.id}")
    open_saml_requests[req.id] = req

    response = flask.make_response(flask.redirect("/saml/login", code=302))
    response.set_cookie('mockidp_request_id', value=req.id)
    return response


def get_login_form():
    from flask_wtf import FlaskForm
    metadata = get_metadata()
    attributes = metadata.get('attributes')

    class LoginForm(FlaskForm):
        pass

    for attribute_name in attributes:
        attribute = attributes.get(attribute_name)
        validators = []
        if not attribute.get('optional'):
            validators.append(DataRequired())

        setattr(LoginForm, attribute_name, StringField(attribute.get('display_name'), validators=validators))

    setattr(LoginForm, 'password', PasswordField('Password', validators=[DataRequired()]))

    return LoginForm()


@app.route('/saml/login', methods=['GET'])
def login_view():
    return flask.render_template('login.html', form=get_login_form())


class UserAttribute:
    def __init__(self, name, attr_name=None, value=None):
        self.name = name
        self.attr_name = attr_name
        self.value = value

    @property
    def attribute(self):
        if self.attr_name:
            return self.attr_name
        return self.name


def build_user_object(form):
    username_attribute = get_metadata().get('username')
    attributes = get_metadata().get('attributes')

    user = {
        'username': getattr(form, f"{username_attribute}").data
    }
    user_attributes = []
    for attribute, values in attributes.items():
        user_attributes.append(UserAttribute(attribute, attr_name=values.get('attr_name'), value=getattr(form, attribute).data))

    user.update({
        'attributes': user_attributes
    })
    return user


@app.route('/saml/auth', methods=['POST'])
def authenticate():
    form = get_login_form()
    if form.validate_on_submit():
        if form.password.data == get_metadata().get('password'):
            user = build_user_object(form)
            saml_req_id = flask.request.cookies.get('mockidp_request_id')
            if saml_req_id not in open_saml_requests:
                return '404: Missing login session', 404
            saml_request = open_saml_requests[saml_req_id]
            session = get_session(user, saml_request)
            url, saml_response = create_auth_response(conf, session)
            return flask.render_template('auth_response.html', post_url=url, saml_response=saml_response)
        else:
            print('flashing!')
            flask.flash(f"Incorrect username or password {username}")
            return flask.redirect("/saml/login", code=302)
    else:
        return flask.render_template('login.html', form=form)


@app.route('/saml/logout', methods=['GET'])
def logout_view():
    """ <?xml version="1.0"?>
        <samlp:LogoutRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" 
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_de4a72a1d3fd94ba287289b5b81987884320a6d5eb"
                Version="2.0" 
                IssueInstant="2019-03-06T18:32:52.137Z" 
                Destination="http://mockidp:5000/saml/logout">
            <saml:Issuer>local:onehope:web</saml:Issuer>
            <saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">charlie</saml:NameID>
            <samlp:SessionIndex>
                _be9967abd904ddcae3c0eb4189adbe3f71e327cf93
            </samlp:SessionIndex>
        </samlp:LogoutRequest> """
    saml_request = flask.request.args['SAMLRequest']
    req = parse_request(saml_request)
    username = req.name_id
    print("Logging out {}".format(username))
    session = retrieve_session(username)
    print(" Session is {}".format(session))
    url, saml_response = create_logout_response(conf, session)
    return flask.render_template('saml/logout.html', post_url=url, saml_response=saml_response)

from mockidp.main import main
from mockidp import app
from mockidp import core, saml

if __name__ == "__main__":
    conf, sessions = core.init()
    saml.init(conf)

    for sp in conf['service_providers']:
        print(f"Known Service Provider {sp['name']}")

    app.run(host="0.0.0.0")

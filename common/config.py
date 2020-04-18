import os
import configparser
import logging.config

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.ini'), disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class App:
    def __init__(self, config_path):
        self._config_path = config_path
        self._config = configparser.ConfigParser()
        self._config.read(self._config_path)
        self._id = os.path.basename(os.path.dirname(self._config_path))

    def __str__(self):
        return self._id

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._read("general", "app_name")

    @name.setter
    def name(self, name):
        self._update("general", "app_name", name)

    @property
    def size(self):
        return self._read("general", "app_size")

    @size.setter
    def size(self, size):
        self._update("general", "app_size", size)

    @property
    def address(self):
        return self._read("general", "app_base_address")

    @address.setter
    def address(self, address):
        self._update("general", "app_base_address", address)

    @property
    def frequency(self):
        return self._read("general", "app_refresh_cycle")

    @frequency.setter
    def frequency(self, frequency):
        self._update("general", "app_refresh_cycle", frequency)

    @property
    def general(self):
        return dict(self._config.items("general"))

    @general.setter
    def general(self, general):
        for key, value in general.items():
            self._update("general", key, value)

    @property
    def parameter(self):
        return dict(self._config.items("parameter"))

    @parameter.setter
    def parameter(self, parameter):
        for key, value in parameter.items():
            self._update("parameter", key, value)

    def _update(self, section, key, value):
        last_value = self._read(section, key)
        if last_value != value and self._config.has_option(section, key):
            with open(self._config_path, 'w') as file:
                logger.info(F"Update {section}/{key} with {value}")
                self._config.set(section, key, value)
                self._config.write(file)

    def _read(self, section, key, fallback=""):
        return self._config.get(section, key, fallback=fallback)


class Config:
    __instance = None
    _app_dir = os.path.join(os.path.dirname(__file__), "../apps")
    _main_config = os.path.join(_app_dir, "config.cfg")
    _config = None
    _apps = []

    @property
    def apps(self):
        return self._apps

    def get_app(self, app_id):
        for _app in self._apps:
            if str(_app) == app_id:
                return _app
        return None

    # getting the values
    @property
    def active_app(self):
        return self._read("general", "active_app")

    # setting the values
    @active_app.setter
    def active_app(self, active_app):
        self._update("general", "active_app", active_app)

    # getting the values
    @property
    def last_execution(self):
        return self._read("general", "last_execution")

    # setting the values
    @last_execution.setter
    def last_execution(self, last_execution):
        self._update("general", "last_execution", last_execution)

    def _update(self, section, key, value):
        last_value = self._read(section, key)
        if last_value != value:
            with open(self._main_config, 'w') as file:
                logger.info(F"Update {section}/{key} with {value}")
                self._config.set(section, key, value)
                self._config.write(file)

    def _read(self, section, key, fallback=""):
        return self._config.get(section, key, fallback=fallback)

    def _get_app_dirs(self):
        return [os.path.abspath(os.path.join(self._app_dir, d)) for d in os.listdir(self._app_dir) if
                os.path.isdir(os.path.join(self._app_dir, d))]

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read(self._main_config)

        for app_dir in self._get_app_dirs():
            app_config = os.path.join(app_dir, "config.cfg")
            self._apps.append(App(app_config))


config = Config()


if __name__ == '__main__':
    print("active app: ", config.active_app)
    config.active_app = "weather-forecast"
    print("active app: ", config.active_app)
    print("last execution: ", config.last_execution)

    print("available apps:")
    for app in config.apps:
        print(" -", app)
        print("   name: ", app.name)
        print("   frequency: ", app.frequency)
        print("   size: ", app.size)
        print("   address: ", app.address)
        print("   parameter: ", app.parameter)
        app.parameter = {'city': 'Koblenz'}
        print("   parameter: ", app.parameter)

    print(config.get_app('weather-forecast').name)
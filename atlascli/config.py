from configparser import ConfigParser
import os


def initialise():

    org = input("Please specify your organization: ")
    private_key = input("Please enter your private key: ")
    public_key = input("Please input your public key: ")

    cfg = Config()
    cfg.save_config_file_keys(public_key, private_key, org)

    return cfg


class Config:
    #
    # configurations are stored in a file called atlascli.cfg. Configurations are first
    # parsed from the command line. Then from the environment an finally from a config
    # file passed on the command line.
    # Priority is :
    # Command line Args > Named config File > Environment Variables > Default Config file
    #

    default_config_filename = "atlascli.cfg"

    PUBLIC_KEY_ENV = "ATLAS_PUBLIC_KEY"
    PRIVATE_KEY_ENV = "ATLAS_PRIVATE_KEY"

    def __init__(self, default_org: str = None, filename: str = None):

        self._cfg = ConfigParser()
        self._default_org = default_org
        self._private_key = None
        self._public_key = None
        self._filename = Config.default_config_filename

        if filename is None:
            pass
        elif type(filename) is str:
            self._filename = filename
        else:
            raise ValueError(f"{filename} is not a string type")

    def load(self, private_key: str = None, public_key: str = None, filename: str = None):

        if private_key and public_key:
            self.load_from_args(public_key, private_key)
        elif filename:
            return self.load_from_file(filename)
        else:
            try:
                return self.load_from_env()
            except ValueError:
                return self.load_from_file(Config.default_config_filename)

    def load_from_args(self, public_key: str, private_key: str):
        self._public_key = public_key
        self._private_key = private_key

        return self._public_key, self._private_key

    def load_from_env(self):
        self._public_key = os.getenv("ATLAS_PUBLIC_KEY")
        if self._public_key is None:
            raise ValueError("you must specify an ATLAS public key via "
                             "via the environment variable ATLAS_PUBLIC_KEY")

        self._private_key = os.getenv("ATLAS_PRIVATE_KEY")
        if self._private_key is None:
            raise ValueError("you must specify an an ATLAS private key "
                             "using the the environment variable ATLAS_PRIVATE_KEY")

        return self._public_key, self._private_key

    def load_from_file(self, input_file: str = None):
        if type(input_file) is str:
            if os.path.isfile(input_file):
                parsed_list = self._cfg.read(input_file)
                if len(parsed_list) < 1:
                    raise ValueError(f"Failed to parse atlascli configuration file: '{input_file}'")
                else:
                    self._filename = input_file
            else:
                raise ValueError(f"File does not exist: '{input_file}'")
        else:
            if input_file is None and self._filename is None:
                raise ValueError(f"filename for input is not defined")
            elif input_file is None:
                parsed_list = self._cfg.read(self._filename)
                if len(parsed_list) < 1:
                    raise ValueError(f"Failed to parse atlascli configuration file: '{self._filename}'")

        if not self._default_org:
            self._default_org = self.get_default_org()
        self._public_key = self.get_public_key(self._default_org)
        self._private_key = self.get_private_key(self._default_org)

        return self._public_key, self._private_key

    @property
    def filename(self):
        return self._filename

    def set_default_org(self, org: str):
        if "DEFAULT" not in self._cfg:
            self._cfg["DEFAULT"] = {}

        self._cfg["DEFAULT"]["organization"] = org
        self.save_config()
        self._default_org = org

    def get_default_org(self):
        if "DEFAULT" in self._cfg:
            if "organization" in self._cfg["DEFAULT"]:
                self._default_org = self._cfg["DEFAULT"]["organization"]
                return self._default_org

        return None

    def is_org(self, org:str):
        return org in self._cfg

    @property
    def config_filename(self):
        return self._filename

    def has_keys(self, org:str = None):

        if org is None:
            org = self._default_org
        return org in self._cfg and "public_key" in self._cfg[org] and "private_key" in self._cfg[org]

    def _get_key(self, section: str, name: str):
        if section in self._cfg:
            if name in self._cfg[section]:
                return self._cfg[section][name]
            else:
                raise ValueError(f"No such key '{section}:{name}' in {self.config_filename}")
        else:
            raise ValueError(f"No such section '{section}' in {self.config_filename}")

    def get_private_key(self, org: str=None):
        if org :
            return self._get_key(org, "private_key")
        else:
            return self._private_key

    def get_public_key(self, org: str = None):
        if org:
            return self._get_key(org, "public_key")
        else:
            return self._public_key

    def get_config_file_keys(self, org: str = None):
        self.load_from_file()
        return self.get_public_key(org), self.get_private_key(org)

    def save_config_file_keys(self, public_key, private_key, org: str=None):

        if org is None:
            org = self._default_org
        if org not in self._cfg:
            self._cfg[org] = {}
        self._cfg[org]["public_key"] = public_key
        self._cfg[org]["private_key"] = private_key

        self.save_config()

    def save_config(self, output_filename=None):
        if output_filename is None:
            output_filename = self._filename
        with open(output_filename, "w") as output_file:
            self._cfg.write(output_file)

    @staticmethod
    def obfuscator(s):
        l = len(s)
        if l > 3:
            obs = "X" * (l-3)
            return f"{obs}{s[-3:]}"
        else:
            return s

    def obfuscate(self, org: str = None):
        public_key = ""
        private_key = ""
        if self.has_keys(org):
            public_key, private_key = self.get_config_file_keys(org)
        else:
            raise ValueError(f"No such organization: {org}")

        return f"'{org}' -> public key: '{self.obfuscator(public_key)}' private key: '{self.obfuscator(private_key)}'"

    def pprint(self):
        def_org = self.get_default_org()
        if def_org:
            print(f"Default organization: {def_org}")
        print(self)

    def __str__(self):
        return"\n".join([self.obfuscate(k) for k in self._cfg.keys()])

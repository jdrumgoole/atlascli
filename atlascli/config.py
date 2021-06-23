from configparser import ConfigParser
import os


def initialise():

    org = input("Please specify your organization: ")
    private_key = input("Please enter your private key: ")
    public_key = input("Please input your public key: ")

    cfg = Config()
    cfg.save_keys(public_key, private_key, org)

    return cfg


class Config:

    default_config_filename = "atlascli.cfg"

    def __init__(self, filename: str = None):
        self._cfg = ConfigParser()
        self._private_key = None
        self._public_key = None
        if filename:
            self._filename = filename
        else:
            self._filename = Config.default_config_filename

        if os.path.exists(self._filename):
            self.load()

    @property
    def filename(self):
        return self._filename

    def set_default_org(self, org: str):
        if "DEFAULT" not in self._cfg:
            self._cfg["DEFAULT"] = {}

        self._cfg["DEFAULT"]["organization"] = org
        self.save()

    def get_default_org(self):
        if "DEFAULT" in self._cfg:
            if "organization" in self._cfg["DEFAULT"]:
                return self._cfg["DEFAULT"]["organization"]
        return None

    @property
    def config_filename(self):
        return self._filename

    def has_keys(self, org:str = None):

        return org in self._cfg and "public_key" in self._cfg[org] and "private_key" in self._cfg[org]

    def private_key(self, org: str):
        if org in self._cfg and "private_key" in self._cfg[org]:
            return self._cfg[org]["private_key"]
        else:
            return None

    def public_key(self, org: str = None):
        if org in self._cfg and "public_key" in self._cfg[org]:
            return self._cfg[org]["public_key"]
        else:
            return None

    def get_keys(self, org: str = None):
        self.load()
        return self.public_key(org), self.private_key(org)

    def save_keys(self, public_key, private_key, org: str):

        if org not in self._cfg:
            self._cfg[org] = {}
        self._cfg[org]["public_key"] = public_key
        self._cfg[org]["private_key"] = private_key

        self.save()

    def is_org(self, org:str):
        return org in self._cfg

    def load(self, input_file=None):
        if input_file:
            self._filename = input_file
        self._cfg.read(self._filename)

    def save(self, output_file=None):
        if output_file:
            self._filename = output_file
        with open(self._filename, "w") as output_file:
            self._cfg.write(output_file)

    @staticmethod
    def obfuscator(s):
        l = len(s)
        if l > 3:
            obs = "X" * (l-3)
            return f"{obs}{s[-3:]}"
        else:
            return s

    def obfuscate(self, org:str = None):
        public_key = ""
        private_key = ""
        if self.has_keys(org):
            public_key, private_key = self.get_keys(org)
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

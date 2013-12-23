from Fifa14Client import LoginManager
from Fifa14Client import WebAppFunctioner
import ConfigParser
from extra import EAHash


def do_main():
    Config = ConfigParser.ConfigParser()
    Config.read("accounts_example.ini")
    for section in Config.sections():
        email = Config.get(section, 'Email')
        password = Config.get(section, 'Password')
        secret_answer = Config.get(section, 'Secret')
        security_hash = EAHash.EAHashingAlgorithm().EAHash(secret_answer)
        form_data = eval(Config.get(section, 'FormData'))

        login = LoginManager.LoginManager(email,password,security_hash,form_data)
        print login.login()
        func = WebAppFunctioner.WebAppFunctioner(login)
        print func.get_coin_amount()



if __name__ == "__main__":
    do_main()

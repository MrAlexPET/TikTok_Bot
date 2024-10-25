import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tiktok_captcha_solver import SeleniumSolver
import undetected_chromedriver as uc

import os
from dotenv import load_dotenv, find_dotenv


class TikTokBot:
    def __init__(self):
        self.url = "https://www.tiktok.com/"
        self.driver = uc.Chrome(headless=False)
        self.file_path = "days.txt"
        self.max_value = 366
        load_dotenv(find_dotenv())
        self.api_key = os.getenv('api_key')
        self.solver = SeleniumSolver(self.driver, self.api_key)
        self.day = self.load_day()

    def load_day(self):
        """Загружает или инициализирует значение из файла."""
        try:
            with open(self.file_path, "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            with open(self.file_path, "w") as f:
                f.write("1")
            return 1

    def save_day(self):
        """Сохраняет текущее значение day в файл."""
        with open(self.file_path, "w") as f:
            f.write(str(self.day))

    def xpath_exists(self, xpath):
        """Проверяет, существует ли элемент с данным XPath."""
        try:
            self.driver.find_element(By.XPATH, xpath)
            return True
        except NoSuchElementException:
            return False

    def authenticate(self):
        """Авторизация на TikTok."""
        self.driver.get(self.url)
        time.sleep(7)
        self.driver.find_element(By.ID, "header-login-button").click()
        time.sleep(5)

        if self.xpath_exists("//div[contains(text(), 'Введите телефон / почту / имя пользователя')]"):
            self.driver.find_element(By.XPATH,
                                     "//div[contains(text(), 'Введите телефон / почту / имя пользователя')]").click()
            time.sleep(5)

        self.driver.find_element(By.LINK_TEXT, "Войти через эл. почту или имя пользователя").click()
        time.sleep(5)

        email_input = self.driver.find_element(By.NAME, "username")
        email_input.clear()
        email_input.send_keys(os.getenv('login'))
        time.sleep(3)

        password_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.clear()
        password_input.send_keys(os.getenv('password'), Keys.ENTER)
        time.sleep(30)

        # self.solver.solve_captcha_if_present()
        # time.sleep(10)

    def find_chat(self, target_username="dragneel"):
        """Находит нужный чат с заданным именем пользователя."""
        self.driver.get("https://www.tiktok.com/messages")
        time.sleep(10)

        wait = WebDriverWait(self.driver, 10)
        chat_items = self.driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='chat-list-item']")

        for item in chat_items:
            try:
                item.click()
                nickname_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-e2e='chat-nickname']"))
                )
                if nickname_element.text == target_username:
                    print(f"Найден нужный чат с пользователем {target_username}")
                    time.sleep(5)
                    break
            except NoSuchElementException:
                print(f"Имя пользователя '{target_username}' не найдено в этом элементе.")
            except Exception as e:
                print(f"Произошла ошибка: {e}")

    def send_message(self):
        """Отправляет сообщение с текущим значением day и увеличивает его."""
        message_input = self.driver.find_element(By.CSS_SELECTOR,
                                                 '.DraftEditor-editorContainer [contenteditable="true"]')
        message_input.click()
        message_input.send_keys(str(self.day))
        message_input.send_keys(Keys.ENTER)
        print(f"Отправлено сообщение: {self.day}")

        self.day += 1
        self.save_day()
        print(f"Новое значение записано: {self.day}")

    def run(self):
        """Запускает основной цикл отправки сообщений, пока day не достигнет max_value."""
        self.authenticate()
        self.find_chat()

        while self.day <= self.max_value:
            try:
                self.send_message()
                time.sleep(3600)
            except Exception as e:
                print(f"Произошла ошибка во время отправки сообщения: {e}")
                break

        self.driver.quit()


if __name__ == '__main__':
    bot = TikTokBot()
    bot.run()

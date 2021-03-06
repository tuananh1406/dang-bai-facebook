# coding: utf-8
import os
import sys
import logging
import requests
import json

from datetime import datetime

from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class CustomLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'cookies_name'):
            record.cookies_name = EXTRA.get('cookies_name')
        return True


EXTRA = dict(cookies_name=None)
TESTING = None
URL = 'https://sweepwidget.com/view/43885-am23udvs/sk9wul-43885'


def thiet_lap_logging(name):
    log_format = ' - '.join([
        '%(asctime)s',
        '%(name)s',
        '%(levelname)s',
        '%(message)s',
    ])
    formatter = logging.Formatter(log_format)
    file_handles = logging.FileHandler(
        filename='logs.txt',
        mode='a',
        encoding='utf-8',
    )
    file_handles.setFormatter(formatter)

    syslog = logging.StreamHandler()
    syslog.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger.addHandler(syslog)
    if not TESTING:
        logger.addHandler(file_handles)

    return logger


def tam_ngung_den_khi(driver, _xpath):
    '''Hàm tạm ngưng đến khi xuất hiện đường dẫn xpath
    '''
    _tam_ngung = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            _xpath,
        )),
    )
    return _tam_ngung


def tam_ngung_va_tim(driver, _xpath):
    '''Hàm tạm ngưng đến khi xuất hiện đường dẫn xpath và chọn xpath đó
    '''
    tam_ngung_den_khi(driver, _xpath)
    return driver.find_element(by='xpath', value=_xpath)


def chay_trinh_duyet(headless=True):
    '''Mở trình duyệt và trả về driver
    '''
    options = Options()
    options.add_argument('--headless')
    service = Service(ChromeDriverManager().install())
    LOGGER.info('Chạy trình duyệt, headless=%s', headless)
    _driver = webdriver.Chrome(
        # options=options,
        service=service,
    )
    # Hàm đặt thời gian tải trang, dùng khi tải trang quá lâu
    # _driver.set_page_load_timeout(5)
    return _driver


def mo_sweepwidget(_driver):
    _driver.get(URL)
    return _driver


def tu_dong_sweepwidget(_driver, _email):
    _xpath_name = '//input[@type="text"]'
    _xpath_email = '//input[@type="email"]'
    _xpath_button = '//button[@id="sw_login_button"]'
    _input_name = tam_ngung_va_tim(_driver, _xpath_name)
    _input_name.send_keys(_email.split('@')[0])
    _input_email = _driver.find_element(by='xpath', value=_xpath_email)
    _input_email.send_keys(_email)
    input()
    return _driver


LOGGER = thiet_lap_logging(__file__)


if __name__ == '__main__':
    LOGGER.info('Chạy chương trình')
    THOI_GIAN_HIEN_TAI = datetime.now()
    DRIVER = None

    try:
        TESTING = True
        if TESTING:
            LOGGER.info('*' * 50)
            HEADLESS = False
            EMAILS_PATH = sys.argv[1]
        else:
            COOKIES_PATH = 'tuananh.bak'
            HEADLESS = True

        DRIVER = chay_trinh_duyet(headless=HEADLESS)
        DRIVER = mo_sweepwidget(DRIVER)
        input('Kiem tra capcha')
        # DRIVER.maximize_window()
        # SIZE = DRIVER.get_window_size()
        # DRIVER.set_window_size(SIZE['width'] / 2, SIZE['height'])
        # DRIVER.set_window_position(
        #     # (SIZE['width'] / 2) + SIZE['width'],
        #     (SIZE['width'] / 2),
        #     0,
        #     windowHandle='current',
        # )

        # with open(EMAILS_PATH, 'r', encoding='utf-8') as emails_data:
        #     list_emails = emails_data.readlines()

        # LOGGER.info(list_emails[0])
        # DRIVER = tu_dong_sweepwidget(DRIVER, list_emails[0])
        THOI_GIAN_XU_LY = datetime.now() - THOI_GIAN_HIEN_TAI
        LOGGER.info('Thời gian xử lý: %s', THOI_GIAN_XU_LY)
        if TESTING:
            input("Ấn Enter để thoát: ")
    except Exception as error:
        LOGGER.exception(error)
        if TESTING:
            input("Ấn Enter để thoát: ")
    finally:
        if DRIVER:
            DRIVER.quit()


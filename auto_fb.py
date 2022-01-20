# coding: utf-8
'''Tự động đăng nhập facebook
'''
import os
import pickle
import random
import logging

from datetime import datetime
from time import sleep
import requests

from getpass import getpass
import sentry_sdk
from webdriver_manager.firefox import GeckoDriverManager
from configparser import ConfigParser

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains


class CustomLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'cookies_name'):
            record.cookies_name = EXTRA.get('cookies_name')
        return True


EXTRA = dict(cookies_name=None)
TESTING = None
URL = 'https://www.facebook.com/'
NAME = 'auto_fb'


def thiet_lap_logging(name):
    sentry_sdk.init(
        'https://2e084979867c4e8c83f0b3b8062afc5b@o1086935.'
        'ingest.sentry.io/6111285',
        traces_sample_rate=1.0,
    )

    log_format = ' - '.join([
        '%(asctime)s',
        '%(name)s',
        '%(levelname)s',
        '%(cookies_name)s',
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
    logger.addFilter(CustomLogFilter())

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
    options.headless = headless
    service = Service(GeckoDriverManager().install())
    LOGGER.info('Chạy trình duyệt, headless=%s', headless)
    _driver = webdriver.Firefox(
        options=options,
        service=service,
    )
    # Hàm đặt thời gian tải trang, dùng khi tải trang quá lâu
    # _driver.set_page_load_timeout(5)
    return _driver


def dang_nhap_facebook(_driver, url):
    '''Hàm đăng nhập facebook
    '''
    print('Lấy thông tin tài khoản')
    _ten_dang_nhap = input('Nhập tên đăng nhập: ')
    _mat_khau = getpass(prompt='Nhập mật khẩu: ')

    # Mở trang
    _driver.get(url)

    _xpath_username = '//input[@id="email"]'
    _xpath_password = '//input[@id="pass"]'
    _xpath_login = '//button[@name="login"]'
    _username = _driver.find_element(by='xpath', value=_xpath_username)
    _username.send_keys(_ten_dang_nhap)
    _password = _driver.find_element(by='xpath', value=_xpath_password)
    _password.send_keys(_mat_khau)
    _button = _driver.find_element(by='xpath', value=_xpath_login)
    _button.click()
    return _driver


def dang_nhap_bang_cookies(_driver, _duong_dan_tep_cookie, url):
    '''Hàm đăng nhập facebook bằng cookies
    '''
    LOGGER.info('Đăng nhập %s bằng cookies', url)
    _driver.get(url)
    with open(_duong_dan_tep_cookie, 'rb') as _tep_cookie:
        for value in pickle.load(_tep_cookie):
            if 'expiry' in value:
                del value['expiry']
            _driver.add_cookie(value)

    # Tải lại trang để lấy cookies
    _driver.get(url)
    return _driver


def luu_cookies(_driver, _ten_tep_cookie=None):
    '''Hàm lưu cookies trình duyệt
    '''
    _thu_muc_goc = os.getcwd()
    if _ten_tep_cookie is None:
        # Nếu không chỉ định tên thì lấy tên người dùng để lưu
        _link_facebook_ca_nhan = 'https://www.facebook.com/me'
        _driver.get(_link_facebook_ca_nhan)
        _xpath_ten_nguoi_dung = '//h1[@class="gmql0nx0 l94mrbxd p1ri9a11 '\
            'lzcic4wl bp9cbjyn j83agx80"]'
        _ten_nguoi_dung = _driver.find_element(
            by='xpath',
            value=_xpath_ten_nguoi_dung).text
        _ten_nguoi_dung = _ten_nguoi_dung.split('\n')[0]
        _duong_dan_tep_cookie = os.path.join(
            _thu_muc_goc,
            _ten_nguoi_dung + '.bak',
        )
    else:
        # Nếu có tên thì lưu bằng tên được chỉ định
        _duong_dan_tep_cookie = os.path.join(_thu_muc_goc, _ten_tep_cookie)

    # Lưu cookies
    with open(_duong_dan_tep_cookie, 'wb') as tep_tin:
        pickle.dump(_driver.get_cookies(), tep_tin)
    return _duong_dan_tep_cookie


def auto_post(driver, content):
    content = '\n'.join([
        '[Chuyên mục nói đạo lý]',
        content.strip('\n'),
        'P/s: Đây là bài tự đăng nhá mọi người.',
    ])
    url = 'https://m.facebook.com'
    LOGGER.info('Tự động đăng bài %s', url)
    driver.get(url)
    LOGGER.info('Chọn nút đăng bài mới')
    post_area = tam_ngung_va_tim(
        driver,
        '//div[@class="_4g34 _6ber _78cq _7cdk _5i2i _52we"]')
    post_area.click()
    LOGGER.info('Nhập nội dung bài')
    input_post_area = tam_ngung_va_tim(
        driver,
        '//textarea[@id="uniqid_1"]')
    input_post_area.send_keys(content)
    LOGGER.info('Đăng bài')
    post_button = driver.find_elements(
        by='xpath',
        value='//button[@type="submit" and '
        '@data-sigil="touchable submit_composer"]')
    post_button[1].click()
    return driver


def auto_like(driver):
    LOGGER.info('Tự động thích bài viết')
    url = 'https://m.facebook.com/profile.php'
    driver.get(url)
    LOGGER.info('Lấy danh sách bài đăng')
    list_post = driver.find_elements(
        by='xpath',
        value='//article',
    )
    LOGGER.info('Chọn bài mới nhất')
    bai_moi_nhat = list_post[0]
    bai_moi_nhat.click()
    LOGGER.info('Ấn nút thích')
    nut_thich = tam_ngung_va_tim(
        driver=driver,
        _xpath='//a[@data-sigil="touchable ufi-inline-like '
        'like-reaction-flyout"]',
    )
    nut_thich.click()
    return driver


def auto_comment(driver, content):
    LOGGER.info('Tự động đăng bình luận')
    content = '\n'.join([
        '[Tự bình luận]',
        content.strip('\n'),
    ])
    url = 'https://m.facebook.com/profile.php'
    driver.get(url)
    LOGGER.info('Lấy danh sách bài đăng')
    list_post = driver.find_elements(
        by='xpath',
        value='//article',
    )
    LOGGER.info('Chọn bài mới nhất')
    bai_moi_nhat = list_post[0]
    bai_moi_nhat.click()
    LOGGER.info('Ấn nút bình luận')
    nut_binh_luan = tam_ngung_va_tim(
        driver,
        '//a[@data-sigil="feed-ufi-focus feed-ufi-trigger ufiCommentLink '
        'mufi-composer-focus"]')
    nut_binh_luan.click()
    LOGGER.info('Viết bình luận')
    viet_binh_luan = tam_ngung_va_tim(
        driver,
        '//textarea',
    )
    viet_binh_luan_act = ActionChains(driver).move_to_element(viet_binh_luan)
    viet_binh_luan_act.perform()
    viet_binh_luan.send_keys(content)
    sleep(3)
    LOGGER.info('Đăng bình luận')
    nut_dang = driver.find_element(
        by='xpath',
        value='//button[@data-sigil="touchable composer-submit"]',
    )
    sleep(3)
    nut_dang.click()
    sleep(3)
    return driver


def lay_noi_dung(tep_noi_dung):
    with open(tep_noi_dung, 'r', encoding='utf-8') as tep_tin:
        ds_noi_dung = tep_tin.readlines()
    id_noi_dung = random.randint(0, len(ds_noi_dung) - 1)
    return ds_noi_dung[id_noi_dung]


if __name__ == '__main__':
    LOGGER = thiet_lap_logging(NAME)
    LOGGER.info('Chạy chương trình')
    LOGGER.info('Load config')
    CONFIG = ConfigParser()
    CONFIG.read('tele.conf')
    BOT_TELE = CONFIG.get('BOT_TELE')
    CHAT_ID = CONFIG.get('CHAT_ID')
    LOGGER.info('Gửi thông báo qua telegram')
    url = f'https://api.telegram.org/bot{BOT_TELE}/sendMessage'
    params = {
        'chat_id': CHAT_ID,
        'text': 'Chạy auto facebook',
    }
    THOI_GIAN_HIEN_TAI = datetime.now()
    DRIVER = None

    try:
        # TESTING = True
        if TESTING:
            LOGGER.info('*' * 50)
            LOGGER.info('Chạy thử tự động facebook')
            LOGGER.info('*' * 50)
            HEADLESS = False
            COOKIES_PATH = 'Nguyen Huu Tuan Anh.bak'
        else:
            COOKIES_PATH = 'tuananh.bak'
            HEADLESS = True
        EXTRA['cookies_name'] = COOKIES_PATH

        DRIVER = chay_trinh_duyet(headless=HEADLESS)
        DRIVER.maximize_window()
        SIZE = DRIVER.get_window_size()
        DRIVER.set_window_size(SIZE['width'] / 2, SIZE['height'])
        DRIVER.set_window_position(
            (SIZE['width'] / 2) + SIZE['width'],
            0,
            windowHandle='current',
        )
        LOGGER.info('Tiến hành đăng nhập')
        DRIVER = dang_nhap_bang_cookies(DRIVER, COOKIES_PATH, URL)
        NOI_DUNG = lay_noi_dung('cham_ngon.txt')
        LOGGER.info('Lấy nội dung: %s', NOI_DUNG)
        if THOI_GIAN_HIEN_TAI.hour == 6:
            DRIVER = auto_post(DRIVER, NOI_DUNG)
        if THOI_GIAN_HIEN_TAI.hour == 14:
            DRIVER = auto_like(DRIVER)
            DRIVER = auto_comment(DRIVER, NOI_DUNG)
        if TESTING:
            DRIVER = auto_post(DRIVER, NOI_DUNG)
            DRIVER = auto_like(DRIVER)
            DRIVER = auto_comment(DRIVER, NOI_DUNG)
        # driver = dang_nhap(driver)
        # link_danh_sach_ban_be = 'https://www.facebook.com/me/friends'
        # print("Lưu cookies tài khoản")
        # duong_dan_tep_cookies = luu_cookies(driver)
        # if duong_dan_tep_cookies:
        #     print('Tệp cookies được lưu tại: %s' % (duong_dan_tep_cookies))
        THOI_GIAN_XU_LY = datetime.now() - THOI_GIAN_HIEN_TAI
        LOGGER.info('Thời gian xử lý: %s', THOI_GIAN_XU_LY)
        if TESTING:
            input("Ấn Enter để thoát: ")
    except Exception as error:
        LOGGER.exception(error)
    finally:
        if DRIVER:
            DRIVER.quit()

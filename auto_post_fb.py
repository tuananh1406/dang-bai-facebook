# coding: utf-8
'''Tự động đăng nhập facebook
'''
import os
import pickle
import random
import logging

from datetime import datetime
from time import sleep

from getpass import getpass
import sentry_sdk
from webdriver_manager.firefox import GeckoDriverManager

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
            record.cookies_name = None
        return True


EXTRA = dict(cookies_name=None)


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
    logger.info(f'Chạy trình duyệt, headless={headless}', extra=EXTRA)
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
    logger.info(f'Đăng nhập {url} bằng cookies', extra=EXTRA)
    _driver.get(url)
    for value in pickle.load(open(_duong_dan_tep_cookie, 'rb')):
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
        driver.get(_link_facebook_ca_nhan)
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
    logger.info(f'Tự động đăng bài {url}', extra=EXTRA)
    driver.get(url)
    logger.info('Chọn nút đăng bài mới', extra=EXTRA)
    post_area = tam_ngung_va_tim(
        driver,
        '//div[@class="_4g34 _6ber _78cq _7cdk _5i2i _52we"]')
    post_area.click()
    logger.info('Nhập nội dung bài', extra=EXTRA)
    input_post_area = tam_ngung_va_tim(
        driver,
        '//textarea[@id="uniqid_1"]')
    input_post_area.send_keys(content)
    logger.info('Đăng bài', extra=EXTRA)
    post_button = driver.find_elements(
        by='xpath',
        value='//button[@type="submit" and '
        '@data-sigil="touchable submit_composer"]')
    post_button[1].click()
    return driver


def auto_comment(driver, content):
    logger.info('Tự động đăng bình luận', extra=EXTRA)
    content = '\n'.join([
        '[Tự bình luận]',
        content.strip('\n'),
    ])
    url = 'https://m.facebook.com/profile.php'
    driver.get(url)
    logger.info('Lấy danh sách bài đăng', extra=EXTRA)
    list_post = driver.find_elements(
        by='xpath',
        value='//article',
    )
    logger.info('Chọn bài mới nhất', extra=EXTRA)
    bai_moi_nhat = list_post[0]
    bai_moi_nhat.click()
    logger.info('Ấn nút bình luận', extra=EXTRA)
    nut_binh_luan = tam_ngung_va_tim(
        driver,
        '//a[@data-sigil="feed-ufi-focus feed-ufi-trigger ufiCommentLink '
        'mufi-composer-focus"]')
    nut_binh_luan.click()
    logger.info('Viết bình luận', extra=EXTRA)
    viet_binh_luan = tam_ngung_va_tim(
        driver,
        '//textarea',
    )
    viet_binh_luan_act = ActionChains(driver).move_to_element(viet_binh_luan)
    viet_binh_luan_act.perform()
    viet_binh_luan.send_keys(content)
    sleep(3)
    logger.info('Đăng bình luận', extra=EXTRA)
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
    url = 'https://www.facebook.com/'
    name = 'auto_post_fb.py'
    logger = thiet_lap_logging(name)
    logger.info('Chạy chương trình', extra=EXTRA)
    thoi_gian_hien_tai = datetime.now()
    driver = None

    try:
        # headless = False
        headless = True
        driver = chay_trinh_duyet(headless=headless)
        logger.info('Tiến hành đăng nhập', extra=EXTRA)
        cookies_path = 'tuananh.bak'
        # cookies_path = 'Nguyen Huu Tuan Anh.bak'
        driver = dang_nhap_bang_cookies(driver, cookies_path, url)
        EXTRA['cookies_name'] = cookies_path
        noi_dung = lay_noi_dung('cham_ngon.txt')
        logger.info(f'Lấy nội dung: {noi_dung}', extra=EXTRA)
        if thoi_gian_hien_tai.hour == 6:
            driver = auto_post(driver, noi_dung)
        if thoi_gian_hien_tai.hour == 14:
            driver = auto_comment(driver, noi_dung)
        # driver = dang_nhap(driver)
        # link_danh_sach_ban_be = 'https://www.facebook.com/me/friends'
        # print("Lưu cookies tài khoản")
        # duong_dan_tep_cookies = luu_cookies(driver)
        # if duong_dan_tep_cookies:
        #     print('Tệp cookies được lưu tại: %s' % (duong_dan_tep_cookies))
        thoi_gian_xu_ly = datetime.now() - thoi_gian_hien_tai
        logger.info(f'Thời gian xử lý: {thoi_gian_xu_ly}', extra=EXTRA)
    except Exception as error:
        logger.error(error)
    finally:
        if driver:
            driver.quit()

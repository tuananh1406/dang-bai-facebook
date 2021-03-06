# coding: utf-8
'''Tự động đăng nhập facebook
'''
import os
import time
import pickle

from getpass import getpass
from webdriver_manager.firefox import GeckoDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def tam_ngung_den_khi(_xpath):
    '''Hàm tạm ngưng đến khi xuất hiện đường dẫn xpath
    '''
    print('[INFO] Đang chờ trang web phản hồi...')
    _tam_ngung = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            _xpath,
        )),
    )
    return _tam_ngung


def tam_ngung_va_tim(_xpath):
    '''Hàm tạm ngưng đến khi xuất hiện đường dẫn xpath và chọn xpath đó
    '''
    tam_ngung_den_khi(_xpath)
    return driver.find_element_by_xpath(_xpath)


def chay_trinh_duyet():
    '''Mở trình duyệt và trả về driver
    '''
    _driver = webdriver.Firefox(
        # executable_path=_exec_driver_path,
        executable_path=GeckoDriverManager().install(),
    )
    # Hàm đặt thời gian tải trang, dùng khi tải trang quá lâu
    # _driver.set_page_load_timeout(5)
    return _driver


def dang_nhap(_driver):
    '''Hàm đăng nhập facebook
    '''
    print('Lấy thông tin tài khoản')
    _ten_dang_nhap = input('Nhập tên đăng nhập: ')
    _mat_khau = getpass(prompt='Nhập mật khẩu: ')
    # Mở trang facebook
    _driver.get(DUONG_DAN)

    _xpath_username = '//input[@id="email"]'
    _xpath_password = '//input[@id="pass"]'
    _xpath_login = '//button[@name="login"]'
    _username = _driver.find_element_by_xpath(_xpath_username)
    _username.send_keys(_ten_dang_nhap)
    _password = _driver.find_element_by_xpath(_xpath_password)
    _password.send_keys(_mat_khau)
    _button = _driver.find_element_by_xpath(_xpath_login)
    _button.click()
    return _driver


def dang_nhap_bang_cookies(_driver, _duong_dan_tep_cookie):
    '''Hàm đăng nhập facebook bằng cookies
    '''
    _driver.get(DUONG_DAN)
    for value in pickle.load(open(_duong_dan_tep_cookie, 'rb')):
        if 'expiry' in value:
            del value['expiry']
        _driver.add_cookie(value)

    # Tải lại trang để lấy cookies
    _driver.get(DUONG_DAN)
    return _driver


def luu_cookies(_driver, _ten_tep_cookie=None):
    '''Hàm lưu cookies trình duyệt
    '''
    _thu_muc_goc = os.getcwd()
    if _ten_tep_cookie is None:
        # Nếu không chỉ định tên thì lấy tên người dùng để lưu
        _link_facebook_ca_nhan = 'https://www.facebook.com/me'
        driver.get(_link_facebook_ca_nhan)
        _xpath_ten_nguoi_dung = '//h1[@class="gmql0nx0 l94mrbxd p1ri9a11 lzcic4wl bp9cbjyn j83agx80"]'
        _ten_nguoi_dung = _driver.find_element_by_xpath(_xpath_ten_nguoi_dung).text
        _ten_nguoi_dung = _ten_nguoi_dung.split('\n')[0]
        _duong_dan_tep_cookie = os.path.join(_thu_muc_goc, _ten_nguoi_dung)
    else:
        # Nếu có tên thì lưu bằng tên được chỉ định
        _duong_dan_tep_cookie = os.path.join(_thu_muc_goc, _ten_tep_cookie)

    # Lưu cookies
    with open(_duong_dan_tep_cookie, 'wb') as tep_tin:
        pickle.dump(_driver.get_cookies(), tep_tin)
    return _duong_dan_tep_cookie


if __name__ == '__main__':
    DUONG_DAN = 'https://www.facebook.com/'
    print('Chạy chương trình')
    thoi_gian_hien_tai = time.time()
    driver = chay_trinh_duyet()
    print('Tiến hành đăng nhập')
    # driver = dang_nhap_bang_cookies(driver, 'Nguyen Huu Tuan Anh')
    driver = dang_nhap(driver)
    link_danh_sach_ban_be = 'https://www.facebook.com/me/friends'
    print("Lưu cookies tài khoản")
    duong_dan_tep_cookies = luu_cookies(driver, 'tuananh')
    if duong_dan_tep_cookies:
        print('Tệp cookies được lưu tại: %s' % (duong_dan_tep_cookies))
    thoi_gian_xu_ly = time.time() - thoi_gian_hien_tai
    print('Thời gian xử lý:', thoi_gian_xu_ly)
    input('Nhập enter')
    driver.quit()

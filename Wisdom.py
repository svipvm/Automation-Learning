from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os, time, re

lessonKind = {
    '共享课': 'sharingClassed',
    '翻转课': 'flipLessoned'
}

driver = webdriver.Firefox()

def Waiting(aim, elem, outTime = 10):
    WebDriverWait(aim, outTime, 0.5).until(EC.presence_of_element_located(elem))


def loginZHS():
    driver.get('https://passport.zhihuishu.com/login')
    text_username = driver.find_element_by_id('lUsername')
    text_password = driver.find_element_by_id('lPassword')
    text_username.send_keys(os.environ['USERNAME'])
    text_password.send_keys(os.environ['PASSWORD'])
    driver.find_element_by_class_name('wall-sub-btn').click()
    Waiting(driver, (By.CLASS_NAME, 'loggedIn'))
    driver.get('https://onlineh5.zhihuishu.com/onlineWeb.html#/studentIndex')
    time.sleep(3)


def getLesson():
    lessonList = []
    for lesson, kind in lessonKind.items():
        try:
            Waiting(driver, (By.ID, kind), 3)
            sharingClass = driver.find_element_by_id(kind)
            Waiting(sharingClass, (By.CLASS_NAME, 'datalist'))
            sharingList = sharingClass.find_elements_by_class_name('datalist')
            for sharing in sharingList:
                Waiting(sharing, (By.CLASS_NAME, 'courseName'))
                course = sharing.find_element_by_class_name('courseName').get_attribute('textContent')
                Waiting(sharing, (By.CLASS_NAME, 'processNum'))
                process = sharing.find_element_by_class_name('processNum').get_attribute('textContent')
                Waiting(sharing, (By.CLASS_NAME, 'hoverList'))
                div = sharing.find_element_by_class_name('hoverList')
                result = {
                    'kind': lesson,
                    'course': course,
                    'process': process,
                    'div': div
                }
                lessonList.append(result)
        except:
            pass
    return lessonList


def solveCourse(div):
    div.click()
    try:
        Waiting(driver, (By.CLASS_NAME))
        button = driver.find_elements_by_class_name('el-button--primary')
        print(button)
    except:
        pass


if __name__ == '__main__':
    loginZHS()
    lessonList = getLesson()
    # for lesson in lessonList:
    #     print(lesson)
    for x in range(0, len(lessonList)):
        lesson = lessonList[x]
        print(x + 1, '：', lesson['kind'], lesson['process'], lesson['course'])
    index = int(input('请输入编号：')) - 1
    solveCourse(lessonList[index]['div'])

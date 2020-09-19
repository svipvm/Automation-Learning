from selenium import webdriver
import re, os, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

base_url = 'https://jjzyjsxy.zjy2.icve.com.cn'
driver = webdriver.Firefox()

def Waiting(aim, elem, outTime = 10):
    WebDriverWait(aim, outTime, 0.5).until(EC.presence_of_element_located(elem))

def loginICVE():
    text_username = driver.find_element_by_name('userName')
    text_password = driver.find_element_by_name('userPassword')
    text_verifyCode = driver.find_element_by_name('photoCode')
    text_verifyCode.send_keys(input('请输入验证码：'))
    text_username.send_keys(os.environ['ICVEUSER'])
    text_password.send_keys(os.environ['ICVEPASS'])
    driver.find_element_by_id('btnLogin').click()

def getLearningList():
    Waiting(driver, (By.CLASS_NAME, 'kt-lesson-li'))
    lesson_list = driver.find_elements_by_class_name('kt-lesson-li')
    result_list = []
    for lesson in lesson_list:
        infor = {}
        html = lesson.get_attribute('innerHTML')
        try:
            href = re.search(r'href="(.*?)"', html).group(1)
            title = re.search(r'title="(.*?)"', html).group(1)
            complete = re.search(r'20px">(.*?)</span>', html).group(1)
            infor['title'] = title
            infor['href'] = href
            infor['complete'] = complete
            result_list.append(infor)
        except:
            pass

    return result_list

def getCourse(href):
    print('正在获取节点资源……')
    # 进入课程页面
    url = (base_url + href).replace('amp;', '').replace('jjzyjsxy.', '')
    driver.get(url)
    # 获取所有课的信息
    Waiting(driver, (By.CLASS_NAME, 'moduleList'))
    moduleList = driver.find_elements_by_class_name('moduleList')
    for module in moduleList:
        try:
            Waiting(module, (By.CLASS_NAME, 'openOrCloseModule'))
            openOrClose = module.find_element_by_class_name('openOrCloseModule')
            Waiting(module, (By.CLASS_NAME, 'topic_container'))
            content = module.find_element_by_class_name('topic_container')
            if content.get_attribute('innerHTML') == '':
                openOrClose.click()
            Waiting(module, (By.TAG_NAME, 'a'))
            expandList = module.find_elements_by_tag_name('a')
            for expand in expandList:
                expand.click()
                try:
                    module.find_element_by_class_name('sgBtn').click()
                except:
                    continue
        except:
            pass
            # time.sleep(0.5)

    # 在获取的课中选出未解决的课
    print('正在获取未完成节点资源……')
    pendingList = []
    spanList = driver.find_elements_by_class_name('sh-res-b')
    hrefList = driver.find_elements_by_class_name('isOpenModulePower')
    for x in range(0, len(spanList)):
        title = hrefList[x].get_attribute('title')
        content = spanList[x].get_attribute('innerHTML')
        color = re.search(r'color:(.*?)"', content)
        kind = spanList[x].find_element_by_xpath('./span').get_attribute('textContent')
        try:
            if color.group(1).replace(';', '') == '#fff':
                continue
            result = {
                'title' : title,
                'kind' : ''.join(kind.split()),
                'href' : hrefList[x].get_attribute('data-href')
            }
            pendingList.append(result)
        except:
            pass

    print('已获取所有节点资源，共有', len(pendingList), '个节点待学习！\n')
    return pendingList

# {'title': '2.1.1.mp4', 'kind': '视频', 'href': '/common/directory/directory.html?courseOpenId=qtvaxgpoydgidrf2vrla&openClassId=9ihoav2rzqto0bcacs8hw&cellId=zjd1ayip1k9lplu9ydg2a&flag=s'}
def solveCourse(pendingList):
    for x in range(0, len(pendingList)):
        print('正在学习', (x + 1), '/', len(pendingList), '：')
        print('\t\t', pendingList[x]['kind'], pendingList[x]['title'], '学习中')
        url = base_url + pendingList[x]['href']
        try:
            driver.get(url.replace('jjzyjsxy.', ''))
            try:
                Waiting(driver, (By.ID, 'studyNow'), 3)
                driver.find_element_by_id('studyNow').click()
            except:
                pass
            if pendingList[x]['kind'] == '文档' or pendingList[x]['kind'] == '文本':
                Waiting(driver, (By.CLASS_NAME, 'MPreview-pageCount'))
                span = driver.find_element_by_class_name('MPreview-pageCount')
                count = int(span.find_element_by_xpath('./em').get_attribute('textContent'))
                Waiting(driver, (By.CLASS_NAME, 'MPreview-pageNext'))
                nextPage = driver.find_element_by_class_name('MPreview-pageNext')
                for i in range(count):
                    nextPage.click()
                    time.sleep(0.3)
                time.sleep(30)
            elif pendingList[x]['kind'] == 'ppt': #MPreview-arrowBottom stage-next-btn
                time.sleep(2)
                try:
                    Waiting(driver, (By.CLASS_NAME, 'MPreview-arrowBottom'), outTime=3)
                    goal = 'MPreview-arrowBottom'
                except:
                    goal = 'stage-next-btn'
                for x in range(0, 200):
                    try:
                        driver.find_element_by_class_name(goal).click()
                    except:
                        break
                    time.sleep(0.1)
                time.sleep(1)
            elif pendingList[x]['kind'] == '图文' or pendingList[x]['kind'] == '压缩包':
                time.sleep(30)
            elif pendingList[x]['kind'] == '视频':
                try:
                    Waiting(driver, (By.CLASS_NAME, 'jw-icon-hd'))
                    driver.find_element_by_class_name('jw-icon-hd').click()
                    for x in range(3, -1, -1):
                        try:
                            driver.find_element_by_class_name('jw-item-' + str(x)).click()
                            break
                        except:
                            pass
                except:
                    Waiting(driver, (By.CLASS_NAME, 'jw-slider-horizontal'))
                    driver.find_element_by_class_name('jw-slider-horizontal').click()
                    driver.find_element_by_class_name('jw-icon-playback').click()
                Waiting(driver, (By.CLASS_NAME, 'jw-text-duration'))
                endTime = '00:00'
                while endTime == '00:00':
                    endTime = driver.find_element_by_class_name('jw-text-duration').get_attribute('textContent')
                    time.sleep(0.5)
                Waiting(driver, (By.CLASS_NAME, 'jw-text-elapsed'))
                nowTime = '--:--'
                while nowTime != endTime:
                    nowTime = driver.find_element_by_class_name('jw-text-elapsed').get_attribute('textContent')
                    time.sleep(0.9)
                # pass
            elif pendingList[x]['kind'] == '图片':
                time.sleep(30)
            else:
                print(pendingList[x])
        except: continue

        print('\t', '已学习')

if __name__ == '__main__':
    driver.get('https://zjy2.icve.com.cn/portal/login.html')
    loginICVE()
    course_list = getLearningList()
    while True:
        print('\n----------------------------------------------')
        for x in range(0, len(course_list)):
            course = course_list[x]
            print(str(x + 1) + "：" + course['title'] + " " + course['complete'])
        try:
            index = int(input("请输入要操作课程的编号："))
            print('----------------------------------------------\n')
            if index < 1 or len(course_list) < index: break
            pendingList = getCourse(course_list[index - 1]['href'])
            solveCourse(pendingList)
        except:
            break
    print("欢迎下次使用！")

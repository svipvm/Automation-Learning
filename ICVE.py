import requests, time, os, json, random, datetime

verify_url = 'https://zjy2.icve.com.cn/api/common/VerifyCode/index?t='
login_url = 'https://zjy2.icve.com.cn/api/common/login/login'
inform_url = 'https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList'
get_topic_url = 'https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId'
get_cell_url = 'https://zjy2.icve.com.cn/api/study/process/getCellByTopicId'
view_url = 'https://zjy2.icve.com.cn/api/common/Directory/viewDirectory'
status_url = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

class ICVE:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit'
    }

    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit'
        }
        self.username = None
        self.password = None
        self.sesson = None
        self.courseOpenId = None
        self.openClassId = None
        self.moduleId = None
        self.topicId = None
        self.cellId = None

    def run(self, username, password):
        self.username = username
        self.password = password
        self.sesson = requests.session()
        self.save_verify_code(round(time.time() * 1000))
        self.login_mooc()
        lesson_list = self.get_lesson()
        self.select_lesson(lesson_list)

    def save_verify_code(self, value):
        r = self.sesson.get(verify_url.format(value), headers=self.headers)
        with open('verify.jpg', 'wb') as file:
            file.write(r.content)

    def login_mooc(self):
        data = {
            'userName': self.username,
            'userPwd': self.password,
            'verifyCode': input("input verify code: ")
        }
        self.sesson.post(login_url, headers=self.headers, data=data)

    def get_lesson(self):
        r = self.sesson.get(inform_url, headers=self.headers)
        data = json.loads(r.content.decode("utf-8"))
        return data['courseList']

    def select_lesson(self, lesson_list):
        while True:
            self.print_menu(lesson_list)
            index = int(input('请输出课程序号（-1退出）：'))
            if index <= 0 or len(lesson_list) < index: break
            print('\n-------------------------------')
            self.courseOpenId = lesson_list[index - 1]['courseOpenId']
            self.openClassId = lesson_list[index - 1]['openClassId']
            print('开始学习', lesson_list[index - 1]['courseName'])
            proces_list = self.get_proces_list()
            self.solve_lesson(proces_list)
            print('开始完成', lesson_list[index - 1]['courseName'])
            print('-------------------------------\n')

    def print_menu(self, lesson_list):
        print('-------------------------------')
        for index in range(len(lesson_list)):
            lesson = lesson_list[index]
            print(index + 1, ':', lesson['courseName'], str(lesson['totalScore']) + '分', str(lesson['process']) + '%')
        print('-------------------------------')

    def get_proces_list(self):
        url = 'https://zjy2.icve.com.cn/api/study/process/getProcessList'
        data = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId
        }
        r = self.sesson.post(url, headers=self.headers, data=data)
        data = json.loads(r.content.decode('utf-8'))
        proces_list = []
        for module in data['progress']['moduleList']:
            proces_list.append({'id': module['id'], 'name': module['name']})
        return proces_list

    def solve_lesson(self, proces_list):
        data1 = {
            'courseOpenId': self.courseOpenId
        }
        data2 = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId
        }
        for i in range(len(proces_list)):
            data1['moduleId'] = proces_list[i]['id']
            self.moduleId = data1['moduleId']
            r = self.sesson.post(get_topic_url, headers=self.headers, data=data1)
            conetent = json.loads(r.content.decode('utf-8'))
            topic_list = conetent['topicList']
            print(proces_list[i]['name'])
            for topic in topic_list:
                data2['topicId'] = topic['id']
                self.topicId = data2['topicId']
                r = self.sesson.post(get_cell_url, headers=self.headers, data=data2)
                content = json.loads(r.content.decode('utf-8'))
                cell_list = content['cellList']
                for cell in cell_list:
                    self.cellId = cell['Id']
                    print('\t', cell['categoryNameDb'], cell['cellName'])
                    if cell['categoryName'] == '子节点':
                        for node in cell['childNodeList']:
                            self.solve_node(node)
                    else:
                        self.solve_node(cell)

    def solve_node(self, node):
        stuCellCount = node['stuCellCount']
        if stuCellCount == False:
            print('\t× 未完成', node['cellName'])
            self.cellId = node['Id']
            # self.viewDirectory()
        print('\t√ 已完成', node['cellName'])

    def viewDirectory(self):
        data = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId,
            'moduleId': self.moduleId,
            'cellId': self.cellId
        }
        r = self.sesson.post(view_url, headers=self.headers, data=data)
        content = json.loads(r.text)
        CategoryName = content['courseCell']['CategoryName']
        VideoTimeLong = content['courseCell']['VideoTimeLong']
        if CategoryName == '测验' or CategoryName == '作业':
            time.sleep(3)
            return
        if 3600 < VideoTimeLong:
            time.sleep(3)
            return
        data['videoTimeTotalLong'] = VideoTimeLong
        if VideoTimeLong < 10:
            VideoTimeLong = random.randrange(10, 30)
        start_time = datetime.datetime.now()
        end_time = (start_time + datetime.timedelta(seconds=VideoTimeLong)).strftime("%H:%M:%S")
        start_time = start_time.strftime('%H:%M:%S')
        # 图片, 视频, 其它, 文档, ppt, 压缩包, 测验
        print('\t\t类型：' + CategoryName + '，' + start_time, '开始学习，预计', end_time, '结束')
        time.sleep(VideoTimeLong)
        if CategoryName == '视频':
            data['auvideoLength'] = data['videoTimeTotalLong']
            data['sourceForm'] = 1229
        else:
            data['sourceForm'] = 1030
        r = self.sesson.post(status_url, headers=self.headers, data=data)
        if json.loads(r.text)['isStudy']:
            print('\t\t\t√ 学习完成 √')
        else:
            print('\t\t\t× 学习失败 ×')


if __name__ == '__main__':
    icve = ICVE()
    icve.run('201820800124', 'Shadow24')
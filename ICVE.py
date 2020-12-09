import requests, time, os, json, random, datetime

class ICVE:
    def __init__(self):
        self.headers = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit' }
        self.kind_list = ['视频', '压缩包', '文档', '简单文本', 'ppt']
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
        url = 'https://zjy2.icve.com.cn/api/common/VerifyCode/index?t='
        r = self.sesson.get(url.format(value), headers=self.headers)
        with open('verify.jpg', 'wb') as file:
            file.write(r.content)

    def login_mooc(self):
        url = 'https://zjy2.icve.com.cn/api/common/login/login'
        data = {
            'userName': self.username,
            'userPwd': self.password,
            'verifyCode': input("input verify code: ")
        }
        self.sesson.post(url, headers=self.headers, data=data)

    def get_lesson(self):
        url = 'https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList'
        r = self.sesson.get(url, headers=self.headers)
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
            print(index + 1, ':', lesson['courseName'],
                  str(lesson['totalScore']) + '分', str(lesson['process']) + '%')
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
        get_topic_url = 'https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId'
        get_cell_url = 'https://zjy2.icve.com.cn/api/study/process/getCellByTopicId'
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
            flag = self.viewDirectory(node['categoryName'], node['cellName'])
            if flag:
                print('\t√ 已完成', node['cellName'])
            else:
                time.sleep(2)
                print('\t× 学习失败', node['cellName'])
        else:
            print('\t√ 已完成', node['cellName'])

    def view(self, _kind, _logId, _time, _num, _token):
        url = 'https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog'
        data = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId,
            'cellId': self.cellId,
            'picNum': _num,
            'studyNewlyTime': _time,
            'studyNewlyPicNum': _num,
            'token': _token
        }
        if _time < 10:
            _time = random.randrange(10, 20)
        start_time = datetime.datetime.now()
        end_time = (start_time + datetime.timedelta(seconds=int(_time))).strftime("%H:%M:%S")
        start_time = start_time.strftime('%H:%M:%S')
        # 图片, 视频, 其它, 文档, ppt, 压缩包, 测验
        print('\t\t类型：' + _kind + '，' + start_time, '开始学习，预计', end_time, '结束')
        time.sleep(_time)
        r = self.sesson.post(url, headers=self.headers, data=data)
        return json.loads(r.text)['code'] == 1

    def changeProcess(self, cellName):
        url = 'https://zjy2.icve.com.cn/api/common/Directory/changeStuStudyProcessCellData'
        data = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId,
            'moduleId': self.moduleId,
            'cellId': self.cellId,
            'cellName': cellName
        }
        self.sesson.post(url, headers=self.headers, data=data)


    def viewDirectory(self, kind, cellName):
        url = 'https://zjy2.icve.com.cn/api/common/Directory/viewDirectory'
        data = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId,
            'moduleId': self.moduleId,
            'cellId': self.cellId,
            'flag': 's'
        }
        r = self.sesson.post(url, headers=self.headers, data=data)
        content = json.loads(r.text)
        if content['code'] == -100:
            self.changeProcess(cellName)
            r = self.sesson.post(url, headers=self.headers, data=data)
            content = json.loads(r.text)
        try:
            print(content['downLoadUrl'])
            _logID = content['cellLogId']
            _time = content['audioVideoLong']
            _num = content['pageCount']
            _token = content['guIdToken']
            if kind in self.kind_list:
                return self.view(kind, _logID, _time, _num, _token)
            else:
                return False
        except:
            return False


if __name__ == '__main__':
    icve = ICVE()
    icve.run('201820800124', 'Shadow24')
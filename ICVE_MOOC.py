import requests, time, os, json, random, datetime

class ICVE:
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit'
        }
        self.username = None
        self.password = None
        self.sesson = None
        self.courseOpenId = None
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
        verify_url = 'https://mooc.icve.com.cn/portal/LoginMooc/getVerifyCode?ts='
        r = self.sesson.get(verify_url.format(value), headers=self.headers)
        with open('verify.jpg', 'wb') as file:
            file.write(r.content)

    def login_mooc(self):
        login_url = 'https://mooc.icve.com.cn/portal/LoginMooc/loginSystem'
        data = {
            'userName': self.username,
            'password': self.password,
            'verifycode': input("input verify code: ")
        }
        self.sesson.post(login_url, headers=self.headers, data=data)

    def get_lesson(self):
        inform_url = 'https://mooc.icve.com.cn/portal/course/getCourseOpenList'
        r = self.sesson.get(inform_url, headers=self.headers)
        data = json.loads(r.content.decode("utf-8"))
        return data['list']

    def select_lesson(self, lesson_list):
        while True:
            self.print_menu(lesson_list)
            index = int(input('请输出课程序号（-1退出）：'))
            if index <= 0 or len(lesson_list) < index: break
            print('\n-------------------------------')
            self.courseOpenId = lesson_list[index - 1]['id']
            print('开始学习', lesson_list[index - 1]['text'])
            proces_list = self.get_proces_list()
            self.solve_lesson(proces_list)
            print('开始完成', lesson_list[index - 1]['text'])
            print('-------------------------------\n')

    def print_menu(self, lesson_list):
        print('-------------------------------')
        for index in range(len(lesson_list)):
            print(index + 1, ':', lesson_list[index]['text'])
        print('-------------------------------')

    def get_proces_list(self):
        url = 'https://mooc.icve.com.cn/study/learn/getProcessList'
        data = { 'courseOpenId': self.courseOpenId }
        r = self.sesson.post(url, headers=self.headers, data=data)
        data = json.loads(r.content.decode('utf-8'))
        proces_list = []
        for module in data['proces']['moduleList']:
            proces_list.append({'id': module['id'], 'name': module['name']})
        return proces_list

    def solve_lesson(self, proces_list):
        get_topic_url = 'https://mooc.icve.com.cn/study/learn/getTopicByModuleId'
        get_cell_url = 'https://mooc.icve.com.cn/study/learn/getCellByTopicId'
        data1 = {'courseOpenId': self.courseOpenId}
        data2 = {'courseOpenId': self.courseOpenId}
        for i in range(len(proces_list)):
            data1['moduleId'] = proces_list[i]['id']
            self.moduleId = data1['moduleId']
            r = self.sesson.post(get_topic_url, headers=self.headers, data=data1)
            conetent = json.loads(r.content.decode('utf-8'))
            topic_list = conetent['topicList']
            print(proces_list[i]['name'])
            for topic in topic_list:
                self.topicId = data2['topicId'] = topic['id']
                r = self.sesson.post(get_cell_url, headers=self.headers, data=data2)
                content = json.loads(r.content.decode('utf-8'))
                cell_list = content['cellList']
                for cell in cell_list:
                    if cell['categoryName'] == '子节点':
                        for node in cell['childNodeList']:
                            self.solve_node(node)
                    else:
                        self.solve_node(cell)

    def solve_node(self, node):
        isStudyFinish = node['isStudyFinish']
        if isStudyFinish == False:
            print('\t× 未完成', node['cellName'])
            self.cellId = node['Id']
            self.viewDirectory()
        print('\t√ 已完成', node['cellName'])

    def viewDirectory(self):
        view_url = 'https://mooc.icve.com.cn/study/learn/viewDirectory'
        status_url = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'
        data = {
            'courseOpenId': self.courseOpenId,
            'moduleId': self.moduleId,
            'cellId': self.cellId,
            'fromType': 'stu'
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
    icve.run(os.environ['ICVEUSER'], os.environ['ICVEPASS'])
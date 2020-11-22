import requests, time, os, json, random, datetime

verify_url = 'https://mooc.icve.com.cn/portal/LoginMooc/getVerifyCode?ts='
login_url = 'https://mooc.icve.com.cn/portal/LoginMooc/loginSystem'
inform_url = 'https://mooc.icve.com.cn/portal/course/getCourseOpenList'
get_topic_url = 'https://mooc.icve.com.cn/study/learn/getTopicByModuleId'
get_cell_url = 'https://mooc.icve.com.cn/study/learn/getCellByTopicId'
view_url = 'https://mooc.icve.com.cn/study/learn/viewDirectory'
status_url = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit'
}

sesson = requests.session()

def save_verify_code(value):
    r = sesson.get(verify_url.format(value), headers=headers)
    with open('verify.GIF', 'wb') as file:
        file.write(r.content)

def login_mooc():
    data = {
        'userName': os.environ['ICVEUSER'],
        'password': os.environ['ICVEPASS'],
        'verifycode': input("input verify code: ")
    }
    sesson.post(login_url, headers=headers, data=data)

def get_lesson():
    r = sesson.get(inform_url, headers=headers)
    data = json.loads(r.content.decode("utf-8"))
    return data['list']

def get_proces_list(value):
    url = 'https://mooc.icve.com.cn/study/learn/getProcessList'
    data = { 'courseOpenId': value }
    r = sesson.post(url, headers=headers, data=data)
    data = json.loads(r.content.decode('utf-8'))
    proces_list = []
    for module in data['proces']['moduleList']:
        proces_list.append({'id': module['id'], 'name': module['name']})
    return proces_list

def print_menu(lesson_list):
    print('-------------------------------')
    for index in range(len(lesson_list)):
        print(index + 1, ':', lesson_list[index]['text'])
    print('-------------------------------')

def viewDirectory(courseOpenId, moduleId, cellId):
    data = {
        'courseOpenId': courseOpenId,
        'moduleId': moduleId,
        'cellId': cellId,
        'fromType': 'stu'
    }
    r = sesson.post(view_url, headers=headers, data=data)
    content = json.loads(r.text)
    CategoryName = content['courseCell']['CategoryName']
    VideoTimeLong = content['courseCell']['VideoTimeLong']
    if CategoryName == '测验' or CategoryName == '作业':
        time.sleep(random.randrange(10, 30))
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
    r = sesson.post(status_url, headers=headers, data=data)
    if json.loads(r.text)['isStudy']:
        print('\t\t\t√ 学习完成 √')
    else:
        print('\t\t\t× 学习失败 ×')

def solve_node(courseOpenId, moduleID, node):
    isStudyFinish = node['isStudyFinish']
    if isStudyFinish == False:
        print('\t× 未完成', node['cellName'])
        viewDirectory(courseOpenId, moduleID, node['Id'])
    print('\t√ 已完成', node['cellName'])

def solve_lesson(courseOpenId, proces_list):
    data1 = {'courseOpenId': courseOpenId}
    data2 = {'courseOpenId': courseOpenId}
    for i in range(len(proces_list)):
        data1['moduleId'] = proces_list[i]['id']
        r = sesson.post(get_topic_url, headers=headers, data=data1)
        conetent = json.loads(r.content.decode('utf-8'))
        topic_list = conetent['topicList']
        moduleID = conetent['moduleId']
        print(proces_list[i]['name'])
        for topic in topic_list:
            data2['topicId'] = topic['id']
            r = sesson.post(get_cell_url, headers=headers, data=data2)
            content = json.loads(r.content.decode('utf-8'))
            cell_list = content['cellList']
            for cell in cell_list:
                if cell['categoryName'] == '子节点':
                    for node in cell['childNodeList']:
                        solve_node(courseOpenId, moduleID, node)
                else:
                    solve_node(courseOpenId, moduleID, cell)

def select_lesson(lesson_list):
    while True:
        print_menu(lesson_list)
        index = int(input('请输出课程序号（-1退出）：'))
        if index <= 0 or len(lesson_list) < index: break
        print('\n-------------------------------')
        print('开始学习', lesson_list[index - 1]['text'])
        proces_list = get_proces_list(lesson_list[index - 1]['id'])
        solve_lesson(lesson_list[index - 1]['id'], proces_list)
        print('开始完成', lesson_list[index - 1]['text'])
        print('-------------------------------\n')

if __name__ == '__main__':
    save_verify_code(round(time.time() * 1000))
    login_mooc()
    lesson_list = get_lesson()
    select_lesson(lesson_list)

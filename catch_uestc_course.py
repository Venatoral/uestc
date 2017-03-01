import requests
import threading
import uestc_login
import optparse
import time
import getpass

def get_mid_text(text, left_text, right_text, start = 0):
    left = text.find(left_text, start)
    if left == -1:
        return None
    left += len(left_text)
    right = text.find(right_text, left)
    if right == -1:
        return None
    return (text[left:right], left)
def get_open_url_data(data):
    url = 'http://eams.uestc.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id='
    while data[0] < 1000:
        data[1].acquire()
        num = data[0]
        data[0] += 1
        data[1].release()
        r = data[2].get(url + str(num))
        if '学号' in r.text:
            data[1].acquire()
            data.append(num)
            data[1].release()

def get_open_url(u, threading_max = 50):
    data = [0,threading.Lock(),u]
    threads = []
    while data[0] < 1000:
        if len(threads) <= min(threading_max, 1000 - data[0]):
            threads.append(threading.Thread(target=get_open_url_data, args = (data, )))
            threads[len(threads) - 1].start()
    for i in threads:
        i.join()
    ret = data[3:]
    ret.sort()
    return ret

def catch_course(u, port, id, choose = True, sleep = 0):
    count = 0
    while True:
        postdata = {'operator0': '%s:%s:0' % (str(id), str(choose).lower())}
        r = u.get(url = 'http://eams.uestc.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=917') #获取jesession
        r = u.post('http://eams.uestc.edu.cn/eams/stdElectCourse!batchOperator.action?profileId=917', data = postdata)
        (info, end) = get_mid_text(r.text, 'text-align:left;margin:auto;">', '</br>')
        info = info.replace(' ','').replace('\n','').replace('\t','')
        count += 1
        print('正在进行第%d次尝试    ' % (count, ))
        print(info)
        if '成功' in info:
            break
        time.sleep(sleep)

parser = optparse.OptionParser()
parser.add_option('-n', '--num',
                  help="学号")
parser.add_option('-p', '--password',
                  help="密码")
parser.add_option('-P', '--port',
                  help="抢课端口（任意一个，可以用-g获得）")
#parser.add_option('-t', '--time',
#                  help="每次抢课的延时 单位为秒")
parser.add_option('-g', '--getport', action = 'store_true',
                  help="获取抢课端口")
parser.add_option('-l', '--list',
                  help="课程编号 即?lesson.id=276731后的数字 格式：c1,c2,c3...")
(options, args) = parser.parse_args()
print(options)
if options.num == None:
    options.num = input('请输入你的学号:')
if options.password == None:
    options.password = getpass.getpass('请输入你的密码:')
while True:
    if options.list != None:
        options.list = options.list.split(',')
        for i in range(len(options.list)):
            try:
                options.list[i] = int(options.list[i])
            except Exception:
                print('课程编号输入有误')
                break
        else:
            break
    print('接下来输入课程编号')
    print('课程编号 即?lesson.id=276731后的数字 格式：c1,c2,c3...')
    options.list = input('请输入你的课程编号：')
    
print(options.list)
while True:
    try:
        options.port = int(options.port)
    except Exception:
        options.port = input('请输入正确的抢课端口:')
        continue
    break

u = uestc_login.login(options.num, options.password)
if u == None:
    print(uestc_login.uestcget_last_error())
    exit()
print('登陆成功')
print('开始抢课')
if options.getport:
    print('url:\nhttp://eams.uestc.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=')
    print('port:\n' + str(get_open_url(u, threading_max = 50)))
    exit()

threads = []
for i in options.list:
    threads.append(threading.Thread(target=catch_course, args = (u, options.port, i, True, 0.5)))
    threads[len(threads) - 1].start()
#catch_course(u, options.port, 276926, False)
for i in threads:
    i.join()
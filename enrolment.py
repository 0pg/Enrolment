import requests, time
from urllib.parse import urlencode, quote_plus
from multiprocessing import Process, Pipe
from getpass import getpass
from bs4 import BeautifulSoup

sesserr = '세션이 만료되었습니다'
errcd000 = '신청되었습니다.'
errcd101 = '신청기간이 아닙니다.'
errcd102 = '신청할 수 있는 학점이 초과되었습니다.!!'
errcd104 = '이미 취득한 과목으로 취득 등급이 B(P) 등급 이상입니다.'
errcd103 = '금학기 수강신청한 과목이 중복되었습니다.'
errcd110 = '타 학과/학년에 개설 강좌입니다. 수강신청할 수 없습니다.'
errcd112 = '[] 교과목과 시간표가 중복되었습니다.'
errcd113 = '수강제한인원을 초과하였습니다.'
errcd999 = '개설 과목이 존재하지 않습니다.'
fatalerrlist = { 
            'errcd104' : '이미 취득한 과목으로 취득 등급이 B(P) 등급 이상입니다.',
            'errcd112' : '시간표가 중복되었습니다.',
            'errcd999' : '개설 과목이 존재하지 않습니다.',
            }

def get_session(memid,passwd):
    loginURL = "http://smsg.smuc.ac.kr:9100/sugang/common/inlogin.do?method=login"
    ver = 0
    headers = {
        "Host": "smsg.smuc.ac.kr:9100",
        "Content-Length" : '86',
        "Cache-Control" : "max-age=0",
        "Origin": "http://smsg.smuc.ac.kr:9100",
        "Upgrade-Insecure-Requests": '1',
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "http://smsg.smuc.ac.kr:9100/sugang/common/loginForm.do",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "close",
        }
    data = {
        'memnonob' : memid,
        'apssrowd' : passwd,
        'loginMode' : 'normal',
        }
    data1 = urlencode(data, quote_via=quote_plus)

    ses = requests.session()



    # ses.post(loginURL,data=data1, headers = headers, timeout=0.1)
    # print(ses.headers)
    while(True):
        try:
            res = ses.post(loginURL,data=data1, headers = headers, timeout=0.1)
            if 'Pragma' in res.headers:
                ses = '로그인 실패'
                break
            else:
                break
        except requests.exceptions.ConnectionError:
            ver += 1
            if ver > 50:
                ses = '네트워크 오류'
                break
        except requests.exceptions.HTTPError:
            ver += 1
            if ver > 50:
                ses = '페이지 오류'
                break
        except requests.exceptions.RequestException as e:
            pass
    return ses 
        
def stdname(s):
    res = s.get("http://smsg.smuc.ac.kr:9100/sugang/common/frame.do?method=left")
    soup = BeautifulSoup(res.text, 'html.parser')
    name = soup.select(
            'td > table > tr > td > span.Text_gray6'
            )
    uname = []
    for i in range(0,len(name)):
        uname.append(name[i].get_text())
    
    return uname

def sign_updata(subject, div):
    headers = {
        "Host": 'smsg.smuc.ac.kr:9100',
        "Content-Length": '145',
        "Cache-Control": 'max-age=0',
        "Origin": 'http://smsg.smuc.ac.kr:9100',
        "Upgrade-Insecure-Requests": '1',
        "Content-Type": 'application/x-www-form-urlencoded',
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        "Referer": 'http://smsg.smuc.ac.kr:9100/sugang/common/frame.do?method=left',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        "Connection": 'close',
    }
    data = {
        'D_CAMP_CD' : '100',
        'GWAJEONG' : '',
        'D_COLG' : '',
        'D_SUST' : '',
        'HAKNYEON' : '',
        'GB' : '10',
        'GB_NM' : '',
        'param' : '',
        'SBJT_NO' : subject,
        'DECS' : div,
        'GUBUN' : 'INSERT',
        'MODE' : 'NORMAL',
        'CAMP_CD' : '100',
        'CAMP_CHANGE' : '',
    }
    data1 = urlencode(data, quote_via=quote_plus) 
    lists = [data1 ,headers, subject+'-'+div]
    return lists

def sing_up(s, lists, term=1, pipe='none'):
    signURL = "http://smsg.smuc.ac.kr:9100/sugang/register/major.do?method=proc"
    ver = 0
    try:
        response = s.post(signURL, data=lists[0], headers=lists[1], timeout=0.1).text
        signed_list = get_list(s)
        signed_list_key = signed_list.keys()
        errmatch = [fatalerrlist[i]+' 다시 확인 후 신청바랍니다.' for i in fatalerrlist if fatalerrlist[i] in response]

        if sesserr in response:
             s = get_session(stnum, pwd)
        elif errmatch:
            for err in errmatch:
                    pipe.send(err)
            return 0
        elif errcd102 in response:
            if lists[2] in signed_list_key:
               pipe.send(signed_list(lists[2])+' '+errcd103)
               return 0
        elif errcd000 in response:
            pipe.send(signed_list(lists[2])+' 수강신청 성공')
            return 0
        elif errcd103 in response:
            pipe.send(errcd103)
            return 0
    except requests.exceptions.RequestException as e:
        ver += 1
        if ver > 50:
            pipe.send('네트워크 오류')
            return -1
        pass

def get_list(s):
    signed_list = {}
    res = s.get("http://smsg.smuc.ac.kr:9100/sugang/register/result.do?method=list1")
    soup = BeautifulSoup(res.text, 'html.parser')
    subnum = soup.select(
            'tr > td:nth-of-type(5)'
        )
    subname = soup.select(
            'tr > td:nth-of-type(6)'
        )
    for i in range(1,len(subnum)):
        signed_list[subnum[i].get_text()] = subname[i].get_text()
        
    return signed_list

def excute(s,sub, div, nos):
    process = []
    proc = []
    pids = []
    pipe = Pipe()
    term = 3 #int(input('수강신청 요청속도(0.1sec): ')) *0.1
    for i in range(0,nos):
        lists = sign_updata(sub[i], div[i])
        proc.append(Process(target=sing_up, args=(s, lists,term, pipe[0])))
    
    for i in range(0,nos):
        proc[i].start()
        pids.append(proc[i].pid)

    process.append(proc)
    process.append(pipe)

    return process
	

if __name__ == '__main__':
    excute()

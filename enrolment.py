import requests, time
from urllib.parse import urlencode, quote_plus
from getpass import getpass
from multiprocessing import Process
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

proc = []

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
            print(e)
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
    lists = [data1 ,headers]
    return lists

def sing_up(s, lists):
    signURL = "http://smsg.smuc.ac.kr:9100/sugang/register/major.do?method=proc"
    try:
        response = s.post(signURL, data=lists[0], headers=lists[1], timeout=0.1).text
        signed_list = get_list(s)
        signed_list_key = signed_list.keys()
        subject = lists[0].split('&')[8].split('=')[1]+'-'+lists[0].split('&')[9].split('=')[1]
        errmatch = [fatalerrlist[i]+' 다시 확인 후 신청바랍니다.' for i in fatalerrlist if fatalerrlist[i] in response]
        print(subject+' 수강신청 중')
        if sesserr in response:
            print(sesserr+' 세션을 새로 받습니다.')
            s = get_session(stnum, pwd)
        elif errmatch:
            for err in errmatch:
                print('경고 : '+err+' 프로그램을 종료합니다.')
        elif errcd102 in response:
            if subject in signed_list_key:
                print(signed_list(subject)+' '+errcd103)
            print('주의 : 신청할 수 있는 학점이 초과되었습니다. 수강신청이 불가능 할 수 있습니다!!')
        elif errcd000 in response:
            print(signed_list(subject)+' '+errcd000)
        elif errcd103 in response:
            print(signed_list(subject)+' '+errcd103)
        elif errcd110 in response:
            print('주의 : 타 학과/학년에 개설 강좌입니다. 수강신청이 불가능 할 수 있습니다.')
        elif errcd101 in response:
            print('주의 : '+errcd101)

    except requests.exceptions.RequestException as e:
        print (e)
        pass
            

def get_list(s):
    signed_list = {}
    res = s.get("http://smsg.smuc.ac.kr:9100/sugang/register/result.do?method=list1")
    soup = BeautifulSoup(res.text, 'html.parser')
    subnum = soup.select(
            'tr > td:nth-of-type(4)'
        )
    subname = soup.select(
            'tr > td:nth-of-type(6)'
        )
    for i in range(1,len(subnum)):
        signed_list[subnum[i].get_text()] = subname[i].get_text()
        
    return signed_list

def excute(s,sub,div,nos):
    for i in range(0,nos):
        lists = sign_updata(sub[i], div[i])
        proc.append(Process(target=sing_up, args=(s, lists,term)))

    for i in range(0,nos):
        proc[i].start()

def pterminate():
    for p in proc:
        p.terminate()

if __name__ == '__main__':
    excute()

# Enrolment
## smu 수강신청 보조 웹서버 | python3.5 이상 버전에서 실행
<hr>-<hr/>
웹서버를 실행하는데 필요한 패키지설치
<pre><code>git clone https://github.com/201311105/Enrolment
cd Enrolment
pip install -r requirements.txt</code></pre>

enrolment.py 모듈설치
<pre><code>mv enrolment.py [자신의 python 설치폴더]</code></pre>
(혹은<code>python -c 'import sys;print(sys.path)'</code>를 실행하여 출력되는 경로들 중 하나)

서버를 실행시킨다. 127.0.0.1:80 으로 접속하거나 외부에서 접속도 가능
<pre><code>python enrol_server/run.py</code></pre>

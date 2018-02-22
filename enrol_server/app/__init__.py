from flask import Flask, flash, g, request, render_template, url_for, redirect
import enrolment, json

app = Flask(__name__)
app.secret_key = 'random string'
s = 'none'
@app.route('/')
def main():
	return render_template('auth/index.html')

@app.route('/sign',methods=['GET','POST'])
def login():
	if request.method == 'GET':
		flash('로그인 하십시오')
		return redirect(url_for('main'))
	memid = request.form['memid']
	pwd = request.form['pwd']
	
	global s
	s = smu.get_session(memid, pwd)
	if s in ("로그인 실패" ,"네트워크 오류", "페이지 오류"):
		flash(s)
		return redirect(url_for('main'))
	name = smu.stdname(s)
	return render_template('auth/sign.html', username=name[5], sess=s) 			

@app.route('/signing',methods=['GET','POST'])
def sign():
	if request.method == 'GET':
		flash('로그인 하십시오')
		return redirect(url_for('main'))
	dic = {}
	data = request.values
	subs = (data.getlist('sub'))
	divs = (data.getlist('div'))
	for i in range(0,len(subs)):
		dic[subs[i]] = divs[i]
	
	smu.excute(s,subs,divs,len(subs))

	return render_template('auth/signing.html', subs=dic)
	
@app.route('/cancle')
def cancle():
	if s is 'none' :
		flash('로그인 하십시오')
		return redirect(url_for('main'))
	smu.pterminate()
	s.close()
	flash('취소하셨습니다')

	return redirect(url_for('main'))



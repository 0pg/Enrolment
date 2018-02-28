from flask import Flask, flash, g, request, render_template, url_for, redirect
from collections import OrderedDict
import smu, json, requests, os

app = Flask(__name__)
app.secret_key = 'random string'
proc = {}
pids = {}
sess = {}

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
	s = smu.get_session(memid, pwd)
	sess[memid] = s
	if s in ("로그인 실패" ,"네트워크 오류", "페이지 오류"):
		flash(s)
		return redirect(url_for('main'))
	name = smu.stdname(s)
	return render_template('auth/sign.html', username=name[5], memid=memid) 

@app.route('/signing',methods=['GET','POST'])
def sign(): 
	if request.method == 'GET':
		flash('로그인 하십시오')
		return redirect(url_for('main'))
	memid = request.form['memid']
	s = sess[memid]
	dic = {}
	data = request.values
	subs = (data.getlist('sub'))
	divs = (data.getlist('div'))
	for i in range(0,len(subs)):
		dic[subs[i]] = divs[i]
	
	pids[memid] = smu.excute(s, subs, divs, len(subs))

	
	return render_template('auth/signing.html', subs=dic, username=memid)

	
@app.route('/cancle', methods=['GET','POST'])
def cancle():
	if request.method == 'GET' or request.form['memid'] not in sess.keys():
		flash('로그인 하십시오')
		return redirect(url_for('main'))
	memid = request.form['memid']
	sess[memid].close()
	res = []
	for pid in pids[memid][1]:
		res.append(pid.recv())
	for pid in pids[memid][0]:
		pid.terminate()
		pid.join()
	
	for r in res:
		flash(r)
	
	del(sess[memid])

	return redirect(url_for('main'))

 

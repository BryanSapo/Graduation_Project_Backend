# Import flask and datetime module for showing date and time
from flask import Flask,request,redirect
# from flask_socketio import SocketIO,emit
from flask_sockets import Sockets
from flask_cors import CORS
import datetime
import json
import os
from tinydb import TinyDB,Query
from myUtil import pp
from  geventwebsocket.exceptions import WebSocketError as wse
from werkzeug.utils import secure_filename
from temi_class import TemiClass

db=TinyDB('temi.json')
db.truncate()
temi = Query()

# print(db.search(User.name == 'id123'))

x = datetime.datetime.now()
 
# Initializing flask app
app = Flask(__name__)

sockets=Sockets(app)
ALLOWED_EXTENSIONS = {'xlsx'}
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
clients=[]
CORS(app,supports_credentials=True)
####################################
# Web route methods ################
####################################
# Route for seeing a data

@app.route('/data')
def get_time():

	# Returning an api for showing in  reactjs
	return {
		'Name':"this Name",
		"Age":"300",
		"Date":x,
		"programming":"python"
	}

@app.route('/controlPanel')
def controlPanel():
	pp("controlPanel")
	with open("temi.json", "r",encoding='utf-8') as f:
		try:
			f.seek(0, os.SEEK_END)
			# print("len-> ",end='')
			# print(f.tell())
			l=f.tell()
			f.seek(0)
			if l:
				content=json.dumps(json.load(f))
				# print(type(content))
				# print(content)
				f.close()
				return content
			else:
				content=json.loads('{"Temi":"No Temi Yet"}')
				print("file empty")
				f.close()
				return content
		except Exception as e:	
			print(e)
			return json.loads('{"Error":"Something went wrong!"}')

@app.route('/fake_temi')
def fake_temi():
	t=str(datetime.datetime.now().year)+"/"+str(datetime.datetime.now().month)+"/"+str(datetime.datetime.now().day)+" "+str(datetime.datetime.now().hour)+":"+str(datetime.datetime.now().minute)+":"+str(datetime.datetime.now().second)
	print(f"receive a request from {request.remote_addr} at {t}")
	with open("temi.json", "r",encoding='utf-8') as f:
		try:
			f.seek(0, os.SEEK_END)
			# print("len-> ",end='')
			# print(f.tell())
			l=f.tell()
			f.seek(0)
			if l:
				content=json.dumps(json.load(f))
				# print(type(content))
				# print(content)
				f.close()
				return content
			else:
				content=json.loads('{"Temi":"No Temi Yet"}')
				print("file empty")
				f.close()
				return content
		except Exception as e:	
			print(e)
			return json.loads('{"Error":"Something went wrong!"}')
		
# Need to change -> when a ws connect, create a temi object and when a ws closed, remove a temi object....
@app.route('/new_temi',methods=['POST','GET'])
def new_temi():
	global clients
	if request.method=='POST':
		id = request.form['id']
		ip =request.form['ip']
		location =request.form['location']
		status =request.form['status']
		url=request.form['link']
	else:
		id=request.args.get('id')
		ip=request.args.get('ip')
		location=request.args.get('location')
		status=request.args.get('status')
		url=request.args.get('link')
	temi=createTemiJson(id,ip,location,status)
	# writeTemiJson(temi)
	print(url)
	return redirect(url,code=302)
	# return jsonify(temi)


@app.route('/DoSomething',methods=["POST"])
def DoSomething():
	print("Someone click the dosomething button !!!")
	id = request.values['id']
	command = request.values['command']
	args = request.values['args']
	# if command == 'Go':
	# 	location = request.values['location']
	rtn=json.dumps(json.loads('{"id":"'+id+'","command":"'+command+'","args":"'+args+'"}'))
	# elif command == 'Speak':
	# 	rtn=json.loads('{"id":"'+id+'","command":"'+command+'"}')
	print(rtn)
	for client in clients:# 個別傳送訊息
		if client.get(id) != None:
			client.get(id).send(str(rtn))
	return rtn
@app.route('/uploadFile',methods=['POST'])
def uploadFile():
	file = request.files['file']
	print("#")
	print(file)
	print("#")
	filename = secure_filename(file.filename)
	print(filename)
	file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))# this is the file savign part, need to change file name to increse the flexibility of app
	rtn=json.loads('{"msg":"成功"}')
	return rtn
	# elif command == 'Speak':
####################################
# Local methods ####################
####################################

#create a json include temi informations
def createTemiJson(id,ip,location,status):
	dic={
		"id":id,
		"ip":ip,
		"location":location,
		"status":status
	}
	
	# temi_json=json.dumps(dic, indent=4)
	db.insert(dic)
	temi_json=""
	return temi_json
def updateTemi(id,ip,location,status):
	dic={
		"ip":ip,
		"location":location,
		"status":status
	}
	db.update(dic, temi.id == id)

#clear all temi(json file)
def clearTemiJson():
	with open("temi.json", "w") as f:
		f.truncate(0)
#pretty print

####################################
# WebSocket ########################
####################################

#Flask所應該要有的websocket實做方案，實際測起來會有WebsocketMismatch的Exception
#根據https://github.com/heroku-python/flask-sockets/pull/82#issuecomment-938534248，應該要有解決方案。

# d=(dir(Sockets))
# for i in d:
# 	print(i)
@sockets.route('/hello',websocket=True)# 在改寫完flask_sockets之後成功可以使用了 請參考筆記:https://hackmd.io/@BryanSapo/FlaskSocket
def onHello(ws):
	global clients
	client_ip = request.remote_addr# 想要取得請求端的ip，目前不知道到底是哪裡來的ip，還需要上實機或是多億台電腦用PieSockets測試才知道
	currentTemi=None
	has=False
	temi_json=None
		# currentTemi=TemiClass(id="123",ip="456",ws=ws)
		# clients.append(currentTemi)
	pp('onHello')
	# print(client_ip)
	# print(dir(ws))
	# print(ws.origin)
	try:
		while not ws.closed:
			msg=ws.receive()
			# print(clients)
			if msg!=None:
				
				try:
					temi_json=json.loads(msg)
					
					msg_type=temi_json['type']
					id=temi_json['id']
					ip=temi_json['ip']
					location=temi_json['location']
					status=temi_json['status']
					for i in clients:
						has=False
						if i.get(id)!=None:
							has=True
							break
					if not has :
						clients.append({temi_json['id']:ws})
					print(clients)
					if msg_type=='onConnect':
						if db.get(temi.id==id) ==None:
							createTemiJson(id,ip,location,status)
							
							# ws.send(str(id))
						else:
							updateTemi(id,ip,location,status)	# 該考慮一下何時該update何時該insert，看來tinyDB無法在資料不存在時使用insert，存在時使用update。
						print("["+msg_type+"]","Create a Temi object with the following data-> ["+msg+"]")
					elif msg_type=='onMessage':
						print("["+msg_type+"]","send something to Temi with the following data-> ["+msg+"]")
						data = datetime.datetime.now()
						try:
							ws.send(str(data))
						except wse as e:
							print(e)
							pass					
					
				except Exception as e:
					print('receive exception: '+str(e))
					print(msg)
					ws.send('receive exception: '+str(e))
	except Exception as e:
		print(e)
	#加入自動刪除已斷線的機制
	for i in range(len(clients)):
		if temi_json['id'] in clients[i].keys():
			del clients[i]
			db.remove(temi.id==temi_json['id'])
			break
	# if ws in clients:
	# 	clients.remove(ws)# 未來有機會可以試著釋放記憶體空間？目前不知道是否會繼續佔用記憶體。
	pp("WebSocket is closed !!")
	

		





# socketio=SocketIO(app)
# socketio.init_app(app,cors_allowed_origins='*') #allow cross oringins request (fetch or something else, if u know , u know)
# namespace='/temi_ws'

# # @socketio.on('connect')
# # def on_connect(data):
# # 	pp("Hola")


# @socketio.on('connect',namespace=namespace)
# def connected_msg():
# 	pp('connected')

# @socketio.on('message')
# def handle_message(data):
#     print('received message: ' + data)

# @socketio.on('json')
# def handle_json(json):
#     print('received json: ' + str(json))
####################################
# Running app ######################
####################################
if __name__ == '__main__':
	# clearTemiJson()
	# socketio.run(app, debug=True)
	# app.run(host="0.0.0.0",port=1108,debug=True)
	from gevent import pywsgi
	from geventwebsocket.handler import WebSocketHandler
	server=pywsgi.WSGIServer(('0.0.0.0',1107),app,handler_class=WebSocketHandler)
	pp('Server Start')
	server.serve_forever()
	
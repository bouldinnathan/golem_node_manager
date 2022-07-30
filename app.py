#Version 1.0

import easy_mode
easy_installer=easy_mode.Easy_installer()


#function of import and install
easy_installer.easy("Flask","flask")
easy_installer.easy("socket")
easy_installer.easy("flask_restful")
easy_installer.easy("requests")
easy_installer.easy("wtforms")


# importing 
import os
from flask import Flask, request, jsonify, json, render_template
from flask_restful import Resource, Api
import threading
import time
from time import sleep
import socket
import subprocess
from subprocess import Popen, PIPE
import requests



auto_undercut_median_price=True


app = Flask(__name__,template_folder='template')
api = Api(app)


##from wtforms import Form, BooleanField, StringField, PasswordField, DecimalField,IntegerField, validators
##
##class RegistrationForm(Form):
##    name = StringField('Node Name', [validators.Length(min=4, max=50),validators.DataRequired()])
##    cores = IntegerField('cores', [validators.NumberRange(min=1, max=1000),validators.DataRequired()])
##    memory = str(DecimalField('memory in GiB', [validators.NumberRange(min=1, max=1000),validators.DataRequired()],places=25))+" GiB"
##    storage = str(DecimalField('storage in GiB', [validators.NumberRange(min=1, max=1000),validators.DataRequired()],places=25))+" GiB"
##    
##    starting_fee = str(DecimalField('in GLM', [validators.NumberRange(min=0.0001, max=1),validators.DataRequired()],places=25))
##    env_per_hour = str(DecimalField('in GLM', [validators.NumberRange(min=0.0001, max=1),validators.DataRequired()],places=25))
##    cpu_per_hour = str(DecimalField('in GLM', [validators.NumberRange(min=0.0001, max=1),validators.DataRequired()],places=25))
##
##    address = StringField('Address', [validators.Length(min=42, max=42),validators.DataRequired()])
##    #password = PasswordField('New Password', [
##    #    validators.DataRequired(),
##    #    validators.EqualTo('confirm', message='Passwords must match')
##    #])
##    #confirm = PasswordField('Repeat Password')
##    #accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


#default

def get_additional_settings():
    #default
    autoprice_toggle=True
    autoprice_offset=0.9999

    try:
        f=open("settings.json","r")
        settings=json.loads(f)
        f.close()
    except:
        settings={"autoprice_toggle":autoprice_toggle,"autoprice_offset":autoprice_offset}

    return settings

def set_additional_settings(settings):

    try:
        f=open("settings.json","w")
        f.write(jsonify(settings))
        f.close()
    except:
        print("Save failed")


def get_median_price():
    location='''https://api.stats.golem.network/v1/network/pricing/median'''
    r = requests.get(location)
    print("Request to api status code: "+str(r.status_code))
    return r.json()
    
##    try:
##        process = Popen(['curl', location], stdout=PIPE, stderr=PIPE)
##        stdout, stderr = process.communicate()
##    except:
##        output=subprocess.run(['curl', location], capture_output=True)
##        stdout=output.stdout
##    stdout=json.loads(stdout.decode('UTf-8'))
##    return stdout#{'cpuhour': 0.0179137233409757, 'perhour': 0.0, 'start': 0.0}

    
def autopricing(all_settings_):
    output=""

    print(all_settings_)
    print("AutoPrice adjust is: "+str(all_settings_["autoprice_toggle"]))
    if str(all_settings_["autoprice_toggle"]).lower() in "True true Yes yes 1 ok OK Ok okay Okay":

        print("Price Offset is: "+str(all_settings_["autoprice_offset"]))
        percent_offset=float(str(all_settings_["autoprice_offset"]).replace(" ",""))
        
        median_price=get_median_price()#{'cpuhour': 0.0179137233409757, 'perhour': 0.0, 'start': 0.0}
        print(str(median_price))
        
        output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --cpu-per-hour "+str(median_price['cpuhour']*percent_offset),shell=True).decode("UTF-8")
        output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --env-per-hour "+str(median_price['perhour']*percent_offset),shell=True).decode("UTF-8")
        output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --starting-fee "+str(median_price['start']*percent_offset),shell=True).decode("UTF-8")


        print("Autopricing exit code: "+str(output))
    

def threaded_autopricing(wait_time=600):

    #This attempts to get the newest prices now
    try:
        sleep(wait_time/10)
        autopricing(get_additional_settings())
    except:
        pass
    

    #this will get the newest prices over time
    while 1:
        sleep(wait_time)
        try:
            sleep(wait_time)
            autopricing(get_additional_settings())
        except:
            pass




#hostname = socket.gethostname()
#local_ip = socket.gethostbyname(hostname)

def get_ip():# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


local_ip=get_ip()


try:
    f=open("./found.json","r")
    found_ips=json.loads(f)["ip"] 
except:
    found_ips=[local_ip]
all_found_ips=[local_ip]
network_state=dict()


def golemsp_P():
    #temp=str(os.path.join(os.getcwd(),".local","bin","golemsp"))
    temp="golemsp"
    return temp

def pathing():
    return '''export PATH="home/golem/.local/bin:$PATH";'''


def combine_json(json0,json1):#assumes json0 data is out of date

    combine_list_ips=list()
    combine_dict_ips_data=dict()
    #print(json0)
    for ip0 in json0["ip"]:
        combine_list_ips.append(ip0)
        data0=json0[ip0]
        combine_dict_ips_data[ip0]=data0

    for ip1 in json1["ip"]:
        combine_list_ips.append(ip1)
        data1=json1[ip1]
        combine_dict_ips_data[ip1]=data1

    combine_dict_ips_data["ip"]=list(set(combine_list_ips))

    return combine_dict_ips_data
        

    
##    ip0=json0["ip"]
##    data0=json0["data"]
##
##    ip1=json1["ip"]
##    data1=json1["data"]
##
##
##    ip_combine=ip0
##    ip_combine.extend(ip1)
##    ip_combine=list(set(ip_combine))
##
##    data_combine=data0
##    data_combine.extend(data1)
##
##    return {"ip":ip_combine,"data":data_combine}


####### to do#####
def write_local(data):
    global local_ip
    all_settings=data[local_ip]

    output=""
    
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --node-name "+str(all_settings.pop("Node Name")),shell=True).decode("UTF-8")
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --cores "+str(round(float(all_settings.pop("cores")))),shell=True).decode("UTF-8")
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --memory '"+str(all_settings.pop("memory"))+"'",shell=True).decode("UTF-8")
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --disk '"+str(all_settings.pop("disk"))+"'",shell=True).decode("UTF-8")
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --starting-fee "+str(all_settings.pop("VM start")),shell=True).decode("UTF-8")
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --env-per-hour "+str(all_settings.pop("VM hour")),shell=True).decode("UTF-8")
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --cpu-per-hour "+str(all_settings.pop("VM cpuh")),shell=True).decode("UTF-8")
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --account "+str(all_settings.pop("wallet")),shell=True).decode("UTF-8")
    output+=subprocess.check_output(pathing()+golemsp_P()+" settings set --payment-network "+str(all_settings.pop("network")),shell=True).decode("UTF-8")


    autopricing(all_settings)

    set_additional_settings(all_settings)

    return {} #{"ip":["192.168.1.1"],"data":["192.168.1.1":{}]}

def get_local():

    def clean(line):
        return line.replace("│","").replace("─","").replace("\u2502","").replace('"',"").replace('\u001b',"").replace('[32m',"").replace('[0m',"").replace('[35m',"").replace('[35',"").replace('\t',"").replace('[38;5;63m',"")


    
    output=subprocess.check_output(pathing()+golemsp_P()+" settings show",shell=True).decode("UTF-8")
    output_strip=output.replace("   "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ")
    output_lines=output_strip.split("\n")

    data={}
    switch=None
    for line in output_lines:
        line=clean(line)
        if len(line)<5:continue
        if "vm" in line:
            switch=1
        elif "wasmtime" in line:
            switch=2

        if  switch==None:
            if "node name:" in line:
                data["Node Name"]=line.split(":")[-1]
            elif "cores:" in line:
                data["cores"]=float(line.split(":")[-1])
            elif "memory:" in line:
                data["memory"]=line.split(":")[-1]
            elif "disk:" in line:
                data["disk"]=line.split(":")[-1]
        elif switch==1:
            
            if "cpu hour" in line:
                data["VM cpuh"]=float(line.split("GLM")[0])
            elif "per hour" in line:
                data["VM hour"]=float(line.split("GLM")[0])
            elif "for start" in line:
                data["VM start"]=float(line.split("GLM")[0])

        elif switch==2:
            
            if "cpu hour" in line:
                data["wasmtime cpuh"]=float(line.split("GLM")[0])
            elif "per hour" in line:
                data["wasmtime hour"]=float(line.split("GLM")[0])
            elif "for start" in line:
                data["wasmtime start"]=float(line.split("GLM")[0])




    output=subprocess.check_output(pathing()+golemsp_P()+" status",shell=True).decode("UTF-8")

    # checks for dynamic text output and corrects
    if len(output.split("\n")[0])>100:
        output.replace("|","|\n")
    


    # light clean up
    output_strip=output.replace("   "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ")
    output_lines=output_strip.split("\n")

    switch=None
    for line in output_lines:
        line=clean(line)
        if len(line)<5:continue
        

        if "Service" in line:
            data["Service"]=line.split("Service")[-1]
        elif "Version" in line:
            data["Version"]=line.split("Version")[-1]
        elif "Date" in line:
            data["Date"]=line.split("Date")[-1]
        elif "Build" in line:
            data["Build"]=line.split("Build")[-1]
        elif "Node Name" in line:
            data["Node Name"]=line.split("Node Name")[-1]
        elif "Subnet" in line:
            data["Subnet"]=line.split("Subnet")[-1]
        elif "VM" in line:
            data["VM"]=line.split("VM")[-1]

        elif "0x" in line:
            data["wallet"]=str(line)
        elif "network" in line:
            data["network"]=str(line.split("network")[-1])
        elif "(total)" in line:
            data["total"]=float(line.split("total)")[-1].split("GLM")[0])
        elif "(on-chain)" in line:
            data["on-chain"]=float(line.split("(on-chain)")[-1].split("GLM")[0])
        elif "(polygon)" in line:
            data["polygon"]=float(line.split("(polygon)")[-1].split("GLM")[0])
        elif "(zksync)" in line:
            data["zksync"]=float(line.split("(zksync)")[-1].split("GLM")[0])
        elif "pending" in line:
            data["pending"]=str(line.split("pending")[-1].split("GLM")[0])
        elif "issued" in line:
            data["issued"]=float(line.split("issued")[-1].split("GLM")[0])
        
        elif "1h processed" in line:
            data["1h processed"]=float(line.split("1h processed")[-1][:-1])
        elif "1h in process" in line:
            data["1h in process"]=float(line.split("1h in process")[-1][:-1])
        elif "total processed" in line:
            data["total processed"]=float(line.split("total processed")[-1][:-1])


    data.update(get_additional_settings())



            
    return {"ip":[local_ip],local_ip:data}




        
    
##ToDO###
def remove_dead():
    return [] # [192.168.1.1,192.168.1.2]


##ToDO###


def update_save_json(remote_data):
    global network_state
    try:
        f=open("./data.json","r")
        known_data=json.loads(f)
        known_data=combine_json(known_data,get_local())
        known_data=combine_json(known_data,remote_data)#assumes json data is out of date
        #f.close()
        
    except:
        known_data=get_local()

    #f=open("./data.json","w")
    #known_data_json=json.dumps(combine_json(known_data,remote_data))
    if len(network_state)==0:
        network_state=combine_json(known_data,remote_data)
    else:
        network_state=combine_json(network_state,remote_data)
        network_state=combine_json(network_state,known_data)
    #f.write(known_data_json)
    #f.close()
    

    

# updates in record of other nodes information 
@app.route('/api/receive', methods=['POST'])
def getting_json_update():
    #print("posted")
    if request.is_json:   
    
        data=request.get_json()# {"ip":["192.168.1.1","192.168.1.2"],"data":["192.168.1.1":{},"192.168.1.2":{}]}

        print("received data from... "+str(data["ip"]))
        update_save_json(data)
        

        return "True"
    return "False"

# updates it own record
@app.route('/api/setting', methods=['POST'])
def setting_json_update():
    #print("posted")
    if request.is_json:
        pass
        #print("is json")     
    try:
        data=request.get_json()# {"ip":["192.168.1.1","192.168.1.2"],"data":["192.168.1.1":{},"192.168.1.2":{}]}
    except Exception as e: 
        print(e)
    
    write_local(data)
    update_save_json(get_local())

    return "True"

@app.route('/api/receive/ips', methods=['POST'])
def setting_json_ips():
    global all_found_ips
    
    if request.is_json:
    

        data=request.get_json()# ["192.168.1.1","192.168.1.2"]
    
        if data==None:
            return "False"

        data = list(filter(None, data))
        all_found_ips = list(filter(None, all_found_ips))
        data = list(set(data))
        all_found_ips = list(set(all_found_ips))
        if data!=None and all_found_ips!=None:
            print("received ips... "+str(data))
            
            if all_found_ips==None:all_found_ips=data
            else:all_found_ips.extend(data)
            
            all_found_ips.extend(data)
            all_found_ips=list(set(all_found_ips))
        print("IPs are updated from remote")

    return "True"
    




@app.route('/api/ping', methods=['POST',"GET"])
def ping_me():
    return "True"

@app.route('/', methods=['POST',"GET"])
def main_page():
    global network_state
    def get_recent_data():
        try:
            f=open("./data.json","r")
            known_data=json.loads(f)
            if known_data=={}:known_data=get_local()
        except:
            try:
                #requests.post("localhost:8090/api/receive'",json=jsonify(get_local()))
                known_data=combine_json(network_state,get_local())
            except:
                pass
                known_data=get_local()
        return known_data

    
    if request.method == 'POST':

        #shaping the data
        new_settings=dict(request.form)
        ip=new_settings["ip"]
        new_settings={ip:new_settings}

        
        requests.post("http://"+str(ip)+":8090"+"/api/setting",json=new_settings)

        
        known_data=get_recent_data()
        return render_template('main.html',known_data=known_data)

    elif request.method == 'GET':
##        form = RegistrationForm(request.form)
    
        #known_data=get_recent_data()
        known_data=network_state
        print(network_state)
        #return known_data
        return render_template('main.html',known_data=known_data)
    




    



# needs while(1) it update every ip it knows of its condition and on failed to reach marks as a failed ip
# function is only one allowed to write to failed.json
# reads joun.json on fail tries again
def sending_json_update():
    global all_found_ips
    global local_ip

    ips=list()
    try: # if this fails tries to use memory of ips if fails restart the loop after one sec 
        f=open("found.json","r")
        known_data=json.loads(f)
        ips=known_data
    except:pass
        
    if all_found_ips==[] and ips!=[]:all_found_ips=ips

    try:
        ips=list(set(ips.extend(all_found_ips)))
        all_found_ips=ips
    except:pass

    try:
        all_found_ips=list(set(all_found_ips.extend(ips)))
        ips=all_found_ips
    except:pass

    

    while(1):



        if len(all_found_ips)==0:
            print("No ips")
            time.sleep(1)
            continue
            



        # try all known ips
        failed_ip=list()
        success_ip=list()
        for ip in all_found_ips:
            #if local_ip==None: continue
            if local_ip in ip: continue
            
            try:
                requests.post("http://"+ip+''':8090/api/receive''',json=get_local())
                requests.post("http://"+ip+''':8090/api/receive/ips''',json=ips)
                print("Update "+ip+" of current state")

            except:
                print("Failed to talk to..."+str(ip))
                failed_ip.append(ip)


        # update the failed list
        try:
            pass
            #f=open("failed.json","w")
            #failed_data=json.dumps(failed_ip)
            #f.write(failed_data)
            #f.close()
        except:
            pass
                
        time.sleep(1)
        


# function is only one allowed to write to found.json
def find_nodes():
    global local_ip
    global all_found_ips

    long_scan_bool=False
    one_time_scan=True
##    from urllib3.util.retry import Retry
##    from requests.adapters import HTTPAdapter

    time.sleep(5)

    def threaded_pinger(ip):
        try:
            _=requests.get('''http://'''+ip+''':8090/api/ping''')
            return ip
        except Exception as e:
            #print(e)
            return None
##        retries = Retry(total=1,
##                backoff_factor=0.001,
##                status_forcelist=[ 500, 502, 503, 504 ])
##        s=requests.Session()
##
##        s.mount('''http://'''+ip+''':8090/api/ping''',HTTPAdapter(max_retries=retries))
##        try:
##            s.get('''http://'''+ip+''':8090/api/ping''')
##            return ip
##        except Exception as e:
##            #print(e)
##            return None



    ip_tobe_joined=local_ip.split(".")[:4]
    start_ip=str(ip_tobe_joined[0])+"."+str(ip_tobe_joined[1])+"."+str(ip_tobe_joined[2])+"."+str(ip_tobe_joined[3])

    ip_tobe_joined_short=local_ip.split(".")[:2]
    start_ip_short=str(ip_tobe_joined[0])+"."+str(ip_tobe_joined[1])+"."+str(ip_tobe_joined[2])

    print("Scan Start")
    while 1:
        # building short search list
        search_ips=list()
        for short in range(0,255):
            ip=start_ip_short+"."+str(short)
            search_ips.append(ip)

        #print(search_ips)
        found_ips=easy_mode.generic_threader(threaded_pinger,search_ips,thread_count=16) #255 threads
        #print(found_ips)



        found_ips = list(filter(None, found_ips))
        found_ips = list(set(found_ips))

        if found_ips!=[] and found_ips!=None and all_found_ips!=[] and all_found_ips!=None : list(set(all_found_ips.extend(found_ips)))
        elif found_ips!=[] and found_ips!=None and all_found_ips==[] and all_found_ips==None: list(set(all_found_ips=found_ips))
        

        print(found_ips)
        print("Short Scan Complete")
        f=open("found.json","w")
        known_data_json=json.dumps(found_ips)
        f.write(known_data_json)
        #f.close()

        if long_scan_bool:
            # building long search list
            search_ips=list()
            for x in range(0,255):
                for y in range(0,255):
                    ip=start_ip+"."+str(x)+"."+str(y)
                    search_ips.append(ip)

            long_found_ips=easy_mode.generic_threader(threaded_pinger,search_ips,thread_count=16)#65000 threads needed



            # handleing nones
            found_ips = list(filter(None, found_ips))
            all_found_ips = list(filter(None, all_found_ips))
            found_ips = list(set(found_ips))
            all_found_ips = list(set(all_found_ips))
            if found_ips!=[] and all_found_ips!=[]:
                found_ips = list(set(found_ips.extend(all_found_ips)))
                found_ips = list(filter(None, found_ips))
                all_found_ips=found_ips


                

            print("Long Scan Complete")
            f=open("found.json","w")
            known_data_json=json.dumps(found_ips)
            f.write(known_data_json)
            #f.close()

        time.sleep(1)
        if one_time_scan:break
    

    




def self_updater_loop():
    while 1:
        time.sleep(5)
        try:
            update_save_json(get_local())
        except:
            continue





print("Ready...")
if __name__ == '__main__':

    #Fix Pathing
    os.environ['PATH'] = "/home/golem/.local/bin:$PATH"

    
    
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(os.path.join(dname,".local","bin"))
    print(dname)
    print(str(os.getcwd()))
    

    
    temp=golemsp_P()+" run &"
    print(temp)
    _=os.system(temp)
    time.sleep(30)


    # autostarts the undercuting the market

    
    x = threading.Thread(target=sending_json_update)
    x.start()
    x1 = threading.Thread(target=find_nodes)
    x1.start()
    x2 = threading.Thread(target=self_updater_loop)
    x2.start()

    # autostarts the undercuting the market
    if auto_undercut_median_price:
        #threaded_autopricing()
        x3 = threading.Thread(target=threaded_autopricing)
        x3.start()


    

    app.run(host='0.0.0.0',port='8090')

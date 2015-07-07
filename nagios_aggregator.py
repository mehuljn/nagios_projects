import urllib3
import BeautifulSoup
import yaml
import pyaml
import re
from flask import Flask
import json
import threading
import sys
import datetime

app = Flask(__name__)

@app.route('/')
def group_data_to_browser():
    return json.dumps(groups_data_show)


STATUS_MAPPING = { "ack.gif" : "acknowledged",\
                       "passiveonly.gif" : "passiveonly",\
                       "disabled.gif" : "passiveonly",\
                       "ndisabled.gif" : "notifications_disabled",\
                       "downtime.gif" : "scheduled_downtime",\
                       "flapping.gif" : "flapping"}


def host_mon_url(monitors,groups):
                #for group in groups:
                #             print group['name'] + " " + group['regex_pat']
    for monitor in monitors:
        m_url = monitor['url']
        m_name = monitor['name']
        m_username = monitor['username']
        m_password = monitor['password']

        http = urllib3.PoolManager()
        headers = urllib3.util.make_headers(basic_auth= m_username + ":" + m_password)
        try:
            r1 = http.request('GET', m_url + 'status.cgi?hostgroup=all&style=hostdetail',headers=headers)
            #print r1.status

            raw_soup = BeautifulSoup.BeautifulSoup(r1.data)
            #print raw_soup

            table_content = raw_soup('table',{'class': 'status'})[0]

            #print table_content

            trs = table_content('tr', recursive=False)

            trs.pop(0)
            tds = []
            skip = False
            for tr in trs:
                try:
                    skip = False
                    if len(tr('td',recursive=False)) > 1:
                        tds = tr('td',recursive=False)

                        try:
                            host = str(tds[0].table.tr.td.table.tr.td.a.string)
                            #print host
                            status = str(tds[1].string)
                            #print host + " " + status
                            #check if host matches any group regex

                            icons = tds[0].findAll('img')

                            for i in icons:
                                icon = i["src"].split("/")[-1]
                                if icon in STATUS_MAPPING:
                                    status = STATUS_MAPPING[icon] # Discard if ICON present
        
                            for group in groups:
                                name = group['name']
                                regex_pat = group['regex_pat']
                                #print name + " " + regex_pat
                                match_status = re.search(regex_pat,host)
                                if match_status is not None:
                                    #print host + " " + name + " " + regex_pat
                                    if  group.has_key('hoststatus'):
                                        #print "Old array"
                                        try:
                                            num = group['hoststatus'][status]
                                        except:
                                            group['hoststatus'][status] = 0
                                            num = group['hoststatus'][status]

                                        group['hoststatus'][status] = num +1
                                        #print num + " " + groups_info[name]['host'+status]
                                        #print host + " " + name + " " + regex_pat + " " + str(num) + " " str(group['hoststatus'][status])
                                    else:
                                        #print "New array"
                                        group['hoststatus'] = {}
                                        group['hoststatus'][status] = 0
                                        num = group['hoststatus'][status]
                                        group['hoststatus'][status] = num +1

                                    del icons

                                    except:
                                        #print "No Host"
                                        ass
                                except:
                                    pass


                                    #print m_name + "Completed"
                                except:
                                                #print m_name + "Not Completed"
                                    pass

                #for group in groups:
                #             print group
                                del table_content
                                del trs
                                del tds
                                del raw_soup


#             return groups


def service_mon_url(monitors, groups):
                #for group in groups:
                #             print group['name'] + " " + group['regex_pat']


                for monitor in monitors:
                                m_url = monitor['url']
                                m_name = monitor['name']
                                m_username = monitor['username']
                                m_password = monitor['password']

                                http = urllib3.PoolManager()
                                headers = urllib3.util.make_headers(basic_auth= m_username + ":" + m_password)
                                try:
                                                r1 = http.request('GET', m_url + 'status.cgi?host=all&limit=0',headers=headers)
                                                #print r1.status

                                                raw_soup = BeautifulSoup.BeautifulSoup(r1.data)
                                                #print raw_soup

                                                table_content = raw_soup('table',{'class': 'status'})[0]

                                                #print table_content
                                                if len(table_content('tbody')) == 0:
                                                                trs = table_content('tr', recursive=False)
                                                else:
                                                                tbody = table_content('tbody')[0]
                                                                trs = tbody('tr',recursive=False)

                                                trs.pop(0)
                                                tds = []
                                                prevhost = ""
                                                skip = False
                                                for tr in trs:

                                                                try:
                                                                                skip = False
                                                                                tds = tr('td',recursive=False)
                                                                                #print str(tds[0].tr.td.table.tr.td.a.string)
                                                                                #print str(tds[1].tr.td.a.string)
                                                                                #print str(tds[2].string)
                                                                                #print tds[0]
                                                                                #break

                                                                                if len(tds) > 1:
                                                                                                try:
                                                                                                                host = str(tds[0].tr.td.table.tr.td.a.string)
                                                                                                                #print host
                                                                                                except:
                                                                                                                host = prevhost
                                                                                                                pass

                                                                                                                #print host
                                                                                                service = str(tds[1].tr.td.a.string)
                                                                                                status = str(tds[2].string)


                                                                                                #print host + " " + service + " " + status + " " + prevhost
                                                                                                icons = tds[0].findAll('img')

                                                                                                for i in icons:
                                                                                                                icon = i["src"].split("/")[-1]
                                                                                                                if icon in STATUS_MAPPING:
                                                                                                                                status = STATUS_MAPPING[icon] # discard old status incase ICON is present



                                                                                                for group in groups:
                                                                                                                name = group['name']
                                                                                                                regex_pat = group['regex_pat']
                                                                                                                #print name + " " + regex_pat
                                                                                                                match_status = re.search(regex_pat,host)
                                                                                                                if match_status is not None:
                                                                                                                                #print host + " " + name + " " + regex_pat
                                                                                                                                if  group.has_key('servicestatus'):
                                                                                                                                                #print "Old array"
                                                                                                                                                try:
                                                                                                                                                                num = group['servicestatus'][status]
                                                                                                                                                except:
                                                                                                                                                                group['servicestatus'][status] = 0
                                                                                                                                                                num = group['servicestatus'][status]

                                                                                                                                                group['servicestatus'][status] = num +1
                                                                                                                                                #print num + " " + groups_info[name]['host'+status]
                                                                                                                                else:
                                                                                                                                                #print "New array"
                                                                                                                                                group['servicestatus'] = {}
                                                                                                                                                group['servicestatus'][status] = 0
                                                                                                                                                num = group['servicestatus'][status]
                                                                                                                                                group['servicestatus'][status] = num +1


                                                                                prevhost = host

                                                                except:
                                                                                print "Some thing wrong in tr loop"
                                                                                pass


                                except:
                                                pass


                                del table_content
                                del trs
                                del tds
                                del raw_soup

#             return groups


def my_main_thread():
                # first time population
                global groups_data
                global groups_data_show
                groups_data_show = ["In my Main thread"]
                f_monitor = open("groups.yaml","r")
                groups_data = yaml.load(f_monitor)
                f_monitor.close()

                groups_data_show = {"Assigning Group Data"}
                groups_data_show = [""]

                groups_data_show = list(groups_data)

                while True:
                                print str(datetime.datetime.now()) + " my my_main_thread routine start"
                                sys.stdout.flush()
                                f_monitor = open("monitor.yaml","r")
                                monitor_data = yaml.load(f_monitor)
                                f_monitor.close()

                                f_monitor = open("groups.yaml","r")
                                groups_data = yaml.load(f_monitor)
                                f_monitor.close()

                                print str(datetime.datetime.now()) + " Reload Configs"
                                sys.stdout.flush()

                                #monitor_data now has all info about all monitors
                                #groups_info = {}

                                print str(datetime.datetime.now()) + " Getting Host data"
                                sys.stdout.flush()
                                #groups_data = host_mon_url(monitor_data,groups_data)
                                host_mon_url(monitor_data, groups_data)
                                print str(datetime.datetime.now()) + " Host Data Gather Completed"
                                sys.stdout.flush()
                                #for group in groups_data:
                                #             print group
                                #             sys.stdout.flush()
                                groups_data_show[:]
                                groups_data_show = list(groups_data)

                                print str(datetime.datetime.now()) + " Getting Service data"
                                sys.stdout.flush()
                                #groups_data = service_mon_url(monitor_data,groups_data)
                                service_mon_url(monitor_data,groups_data)
                                print str(datetime.datetime.now()) + " Service data Completed"
                                sys.stdout.flush()
                                #service_mon_url(monitor_data)
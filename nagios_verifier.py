import urllib3
import BeautifulSoup
import yaml
import pyaml
import re
import sys
import datetime

STATUS_MAPPING = { "ack.gif" : "acknowledged",\
                       "passiveonly.gif" : "passiveonly",\
                       "disabled.gif" : "passiveonly",\
                       "ndisabled.gif" : "notifications_disabled",\
                       "downtime.gif" : "scheduled_downtime",\
                       "flapping.gif" : "flapping"}

def service_check_mon_url(monitors, services):
	
	# Getting all details monitor by monitor 
	for monitor in monitors:
		# Nagios URL
		m_url = monitor['url']
		# Nagios Name
		m_name = monitor['name']
		# Nagios Username
		m_username = monitor['username']
		# Nagios Password
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
			remaining_services = []
			
			for tr in trs:

				try:
					
					tds = tr('td',recursive=False)
					
					if len(tds) > 1:
						# Lets get host from HTML or use the Host if the HTNL grab fails
						try:
							host = str(tds[0].tr.td.table.tr.td.a.string)
							#print host
						except:
							host = prevhost
							pass

						# Lets get Service Name	
						service = str(tds[1].tr.td.a.string)
						# Lets get Service Status ( We actually dont need this)
						status = str(tds[2].string)


						#print host + " " + service + " " + status + " " + prevhost

						# Lets get icons (detailed map above) again we dont need it
						icons = tds[0].findAll('img')

						for i in icons:
							icon = i["src"].split("/")[-1]
							if icon in STATUS_MAPPING:
								status = STATUS_MAPPING[icon] # discard old status incase ICON is present


						# Now looping through all service check hosts and checking if host regex pattern matches
						for service_ch in services:
							# Host Type Name 
							name = service_ch['name']
							# Host Regex
							regex_pat = service_ch['regex_pat']
							# Host-Service List
							svc_list = service_ch['servicelist']
							#print name + " " + regex_pat
							match_status = re.search(regex_pat,host)
							#check if host pattern matches
							if match_status is not None:
								#if here than host pattern has matched
								#Lets check if the prevhost is same as current host
								if prevhost == host:
								#     If yes then pull current service out of remaining list
									try:
										rem = remaining_services.index(service)
										print "for " + host + " " + service + " is present in Configs"
										del remaining_services[rem]
										del rem
								#       If current service not in remaining give a warning that additional service check present for this host
									except:
										print "WARN for " + host + " in " + m_name + " : " + service + "is not present in Configs"
								#     else 
								else:
									if not remaining_services:
										#print "the remaining list is empty then good"
										print "\n"
										#looks good
									else:
										#else if the remaining list is not empty then put a message that for prevehost remainglist is missing
										print "Following Service not present for host " + prevhost + " on Nagios " + m_name
										#print "Current Host is " + host 
										for sc in remaining_services:
											print sc
											remaining_services.remove(sc)

										#print "Removed all Items from Prev remaining_services list and assigned new servicelist"
									# This is a bad hack for new host handling and first service that we get (no loop thru once again)
									#		 In the end extract the list from service check group and assign a new remaining list 
									remaining_services = list(svc_list)

									try:
										rem = remaining_services.index(service)
										print "for " + host + " " + service + " is present in Configs"
										del remaining_services[rem]
										del rem
								#       If current service not in remaining give a warning that additional service check present for this host
									except:
										print "WARN for " + host + " in " + m_name + " : " + service + "is not present in Configs"
							#else:
								#if here than host pattern does not match
								#check for next service group or maybe the host does not belong to any group
					prevhost = host

				except:
					print "Some thing wrong in tr loop"
					pass


		except:
			print "Some really Weird Error. Maybe due to the connection to the monitor server"
			sys.exit(1)


		del table_content
		del trs
		del tds
		del raw_soup

#	return groups

if __name__ == '__main__':

	# Lets get all Service Checks from yaml
	f_monitor = open("servicecheck.yaml","r")
	servicecheck_data = yaml.load(f_monitor)
	f_monitor.close()


	# Lets get all monitor (Nagios) details
	f_monitor = open("monitor.yaml","r")
	monitor_data = yaml.load(f_monitor)
	f_monitor.close()

	print "::Nagios Service check Verification Report::"
	# Fire!!!
	service_check_mon_url(monitor_data,servicecheck_data)
	print "::Done::"
These are nagios based projects.

1. Nagios Aggregator : This aggregrates OK CRITICAL and WARNING counts from all monitors specifed 
in yaml file as per Groups specified in groups.yaml file and presents then via a webpage supported
by Flask. A javascript can be written on the webpage which can show the data as a flow chart 
indicating which groups have the most impacted alerts 

2. Nagios Verifier : This is the extension of above project where the monitors are specified in 
monitors.yaml and a service template check is specified in a service template file. The script 
collects data from nagios server and validates if the alerts set on nagios are similar to template
files are not.


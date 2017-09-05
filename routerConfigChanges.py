# module imports
import sys
from netmiko import ConnectHandler


# ensure that the correct amounts of arguments are passed when the script is called
if len(sys.argv) != 4:
    sys.exit("Usage: ./routerUpdate.py <textfile> <username> <password> .  Please used 'DMVPNRouterIPAddressesPrimary.txt' to run against primary routers and 'DMVPNRouterIPAddressesSecondary.txt' to run against secondary ")

	
# pass script arguments into an array to be referenced later
cliArguments = sys.argv


# variable assignments from arguments passed at the CLI
textFile = cliArguments[1]
username = cliArguments[2]
password = cliArguments[3]
	
	
# open the file for reading
try:
	ipAddressesFile = open(textFile)
except IOError:
	sys.exit("The filename that you entered does not exist in the current working directory. Please ensure it is present, and that it was entered as the first argument passed to the script.")
	
	
# depending on the filename that is passed to the script when called, set the appropriate tunnel interface and IKE profile for primary/secondary
if textFile == "DMVPNRouterIPAddressesPrimary.txt":
	tunnelValue = "interface tunnel100"
	ikev2Value = "FVRF-IKEv2-IWAN-MPLS"

if textFile == "DMVPNRouterIPAddressesSecondary.txt":
	tunnelValue = "interface tunnel200"
	ikev2Value = "FVRF-IKEv2-IWAN-MPLS2"
	
	
# build commands that will be applied to the router via the SSH handlers
MTUCommand = [tunnelValue,'ip mtu 1400','ip tcp adjust-mss 1360','tunnel path-mtu-discovery']
DPDCommand = ['crypto ikev2 profile '+ ikev2Value,'dpd 30 2 on-demand']
HostnameCommand = 'show run | i hostname'
BootCommand = 'boot system flash:c2900-universalk9-mz.SPA.154-3.M7.bin'
ImageCommand = "sh flash: | i c2900-universalk9-mz.SPA.154-3.M7.bin"
SNMPCommand = ['ip access-list standard snmphosts','remark SNMP Allowed access list','permit 10.51.0.254','permit 10.51.1.0 0.0.0.255','permit 10.49.0.0 0.0.255.255']
	

# iterate through the lines in the text file that contains all the router IP addresses
for line in ipAddressesFile:
	# if the line begins with a '#' then it is a comment, and we don't want to process it, otherwise go ahead
	if not line.startswith("#"):
		# remove the carriage return from the line by splitting it and just taking the first array element
		ipAddress = line.splitlines()
		ipAddress = ipAddress[0]
		
		# create device
		currentRouter = {
			'device_type': 'cisco_ios', 
			'ip': ipAddress, 
			'username': username, 
			'password': password
		}
		
		# build an SSH connection to the device
		sshConnection = ConnectHandler(**currentRouter)
		
		# get the router hostname
		routerHostname = sshConnection.send_command(HostnameCommand)
		
		# edit the return string to include only interesting data
		# hostname string returns in the format:
		# hostname <hostname>
		# split string into an array on a whitespace delimeter and use the second argument in the array
		routerHostname = routerHostname.split(' ')
		routerHostname = routerHostname[1]
		print ("*** WORKING ON ROUTER: " + routerHostname + " ***")
		
		# change the tunnel MTU parameters
		output = sshConnection.send_config_set(MTUCommand)
		print output
		print ("*** MTU CONFIGURATION APPLIED ***")
		
		# change the tunnel crypto profile DPD parameters
		output = sshConnection.send_config_set(DPDCommand)
		print output
		print ("*** DPD CONFIGURATION APPLIED ***")	
		
		# add the new SNMP ACL
		output = sshConnection.send_config_set(SNMPCommand)
		print output
		print ("*** SNMP CONFIGURATION APPLIED ***")		
			
		# build the command required to identify if the IOS image is already present on the router, taking the
		# image name that was passed as an argument when the script was invoked.  This string is then passed
		# to the router and executed.
		imagePresent = sshConnection.send_command(ImageCommand)
		
		# check that the image is present in the router flash
		if imagePresent == "":
			# if image isn't present, leave the boot parameter intact
			print ("*** IMAGE NOT PRESENT IN FLASH, BOOT PARAMETERS NOT CHANGED ***")
		else:
			# if the image is present, update boot parameters
			output = sshConnection.send_config_set(BootCommand)
			print output
			print ("*** BOOT PARAMETERS CHANGED ***")
			
		# save the config and reload the router
		output = sshConnection.send_command_expect('write mem')
		output += sshConnection.send_command_timing('reload')
		if 'System configuration has been modified' in output:
			output = sshConnection.send_config_timing('yes') 
		elif 'Proceed with reload? [confirm]' in output:
			output = sshConnection.send_command_timing('')
		
		print ("*** CONFIGURATION SAVED AND RELOAD ISSUED *** \n\n\n\n")
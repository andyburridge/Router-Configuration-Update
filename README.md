# Router Configuration Update

## Description 
Using Netmiko, SSH to a list of routers taken from a given text file and perform an series of configuration changes.

Python 2.7


## Prerequisites

Netmiko, Paramiko


## Usage

Usage: ./routerUpdate.py <textfile> <username> <password> .  Please used 'DMVPNRouterIPAddressesPrimary.txt' to run against primary routers and 'DMVPNRouterIPAddressesSecondary.txt' to run against secondary
where:
- <textfile> a list of router IP addresses to connect to.  Any lines that start with a '#' are igorned as comments.	
- <username> the username used for authentication to the devices
- <password> the password used for authentication to the devices	


## Author

Andrew Burridge

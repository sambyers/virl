# Simple PnP Demo
In this demo we're using an APIC-EM VM off of the Flat L2 network in VIRL and the Network Plug 'n Play feature.
## Steps
- Provision an APIC-EM VM and attach it to the Flat L2 network in VIRL (10.1.1.10/24)
- Make sure APIC-EM can also be managed via some other network
- Start simulation in VIRL
- Use this config snippet to simulate either someone boot strapping the router with the PnP app or the cloud PnP service:
- - ```
	conf t
	int gi0/1
	no shut
	ip add dhcp
	!
	pnp profile pnp-zero-touch 
	transport http ipv4 10.1.1.10 port 80
	end
- Bootstrap the hub first and claim it with the hub.txt configuration
- Do the same for spoke2, spoke3, and spoke4
- You'll probably need to add routes in APIC-EM to reach the spokes, as usually DHCP would give the spoke routers IP addresses that would be routable from the controller
- - ```
	ip route add 10.1.2.0/24 via 10.1.1.1
	ip route add 10.1.3.0/24 via 10.1.1.1
	ip route add 10.1.4.0/24 via 10.1.1.1
## Files used
- pnp.virl
- hub.txt
- spoke_template.txt

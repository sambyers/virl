# Simple PnP Demo
In this demo we're using an APIC-EM VM off of the Flat L2 network in VIRL and the Network Plug 'n Play feature.
## Steps
- Provision an APIC-EM VM and attach it to the Flat L2 network in VIRL
- Make sure APIC-EM can also be managed via some other network
- Start simulation in VIRL
- Use this config snippet to simulate either someone boot strapping the route with the PnP app or the cloud PnP service:
- - `conf t
		int gi0/1
		no shut
		ip add dhcp
		!
		pnp profile pnp-zero-touch 
		transport http ipv4 10.1.1.10 port 80 
	end`
## Files used
- pnp.virl
- hub.txt
- spoke_template.txt

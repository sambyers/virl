#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""net_dev_test_example Console Script.
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Sam Byers"
__email__ = "sabyers@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import re
import logging
from ats import aetest
from ats.log.utils import banner

#
# create a logger for this testscript
#
logger = logging.getLogger(__name__)

#
# Common Setup Section
#

class common_setup(aetest.CommonSetup):
    '''Common Setup Section

    Defines subsections that performs configuration common to the entire script.

    '''

    @aetest.subsection
    def check_topology(self, testbed):
        '''
        check that we have at least two devices and a link between the devices
        If so, mark the next subsection for looping.
        '''

        # abort/fail the testscript if no testbed was provided
        if not testbed or not testbed.devices:
            self.failed('No testbed was provided to script launch', goto = ['exit'])

        router1 = testbed.devices['router1']
        router2 = testbed.devices['router2']
        router3 = testbed.devices['router3']
        router4 = testbed.devices['router4']
        router5 = testbed.devices['router5']
        router6 = testbed.devices['router6']

        routers = (router1, router2, router3, router4, router5, router6)

        # abort/fail the testscript if no matching device was provided
        for ios_name in routers:
            if ios_name not in testbed:
                self.failed('testbed needs to contain device {ios_name}'.format
                            (ios_name=ios_name,), goto=['exit'])

        # add them to testscript parameters
        self.parent.parameters.update(router1 = router1, router2 = router2,
                                        router3 = router3, router4 = router4,
                                        router5 = router5, router6 = router6,
                                        routers = routers)

        # get corresponding ips
        ipv4s = []
        for dev in testbed:
            for intf in dev:
                if 'cisco' not in str(intf.link):
                    ipv4s.append(str(intf.ipv4.ip))

        assert len(ipv4s) >= 1, 'quick check of ips'

        # save ips as uut link parameter
        self.parent.parameters['uut_ips'] = ipv4s


    @aetest.subsection
    def establish_connections(self, steps, routers):
        '''
        establish connection to both devices
        '''

        for rtr in routers:
            with steps.start('Connecting to {}'.format(rtr)):
                rtr.connect()

        # abort/fail the testscript if any device isn't connected
        for rtr in routers:
            if not rtr.connected:
                self.failed('One of the devices could not be connected to',
                            goto = ['exit'])

    @aetest.subsection
    def marking_interface_count_testcases(self, testbed):
        '''
        mark the VerifyInterfaceCountTestcase for looping.
        '''
        # ignore VIRL lxc's
        devices = [d for d in testbed.devices.keys() if 'mgmt' not in d]

        logger.info(banner('Looping VerifyInterfaceCountTestcase'
                           ' for {}'.format(devices)))

        # dynamic loop marking on testcase
        aetest.loop.mark(VerifyInterfaceCountTestcase, device = devices)


#
# Ping Testcase: leverage dual-level looping
#
@aetest.loop(device = ('router1','router2','router3','router4','router5','router6'))
class PingTestcase(aetest.Testcase):
    '''Ping test'''

    groups = ('basic', 'looping')

    @aetest.setup
    def setup(self, uut_ips):
        destination = uut_ips
        print(destination)
        # apply loop to next section
        aetest.loop.mark(self.ping, destination = destination)


    @aetest.test
    def ping(self, device, destination):
        '''
        ping destination ip address from device

        Sample of ping command result:

        ping
        Protocol [ip]:
        Target IP address: 10.10.10.2
        Repeat count [5]:
        Datagram size [100]:
        Timeout in seconds [2]:
        Extended commands [n]: n
        Sweep range of sizes [n]: n
        Type escape sequence to abort.
        Sending 5, 100-byte ICMP Echos to 10.10.10.2, timeout is 2 seconds:
        !!!!!
        Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms

        '''

        try:
            # store command result for later usage
            result = self.parameters[device].ping(destination)

        except Exception as e:
            # abort/fail the testscript if ping command returns any exception
            # such as connection timeout or command failure
            self.failed('Ping {} from device {} failed with error: {}'.format(
                                destination,
                                device,
                                str(e),
                            ),
                        goto = ['exit'])
        else:
            # extract success rate from ping result with regular expression
            match = re.search(r'Success rate is (?P<rate>\d+) percent', result)
            success_rate = match.group('rate')
            # log the success rate
            logger.info(banner('Ping {} with success rate of {}%'.format(
                                        destination,
                                        success_rate,
                                    )
                               )
                        )

#
# Verify Interface Count Testcase
#
class VerifyInterfaceCountTestcase(aetest.Testcase):
    '''Verify interface count test'''

    groups = ('basic', 'looping')

    @aetest.test
    def extract_interface_count(self, device):
        '''
        extract interface counts from `show version`

        Sample of show version command result:

        show version
        Cisco IOS XE Software, Version 16.09.01
        Cisco IOS Software [Fuji], Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.9.1, RELEASE SOFTWARE (fc2)
        Technical Support: http://www.cisco.com/techsupport
        Copyright (c) 1986-2018 by Cisco Systems, Inc.
        Compiled Tue 17-Jul-18 16:57 by mcpre


        Cisco IOS-XE software, Copyright (c) 2005-2018 by cisco Systems, Inc.
        All rights reserved.  Certain components of Cisco IOS-XE software are
        licensed under the GNU General Public License ("GPL") Version 2.0.  The
        software code licensed under GPL Version 2.0 is free software that comes
        with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
        GPL code under the terms of GPL Version 2.0.  For more details, see the
        documentation or "License Notice" file accompanying the IOS-XE software,
        or the applicable URL provided on the flyer accompanying the IOS-XE
        software.


        ROM: IOS-XE ROMMON

        router6 uptime is 1 hour, 32 minutes
        Uptime for this control processor is 1 hour, 34 minutes
        System returned to ROM by reload
        System image file is "bootflash:packages.conf"
        Last reload reason: Reload Command



        This product contains cryptographic features and is subject to United
        States and local country laws governing import, export, transfer and
        use. Delivery of Cisco cryptographic products does not imply
        third-party authority to import, export, distribute or use encryption.
        Importers, exporters, distributors and users are responsible for
        compliance with U.S. and local country laws. By using this product you
        agree to comply with applicable laws and regulations. If you are unable
        to comply with U.S. and local laws, return this product immediately.

        A summary of U.S. laws governing Cisco cryptographic products may be found at:
        http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

        If you require further assistance please contact us by sending email to
        export@cisco.com.

        License Level: ax
        License Type: Default. No valid license found.
        Next reload license Level: ax

        cisco CSR1000V (VXE) processor (revision VXE) with 1217428K/3075K bytes of memory.
        Processor board ID 9IOUX800GMO
        2 Gigabit Ethernet interfaces
        32768K bytes of non-volatile configuration memory.
        3018864K bytes of physical memory.
        7774207K bytes of virtual hard disk at bootflash:.
        0K bytes of WebUI ODM Files at webui:.

        Configuration register is 0x2102

        '''

        try:
            # store execution result for later usage
            result = self.parameters[device].execute('show version')

        except Exception as e:
            # abort/fail the testscript if show version command returns any
            # exception such as connection timeout or command failure
            self.failed('Device {} \'show version\' failed: {}'.format(device,
                                                                       str(e)),
                        goto = ['exit'])
        else:
            # extract interfaces counts from `show version`
            match = re.search(r'(?P<ethernet>\d+) Gigabit Ethernet interfaces\r\n', result)
            ethernet_intf_count = int(match.group('ethernet'))
            # log the interface counts
            logger.info(banner('\'show version\' returns {} ethernet interfaces'
                                            .format(
                                            ethernet_intf_count

                                        )
                               )
                        )
            # add them to testcase parameters
            self.parameters.update(ethernet_intf_count = ethernet_intf_count,
                                   serial_intf_count = 0)

    @aetest.test
    def verify_interface_count(self,
                               device,
                               ethernet_intf_count = 0,
                               serial_intf_count = 0):
        '''
        verify interface counts with `show ip interface brief`

        Sample of show ip interface brief command result:

        show ip interface brief
        Interface              IP-Address      OK? Method Status                Protocol
        GigabitEthernet1       10.255.0.45     YES TFTP   up                    up
        GigabitEthernet2       10.0.0.22       YES TFTP   up                    up
        GigabitEthernet3       10.0.0.25       YES TFTP   up                    up
        GigabitEthernet4       10.0.0.14       YES TFTP   up                    up
        Loopback0              192.168.0.5     YES TFTP   up                    up
        '''

        try:
            # store execution result for later usage
            result = self.parameters[device].execute('show ip interface brief')

        except Exception as e:
            # abort/fail the testscript if show ip interface brief command
            # returns any exception such as connection timeout or command
            # failure
            self.failed('Device {} \'show ip interface brief\' failed: '
                            '{}'.format(device, str(e)),
                        goto = ['exit'])
        else:
            # extract ethernet interfaces
            ethernet_interfaces = re.finditer(r'GigabitEthernet\d', result)
            # total number of ethernet interface
            len_ethernet_interfaces = len(tuple(ethernet_interfaces))

            # log the ethernet interface counts
            logger.info(banner('\'show ip interface brief\' returns {} ethernet'
                               ' interfaces'.format(len_ethernet_interfaces)))

            # compare the ethernet interface count between
            # `show ip interface brief` and `show version`
            assert len_ethernet_interfaces == ethernet_intf_count



class common_cleanup(aetest.CommonCleanup):
    '''disconnect from ios routers'''

    @aetest.subsection
    def disconnect(self, steps, routers):
        '''disconnect from both devices'''

        for rtr in routers:
            with steps.start('Disconnecting from {}'.format(rtr)):
                rtr.disconnect()
        for rtr in routers:
            if rtr.connected:
                # abort/fail the testscript if device connection still exists
                self.failed('One of the devices could not be disconnected from',
                            goto = ['exit'])


if __name__ == '__main__':

    # local imports
    import argparse
    from ats.topology import loader

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed',
                        type = loader.load)
    # parse args
    args, unknown = parser.parse_known_args()

    # and pass all arguments to aetest.main() as kwargs
    aetest.main(**vars(args))

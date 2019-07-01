Eagle200 Reader
===============

Gather data locally from a Rainforest Eagle-200 device.

Eagle200 Rader provides the ability to retrieve data from a Rainforest 
Eagle-200 device from the local network, rather than from the cloud.  Three
arguments are needed to connect to the device; IP Address, Cloud ID (aka Username),
and Install Code (aka Password).

Typical usage often looks like this::

    #!/usr/bin/env python

    import eagle200_reader

    IP_ADDR = 1.1.1.1
    CLOUD_ID = '0012ef'
    INSTALL_CODE = '4234343242343242'

    device = eagle200_reader.EagleReader(IP_ADDR, CLOUD_ID, INSTALL_CODE)

    print("Instantanous Demand:     {} kW".format(device.instantanous_demand()))
    print("Total Energy Delivered:  {} kWh".format(device.summation_delivered()))
    print("Total Energy Received:   {} kWh".format(device.summation_received()))
    print("Total Net Energy:        {} kWh".format(device.summation_total()))

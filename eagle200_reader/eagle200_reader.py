import requests
import sys, traceback
import xml.etree.ElementTree as ET

HTTP_DEVICE_LIST = """
    <Command>
      <Name>device_list</Name>
    </Command>
"""

class EagleReader:

    def __init__(self, ip_addr, cloud_id, install_code):
        self.ip_addr = ip_addr
        self.cloud_id = cloud_id
        self.install_code = install_code
        
    def call_api(self):
        devices = self.get_device_address()
        if len(devices) == 1:
            http_device_query = self.build_xml_device_query(devices[0])
            response = requests.post("http://" + self.ip_addr + 
                "/cgi-bin/post_manager", http_device_query, auth=(self.cloud_id, self.install_code))
        elif len(devices) > 1 and len(devices) != 0:
            print("Currently only the API only supports a single device")
        else:
            print("Device list is empty!")            
        return self.create_attributes(response)

    def get_device_address(self):
        devices = []
        response = requests.post("http://" + self.ip_addr + 
            "/cgi-bin/post_manager", HTTP_DEVICE_LIST, auth=(self.cloud_id, self.install_code))
        tree = ET.fromstring(response.content)
        for node in tree.iter('HardwareAddress'):
            devices.append(node.text)
        return devices

    def build_xml_device_query(self, hardware_address):
        http_device_query = """
            <Command>
              <Name>device_query</Name>
              <DeviceDetails>
                <HardwareAddress>""" + hardware_address + """</HardwareAddress>
              </DeviceDetails>
              <Components>
                <All>Y</All>
              </Components>
            </Command>
        """
        return http_device_query

    def create_attributes(self, xml_output):
        i = 0
        attribs = []
        tree = ET.fromstring(xml_output.content)
        for node in tree.iter('Variable'):
            attribs.append([])
            for child in node:
                attribs[i].append({child.tag : child.text})
            i = i + 1
        return attribs

    def get_value(self, attribs, value_name):
        for child in attribs:
            if child[0]['Name'] == value_name:
                return child[1]['Value']
    
    def instantanous_demand(self):
        try:
            device_attributes = EagleReader.call_api(self)
            instantanous_demand = self.get_value(device_attributes, 'zigbee:InstantaneousDemand')
            return float(instantanous_demand)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            
    def get_summation_delivered(self):
        try:
            device_attributes = EagleReader.call_api(self)
            instantanous_demand = self.get_value(device_attributes, 'zigbee:CurrentSummationDelivered')
            return float(instantanous_demand)
        except Exception:
            traceback.print_exc(file=sys.stdout)

    
    def get_summation_received(self):
        try:
            device_attributes = EagleReader.call_api(self)
            instantanous_demand = self.get_value(device_attributes, 'zigbee:CurrentSummationReceived')
            return float(instantanous_demand)
        except Exception:
            traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    testreader = EagleReader(sys.argv[1], sys.argv[2], sys.argv[3])
    print("Instantanous Demand:     {} kW".format(testreader.instantanous_demand()))
    print("Total Energy Delivered:  {} kWh".format(testreader.get_summation_delivered()))
    print("Total Energy Received:   {} kWh".format(testreader.get_summation_received()))

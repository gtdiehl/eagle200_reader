import requests
import sys
import xml.etree.ElementTree as ET

HTTP_DEVICE_LIST = """
    <Command>
      <Name>device_list</Name>
    </Command>
"""

'''
TODO:
    - Add logging messages for better debugging
'''

class EagleReader:

    def __init__(self, ip_addr, cloud_id, install_code):
        self.ip_addr = ip_addr
        self.cloud_id = cloud_id
        self.install_code = install_code
        
        self.instantanous_demand_value = 0.0
        self.summation_delivered_value = 0.0
        self.summation_received_value = 0.0
        self.summation_total_value = 0.0
        
        self._call_api()
        
    '''
    Entry point from public functions
    '''    
    def _call_api(self):
        '''
        Get the hardware address of the Power Meter.  This address is required
        to build the XML Post request.
        '''
        devices = self._get_device_address()
        
        '''
        Currently only one Power Meter and no other devices associated with
        the Eagle-200 is supported.  Check if the length of the list is 1, > 1,
        or none.
        
        An empty devices list can occur if a timeout occurs while making the 
        HTTP Post request to get the hardware address.
        '''
        if len(devices) == 1:
            http_device_query = self._build_xml_device_query(devices[0])
            try:
                response = requests.post("http://" + self.ip_addr + 
                    "/cgi-bin/post_manager", http_device_query, auth=(self.cloud_id, self.install_code), timeout=2)
                '''
                This exception occurs after if a resonse from the request is not received
                in 2 seconds. And returns None
                '''
            except requests.exceptions.Timeout as e:
                return None
                '''
                This exception occurs if a new connection cannot be made to the
                Eagle-200. And returns None
                '''
            except requests.exceptions.ConnectionError as e:
                return None
                '''
                Returns None for all other Request Exceptions
                '''
            except requests.exceptions.RequestException as e:
                return None
                '''
                If no exceptions occur, process the response and create a dictionary
                of all variable names and values
                '''
            else:
                self._instantanous_demand(self._create_attributes(response))
                self._summation_delivered(self._create_attributes(response))
                self._summation_received(self._create_attributes(response))
                self._summation_total(self._create_attributes(response))
                
        elif len(devices) > 1 and len(devices) != 0:
            print("Currently only the API only supports a single device")
            return None
        else:
            print("Device list is empty!")
            return None
        
    '''
    This function gets the hardware address of the Power Meter than it associated
    to the Eagle-200 device.
    
    TODO: 
        - Update function to handle multiple Power Meters
        - Update function to handle other types of devices
          that can be associated to the Eagle-200; ie: Thermostat or SmartPlug
    '''
    def _get_device_address(self):
        devices = []
        try:
            response = requests.post("http://" + self.ip_addr + 
                "/cgi-bin/post_manager", HTTP_DEVICE_LIST, auth=(self.cloud_id, self.install_code), timeout=2)
            '''
            This exception occurs after if a resonse from the request is not received
            in 2 seconds. And return an empty devices list
            '''
        except requests.exceptions.Timeout as e:
            return devices
            '''
            This exception occurs if a new connection cannot be made to the
            Eagle-200. And return an empty devices list
            '''
        except requests.exceptions.ConnectionError as e:
            return devices
            '''
            Returns an empty devices list for all other Request Exceptions
            '''
        except requests.exceptions.RequestException as e:
            return devices
            '''
            Process the XML if no exceptions occur
            '''
        else:
            tree = ET.fromstring(response.content)
            for node in tree.iter('HardwareAddress'):
                devices.append(node.text)
            return devices

    def _build_xml_device_query(self, hardware_address):
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

    '''
    Builds a dictionary of all the Variable names and values of the Attributes
    that are returned from the Power Meter that is associated to the Eagle-200
    
    TODO:
        - Need to handle the case when building the dictionary fails
    '''
    def _create_attributes(self, xml_output):
        i = 0
        attribs = []
        tree = ET.fromstring(xml_output.content)
        for node in tree.iter('Variable'):
            attribs.append([])
            for child in node:
                attribs[i].append({child.tag : child.text})
            i = i + 1
        return attribs

    '''
    Searches the dictionary created by the create_attributes() function for a
    specific Variable name and returns its value.
    
    TODO:
        - Need to handle the case when a value is not found in the dictionary
    '''
    def _get_value(self, attribs, value_name):
        for child in attribs:
            if child[0]['Name'] == value_name:
                return child[1]['Value']
    
    def instantanous_demand(self):
        if self.instantanous_demand_value is not None:
            return float(self.instantanous_demand_value)
        else:
            return None
    
    def _instantanous_demand(self, device_attributes):
        try:
            if device_attributes is None:
                return None
            instantanous_demand = self._get_value(device_attributes, 'zigbee:InstantaneousDemand')
            # Eagle-200 has a bug, sometimes the Value for Instantanous Demand will be blank.  When this
            # occurs a value of None will be returned
            if instantanous_demand is not None:
                self.instantanous_demand_value = instantanous_demand
            else:
                self.instantanous_demand_value = None
        except Exception as e:
            print(e)

    def summation_delivered(self):
        if self.summation_delivered_value is not None:
            return float(self.summation_delivered_value)
        else:
            return None
            
    def _summation_delivered(self, device_attributes):
        try:
            if device_attributes is None:
                return None
            summation_delivered = self._get_value(device_attributes, 'zigbee:CurrentSummationDelivered')
            # Eagle-200 has a bug, sometimes the Value for Summation Delivered will have the incorrect
            # decimal place.  If six zeros to the right of the decimal point are found than it'll assume
            # the value is incorrect and return None
            if summation_delivered[summation_delivered.find('.')+1:] != "000000":
                self.summation_delivered_value = summation_delivered
            else:
                self.summation_delivered_value = None
        except Exception as e:
            print(e)

    def summation_received(self):
        if self.summation_received_value is not None:
            return float(self.summation_received_value)
        else:
            return None
        
    def _summation_received(self, device_attributes):
        try:
            if device_attributes is None:
                return None
            summation_received = self._get_value(device_attributes, 'zigbee:CurrentSummationReceived')
            # Eagle-200 has a bug, sometimes the Value for Summation Received will have the incorrect
            # decimal place.  If six zeros to the right of the decimal point are found than it'll assume
            # the value is incorrect and return None
            if summation_received[summation_received.find('.')+1:] != "000000":
                self.summation_received_value = summation_received
            else:
                self.summation_received_value = None
        except Exception as e:
            print(e)
            
    def summation_total(self):
        if self.summation_total_value is not None:
            return float(self.summation_total_value)
        else:
            return None
    
    def _summation_total(self, device_attributes):
        
        if self.summation_delivered_value is not None and self.summation_received_value is not None:
            self.summation_total_value = (float(self.summation_delivered_value) - float(self.summation_received_value))
        else:
            self.summation_total_value = None

    def update(self):
        data = {}
        self._call_api()
        
        data['instantanous_demand'] = self.instantanous_demand_value
        data['summation_delivered'] = self.summation_delivered_value
        data['summation_received'] = self.summation_received_value
        data['summation_total'] = self.summation_total_value
        
        return data
        

if __name__ == "__main__":
    testreader = EagleReader(sys.argv[1], sys.argv[2], sys.argv[3])
    print("Instantanous Demand:     {} kW".format(testreader.instantanous_demand()))
    print("Total Energy Delivered:  {} kWh".format(testreader.summation_delivered()))
    print("Total Energy Received:   {} kWh".format(testreader.summation_received()))
    print("Total Net Energy:        {} kWh".format(testreader.summation_total()))

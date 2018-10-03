import subprocess
import glob
import os
from xml.dom.minidom import parse
import xml.dom.minidom
import re
import zipfile
from shutil import copyfile
from os.path import basename


dir_path = os.path.dirname(os.path.realpath(__file__))

def openhw(hdf):
	base = os.path.basename(hdf)
	base = os.path.splitext(base)[0]
	base_dir = dir_path+"\\"+base
	copyfile(hdf, 'ultra96_wrapper.zip')
	zip_ref = zipfile.ZipFile('ultra96_wrapper.zip', 'r')
	if not os.path.exists(base_dir):
		os.makedirs(base_dir)
	zip_ref.extractall(base_dir)
	zip_ref.close()
	os.remove('ultra96_wrapper.zip')
	createlog(base)

#there are permission error here	
def closehw():
	if os.path.exists('openhw.log'):
		os.remove('openhw.log')
	
def createlog(base):
	try:
		if not os.path.isfile('openhw.log'):
			f= open("openhw.log","w+")
			f.write(base)
			f.close() 
	except OSError:
		print("Error: Creating log "+ directory)

def current_hw_design():
	try:
		if os.path.isfile('openhw.log'):
			f = open("openhw.log","r")
			base = f.readlines(1)
			f.close()
			return (base[0])
	except OSError:
		return -1	
		
def get_cells(*args):
	params = []
	values = []
	cells = []
	if not os.path.isfile('openhw.log'):
			print("Error: No HW design Open")
			print("Please run openhw <path to hdf>")
			return 0
	for pl_cell in get_pl_ip():
		cells.append(pl_cell)
	if ps_ddr_enabled() != 0:
		cells.append(ps_ddr_enabled())
	for ps_cell in get_ps_ip():
			cells.append(ps_cell)
	
	if len(args) < 1:
		return (cells)
	if args[0] == "*":
		return (cells)
	else:
		for cell in cells:
			cell_name = re.findall(r'' + re.escape(args[0]) + '', cell)
			if len(cell_name) == 1:
				return (cell_name[0])
		return 0
		
def get_ddr_addr_info(cell):
	ddr_info = []
	if cell == get_cells(cell):
		if cell == "psu_ddr_0" or cell == "ps_ddr_0":
			params = []
			values = []
			cells = []
			base = current_hw_design()
			base_dir = dir_path+"\\"+base
			hwh = glob.glob(base_dir+'\*.hwh') 
			DOMTree = xml.dom.minidom.parse(hwh[0])
			collection = DOMTree.documentElement
			modules =  collection.getElementsByTagName("MODULE")
			for module in modules:
				name = module.getAttribute("FULLNAME")
				name=os.path.basename(name)
				if get_device_info("ARCH") == "zynquplus":
					processor = re.findall(r'zynq_ultra_ps_e', name)
				elif get_device_info("ARCH") == "zynq":
					processor = re.findall(r'zynq_ps_e', name)
				else:
					return 0
				if len(processor) == 1:
					psu_params = module.getElementsByTagName("PARAMETER")
					for psu_param in psu_params:
						param_name = psu_param.getAttribute("NAME")
						param_value = psu_param.getAttribute("VALUE")
						highaddr = re.findall(r'PSU_DDR_RAM_HIGHADDR', param_name) 
						lowaddr = re.findall(r'PSU_DDR_RAM_LOWADDR', param_name) 
						if len(highaddr) == 1 or len(lowaddr) == 1:
							ddr_info.append(param_value)
		if len(ddr_info) == 0:
			return 0
		else:
			return ddr_info
	else:
		print("cell not found")
		return 0

def get_psu_pl_clks():
	ps_pl_clks = []
	ps_pl_clks_nm = []
	ps_pl_clks_en = []
	ps_pl_clks_hz = []
	params = []
	values = []
	cells = []
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh') 
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	modules =  collection.getElementsByTagName("MODULE")
	for module in modules:
		name = module.getAttribute("FULLNAME")
		name=os.path.basename(name)
		if get_device_info("ARCH") == "zynquplus":
			processor = re.findall(r'zynq_ultra_ps_e', name)
		else:
			return 0
		if len(processor) == 1:
			psu_params = module.getElementsByTagName("PARAMETER")
			for psu_param in psu_params:
				param_name = psu_param.getAttribute("NAME")
				param_value = psu_param.getAttribute("VALUE")
				fclk0 = re.findall(r'PSU__FPGA_PL0_ENABLE', param_name) 
				fclk0_hz = re.findall(r'PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ', param_name) 
				if len(fclk0) == 1:
					ps_pl_clks_nm.append("fclk0")
					ps_pl_clks_en.append(param_value)
				if len(fclk0_hz) == 1:
					ps_pl_clks_hz.append(param_value)
				fclk1 = re.findall(r'PSU__FPGA_PL1_ENABLE', param_name)
				fclk1_hz = re.findall(r'PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ', param_name)
				if len(fclk1) == 1:
					ps_pl_clks_nm.append("fclk1")
					ps_pl_clks_en.append(param_value)
				if len(fclk1_hz) == 1:
					ps_pl_clks_hz.append(param_value)
				fclk2 = re.findall(r'PSU__FPGA_PL2_ENABLE', param_name)
				fclk2_hz = re.findall(r'PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ', param_name)
				if len(fclk2) == 1:
					ps_pl_clks_nm.append("fclk2")
					ps_pl_clks_en.append(param_value)
				if len(fclk2_hz) == 1:
					ps_pl_clks_hz.append(param_value)
				fclk3 = re.findall(r'PSU__FPGA_PL3_ENABLE', param_name)
				fclk3_hz = re.findall(r'PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ', param_name)				
				if len(fclk3) == 1:
					ps_pl_clks_nm.append("fclk3")
					ps_pl_clks_en.append(param_value)
				if len(fclk3_hz) == 1:
					ps_pl_clks_hz.append(param_value)

	if len(ps_pl_clks_nm) == 0:
		return 0
	else:
		for i in range(0,len(ps_pl_clks_nm)):
				ps_pl_clks.append(ps_pl_clks_nm[i])
				ps_pl_clks.append(ps_pl_clks_en[i])
				ps_pl_clks.append(ps_pl_clks_hz[i])	
		return ps_pl_clks
		
def get_pl_ip():
	params = []
	values = []
	cells = []
	pl_cells = []
	if not os.path.isfile('openhw.log'):
			print("Error: No HW design Open")
			print("Please run openhw <path to hdf>")
			return 0
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh') 
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	modules =  collection.getElementsByTagName("MODULE")
	for module in modules:
		name = module.getAttribute("FULLNAME")
		name=os.path.basename(name)
		zynqu_ps = re.findall(r'zynq_ultra_ps_e', name)
		zynq_ps = re.findall(r'zynq_ps_e', name)
		if len(zynqu_ps) != 1 and len(zynq_ps) != 1:
			cells.append(name)
	return(cells)

def ps_ddr_enabled() :
	params = []
	values = []
	cells = []
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh') 
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	modules =  collection.getElementsByTagName("MODULE")
	for module in modules:
		name = module.getAttribute("FULLNAME")
		name=os.path.basename(name)
		if get_device_info("ARCH") == "zynquplus":
			processor = re.findall(r'zynq_ultra_ps_e', name)
		elif get_device_info("ARCH") == "zynq":
			processor = re.findall(r'zynq_ps_e', name)
		else:
			return 0
		if len(processor) == 1:
			psu_params = module.getElementsByTagName("PARAMETER")
			for psu_param in psu_params:
				param_name = psu_param.getAttribute("NAME")
				param_value = psu_param.getAttribute("VALUE")
				params.append(param_name)
				values.append(param_value)
	for i in range(len(params)):
		psu_enabled = re.findall(r'PSU__DDRC__ENABLE', params[i])
		ps_enabled = re.findall(r'PS__DDRC__ENABLE', params[i])
		if len(psu_enabled) == 1 and values[i] == '1':
			return("psu_ddr_0")
		if len(ps_enabled) == 1 and values[i] == '1':
			return("ps_ddr_0")
	return 0
		
#This will only report the properties for PL IP
def report_property(cell):
	target_properties = []
	target_params = []
	if (is_cell_pl(cell)) == 0:
		print("Error " + cell + " not found in PL")
		print("This script will only report on PL IP")
		return 0
		
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh')  
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	modules =  collection.getElementsByTagName("MODULE")
	for module in modules:
		name = module.getAttribute("FULLNAME")
		name=os.path.basename(name)
		if name == cell:
				for cell_attribute in module.attributes.values():
					target_properties.append(cell_attribute.name + " " + cell_attribute.value)
				parameters =  module.getElementsByTagName("PARAMETERS")
				for parameter in parameters:
						for parameter in parameter.getElementsByTagName('PARAMETER'):
							temp_param = ""
							for param_attribute in parameter.attributes.values():
								temp_param = temp_param + param_attribute.value + " "
								target_params.append(temp_param)
	for target_param in target_params:
			target_properties.append(target_param.rstrip())
	return(target_properties)


#only works on PL IP	
def get_pins(*args):
	port_names = []
	found = 0
	cell = args[0]
	add_filter = 0
	type = []
	type_value = []
	for x in range(0, len(args)):
		filter = re.findall(r'-filter', args[x])
		if len(filter) == 1:
			add_filter = 1
			temp_filter = args[x].split(" ")
			for y in range(1, len(temp_filter)):
				filter = temp_filter[y].split("==")
				type.append(filter[0])
				type_value.append(filter[1])
	
	if (is_cell_pl(cell)) == 0:
		print("Error " + cell + " not found in PL")
		print("This script will only report on PL IP")
		return 0	
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh')  
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	modules =  collection.getElementsByTagName("MODULE")
	for module in modules:
		name = module.getAttribute("FULLNAME")
		name=os.path.basename(name)
		if name == cell:
				ports =  module.getElementsByTagName("PORTS")
				for port in ports:
						for port in port.getElementsByTagName('PORT'):
							name = ""
							for port_attribute in port.attributes.values():
								if (port_attribute.name) == "NAME":
									name = port_attribute.value
							for i in range(0, len(type)):
								for port_attribute in port.attributes.values():
									if add_filter == 1:
										if (port_attribute.name) == type[i].strip() and (port_attribute.value) == type_value[i].strip():
											found = found + 1	
									else:
										if len(name) != 0:
											port_names.append(name)	
							if found == len(type):
								port_names.append(name)
								found = 0								
	return(port_names)

def get_device_info(*args):
	device_info = []
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh')  
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	props =  collection.getElementsByTagName("SYSTEMINFO")
	for prop in props:
		for prop_attribute in prop.attributes.values():	
			if len(args) > 0 and args[0] == prop_attribute.name:
				return prop_attribute.value
			else :
				device_info.append(prop_attribute.name+" "+prop_attribute.value)
	return device_info			


def get_ps_ip(*args):
	params = []
	values = []
	cells = []
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh') 
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	modules =  collection.getElementsByTagName("MODULE")
	for module in modules:
		name = module.getAttribute("FULLNAME")
		name=os.path.basename(name)
		if get_device_info("ARCH") == "zynquplus":
			processor = re.findall(r'zynq_ultra_ps_e', name)
		elif get_device_info("ARCH") == "zynq":
			processor = re.findall(r'zynq_ps_e', name)
		else:
			return 0
		if len(processor) == 1:
			psu_params = module.getElementsByTagName("PARAMETER")
			for psu_param in psu_params:
				param_name = psu_param.getAttribute("NAME")
				param_value = psu_param.getAttribute("VALUE")
				params.append(param_name)
				values.append(param_value)
	for i in range(len(params)):
		psu_enabled = re.findall(r'PERIPHERAL__ENABLE', params[i])
		if len(psu_enabled) == 1 and values[i] == '1':
			temp = params[i].split("__")
			new_param = temp[0]+"_"+temp[1]
			cells.append(new_param.lower())
	if get_device_info("ARCH") == "zynquplus":
		cells.append("psu_cortexa53_0")
		cells.append("psu_cortexa53_1")	
		cells.append("psu_cortexa53_2")	
		cells.append("psu_cortexa53_3")	
		cells.append("psu_cortexr5_0")	
		cells.append("psu_cortexr5_1")
		cells.append("psu_pmu_0")
	else:
		cells.append("psu_cortexa9_0")
		cells.append("psu_cortexa9_1")	

	return cells
	
#get the source pin of a pin	
def get_sink_pin(*args):
	cell = args[0]
	pin = args[1]
	return_pin = []
	
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh')  
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	modules =  collection.getElementsByTagName("MODULE")
	for module in modules:
		name = module.getAttribute("FULLNAME")
		name=os.path.basename(name)
		if name == cell:
				ports =  module.getElementsByTagName("PORTS")
				for port in ports:
						for port in port.getElementsByTagName('PORT'):
							name = ""
							for port_attribute in port.attributes.values():
								if (port_attribute.name) == "NAME":
									name = port_attribute.value
									if name == pin:
										connections =  port.getElementsByTagName("CONNECTIONS")
										for connection in connections:
											for connection in connection.getElementsByTagName('CONNECTION'):
												for connection_attribute in connection.attributes.values():
													if (connection_attribute.name) == "INSTANCE":
														return_pin.append(connection_attribute.value)
													if (connection_attribute.name) == "PORT":
														return_pin.append(connection_attribute.value)
	if len(return_pin) != 0:
		return return_pin
	else:
		return 0

def is_cell_pl(cell):
	if (get_cells(cell, "pl_ip")) == 0:
		return 0
	else:
		return 1

def get_ext_pins(*args):
	found = 0
	add_filter = 0
	type = []
	type_value = []
	ext_pins = []
	for x in range(0, len(args)):
		filter = re.findall(r'-filter', args[x])
		if len(filter) == 1:
			add_filter = 1
			temp_filter = args[x].split(" ")
			for y in range(1, len(temp_filter)):
				filter = temp_filter[y].split("==")
				type.append(filter[0])
				type_value.append(filter[1])

	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh')  
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	external_pins =  collection.getElementsByTagName("EXTERNALPORTS")
	for external_pin in external_pins:
		for port in external_pin.getElementsByTagName('PORT'):
			name = ""
			for port_attribute in port.attributes.values():
				if (port_attribute.name) == "NAME":
					name = port_attribute.value
			for i in range(0, len(type)):
				for port_attribute in port.attributes.values():	
					if add_filter == 1:
						if (port_attribute.name) == type[i].strip() and (port_attribute.value) == type_value[i].strip():
							found = found + 1	
					else:
						ext_pins.append(name)										
					if found == len(type):
						ext_pins.append(name)
						found = 0
			if len(type) == 0:
				ext_pins.append(name)
				
	if len(ext_pins) != 0:
		return ext_pins
	else:
		return 0
		
def get_memorymap ():
	memory_map = []
	base = current_hw_design()
	base_dir = dir_path+"\\"+base
	hwh = glob.glob(base_dir+'\*.hwh')  
	DOMTree = xml.dom.minidom.parse(hwh[0])
	collection = DOMTree.documentElement
	memories =  collection.getElementsByTagName("MEMORYMAP")
	for memory in memories:
		for memrange in memory.getElementsByTagName('MEMRANGE'):
			for mem_attribute in memrange.attributes.values():
				if (mem_attribute.name) == "BASEVALUE":
					memory_map.append(mem_attribute.value)
				if (mem_attribute.name) == "HIGHVALUE":
					memory_map.append(mem_attribute.value)

	if len(memory_map) != 0:
		return memory_map
	else:
		return 0

#User needs to provide the cell, and the property. This will actually check that the property exists on the cell.
#returns 0 on error, returns value on success
def get_property(*args):
	target_properties = (report_property(args[0]))
	if target_properties != 0:
		for target_property in target_properties:
			temp = target_property.split(" ")
			print(args[1])
			print(temp[0])
			print(temp[1])
			print(len(temp))
			if args[1] == temp[0]:
				print("found")
				return(temp[1])
		#print("Property Value " + args[1] + " is not a valid property in " + args[0])
		#print("Use the command report_property('" + args[0] + "') to get the properties for this cell")
	return 0

exec(open("utilities.py").read())
openhw("design_1_wrapper.hdf")
#print(is_cell_pl("psu_cortexa53_0"))
#print(get_cells("*"))
#print(report_property("axi_uart16550_0"))
#print(get_pins("axi_uart16550_0", "-filter SIGIS==clk DIR==I"))
#print(get_sink_pin("axi_uart16550_0", "s_axi_aclk"))
#print(get_memorymap())
#print(get_ext_pins("-filter SIGIS==undef DIR==I"))
#print(get_property("axi_uart16550_0", "RUSER_BITS_PER_BYTE"))
#print(get_device_info("DEVICE"))
print(get_psu_pl_clks())
closehw()
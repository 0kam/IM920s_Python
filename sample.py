from IM920s import IM920s

# 同一PC（Linux）上に2台のIM920sを接続しているとする
devices = IM920s.search_devices()
im1 = IM920s(devices[0], 19200)
im2 = IM920s(devices[1], 19200)

im1.read_all_settings()
im2.read_all_settings()

im1.reset_settings()
im2.reset_settings()
im1.reset_system()
im2.reset_system()

im1.read_id()
im2.read_id()

im1.set_node_num('0001')
im2.set_node_num('0002')

im1.set_group_num()
im2.set_group_num()

im1.read_group_num()
im2.read_group_num()

im1.send_all('hoge')
data, sender,rssi = im2.read_message()
print(data)

im2.send('0001', 'fuga')
data, sender,rssi = im1.read_message()
print(data)
import serial

class IM920s:
    def __init__(self, port:str = '/dev/ttyUSB0', baudrate:int = 19200) -> None:
        self.port = port
        self.baudrate = baudrate
        self.com = self.set_serial()
        r = self.enable_writing()
        print('Enable writing... {}'.format(r))
        r = self.set_io_mode('str')
        print('Setting string I/O mode... {}'.format(r))
        self.group_num = self.read_group_num()
        self.node_num = self.read_node_num()
        self.id = self.read_id()
        self.set_ack(True)
        print('Group number: {}'.format(self.group_num))
        print('Node number:  {}'.format(self.node_num))
        print('ID:           {}'.format(self.id))
    
    def set_serial(self) -> serial.Serial:
        com = serial.Serial(
            port     = self.port,
            baudrate = self.baudrate,
            bytesize = serial.EIGHTBITS,
            parity   = serial.PARITY_NONE,
            timeout  = 1,
            xonxoff  = False,
            rtscts   = False,
            writeTimeout = None,
            dsrdtr       = False,
            interCharTimeout = None
        )
        # Clear buffer
        com.flushInput()
        com.flushOutput()
        return com
    
    def write(self, cmd:str) -> str:
        self.com.flushInput()
        self.com.write('{}'.format(cmd).encode() + b'\r\n')
        self.com.flushOutput()
        out = self.com.readline().decode().strip()
        return out
    
    def enable_writing(self) -> str:
        r = self.write('ENWR')
        return r
    
    def set_node_num(self, num:str) -> str:
        r = self.write('STNN ' + num)
        self.node_num = self.read_node_num()
        return r
    
    def read_node_num(self) -> str:
        r = self.write('RDNN')
        return r

    def set_group_num(self) -> str:
        '''
        親機（ノードナンバーが0001）なら、自分の製造番号(read_id()で確認可能)をセットし、周囲のIM920sに通知する。
        子機なら親機の信号を受信して親機と同じグループナンバーをセットする。
        子機の場合、受信できたら GRNOREGD という出力が出るので待つ。
        グループ番号設定動作中は誤登録防止のため、自動的に通信距離が短くなる。
        登録する全ての子機を親機から50cm 以内に置く。
        '''
        r = self.write('STGN')
        if self.node_num != '0001':
            while r != 'GRNOREGD':
                r = self.com.readline().decode().strip()
            print(r)
        r = 'OK'
        self.group_num = self.read_group_num()
        return r
    
    def read_group_num(self) -> str:
        r = self.write('RDGN')
        return r
    
    def read_id(self) -> str:
        r = self.write('RDID')
        return r

    def reset_system(self) -> str:
        r = self.write('SRST')
        r = self.enable_writing()
        return r

    def reset_settings(self) -> str:
        r = self.write('PCLR')
        self.node_num = self.read_node_num()
        self.group_num = self.read_group_num()
        r = self.enable_writing()
        return r
    
    def set_io_mode(self, mode:str='str') -> str:
        '''
        入出力モードの切り替え。mode='str'なら文字(ASCII)で、mode='hex'なら16進数でやり取りする。
        '''
        if mode == 'str':
            r = self.write('ECIO')
        elif mode == 'hex':
            r = self.write('DCIO')
        else:
            raise ValueError('Unknown mode. Use either "str" or "hex".')
        return r

    def send_all(self, string:str) -> str:
        r = self.write('TXDA ' + string)
        return r
    
    def send(self, node_num:str, string:str) -> str:
        r = self.write('TXDU ' + node_num + "," + string)
        return r
    
    def read_message(self) -> tuple:
        r = self.com.readline().decode().strip()
        if len(r) == 0:
            return '', '', 0
        else:
            _, sender, r = r.split(",")
            rssi, string = r.split(":")
            rssi = int(rssi, 16)
            return string, sender, rssi
        
    def read_all_settings(self) -> list:
        self.com.flushInput()
        self.com.write('{}'.format("RPRM").encode() + b'\r\n')
        self.com.flushOutput()
        outs = self.com.readlines()
        outs = [o.decode().strip() for o in outs] 
        return outs
    
    def set_network_mode(self, mode:str) -> str:
        if mode == 'simple':
            mode = '1'
        elif mode == 'tree':
            mode = '2'
        elif mode == 'mesh':
            mode = '3'
        else:
            raise ValueError('Unknown mode. Use "simple", "tree", or "mesh" instead.')
        r = self.write('STNM ' + mode)
    
    def read_network_mode(self) -> str:
        mode = self.write('RDNM')
        if mode == '1':
            mode = 'simple'
        elif mode == '2':
            mode = 'tree'
        elif mode == '3':
            mode = 'mesh'
        else:
            raise ValueError("Failed reading!")
        return mode
    
    def set_ack(self, ack:bool):
        '''
        ACKの設定。Trueの場合、ユニキャスト送信時に送信先ノードからの応答を確認するようになる。
        このとき、通信に失敗した場合は最大10回まで自動で再送信する。
        '''
        if ack:
            self.write('ENAK')
        else:
            self.write('DSAK')
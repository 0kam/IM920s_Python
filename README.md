# IM920s_Python
A Python script for manupulating  Interplan's IM920s LPWA module

## 目的
インタープラン社のLPWAモジュール[IM920s](https://www.interplan.co.jp/solution/wireless/im920s/im920s.php)をPythonで操作するためのスクリプト。  
実験環境では、[オフィシャルのUSBインターフェースボード](https://www.interplan.co.jp/solution/wireless/others/im315usb.php)を用いて
接続先のPCとUSBで接続した。

## 注意
IM920sは非常に多機能であるため、すべての機能を網羅できていない。  
全機能については[取扱説明書](https://www.interplan.co.jp/support/solution/wireless/im920s/manual/IM920s_SW_manual.pdf)を
参照すること。

## 使い方


###  接続先のポートとボーレート（デフォルトだと19200）を設定し、インスタンスを作る。
```python
from IM920s import IM920s
im1 = IM920s('/dev/ttyUSB0', 19200)
im2 = IM920s('/dev/ttyUSB1', 19200)
```

###  全部の設定を読む。
```python
im1.read_all_settings()
im2.read_all_settings()
```

### 設定を初期状態に戻し、システムリセットをかける。(任意、設定がすべて消えるので注意！)
```python
im1.reset_settings()
im2.reset_settings()
im1.reset_system()
im2.reset_system()
```

### 製造番号を読む
```python
im1.read_id()
im2.read_id()
```

### ノード番号を設定する。
ノード番号はネットワーク内のIM920sを見分けるための番号。  
'0001'を設定すると親機になる。必ずどれか一台のノード番号を'0001'にすること。  
以下、ノード番号やグループ番号、各種設定は不揮発性メモリに保存されるため、リセットした際も消えない。  

```python
im1.set_node_num('0001')
im2.set_node_num('0002')
```

### 次に、グループ番号を設定する。
グループ番号が同じ端末の間でしか通信はできない。  
親機では、自分の製造番号をグループ番号に設定し、周囲にそれを伝える信号を出し続ける。  
子機では、親機の信号を受信して、親機と同じグループ番号を自分につける。このとき、子機と親機は50 cm以内にいなければならない。  
現状、なぜか子機のグループ番号を設定すると**子機がフリーズ**してしまう。電源を抜き差しして強制的にリセットすれば回復し、
設定されたグループ番号も保存されている。

```python
im1.set_group_num()
im2.set_group_num()
```

グループ番号は親機の製造番号と同じになっているはず。
```python
im1.read_group_num()
im2.read_group_num()
```

### データの送受信
`send_all()`を使うと、同じネットワークの全端末にデータを送信できる。  
受信したデータの確認は、`read_message()`で行う。  
以下の例では親機から送信しているが、子機から送信しても大丈夫。  
`read_message()`は  
- データ
- 送り主のノード番号
- 電波の強度（RSSI）  

を返す。

```python
im1.send_all('hoge')
data, sender,rssi = im2.read_message()
print(data)
```

`send()`を使うと、ノード番号で指定された特定の端末にデータを送ることができる。
```python
im2.send('0001', 'fuga')
data, sender,rssi = im2.read_message()
print(data)
```
デフォルトではACK（送信先からの応答）確認機能がオンになっているため、送信先に届かなかった場合は最大10回までリトライする。  
それでも届かなかった場合はsend()は'NG'を返す。届いた場合は'OK'を返す。
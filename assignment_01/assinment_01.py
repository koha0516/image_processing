import math

# 読み込むファイル名を指定
input_file_name = input('画像を指定してください:')

# 出力先ファイル名を指定
output_file_prefix = input_file_name. replace('.ppm', '') + '_'
output_file_red = output_file_prefix + 'red.pgm'
output_file_green = output_file_prefix + 'green.pgm'
output_file_blue = output_file_prefix + 'blue.pgm'
output_file_avg = output_file_prefix + 'avg.pgm'
output_file_y = output_file_prefix + 'y.pgm'


"""ファイルを読み込む関数"""
def readPpm(input_file_name):
    header_list = list()    # ヘッダー部分を格納するリスト
    rgb_list = list()       # データ部分を格納するリスト
    with open(input_file_name,'rb') as f:
        # ヘッダー部分を1行ずつ読み込む
        for _ in range(4):
            l = f.readline()
            header_list.append(l)

        # 残りのデータ部分を一気に読み込む (bytesオブジェクトとして受け取る)
        data = f.read()     # 0~256(int型)のリストを取得できる

    # 3バイトずつRGBに分けてリストに格納
    for i in range(len(data) // 3):
        r = data[3 * i]
        g = data[3 * i + 1]
        b = data[3 * i + 2]
        rgb_list.append([r, g, b])

    return header_list, rgb_list        # ヘッダーと画像データのリストを返す


"""NTSC方式でグレイスケール変換する関数"""
def toGrayscale(rgb_list):
    ntsc = [[0.299, 0.587, 0.114], [0.596, -0.274, -0.322], [0.212, -0.523, 0.311]]
    gray_list = list()

    # ntsc変換リストとi番目の[r,g,b]の行列積を算出
    for i in range(len(rgb_list)):
        yiq_list = list()
        for j in range(len(ntsc[0])):
            total = 0
            for k in range(len(rgb_list[i])):
                total += ntsc[j][k] * rgb_list[i][k]
            yiq_list.append(math.floor(total))      # 小数点以下を切り捨ててy|i|qを順番に格納
        gray_list.append(yiq_list[0])       # 今回は輝度Yだけを格納する
    return gray_list    # ntsc変換後のリストを返す


"""PGMファイルに出力する関数"""
def writePgm(output_file_name, header_list, data_list):
    with open(output_file_name, 'ab') as f:
        # ヘッダー部分の書き込み
        for h in header_list:
            f.write(h)
        # データ部分の書き込み
        for d in data_list:
            f.write(d.to_bytes())


header_list, rgb_list = readPpm(input_file_name)     # ファイルを読み込む
header_list[0] = b'P5\n'    # 今回はグレイスケールで出力するため形式を修正

# 赤抽出グレイスケール出力
red_list = list()
# 赤成分だけのリストを作成
for i in range(len(rgb_list)):
    red_list.append(rgb_list[i][0])
writePgm(output_file_red, header_list, red_list)

# 緑抽出グレイスケール出力
green_list = list()
# 緑成分だけのリストを作成
for i in range(len(rgb_list)):
    green_list.append(rgb_list[i][1])
writePgm(output_file_green, header_list ,green_list)

# 青抽出グレイスケール出力
blue_list = list()
# 青成分だけのリストを作成
for i in range(len(rgb_list)):
    blue_list.append(rgb_list[i][2])
writePgm(output_file_blue, header_list ,blue_list)

# rgb平均グレイスケール出力
avg_list = list()
# 平均値を算出してリストに格納
for i in range(len(rgb_list)):
    res = math.floor((rgb_list[i][0] + rgb_list[i][1] + rgb_list[i][2]) / 3)
    avg_list.append(res)
writePgm(output_file_avg, header_list ,avg_list)

# 輝度Yグレイスケール出力
y_list = toGrayscale(rgb_list)
writePgm(output_file_y, header_list, y_list)



# 参考
# NumPy配列ndarrayを一次元化（平坦化）するravelとflatten
# https://note.nkmk.me/python-numpy-ravel-flatten/#numpyravel

# Python (バイナリファイル入出力)
# http://www.not-enough.org/abe/manual/api-aa09/fileio2.html

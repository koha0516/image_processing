from copy import deepcopy
import math
import pandas as pd

# 読み込むファイル名を指定
input_file_name = input('画像を指定してください:')


# 出力先ファイル名を指定
output_file_prefix = input_file_name. replace('_noise.pgm', '') + '_'
output_file_fixed = output_file_prefix + 'fixed.pgm'
output_file_average = output_file_prefix + 'average.pgm'
output_file_bayer = output_file_prefix + 'bayer.pgm'
output_file_net = output_file_prefix + 'net.pgm'
output_file_variance = output_file_prefix + 'variance.pgm'


output_file_low_pass = output_file_prefix + 'differential.pgm'
output_file_low_pass = output_file_prefix + 'bayer.pgm'



def readPgm(input_file_name):
    """
    グレイスケール画像を読み込む関数
    :param input_file_name
    """
    header_list = list()  # ヘッダー部分を格納するリスト
    gray_list = list()  # 読み込んだグレイスケール画像のデータを格納するリスト

    with open(input_file_name,'rb') as f:
        # ヘッダー部分を読み込む
        for _ in range(4):
            l = f.readline()
            header_list.append(l)

        data = f.read()     # 残りのデータ部分を読み込む

    # ヘッダーから画像サイズを取得
    width, height = map(int, header_list[2].decode(encoding='utf-8').split())

    # 読み込んだデータを2次元配列に格納する
    for i in range(height):
        gray_list.append(list(map(int, data[i * width : (i+1) * width])))

    return header_list, gray_list    # ヘッダーと画像データのリストを返す


"""PGMファイルに出力する関数"""
def writePgm(output_file_name, header_list, data_list):
    with open(output_file_name, 'ab') as f:
        # ヘッダー部分の書き込み
        for h in header_list:
            f.write(h)
        # データ部分の書き込み
        for d in data_list:
            f.write(d.to_bytes())


"""固定しきい値法"""
def fixed_threshold(pixel):
    result = 0
    if pixel >= 128:
        result = 255
    return result


'しきい値可変'
def threshold(pixel, x):
    result = 0
    if pixel >= x:
        result = 255
    return result


"""bayer"""
def bayer(m):
    m2 = deepcopy(m)
    b_list = [15, 35, 45, 165, 195, 75, 225, 105, 60, 180, 30, 150, 240, 120, 210, 90]
    for i in range(16):
        m2[i] = threshold(m2[i], b_list[i])
    return m2

def net(m):
    n_list = [15, 45, 225, 195, 135, 165, 90, 120, 240, 210, 30, 60, 75, 105, 150, 180]
    for i in range(16):
        m[i] = threshold(m[i], n_list[i])
    return m


"""度数分布表をつくる関数"""
def make_frequency_table(header_list, image_list):
    # 輝度値ごとの画素数（度数）をカウントする
    max_luminance = int(header_list[3])
    luminance_list = [0 for i in range(max_luminance + 1)] 
    for i in range(len(image_list)):
        for j in range(len(image_list[0])):
            luminance_list[int(image_list[i][j])] += 1

    # 度数分布表を作成
    df = pd.DataFrame(luminance_list, columns=['度数'], index=range(max_luminance+1))

    # 度数分布表に累積度数の列を追加
    total = 0
    cumulative_frequency = list()
    for i in range(len(df)):
        total += df.iloc[i,0]
        cumulative_frequency.append(total)
    df['累積度数'] = pd.Series(cumulative_frequency, index=range(max_luminance+1))

    # 度数分布表を表示
    print(df)
    return df

# ================ 処理 ==================
header_list, image_list = readPgm(input_file_name)     # 画像を読み込む
width = len(image_list[0])
height = len(image_list)

fixed_list = list()
average_list = list()
varianse_list = list()
bayer_list = deepcopy(image_list)
net_list = deepcopy(image_list)

avg = sum(sum(image_list, [])) // (width * height)

# 判別分析法のしきい値をもとめる
result = 0
df = make_frequency_table(header_list, image_list)
for t in range(256):
    v1 = 0
    v2 = 0
    sum1 = 0
    sum2 = 0
    for i in range(256):
        if i <= t-1:
            v1 += (df['度数'][i] * math.pow(i - avg, 2))
            sum1 += df['度数'][i]
        else:
            v2 += (df['度数'][i] * math.pow(i - avg, 2))
            sum2 += df['度数'][i]
    # 要素数で割る
    n1 = t+1
    n2 = 255-t

    v1 /= n1
    v2 /= n2

    vw = (n1 * v1 + n2 * v2) // (n1 + n2)

    vb = n1 * math.pow(sum1 / n1 - avg, 2) + n2 * math.pow(sum2 / n2 - avg, 2) // (n1 + n2)

    if vb / vw > result:
        result = t


# 設定したしきい値で二値化する
for i in range(height):
    for j in range(width):
        fixed_list.append(fixed_threshold(image_list[i][j]))
        average_list.append(threshold(image_list[i][j], avg))
        varianse_list.append(threshold(image_list[i][j], result))


# マトリクスを使った二値化
for i in range(0, height, 4):
    for j in range(0, width, 4):
        m = list()
        for k in range(4):
            for l in range(4):
                m.append(image_list[i+k][j+l])
        new_m = bayer(m)
        new_m2 = net(m)
        cnt = 0
        for k in range(4):
            for l in range(4):
                bayer_list[i+k][j+l] = new_m[cnt]
                net_list[i+k][j+l] = new_m2[cnt]
                cnt += 1

writePgm(output_file_fixed, header_list, fixed_list)
writePgm(output_file_average, header_list, average_list)
writePgm(output_file_variance, header_list, varianse_list)
writePgm(output_file_bayer, header_list, sum(bayer_list, []))
writePgm(output_file_net, header_list, sum(net_list, []))







# 判別分析法あとで


# https://ocw.kyoto-u.ac.jp/wp-content/uploads/2021/03/2004_gazoushoriron_05.pdf
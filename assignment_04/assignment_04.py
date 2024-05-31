from copy import deepcopy
import math

# 読み込むファイル名を指定
input_file_name = input('画像を指定してください:')


# 出力先ファイル名を指定
output_file_prefix = input_file_name. replace('_noise.pgm', '') + '_'
output_file_median = output_file_prefix + 'median.pgm'
output_file_laplacian = output_file_prefix + 'laplacian.pgm'
output_file_gaussian = output_file_prefix + 'gaussian.pgm'
output_file_high_pass = output_file_prefix + 'high_pass.pgm'
output_file_low_pass = output_file_prefix + 'low_pass.pgm'



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
        for d in sum(data_list, []):
            f.write(d.to_bytes())


"""メディアンフィルタ"""
def median_filtering(source):
    median = sorted(source)[4]
    return median


"""ラプラシアンフィルタ"""
def laplacian_filtering(source):
    laplacian_filter = [1, 1, 1, 1, -8, 1, 1, 1, 1]
    total = 0

    # 畳み込み
    for i in range(9):
        total += source[i] * laplacian_filter[i]

    res = source[4] - total
    if res < 0:
        res = 0
    elif res > 255:
        res = 255
    return res


"""ガウシアンフィルタ"""
def gaussian_filtering(source):
    gaussian_filter = [0.075, 0.124, 0.075, 0.124, 0.204 ,0.124,0.075, 0.124, 0.075]
    total = 0

    # 畳み込み
    for i in range(9):
        total += source[i] * gaussian_filter[i]
    res = total
    if res < 0:
        res = 0
    elif res > 255:
        res = 255
    return math.floor(res)


# ================ 処理 ==================
header_list, image_list = readPgm(input_file_name)     # 画像を読み込む
width = len(image_list[0])
height = len(image_list)

median_list = deepcopy(image_list)
laplacian_list = deepcopy(image_list)
gaussian_list = deepcopy(image_list)


for i in range(1, height-1):
    for j in range(1, width-1):

        # 元画像の注目画素の周辺を取り出す
        source = list()
        for k in range(-1, 2):
            for l in range(-1, 2):
                source.append(image_list[i + k][j + l])

        # フィルタリング
        median_list[i][j] = median_filtering(source)
        laplacian_list[i][j] = laplacian_filtering(source)
        gaussian_list[i][j] = gaussian_filtering(source)

# PGMを書き出す
writePgm(output_file_median, header_list, median_list)
writePgm(output_file_laplacian, header_list, laplacian_list)
writePgm(output_file_gaussian, header_list, gaussian_list)
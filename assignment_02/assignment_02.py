import math
from decimal import Decimal

# 読み込むファイル名を指定
input_file_name = input('画像を指定してください:')


# 出力先ファイル名を指定
output_file_prefix = input_file_name. replace('.pgm', '') + '_'
output_file_avg = output_file_prefix + 'avg.pgm'
output_file_linear = output_file_prefix + 'linear.pgm'
output_file_rotate = output_file_prefix + 'rotate.pgm'
output_file_scaling = output_file_prefix + 'scaling.pgm'
output_file_rotate2 = output_file_prefix + 'rotate2.pgm'



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
        gray_list.append(data[i * width : (i+1) * width])

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


# ================ 処理 ==================
header_list, gray_list = readPgm(input_file_name)     # 画像を読み込む

"""平均操作法で画像を縮小する関数"""
def average(header_list, gray_list, reduction_ratio):
    width = len(gray_list[0])
    height = len(gray_list)


    avg_list = list()
    for i in range(0, height, reduction_ratio):
        line = list()
        for j in range(0, width, reduction_ratio):
            # 濃度平均を求める(左上、右上、左下、右下)
            result = 0
            for k in range(reduction_ratio):
                for l in range(reduction_ratio):
                    if(i+k > height-1 or j + l > width-1):
                        result += gray_list[i][j]
                    else:
                        result += gray_list[i+k][j+l]

            line.append(result // reduction_ratio**2)
        avg_list.append(line)

    # 画像サイズを指定
    w = len(avg_list[0])
    h = len(avg_list)
    size = f'{w} {h}\n'
    header_list[2] = size.encode()

    return header_list, sum(avg_list, [])

# 平均操作法の関数を呼び出す
h_list, avg_list = average(header_list, gray_list, reduction_ratio=2)
# 画像を書き込む
writePgm(output_file_avg, h_list, avg_list)


"""直線補間法で画像を拡大する関数"""
def linear_interpolation(header_list, gray_list, zoom_ratio):
    width = len(gray_list[0])
    height = len(gray_list)
    # 画像サイズを指定
    w = width*zoom_ratio
    h = height*zoom_ratio
    size = f'{w} {h}\n'
    header_list[2] = size.encode()

    # 処理後のデータを格納する2次元配列を用意
    linear_list = list()
    for i in range(h):
        linear_list.append([0 for _ in range(w)])

    # 直線補間法で算出したデータを格納
    for i in range(height):
        for j in range(width):
            h = i * zoom_ratio
            w = j * zoom_ratio
            linear_list[h][w] = gray_list[i][j] # 左上

            # 右方向の補間
            if j != width - 1:    # 右端ではないとき
                change = (gray_list[i][j + 1] - gray_list[i][j]) // zoom_ratio
            else:   # 右端のとき
                change = (gray_list[i][j - 1] - gray_list[i][j]) // zoom_ratio
            for k in range(1, zoom_ratio):
                linear_list[h][w+k] = gray_list[i][j] + (change * k) if gray_list[i][j] + (change * k) >= 0 else 0

            # 下方向の補間
            if i != height - 1:    # 下端ではないとき
                change = (gray_list[i + 1][j] - gray_list[i][j]) // zoom_ratio
            else:       # 下端のとき
                change = (gray_list[i - 1][j] - gray_list[i][j]) // zoom_ratio
            for k in range(1, zoom_ratio):
                linear_list[h+k][w] = gray_list[i][j] + (change * k) if gray_list[i][j] + (change * k) >= 0 else 0

            # 右下方向の補間
            if i != height - 1 and j != width - 1:    # 右下角ではないとき
                change = (gray_list[i + 1][j + 1] - gray_list[i][j]) // zoom_ratio
            else:       # 右下角のとき
                change = (gray_list[i - 1][j - 1] - gray_list[i][j]) // zoom_ratio
            for k in range(1, zoom_ratio):
                linear_list[h + k][w + k] = gray_list[i][j] + (change * k) if gray_list[i][j] + (change * k) >= 0 else 0

    return header_list, linear_list


"""直線補間法"""
h_list, linear_list = linear_interpolation(header_list, gray_list, zoom_ratio=2)
writePgm(output_file_linear, h_list, sum(linear_list, []))


"""回転して自動でサイズ調整する関数"""
def rotate(header_list, gray_list, angle):
    width = len(gray_list[0])
    height = len(gray_list)
    # 画像サイズを指定
    size = f'{width} {height}\n'
    header_list[2] = size.encode()

    rotate_list = list()
    for i in range(height):
        rotate_list.append([0 for _ in range(width)])

    sin = math.sin(math.radians(angle))
    cos = math.cos(math.radians(angle))

    new_w = width // (sin + cos)
    new_h = height // (sin + cos)


    for i in range(height):
        for j in range(width):
            # 平行移動(逆)
            x = j
            y = i - new_w * sin

            # サイズを元に戻す
            x = x / (new_w / width)
            y = y / (new_h / height)

            # 回転(逆)
            x_0 = math.floor(cos * x - sin * y)
            y_0 = math.floor(sin * x + cos * y)

            if x_0 < 0 or x_0 > width-1 or y_0 < 0 or y_0 > height-1:
                rotate_list[i][j] = 0
            else:
                rotate_list[i][j] = gray_list[y_0][x_0]
    return header_list, sum(rotate_list, [])


"""30度の回転"""
h_list, rotate_list = rotate(header_list, gray_list, angle=30)
writePgm(output_file_rotate, h_list, rotate_list)


"""任意の十数倍に拡大･縮小"""
r = input('倍率を指定してください(少数も可) : ')
fraction = Decimal(r).as_integer_ratio()
h_list, data_list = linear_interpolation(header_list, gray_list, zoom_ratio=fraction[0])
he_list, resize_list = average(h_list, data_list, reduction_ratio=fraction[1])
writePgm(output_file_scaling, he_list, resize_list)


"""任意の角度に回転"""
angle = int(input('角度を指定してください(度数) : '))
h_list, rotate_list = rotate(header_list, gray_list, angle=angle)
writePgm(output_file_rotate2, h_list, rotate_list)
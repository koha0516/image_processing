import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib  # ヒストグラムのラベルを日本語で表示
import math


# 読み込むファイル名を指定
input_file_name = input('画像を指定してください:')

# 出力先ファイル名を指定
output_file_prefix = input_file_name. replace('.pgm', '') + '_'
output_file_smoothed1 = output_file_prefix + 'smoothed1_image.pgm'
output_file_smoothed2 = output_file_prefix + 'smoothed2_image.pgm'

output_file_histogram = output_file_prefix + 'histogram.png'
output_file_histogram_smoothed1 = output_file_prefix + 'histogram_smoothed1.png'
output_file_histogram_smoothed2 = output_file_prefix + 'histogram_smoothed2.png'
output_file_histogram_red = 'histogram_red.png'
output_file_histogram_green = 'histogram_green.png'
output_file_histogram_blue = 'histogram_blue.png'


def readPgm(input_file_name):
    """
    グレイスケール画像を読み込む関数
    """
    header_list = list()  # ヘッダー部分を格納するリスト
    image_list = list()  # 読み込んだグレイスケール画像のデータを格納するリスト

    with open(input_file_name,'rb') as f:
        # ヘッダー部分を読み込む
        for _ in range(4):
            l = f.readline()
            header_list.append(l)

        raw_data = f.read()     # 残りのデータ部分を読み込む
        data = list(map(int, raw_data))


    # ヘッダーから画像サイズを取得
    width, height = map(int, header_list[2].decode(encoding='utf-8').split())

    # 読み込んだデータを2次元配列に格納する
    for i in range(height):
        image_list.append(data[i * width : (i+1) * width])

    return header_list, image_list     # ヘッダーと画像データのリストを返す


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

def make_frequency_table(header_list, image_list):
    """度数分布表をつくる関数"""
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


def draw_histgram(header_list, image_list, output_file_name):
    """ヒストグラムを描画する関数"""
    plt.xlabel('輝度')
    plt.ylabel('度数')
    plt.ylim(0, 2500)
    plt.title('画像の濃度の分布を示すヒストグラム', y=-0.165)
    plt.hist(sum(image_list, []), bins=int(header_list[3]) + 1, color='b')
    plt.savefig(output_file_name)      # ヒストグラムを画像として保存
    plt.close()

header_list, image_list = readPgm(input_file_name)     # 画像を読み込む
df = make_frequency_table(header_list, image_list)      # 度数分布表を作成
draw_histgram(header_list, image_list, output_file_histogram)   #ヒストグラムを作成


def smoothing_1(header_list, image_list):
    """ヒストグラム平滑化その1"""
    smoothed1_list = list()
    smoothing1_translator = list()
    # 濃度の変換用リストを作る
    for i in range(int(header_list[3])+1):
        result = ((df['累積度数'][i] - min(sum(image_list, []))) / (len(image_list[0]) * len(image_list) - min(sum(image_list, [])))) * max(sum(image_list, []))
        smoothing1_translator.append(math.floor(result))
    
    # 平滑化処理後のデータを格納するリスト
    for i in range(len(image_list)):
        smoothed1_list.append([0 for _ in range(len(image_list[0]))])
    # 平滑化処理後のデータを格納    
    for i in range(len(image_list)):
        for j in range(len(image_list[0])):
            smoothed1_list[i][j] = smoothing1_translator[image_list[i][j]]
    return smoothed1_list

# pgmファイルに書き込む
s1_list = smoothing_1(header_list, image_list)
writePgm(output_file_smoothed1, header_list, sum(s1_list, []))
draw_histgram(header_list, s1_list, output_file_histogram_smoothed1)

#======　ここまでが必須課題

"""ヒストグラム平滑化2"""
def smoothing2(header_list, image_list, df):
    smoothed2_list = list()
    smoothing2_translator = list()
    # 目標階調数を決定
    target = len(sum(image_list, [])) // 64
    total_freq = 0
    y = 0
    # 濃度変換用リストを作成
    for i in range(int(header_list[3])+1):
        if abs(target - total_freq) < abs(target - (total_freq + df['度数'][i])):
            total_freq = 0
            y += 1
            if y > 64:
                y = 63

        smoothing2_translator.append([i, y])
        total_freq += df['度数'][i]

    # 平滑化処理後のデータを格納するリスト
    for i in range(len(image_list)):
        smoothed2_list.append([0 for _ in range(len(image_list[0]))])

    # 平滑化処理後のデータを格納する
    for i in range(len(image_list)):
        for j in range(len(image_list[0])):
            smoothed2_list[i][j] = smoothing2_translator[image_list[i][j]][1]

    return smoothed2_list

s2_list = smoothing2(header_list, image_list, df)
header_list[3] = b'63\n'    # 最大濃度を変更
# pgmファイルに書き込む
writePgm(output_file_smoothed2, header_list, sum(s2_list, []))
draw_histgram(header_list, s2_list, output_file_histogram_smoothed2)



"""ppmファイルを読み込む関数"""
def readPpm(input_file_name):
    header_list = list()    # ヘッダー部分を格納するリスト
    r_list = list()
    g_list = list()
    b_list = list()
    red_list = list()
    green_list = list()
    blue_list = list()
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
        r_list.append(int(r))
        g_list.append(int(g))
        b_list.append(int(b))

     # ヘッダーから画像サイズを取得
    width, height = map(int, header_list[2].decode(encoding='utf-8').split())

    # 読み込んだデータを2次元配列に格納する
    for i in range(height):
        red_list.append(r_list[i * width : (i+1) * width])
        green_list.append(g_list[i * width : (i+1) * width])
        blue_list.append(b_list[i * width : (i+1) * width])

    return header_list, red_list, green_list, blue_list     # ヘッダーと画像データのリストを返す

header_list, red_list, green_list, blue_list = readPpm(input('ppm画像を指定してください：'))
# ヒストグラム描画
draw_histgram(header_list, red_list, output_file_histogram_red)
draw_histgram(header_list, green_list, output_file_histogram_green)
draw_histgram(header_list, blue_list, output_file_histogram_blue)

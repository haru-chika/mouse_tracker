import pyautogui
import csv
import time
from datetime import datetime
from pynput import keyboard

# --- ユーザー設定 ---
SAMPLING_RATE = 60  # サンプリングレート (Hz)。この値を変更できます。
TOGGLE_KEY = keyboard.Key.f8  # 記録の開始/停止を切り替えるキー
EXIT_KEY = keyboard.Key.f9    # プログラムを終了して保存するキー
# --------------------

# グローバル変数
is_recording = False
mouse_data = []
keep_running = True

def on_press(key):
    """キーボードのキーが押されたときに呼び出される関数"""
    global is_recording, keep_running

    if key == TOGGLE_KEY:
        is_recording = not is_recording
        if is_recording:
            # 記録開始時のタイムスタンプを基準点として記録
            if not mouse_data:
                start_time = time.time()
                mouse_data.append((start_time, 'START_POINT', ''))
            print("▶ 記録を開始しました。")
        else:
            print("■ 記録を停止しました。")

    if key == EXIT_KEY:
        print("プログラムを終了します...")
        keep_running = False  # メインループを終了させる
        return False  # リスナーを停止する

def get_screen_resolution():
    """画面の解像度を取得して返す"""
    return pyautogui.size()

def save_to_csv(data):
    """データをCSVファイルに保存する"""
    if len(data) <= 1: # 開始点のみ、またはデータなしの場合
        print("記録されたデータがほとんどないため、ファイルは作成されませんでした。")
        return

    # ファイル名を現在の日時で生成
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mouse_log_{timestamp_str}.csv"

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # ヘッダーを書き込む
            writer.writerow(['timestamp', 'x', 'y'])
            # データを書き込む
            writer.writerows(data)
        print(f"データが '{filename}' に保存されました。")
    except IOError as e:
        print(f"ファイルの保存中にエラーが発生しました: {e}")

def main():
    """メイン処理"""
    # 画面解像度を取得して表示
    width, height = get_screen_resolution()
    print(f"画面解像度: {width} x {height}")
    print(f"サンプリングレート: {SAMPLING_RATE} Hz")
    print("-" * 30)
    print(f"[{TOGGLE_KEY}] キーで記録の開始/停止を切り替え")
    print(f"[{EXIT_KEY}] キーでプログラムを終了して保存")
    print("-" * 30)
    print("待機中...")

    # キーボードリスナーを別スレッドで開始
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # サンプリング間隔の計算
    interval = 1.0 / SAMPLING_RATE

    while keep_running:
        if is_recording:
            # 現在の時刻とマウス座標を取得
            current_time = time.time()
            x, y = pyautogui.position()
            
            # データをリストに追加
            mouse_data.append((current_time, x, y))

        # 指定した間隔で待機
        # 処理時間も考慮して、より正確なインターバルを目指す
        # (ただし、高負荷な処理がなければtime.sleep(interval)でも十分です)
        time.sleep(max(0, interval - (time.perf_counter() % interval)))

    # ループが終了したらデータを保存
    save_to_csv(mouse_data)
    listener.join() # リスナースレッドの終了を待つ

if __name__ == '__main__':
    main()
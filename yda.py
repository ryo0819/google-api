import googleapiclient.discovery
import csv
import regex as re


def get_all_comments(api_key: str, video_id: str) -> list:
    """
    指定された動画IDのすべてのコメントを取得する関数。

    Args:
        api_key (str): YouTube Data APIのAPIキー
        video_id (str): コメントを取得したい動画のID

    Returns:
        list: 全てのコメントを格納したリスト
    """

    # YouTube Data APIクライアントを構築
    youtube = googleapiclient.discovery.build(
        "youtube",
        "v3",
        developerKey=api_key
    )

    comments_data = []
    next_page_token = None
    TIMESTAMP_PATTERN = re.compile(r'\b(?:(\d+):)?([0-5]?\d):([0-5]\d)\b')
    # YouTubeのベースURL
    BASE_URL = f"https://www.youtube.com/watch?v={video_id}"

    while True:
        try:
            # コメントスレッドリストAPIを呼び出し
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,  # 1ページあたりの最大取得件数（最大100）
                pageToken=next_page_token
            )
            response = request.execute()

            # レスポンスからコメントを抽出
            for item in response["items"]:
                comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

                # コメントからタイムスタンプを抽出
                match = TIMESTAMP_PATTERN.search(comment_text)
                scene_timestamp = match.group(0) if match else "該当なし"
                link = "該当なし"

                if match:
                    # タイムスタンプを秒数に変換
                    groups = match.groups()
                    hours = int(groups[0]) if groups[0] else 0
                    minutes = int(groups[1])
                    seconds = int(groups[2])
                    total_seconds = hours * 3600 + minutes * 60 + seconds

                    # YouTubeの該当シーンへのリンクを作成
                    link = f"{BASE_URL}&t={total_seconds}s"

                comments_data.append({
                    "comment": comment_text,
                    "scene_timestamp": scene_timestamp,
                    "link": link
                })

            # 次のページトークンを取得
            if "nextPageToken" in response:
                next_page_token = response["nextPageToken"]
            else:
                # nextPageTokenが存在しない場合、最後のページに到達
                break
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            break

    return comments_data


def write_to_csv(data, filename="youtube_comments.csv"):
    """
    コメントデータをCSVファイルに書き出す関数

    Args:
        data (list): コメントと抽出したタイムスタンプを格納した辞書のリスト
        filename (str): 出力するCSVファイル名
    """
    if not data:
        print("出力するデータがありません")
        return

    fieldnames = ["comment", "scene_timestamp", "link"]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            writer.writerow(row)


# --- 使用例 ---
if __name__ == "__main__":
    # 自身のAPIキーと動画IDを設定
    YOUR_API_KEY = ""
    VIDEO_ID = ""

    all_comments_data = get_all_comments(YOUR_API_KEY, VIDEO_ID)

    write_to_csv(all_comments_data, f"comments_in_{VIDEO_ID}.csv")

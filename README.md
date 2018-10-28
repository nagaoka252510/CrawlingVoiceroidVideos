# CrawlingVoiceroidVideos

# 説明
ニコニコ動画 の『スナップショット検索API v2』を利用し、「VOICEROID」を含むタグが登録されている動画を直近12か月分取得し、sqliteに保存する

# Dependency
- Python3.7
- certifi==2018.8.24
- chardet==3.0.4
- idna==2.7
- python-dateutil==2.7.3
- requests==2.19.1
- six==1.11.0
- urllib3==1.23

# Setup
Python3系をインストール後は、必要なライブラリをインストールしてください

```
    $ pip install requests
    $ pip install python-dateutil
```

2018.10.28
dbファイルを保存するディレクトリを環境変数から取得するように変更しました
必要に応じて変更したり、bash_profileに登録してください
```
export ENV_PY_DB_PATH=/var/hogehoge
```

# Usage
基本的にそのまま利用可能です

    $ python crawling_smile_video.py

検索キーワードを変更したい場合は、コードを修正してください

    # crawling_smile_video.py
    get_search_result_count(start_ym.strftime("%Y%m"), "VOICEROID")　# <-第2引数の検索キーワードを変更


# Licence
This software is released under the MIT License, see LICENSE.<br>
MITライセンスを採用しています。詳細はLISENCEを参照ください
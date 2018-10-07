# -*- coding: utf-8 -*-
import json
import urllib.parse as urlparse
import urllib
import requests
import sqlite3
import contextlib
import myutil
import datetime
from dateutil.relativedelta import relativedelta

# ニコニコ動画のコンテンツ検索を行う
NICO_SNAPSHOT_SEARCH_API_END_POINT = "http://api.search.nicovideo.jp/api/v2/snapshot/video/contents/search"
TIME_STRING = "T00:00:00"
DB_PATH = "./nico_video_info.db"
# 指定条件：年月、タグ名

def get_search_result_count(ym, *keywords):
    # 検索期間の設定
    start_date = datetime.datetime(int(ym[:4]), int(ym[4:]), 1)
    end_date = start_date
    end_date += relativedelta(months=1)
    #print(start_date)
    #print(end_date)
    search_keywords = "VOICEROID"
    if len(myutil.convert_tulpe_to_str(keywords)) > 0:
        search_keywords = myutil.convert_tulpe_to_str(keywords)
    search_url = NICO_SNAPSHOT_SEARCH_API_END_POINT
    search_url += "?q=" + urlparse.quote(search_keywords)
    search_url += "&targets=tags"
    search_url += "&_limit=100"
    search_url += "&filters[startTime][gte]=" + start_date.strftime("%Y-%m-%d") + TIME_STRING
    search_url += "&filters[startTime][lt]=" + end_date.strftime("%Y-%m-%d") + TIME_STRING
    search_url += "&_sort=-viewCounter"
    search_url += "&_context=apitest"
    #print(search_url)
    
    # 指定条件でヒットする動画の総件数をAPIから取得する
    # APIは一度に100件しか動画情報を返さないので、総件数からループする回数を確認する
    req = requests.get(search_url)
    req_cnt_json = json.dumps(req.json(), ensure_ascii=False)
    req_cnt_dict = json.loads(req_cnt_json)

    totalCount = 0
    if req_cnt_dict["meta"]["status"] == 200:
        totalCount = int(req_cnt_dict["meta"]["totalCount"])
    else:
        print("get Count Status Error:[0]",str(req_cnt_dict["meta"]["status"]))
    
    print(f"YEAR_MONTH:{ym}, TotalCount:{totalCount}")

    if totalCount == 0:
        return
    
    loopCnt = int(totalCount / 100)
    if totalCount % 100 > 0:
        loopCnt += 1

    # 月ごとにループする回数が決まったら、動画詳細データを取得する
    for i in range(0, loopCnt):
        # 取得する内容は、contentId,title,tags,categoryTags,viewCounter,mylistCounter,commentCounter,startTime,lengthSeconds
        # description,lastCommentTimeはランキングは利用予定もないので取得対象外とする
        search_video_url = search_url
        search_video_url += "&fields=contentId,title,tags,categoryTags,viewCounter,mylistCounter,commentCounter,startTime,lastCommentTime,lengthSeconds"
        search_video_url += "&_offset=" + str(i * 100)

        #print(search_video_url)
        req_video = requests.get(search_video_url)
        req_video_json = json.dumps(req_video.json(), ensure_ascii=False)
        req_video_dict = json.loads(req_video_json)

        insert_json_data(ym, req_video_dict)

# APIは連続で呼び出すと怒られるので少し待ったりするかも

# JSONをディクショナリに変換する
# tagsは10個に分割する

# sqlite3に書き込む
# 「replace into」を利用してupsertを実施
# 書込先テーブルのPKはcontentId
# 履歴は持たない
def insert_json_data(year_month, json_dict):
    with contextlib.closing(sqlite3.connect(DB_PATH)) as con:
        cur = con.cursor()

        create_sql = "create table if not exists NICO_VIDEO_INFO ( \
                      CONTENT_ID text not null \
                    , YEAR_MONTH text not null \
                    , TITLE text not null \
                    , TAG1 text \
                    , TAG2 text \
                    , TAG3 text \
                    , TAG4 text \
                    , TAG5 text \
                    , TAG6 text \
                    , TAG7 text \
                    , TAG8 text \
                    , TAG9 text \
                    , TAG10 text \
                    , TAG11 text \
                    , CATEGORY_TAG text not null \
                    , VIEW_CNT numeric not null \
                    , MYLIST_CNT numeric not null \
                    , COMMENT_CNT numeric not null \
                    , START_DATE text not null \
                    , LENGTH_SEC numeric \
                    , LAST_COMMENT_TIME text \
                    , CREATE_DATE text not null \
                    , constraint SERCH_NICO_VIDEO_PKC primary key (CONTENT_ID) \
                    ) ;"

        cur.execute(create_sql)

        ins_sql = "REPLACE \
                    INTO NICO_VIDEO_INFO( \
                      CONTENT_ID \
                    , YEAR_MONTH \
                    , TITLE \
                    , TAG1 \
                    , TAG2 \
                    , TAG3 \
                    , TAG4 \
                    , TAG5 \
                    , TAG6 \
                    , TAG7 \
                    , TAG8 \
                    , TAG9 \
                    , TAG10 \
                    , TAG11 \
                    , CATEGORY_TAG \
                    , VIEW_CNT \
                    , MYLIST_CNT \
                    , COMMENT_CNT \
                    , START_DATE \
                    , LENGTH_SEC \
                    , LAST_COMMENT_TIME \
                    , CREATE_DATE \
                    ) VALUES ( \
                    ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , ? \
                    , datetime('now', 'localtime') \
                    ) "

        for data in json_dict["data"]:
            # contentId,title,description,tags,categoryTags,
            # viewCounter,mylistCounter,commentCounter,
            # startTime,lastCommentTime,lengthSeconds
            contentid = str(data["contentId"])
            title = str(data["title"])
            tags = str(data["tags"])
            tag_list = tags.split(" ") + ["", "", "", "", "", "", "", "", "", "", ""]
            cat_tag = str(data["categoryTags"])
            viewCnt = str(data["viewCounter"])
            myListCnt = str(data["mylistCounter"])
            commentCnt = str(data["commentCounter"])
            startTime = str(data["startTime"])
            lastCmtTime = str(data["lastCommentTime"])
            lenSec = str(data["lengthSeconds"])

            params = [contentid, year_month, title]
            params += tag_list[:11]
            params += [cat_tag, viewCnt, myListCnt, commentCnt, startTime, lenSec, lastCmtTime]
            #print(params)
            #print(tag_list[:11])

            cur.execute(ins_sql, params)

        con.commit()


if __name__ == "__main__":
    start_ym = datetime.datetime.now()
    start_ym -= relativedelta(years=1)
    
    for i in range(0,13):
        #print(start_ym.strftime("%Y%m"))
        start_ym += relativedelta(months=1)
        get_search_result_count(start_ym.strftime("%Y%m"), "VOICEROID")

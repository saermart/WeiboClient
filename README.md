# WeiBoClient

> 声明：此仓库代码只可用于学习研究交流，严禁用于各类获利用途。
> 如果有人利用本仓库代码技术进行非法操作带来的后果都是操作者自己承担，
> 和本仓库以及本仓库代码作者没有任何关系。

> 学习交流邮件： kukushka@126.com

包含：

* 微博（网页版 +H5版）开源数据采集
* 网页版cookie 账户操作

## 环境

* Python3.7+
* win7 | 10 | 11

## 说明

* 每个接口都有注释，可以参看源码了解使用细节
* 默认情况下，部分接口都是直接保存至`MongoDB`中并返回的，可以在`config.py`中配置MongoDB,如果不需要保存至数据库，
  可以在调用接口函数时传入`into_mongo=False`这个参数来关掉保存
* 默认返回数据格式：`JSON`
* 默认数据清洗处理：`weibo.cleaner`中的各个装饰器，可以自己修改返回自己想要的字段
* 网页版cookie传入文件： `cookies.yaml`，可以传入多个cookie,传入的cookie为网页版请求头部中`cookie`字段的全部内容即可
* **建议控制采集频率，让代码尽量“做个人”**

## 实现的接口：

开源数据采集（无特殊备注皆为无需cookie版本）：

* [x] [获取博主简要主页信息](#id_00)
* [x] [获取博主详细主页信息](#id_01)
* [x] [获取博主发布的微博01](#id_02)
* [x] [获取博主发布的微博02](#id_03)
* [x] [获取博主发布的微博【网页cookie版】](#id_04)
* [x] [获取用户粉丝列表](#id_05)
* [x] [获取用户关注列表](#id_06)
* [x] [通过bid查询微博的详情](#id_07)
* [x] [通过mid查询微博的详情](#id_08)
* [x] [获取实时微博热搜榜](#id_09)
* [x] [获取实时微博话题榜](#id_10)
* [x] [获取实时热门微博 | 各类榜单](#id_11)
* [x] [获取各类频道视频榜单【网页cookie版】](#id_12)
* [x] [获取用户微博一级评论](#id_13)
* [x] [获取用户微博一级评论【H5版cookie】](#id_14)
* [x] [获取用户微博评论回复列表](#id_15)
* [x] [获取用户微博评论回复列表【H5版cookie】](#id_16)
* [x] [获取用户微博点赞列表](#id_17)
* [x] [获取用户微博点赞列表【H5版cookie】](#id_18)
* [x] [获取用户微博转发列表](#id_19)
* [x] [获取用户微博转发列表【H5版cookie】](#id_20)
* [x] [获取用户微博打赏列表](#id_21)
* [x] [获取热门视频号推荐以及优质视频号推荐【网页cookie版】](#id_22)
* [x] [获取微博视频推荐流【网页cookie版】](#id_23)
* [x] [获取精选频道视频推荐流【网页cookie版】](#id_24)
* [x] [获取超话集合信息](#id_25)
* [x] [关键词搜索](#id_26)
* [x] [关键词图片搜索](#id_27)
* [x] [关键词搜索超话](#id_28)
* [x] [获取用户的精选微博列表](#id_29)
* [x] [获取用户的视频微博列表](#id_30)
* [x] [获取用户的图片列表](#id_31)
* [x] [获取用户的微博相册图片列表](#id_32)
* [x] [获取用户的微博相册列表](#id_33)
* [x] [获取视频频道列表](#id_34)
* [x] [获取热门微博频道列表](#id_35)
* [x] [获取默认表情列表](#id_36)
* [x] [获取当前可以发布微博的频道](#id_37)

网页账户操作(必须先填写网页版cookie至`cookie.yaml`中)：

* [x] [上传图片](#ac_00)
* [x] [上传视频](#ac_01)
* [x] [获取当前用户创建的所有视频合集](#ac_02)
* [x] [获取当前用户加入的所有群组](#ac_03)
* [x] [关注超话](#ac_04)
* [x] [发布微博](#ac_05)
* [x] [删除微博](#ac_06)
* [x] [快转微博](#ac_07)
* [x] [转发微博](#ac_08)
* [x] [评论微博](#ac_09)
* [x] [回复评论](#ac_10)
* [x] [删除评论](#ac_11)
* [x] [关注用户](#ac_12)
* [x] [取关用户](#ac_13)
* [x] [点赞微博](#ac_14)
* [x] [取消点赞微博](#ac_15)
* [x] [获取当前用户关注的朋友新发布的微博](#ac_16)
* [x] [获取当前用户发出过的评论](#ac_17)
* [ ] [获取当前用户未读消息](#)
* [ ] [获取@当前用户的微博](#)
* [ ] [获取@当前用户的评论](#)
* [ ] [实时聊天](#)

### <a href="#id_00">00.获取博主简要主页信息</a>

使用：

```python
from weibo import WeiBoClient

client = WeiBoClient()

# 默认保存结果至MongoDB,可以看接口源码注释
user_info = client.fetch_user_info()

# 如果不保存结果至MongoDB
user_info_dont_save = client.fetch_user_info(into_mongo=False)

# 如果需要保存结果至MongoDB的“用户信息”数据库中的“简要信息”集合
user_info_saved = client.fetch_user_info(dbName="用户信息", collectionName="简要信息")
```

返回：

```json
{
  "uid": 2803301701,
  "nickname": "人民日报",
  "gender": "m",
  "domain": None,
  "description": "人民日报法人微博。参与、沟通、记录时代。",
  "mblog_count": 153019,
  "follow_count": 3063,
  "fans_count": "1.51亿",
  "svip": 0,
  "mbrank": 7,
  "mbtype": 12,
  "urank": 48,
  "user_type": None,
  "location": None,
  "weihao": None,
  "wenda": None,
  "is_star": None,
  "is_muteuser": None,
  "verified": True,
  "verified_type": 3,
  "verified_type_ext": 0,
  "verified_reason": "《人民日报》法人微博",
  "profile_url": "https://m.weibo.cn/u/2803301701?uid=2803301701&luicode=10000011&lfid=1005052803301701",
  "sina_blog_url": None,
  "avtar": "https://wx4.sinaimg.cn/orj480/0033ImPzly8h8vgemh8kxj60sa0sadgw02.jpg",
  "background_image": "https://wx1.sinaimg.cn/crop.0.0.640.640.640/0033ImPzly1gs64jwa7uyj60v90v9n1r02.jpg",
  "tabs": [
    {
      "key": "profile",
      "containerid": "2302832803301701"
    },
    {
      "key": "weibo",
      "containerid": "1076032803301701"
    },
    {
      "key": "original_video",
      "containerid": "2315672803301701"
    },
    {
      "key": "self_media_head",
      "containerid": "2319122803301701_-_ordinary"
    }
  ],
  "timestamp": 1673680848902
}
```

### <a href="#id_01">01.获取博主详细主页信息</a>

使用：

```python
from weibo import WeiBoClient

client = WeiBoClient()

# 默认保存结果至MongoDB,可以看接口源码注释
user_info = client.query_user_details()

# 如果不保存结果至MongoDB
user_info_dont_save = client.query_user_details(into_mongo=False)

# 如果需要保存结果至MongoDB的“用户信息”数据库中的“详细信息”集合
user_info_saved = client.query_user_details(dbName="用户信息", collectionName="详细信息")
```

返回：

```json
{
  "sunshine_credit": {
    "level": "信用极好"
  },
  "birthday": "1948-06-15 双子座",
  "created_at": "2012-07-22 02:28:35",
  "location": "北京",
  "ip_location": None,
  "education": None,
  "career": {
    "company": "人民日报社"
  },
  "company": "人民日报社",
  "label_desc": [
    {
      "name": "昨日发博27，阅读数100万+，互动数37万"
    },
    {
      "name": "视频累计播放量377.82亿"
    },
    {
      "name": "群友 701"
    }
  ],
  "timestamp": 1673683187851,
  "uid": 2803301701,
  "nickname": "人民日报",
  "gender": "m",
  "domain": "rmrb",
  "description": "人民日报法人微博。参与、沟通、记录时代。",
  "mblog_count": 153020,
  "follow_count": 3063,
  "fans_count": 150832872,
  "svip": 0,
  "mbrank": 7,
  "mbtype": 12,
  "urank": None,
  "user_type": 0,
  "weihao": "",
  "wenda": None,
  "is_star": "0",
  "is_muteuser": False,
  "verified": True,
  "verified_type": 3,
  "verified_type_ext": 0,
  "verified_reason": "《人民日报》法人微博",
  "profile_url": "/u/2803301701",
  "sina_blog_url": "",
  "avtar": "https://tvax4.sinaimg.cn/crop.0.0.1018.1018.1024/0033ImPzly8h8vgemh8kxj60sa0sadgw02.jpg?KID=imgbed,tva&Expires=1673693986&ssig=FInafD7OSe",
  "background_image": "https://wx1.sinaimg.cn/crop.0.0.640.640.640/0033ImPzly1gs64jwa7uyj60v90v9n1r02.jpg",
  "tabs": None
}
```

### <a href="#id_02">02.获取博主发布的微博01</a>

使用：

```python
from weibo import WeiBoClient

client = WeiBoClient()

# 用户uid
uid = '1111681197'
# 默认保存结果至MongoDB,可以看接口源码注释
user_tweets = client.fetch_user_tweets(uid)
# 第二页数据,根据第一页返回结果中的since_id值传入
user_tweets_page2 = client.fetch_user_tweets(uid, since_id='4857761008977506')
# 如果不保存结果至MongoDB
user_tweets_dont_save = client.fetch_user_tweets(uid, into_mongo=False)
# 如果需要保存结果至MongoDB的“用户微博”数据库中的“来去之间”集合
user_tweets_saved = client.fetch_user_tweets(uid, dbName="用户微博", collectionName="来去之间")
```

返回：

```json
[
  {
    "card_type": 9,
    "profile_type_id": "proweibo_4857881961438732",
    "itemid": "1076031111681197_-_4857881961438732",
    "scheme": "https://m.weibo.cn/status/MohM062hm?mblogid=MohM062hm&luicode=10000011&lfid=1076031111681197",
    "mblog": {
      "visible": {
        "type": 0,
        "list_id": 0
      },
      "created_at": "Sat Jan 14 18:39:37 +0800 2023",
      "id": "4857881961438732",
      "mid": "4857881961438732",
      "can_edit": False,
      "show_additional_indication": 0,
      "text": "//<a href="
      /n/JoannaBlue
      ">@JoannaBlue</a>:回复<a href="
      /n/露露大神
      ">@露露大神</a>:十四改了判决，由监禁改为流放罗马，也允许他和菲利普书信往来，两年后为了让菲利普同意二婚，又把洛林召了回来，因为菲利普和洛林两年异地恋都没断。。//<a href="
      /n/露露大神
      ">@露露大神</a>:后来这事怎么解决的啊？",
      "source": "iPhone 14 Pro",
      "favorited": False,
      "pic_ids": [],
      "is_paid": False,
      "mblog_vip_type": 0,
      "pid": 4857881641353411,
      "pidstr": "4857881641353411",
      "retweeted_status": {
        "visible": {
          "type": 0,
          "list_id": 0
        },
        "created_at": "Sat Jan 14 15:06:22 +0800 2023",
        "id": "4857828294527603",
        "mid": "4857828294527603",
        "can_edit": False,
        "show_additional_indication": 0,
        "text": "<a  href="
        https: //m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E5%87%A1%E5%B0%94%E8%B5%9B%E5%AE%AB%E8%BD%B6%E4%BA%8B%23&extparam=%23%E5%87%A1%E5%B0%94%E8%B5%9B%E5%AE%AB%E8%BD%B6%E4%BA%8B%23&luicode=10000011&lfid=1076031111681197" data-hide=""><span class="surl-text">#凡尔赛宫轶事#</span></a> 路易十四和菲利普最严重的一次公开吵架<br /><br />1670年元旦刚过，路易十四就下令逮捕弟弟菲利普的男宠洛林骑士，这次逮捕是在晚上进行的，毫无征兆下菲利普在圣日耳曼城堡的居所被国王卫队包围，随即洛林被拘捕。<br /><br />菲利普在抗争无效后，一气之下离开了巴黎，举家前往离巴黎70英里外的维莱科特 ...<a href="/status/4857828294527603">全文</a>",
        "textLength"
        :
        2375,
        "source": "微博 weibo.com",
        "favorited": False,
        "pic_ids": [
          "6c15acbbly1ha36xvn7cgj20sg0lcjt4"
        ],
        "thumbnail_pic": "https://wx4.sinaimg.cn/thumbnail/6c15acbbly1ha36xvn7cgj20sg0lcjt4.jpg",
        "bmiddle_pic": "http://wx4.sinaimg.cn/bmiddle/6c15acbbly1ha36xvn7cgj20sg0lcjt4.jpg",
        "original_pic": "https://wx4.sinaimg.cn/large/6c15acbbly1ha36xvn7cgj20sg0lcjt4.jpg",
        "is_paid": False,
        "mblog_vip_type": 0,
        "user": {
          "id": 1813359803,
          "screen_name": "JoannaBlue",
          "profile_image_url": "https://tvax4.sinaimg.cn/crop.131.0.355.355.180/6c15acbbly8foyivl4wwcj20hs0hs7bl.jpg?KID=imgbed,tva&Expires=1673703615&ssig=rAsjrbVnLs",
          "profile_url": "https://m.weibo.cn/u/1813359803?uid=1813359803&luicode=10000011&lfid=1076031111681197",
          "statuses_count": 21291,
          "verified": True,
          "verified_type": 0,
          "verified_type_ext": 1,
          "verified_reason": "知名历史博主",
          "close_blue_v": False,
          "description": "搞点正经的和不正经的西方历史。VX公众号：JoannaBlue欧洲历史那些事儿。",
          "gender": "f",
          "mbtype": 12,
          "svip": 0,
          "urank": 48,
          "mbrank": 7,
          "follow_me": False,
          "following": False,
          "follow_count": 212,
          "followers_count": "105.9万",
          "followers_count_str": "105.9万",
          "cover_image_phone": "https://tva1.sinaimg.cn/crop.0.0.640.640.640/549d0121tw1egm1kjly3jj20hs0hsq4f.jpg",
          "avatar_hd": "https://wx4.sinaimg.cn/orj480/6c15acbbly8foyivl4wwcj20hs0hs7bl.jpg",
          "like": False,
          "like_me": False,
          "badge": {
            "bind_taobao": 1,
            "dzwbqlx_2016": 1,
            "follow_whitelist_video": 1,
            "user_name_certificate": 1,
            "wenchuan_10th": 1,
            "super_star_2018": 1,
            "worldcup_2018": 34,
            "dailv_2018": 3,
            "weibo_display_fans": 1,
            "relation_display": 1,
            "memorial_2018": 1,
            "hongbaofei_2019": 1,
            "status_visible": 1,
            "hongrenjie_2019": 1,
            "china_2019": 1,
            "hongkong_2019": 1,
            "dzwbqlx_2019": 1,
            "rrgyj_2019": 1,
            "gongjiri_2019": 1,
            "hongbao_2020": 2,
            "feiyan_2020": 1,
            "pc_new": 6,
            "dailv_2020": 1,
            "gongyi_2020": 2,
            "hongrenjie_2020": 1,
            "zjszgf_2020": 1,
            "weibozhiye_2020": 1,
            "zhongcaoguan_2021": 1,
            "yuanlongping_2021": 1,
            "ylpshuidao_2021": 1,
            "gaokao_2021": 1,
            "party_cardid_state": 2,
            "aoyun_2021": 1,
            "dailu_2021": 1,
            "companion_card": 1,
            "fishfarm_2021": 1,
            "kaixue21_2021": 1,
            "renrengongyijie_2021": 1,
            "hongbaofei2022_2021": 1,
            "newdongaohui_2022": 1,
            "video_visible": 1,
            "iplocationchange_2022": 1,
            "gaokao_2022": 1,
            "guoqi_2022": 1,
            "gangqi_2022": 1,
            "dailv_2022": 1,
            "hongrenjie_2022": 1,
            "hongrenjienew_2022": 1
          }
        },
        "picStatus": "1",
        "reposts_count": 40,
        "comments_count": 13,
        "reprint_cmt_count": 0,
        "attitudes_count": 277,
        "pending_approval_count": 0,
        "isLongText": True,
        "mlevel": 0,
        "show_mlevel": 0,
        "darwin_tags": [],
        "hot_page": {
          "fid": "232532_mblog",
          "feed_detail_type": 0
        },
        "mblogtype": 0,
        "rid": "0_0_50_4814179716251311060_0_0_0",
        "cardid": "star_1618",
        "number_display_strategy": {
          "apply_scenario_flag": 3,
          "display_text_min_number": 1000000,
          "display_text": "100万+"
        },
        "content_auth": 0,
        "safe_tags": 17179869184,
        "comment_manage_info": {
          "comment_permission_type": -1,
          "approval_comment_type": 0,
          "comment_sort_type": 0,
          "ai_play_picture_type": 0
        },
        "pic_num": 1,
        "new_comment_style": 0,
        "region_name": "发布于 浙江",
        "region_opt": 1,
        "edit_config": {
          "edited": False
        },
        "page_info": {
          "type": "search_topic",
          "object_type": 0,
          "page_pic": {
            "url": "https://wx1.sinaimg.cn/thumb180/0024cZx9ly8gyemyiee8yj605005074d02.jpg"
          },
          "page_url": "https://m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E5%87%A1%E5%B0%94%E8%B5%9B%E5%AE%AB%E8%BD%B6%E4%BA%8B%23&extparam=%23%E5%87%A1%E5%B0%94%E8%B5%9B%E5%AE%AB%E8%BD%B6%E4%BA%8B%23&luicode=10000011&lfid=1076031111681197",
          "page_title": "#凡尔赛宫轶事#",
          "content1": "0讨论 0阅读 "
        },
        "pics": [
          {
            "pid": "6c15acbbly1ha36xvn7cgj20sg0lcjt4",
            "url": "https://wx4.sinaimg.cn/orj360/6c15acbbly1ha36xvn7cgj20sg0lcjt4.jpg",
            "size": "orj360",
            "geo": {
              "width": 360,
              "height": 270,
              "croped": False
            },
            "large": {
              "size": "large",
              "url": "https://wx4.sinaimg.cn/large/6c15acbbly1ha36xvn7cgj20sg0lcjt4.jpg",
              "geo": {
                "width": "1024",
                "height": "768",
                "croped": False
              }
            }
          }
        ],
        "bid": "MognriZPR"
      },
      "reposts_count": 0,
      "comments_count": 0,
      "reprint_cmt_count": 0,
      "attitudes_count": 0,
      "pending_approval_count": 0,
      "isLongText": False,
      "reward_scheme": "sinaweibo://reward?bid=1000293251&enter_id=1000293251&enter_type=1&oid=4857881961438732&seller=1111681197&share=18cb5613ebf3d8aadd9975c1036ab1f47&sign=629625a9897c26367e519d7599a8d1ac",
      "mlevel": 0,
      "show_mlevel": 0,
      "darwin_tags": [],
      "hot_page": {
        "fid": "232532_mblog",
        "feed_detail_type": 0
      },
      "mblogtype": 0,
      "rid": "0_0_50_4814179716251311060_0_0_0",
      "cardid": "star_1624",
      "extern_safe": 0,
      "number_display_strategy": {
        "apply_scenario_flag": 3,
        "display_text_min_number": 1000000,
        "display_text": "100万+"
      },
      "content_auth": 0,
      "safe_tags": 34359738368,
      "comment_manage_info": {
        "comment_permission_type": -1,
        "approval_comment_type": 0,
        "comment_sort_type": 0
      },
      "repost_type": 1,
      "pic_num": 0,
      "new_comment_style": 0,
      "ab_switcher": 4,
      "region_name": "发布于 北京",
      "region_opt": 1,
      "mblog_menu_new_style": 0,
      "edit_config": {
        "edited": False
      },
      "raw_text": "//@JoannaBlue:回复@露露大神:十四改了判决，由监禁改为流放罗马，也允许他和菲利普书信往来，两年后为了让菲利普同意二婚，又把洛林召了回来，因为菲利普和洛林两年异地恋都没断。。//@露露大神:后来这事怎么解决的啊？",
      "bid": "MohM062hm"
    },
    "total": 120518,
    "since_id": 4857761008977506,
    "timestamp": 1673692815678
  }
]
```

### <a href="#id_03">03.获取博主发布的微博02</a>

使用：

```python
from weibo import WeiBoClient

client = WeiBoClient()

# 用户uid
uid = '1111681197'
# 默认保存结果至MongoDB,可以看接口源码注释
user_tweets = client.query_user_tweets(uid)
# 第二页数据,根据第一页返回结果中的since_id值传入
user_tweets_page2 = client.query_user_tweets(uid, since_id='4857761008977506')
# 如果不保存结果至MongoDB
user_tweets_dont_save = client.query_user_tweets(uid, into_mongo=False)
# 如果需要保存结果至MongoDB的“用户微博”数据库中的“来去之间”集合
user_tweets_saved = client.fetch_user_tweets(uid, dbName="用户微博", collectionName="来去之间")
```

返回：

```json
[
  {
    "card_type": 9,
    "card_type_name": "",
    "itemid": "",
    "scheme": "https://m.weibo.cn/status/MohJW3BG6?mblogid=MohJW3BG6&luicode=10000011&lfid=2304131111681197_-_WEIBO_SECOND_PROFILE_WEIBO",
    "mblog": {
      "visible": {
        "type": 0,
        "list_id": 0
      },
      "created_at": "Sat Jan 14 18:34:32 +0800 2023",
      "id": "4857880680859822",
      "mid": "4857880680859822",
      "can_edit": False,
      "show_additional_indication": 0,
      "text": "🙅🙅",
      "source": "iPhone 14 Pro",
      "favorited": False,
      "pic_ids": [],
      "is_paid": False,
      "mblog_vip_type": 0,
      "retweeted_status": {
        "visible": {
          "type": 0,
          "list_id": 0
        },
        "created_at": "Sat Jan 14 17:02:05 +0800 2023",
        "id": "4857857415321937",
        "mid": "4857857415321937",
        "can_edit": False,
        "show_additional_indication": 0,
        "text": "【<a  href="
        https: //m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E5%BC%A0%E6%9C%9D%E9%98%B3%E5%9B%9E%E5%BA%94%E5%8A%9D%E8%AF%AB%E5%B9%B4%E8%BD%BB%E4%BA%BA%E9%81%AD%E7%BE%A4%E5%98%B2%23&extparam=%23%E5%BC%A0%E6%9C%9D%E9%98%B3%E5%9B%9E%E5%BA%94%E5%8A%9D%E8%AF%AB%E5%B9%B4%E8%BD%BB%E4%BA%BA%E9%81%AD%E7%BE%A4%E5%98%B2%23&luicode=10000011&lfid=2304131111681197_-_WEIBO_SECOND_PROFILE_WEIBO" data-hide=""><span class="surl-text">#张朝阳回应劝诫年轻人遭群嘲#</span></a> ：不要断章取义，字面理解】近日，张朝阳做客东方甄选直播间，称年轻人不要只追求赚钱和快乐，大脑的构造就是劳作的命，人生要过得有意义和承担责任，遭到群嘲。14日，张朝阳微博回应表示，不要断章取义，字面理解，他是在讲心理学和脑科学。<a href=\"/n/巨浪视频\">@巨浪视频</a>  ...<a href="/status/4857857415321937">全文</a>",
        "textLength"
        :
        285,
        "source": "微博视频号",
        "favorited": False,
        "pic_ids": [],
        "is_paid": False,
        "mblog_vip_type": 0,
        "user": {
          "id": 7467277921,
          "screen_name": "西部决策",
          "profile_image_url": "https://tvax4.sinaimg.cn/crop.0.0.512.512.180/0089lW6tly8h8vl04kfvhj30e80e8dfv.jpg?KID=imgbed,tva&Expires=1673703897&ssig=E4IvkDI3Zr",
          "profile_url": "https://m.weibo.cn/u/7467277921?uid=7467277921&luicode=10000011&lfid=2304131111681197_-_WEIBO_SECOND_PROFILE_WEIBO",
          "statuses_count": 33099,
          "verified": True,
          "verified_type": 3,
          "verified_type_ext": 50,
          "verified_reason": "西部决策网官方微博",
          "close_blue_v": False,
          "description": "立足西部，放眼全国。",
          "gender": "m",
          "mbtype": 12,
          "svip": 0,
          "urank": 0,
          "mbrank": 5,
          "follow_me": False,
          "following": False,
          "follow_count": 2115,
          "followers_count": "273.8万",
          "followers_count_str": "273.8万",
          "cover_image_phone": "https://tva1.sinaimg.cn/crop.0.0.640.640.640/549d0121tw1egm1kjly3jj20hs0hsq4f.jpg",
          "avatar_hd": "https://wx4.sinaimg.cn/orj480/0089lW6tly8h8vl04kfvhj30e80e8dfv.jpg",
          "like": False,
          "like_me": False,
          "badge": {
            "vip_activity2": 4,
            "user_name_certificate": 1,
            "pc_new": 6,
            "school_2020": 1,
            "hongrenjie_2020": 1,
            "weibozhiye_2020": 1,
            "hongbaofeifuniu_2021": 1,
            "yuanlongping_2021": 1,
            "ylpshuidao_2021": 1,
            "gaokao_2021": 1,
            "aoyun_2021": 1,
            "hongbaofei2022_2021": 2,
            "newdongaohui_2022": 1,
            "nihaochuntian_2022": 1,
            "biyeji_2022": 1,
            "shuidao_2022": 1,
            "gaokao_2022": 1,
            "zhongqiujie_2022": 5,
            "kaixueji_2022": 1,
            "renrengongyijie_2022": 1,
            "shijiebeigolden_2022": 1
          }
        },
        "reposts_count": 12,
        "comments_count": 4,
        "reprint_cmt_count": 0,
        "attitudes_count": 24,
        "pending_approval_count": 0,
        "isLongText": True,
        "mlevel": 0,
        "show_mlevel": 0,
        "expire_time": 1673774154,
        "ad_state": 1,
        "darwin_tags": [],
        "hot_page": {
          "fid": "232532_mblog",
          "feed_detail_type": 0
        },
        "mblogtype": 0,
        "mark": "999_reallog_mark_ad:999|WeiboADNatural",
        "rid": "1_0_50_5224221953397729044_0_0_0",
        "cardid": "star_1170",
        "number_display_strategy": {
          "apply_scenario_flag": 3,
          "display_text_min_number": 1000000,
          "display_text": "100万+"
        },
        "content_auth": 0,
        "safe_tags": 67108864,
        "comment_manage_info": {
          "comment_permission_type": -1,
          "approval_comment_type": 0,
          "comment_sort_type": 0,
          "ai_play_picture_type": 0
        },
        "pic_num": 0,
        "new_comment_style": 0,
        "page_info": {
          "type": "video",
          "object_type": 11,
          "url_ori": "http://t.cn/A69UVojf",
          "page_pic": {
            "pid": "008s5fZbly1ha3c2wjcxcj30u0140tqe",
            "source": 2,
            "is_self_cover": 1,
            "type": -1,
            "url": "https://wx2.sinaimg.cn/orj480/008s5fZbly1ha3c2wjcxcj30u0140tqe.jpg"
          },
          "page_url": "https://video.weibo.com/show?fid=1034%3A4857856063897666&luicode=10000011&lfid=2304131111681197_-_WEIBO_SECOND_PROFILE_WEIBO",
          "object_id": "1034:4857856063897666",
          "page_title": "巨浪视频的微博视频",
          "title": "张朝阳回应劝诫年轻人遭群嘲：不要断章取义，字面理解",
          "content1": "巨浪视频的微博视频",
          "content2": "【#张朝阳回应劝诫年轻人遭群嘲# ：不要断章取义，字面理解】近日，张朝阳做客东方甄选直播间，称年轻人不要只追求赚钱和快乐，大脑的构造就是劳作的命，人生要过得有意义和承担责任，遭到群嘲。14日，张朝阳微博回应表示，不要断章取义，字面理解，他是在讲心理学和脑科学。@巨浪视频",
          "video_orientation": "vertical",
          "play_count": "7万次播放",
          "media_info": {
            "stream_url": "https://f.video.weibocdn.com/o0/T1YeosVFlx082lC71XjW010412001Xew0E010.mp4?label=mp4_ld&template=360x640.24.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696675&ssig=AYVkTD91QI&KID=unistore,video",
            "stream_url_hd": "https://f.video.weibocdn.com/o0/oRMRMBY8lx082lC7EewM010412003zml0E010.mp4?label=mp4_hd&template=540x960.24.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696675&ssig=9yfcxlhMca&KID=unistore,video",
            "duration": 21.222
          },
          "urls": {
            "mp4_720p_mp4": "https://f.video.weibocdn.com/o0/54PZhL4Nlx082lC7eEbS0104120061OO0E010.mp4?label=mp4_720p&template=720x1280.24.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696675&ssig=fESmpusYyc&KID=unistore,video",
            "mp4_hd_mp4": "https://f.video.weibocdn.com/o0/oRMRMBY8lx082lC7EewM010412003zml0E010.mp4?label=mp4_hd&template=540x960.24.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696675&ssig=9yfcxlhMca&KID=unistore,video",
            "mp4_ld_mp4": "https://f.video.weibocdn.com/o0/T1YeosVFlx082lC71XjW010412001Xew0E010.mp4?label=mp4_ld&template=360x640.24.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696675&ssig=AYVkTD91QI&KID=unistore,video"
          }
        },
        "bid": "Moh8pmktH"
      },
      "reposts_count": 7,
      "comments_count": 10,
      "reprint_cmt_count": 0,
      "attitudes_count": 16,
      "pending_approval_count": 0,
      "isLongText": False,
      "reward_scheme": "sinaweibo://reward?bid=1000293251&enter_id=1000293251&enter_type=1&oid=4857880680859822&seller=1111681197&share=18cb5613ebf3d8aadd9975c1036ab1f47&sign=3efddd3032825a4e3d1407b46f95eccb",
      "mlevel": 0,
      "show_mlevel": 0,
      "darwin_tags": [],
      "hot_page": {
        "fid": "232532_mblog",
        "feed_detail_type": 0
      },
      "mblogtype": 0,
      "mark": "999_reallog_mark_ad:999|WeiboADNatural",
      "rid": "1_0_50_5224221953397729044_0_0_0",
      "cardid": "star_1624",
      "extern_safe": 0,
      "number_display_strategy": {
        "apply_scenario_flag": 3,
        "display_text_min_number": 1000000,
        "display_text": "100万+"
      },
      "content_auth": 0,
      "safe_tags": 309237645312,
      "comment_manage_info": {
        "comment_permission_type": -1,
        "approval_comment_type": 0,
        "comment_sort_type": 0
      },
      "repost_type": 1,
      "pic_num": 0,
      "new_comment_style": 0,
      "ab_switcher": 4,
      "region_name": "发布于 北京",
      "region_opt": 1,
      "mblog_menu_new_style": 0,
      "raw_text": "🙅🙅",
      "bid": "MohJW3BG6"
    },
    "show_type": 1,
    "title": "",
    "total": None,
    "since_id": 4857761008977506,
    "timestamp": 1673693097852
  }
]
```

### <a href="#id_02">04.获取博主发布的微博【网页cookie版】</a>

使用：

```python
from weibo import WeiBoClient

client = WeiBoClient.load_from_file('cookies.yaml')

# 用户uid
uid = '1111681197'
# 默认保存结果至MongoDB,可以看接口源码注释
user_tweets = client.crawl_user_tweets(uid)
# 第二页数据,根据第一页返回结果中的since_id值传入
user_tweets_page2 = client.crawl_user_tweets(uid, since_id='4857532763609089kp2')
# 如果不保存结果至MongoDB
user_tweets_dont_save = client.crawl_user_tweets(uid, into_mongo=False)
# 如果需要保存结果至MongoDB的“用户微博”数据库中的“来去之间”集合
user_tweets_saved = client.crawl_user_tweets(uid, dbName="用户微博", collectionName="来去之间")
```

返回：

```json
[
  {
    "visible": {
      "type": 0,
      "list_id": 0
    },
    "created_at": "Sat Jan 14 18:45:00 +0800 2023",
    "id": 4857883315410503,
    "idstr": "4857883315410503",
    "mid": "4857883315410503",
    "mblogid": "MohObmHwb",
    "can_edit": False,
    "text_raw": "转发微博",
    "text": "转发微博",
    "source": "iPhone 14 Pro",
    "favorited": False,
    "rid": "0_0_50_5225514377776657725_0_0_0",
    "cardid": "star_1624",
    "pic_ids": [],
    "geo": "",
    "pic_num": 0,
    "is_paid": False,
    "pic_bg_new": "http://vip.storage.weibo.com/feed_cover/star_1624_mobile_new.png?version=2021091501",
    "mblog_vip_type": 0,
    "number_display_strategy": {
      "apply_scenario_flag": 3,
      "display_text_min_number": 1000000,
      "display_text": "100万+"
    },
    "reposts_count": 7,
    "comments_count": 1,
    "attitudes_count": 10,
    "attitudes_status": 0,
    "isLongText": False,
    "mlevel": 0,
    "content_auth": 0,
    "is_show_bulletin": 2,
    "comment_manage_info": {
      "comment_permission_type": -1,
      "approval_comment_type": 0,
      "comment_sort_type": 0
    },
    "repost_type": 1,
    "share_repost_type": 0,
    "url_struct": [
      {
        "url_title": "贵妃醉影的微博视频",
        "url_type_pic": "https://h5.sinaimg.cn/upload/2015/09/25/3/timeline_card_small_video.png",
        "ori_url": "sinaweibo://video/vvs?mid=4857851275384530&object_id=1034:4857848069554290&url_type=39&object_type=video&pos=1",
        "page_id": "2304444857848069554290",
        "short_url": "http://t.cn/A69UcM1M",
        "long_url": "https://video.weibo.com/show?fid=1034:4857848069554290",
        "url_type": 39,
        "result": False,
        "actionlog": {
          "act_type": 1,
          "act_code": 300,
          "oid": "1034:4857848069554290",
          "uuid": 4857850303086609,
          "cardid": "",
          "lcardid": "",
          "uicode": "",
          "luicode": "",
          "fid": "1076031111681197_-_WEIBO_SECOND_PROFILE_WEIBO",
          "lfid": "",
          "ext": "mid:4857851275384530|rid:0_0_50_5225514377776657725_0_0_0|short_url:http://t.cn/A69UcM1M|long_url:https://video.weibo.com/show?fid=1034:4857848069554290|comment_id:|miduid:1111681197|rootmid:4857851275384530|rootuid:7640678322|authorid:7640678322|uuid:4857850303086609|is_ad_weibo:0|analysis_card:url_struct"
        },
        "storage_type": "oss",
        "hide": 0,
        "object_type": "",
        "ttl": 3600,
        "need_save_obj": 0
      }
    ],
    "mblogtype": 0,
    "showFeedRepost": False,
    "showFeedComment": False,
    "pictureViewerSign": False,
    "showPictureViewer": False,
    "rcList": [],
    "region_name": "发布于 北京",
    "customIcons": [],
    "retweeted_status": {
      "visible": {
        "type": 0,
        "list_id": 0
      },
      "created_at": "Sat Jan 14 16:37:41 +0800 2023",
      "id": 4857851275384530,
      "idstr": "4857851275384530",
      "mid": "4857851275384530",
      "mblogid": "MogYvmALg",
      "user": {
        "id": 7640678322,
        "idstr": "7640678322",
        "pc_new": 6,
        "screen_name": "贵妃醉影",
        "profile_image_url": "https://tvax3.sinaimg.cn/crop.0.0.664.664.50/008l5vt8ly8gt83edy69vj30ig0igq3t.jpg?KID=imgbed,tva&Expires=1673704160&ssig=IUSxqgiZrf",
        "profile_url": "/u/7640678322",
        "verified": True,
        "verified_type": 0,
        "domain": "",
        "weihao": "",
        "verified_type_ext": 0,
        "avatar_large": "https://tvax3.sinaimg.cn/crop.0.0.664.664.180/008l5vt8ly8gt83edy69vj30ig0igq3t.jpg?KID=imgbed,tva&Expires=1673704160&ssig=5w4a1K4ynM",
        "avatar_hd": "https://tvax3.sinaimg.cn/crop.0.0.664.664.1024/008l5vt8ly8gt83edy69vj30ig0igq3t.jpg?KID=imgbed,tva&Expires=1673704160&ssig=ePH0qEgvr%2B",
        "follow_me": False,
        "following": False,
        "mbrank": 4,
        "mbtype": 11,
        "v_plus": 0,
        "planet_video": False,
        "icon_list": [
          {
            "type": "vip",
            "data": {
              "mbrank": 4,
              "mbtype": 11,
              "svip": 0
            }
          },
          {
            "type": "icon",
            "data": {
              "value": "1",
              "icon_img": "https://h5.sinaimg.cn/upload/103/1651/2022/12/20/dayantu_32x48.png",
              "title": "2023让红包飞",
              "url": "https://m.weibo.cn/c/wbox?id=hx1al1cour"
            }
          }
        ]
      },
      "can_edit": False,
      "text_raw": "湖南农民画工，20多年临摹了10万张梵高的画，见到真迹后却沉默了 http://t.cn/A69UcM1M \u200b\u200b\u200b",
      "text": "湖南农民画工，20多年临摹了10万张梵高的画，见到真迹后却沉默了 <a target="
      _blank
      " href="
      https: //video.weibo.com/show?fid=1034:4857848069554290"><img class="icon-link" src="https://h5.sinaimg.cn/upload/2015/09/25/3/timeline_card_small_video_default.png"/>贵妃醉影的微博视频</a> \u200b\u200b\u200b",
      "textLength"
      :
      81,
      "source": "微博视频号",
      "favorited": False,
      "buttons": [
        {
          "type": "follow",
          "name": "加关注",
          "params": {
            "uid": 7640678322,
            "disable_group": 1,
            "extparams": {
              "followcardid": "1008080010_"
            }
          },
          "actionlog": {
            "act_code": "92",
            "oid": "4857851275384530"
          }
        }
      ],
      "rid": "0_0_50_5225514377776657725_0_0_0",
      "pic_ids": [],
      "geo": "",
      "pic_num": 0,
      "is_paid": False,
      "mblog_vip_type": 0,
      "number_display_strategy": {
        "apply_scenario_flag": 3,
        "display_text_min_number": 1000000,
        "display_text": "100万+"
      },
      "reposts_count": 96,
      "comments_count": 9,
      "attitudes_count": 91,
      "attitudes_status": 0,
      "isLongText": False,
      "mlevel": 0,
      "content_auth": 0,
      "is_show_bulletin": 2,
      "comment_manage_info": {
        "comment_permission_type": -1,
        "approval_comment_type": 0,
        "comment_sort_type": 0,
        "ai_play_picture_type": 0
      },
      "mblogtype": 0,
      "showFeedRepost": False,
      "showFeedComment": False,
      "pictureViewerSign": False,
      "showPictureViewer": False,
      "rcList": [],
      "region_name": "发布于 安徽",
      "customIcons": []
    },
    "page_info": {
      "type": "11",
      "page_id": "2304444857848069554290",
      "object_type": "video",
      "object_id": "1034:4857848069554290",
      "content1": "贵妃醉影的微博视频",
      "content2": "湖南农民画工，20多年临摹了10万张梵高的画，见到真迹后却沉默了",
      "act_status": 1,
      "media_info": {
        "video_orientation": "horizontal",
        "name": "贵妃醉影的微博视频",
        "stream_url": "http://f.video.weibocdn.com/o0/W3laDNlslx082lwdp84801041202nz6k0E010.mp4?label=mp4_ld&template=640x360.25.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696903&ssig=d0xwjbqSP%2F&KID=unistore,video",
        "stream_url_hd": "http://f.video.weibocdn.com/o0/js1Hhn48lx082lwdUNxK01041203K9Zw0E020.mp4?label=mp4_hd&template=852x480.25.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696903&ssig=WGKrrzBFsQ&KID=unistore,video",
        "format": "mp4",
        "h5_url": "https://video.weibo.com/show?fid=1034:4857848069554290",
        "mp4_sd_url": "http://f.video.weibocdn.com/o0/W3laDNlslx082lwdp84801041202nz6k0E010.mp4?label=mp4_ld&template=640x360.25.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696903&ssig=d0xwjbqSP%2F&KID=unistore,video",
        "mp4_hd_url": "http://f.video.weibocdn.com/o0/js1Hhn48lx082lwdUNxK01041203K9Zw0E020.mp4?label=mp4_hd&template=852x480.25.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696903&ssig=WGKrrzBFsQ&KID=unistore,video",
        "h265_mp4_hd": "",
        "h265_mp4_ld": "",
        "inch_4_mp4_hd": "",
        "inch_5_mp4_hd": "",
        "inch_5_5_mp4_hd": "",
        "mp4_720p_mp4": "http://f.video.weibocdn.com/o0/NS2B1oKKlx082lwhoATu01041206FBsz0E030.mp4?label=mp4_720p&template=1280x720.25.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1673696903&ssig=izmiyVtxRe&KID=unistore,video",
        "hevc_mp4_720p": "",
        "prefetch_type": 1,
        "prefetch_size": 262144,
        "act_status": 1,
        "protocol": "general,dash",
        "media_id": "4857848069554290",
        "origin_total_bitrate": 16918170,
        "duration": 593,
        "forward_strategy": -1,
        "search_scheme": "sinaweibo://svssearch?containerid=232080",
        "is_short_video": 1,
        "vote_is_show": 0,
        "belong_collection": 1,
        "titles_display_time": "3",
        "show_progress_bar": 1,
        "ext_info": {
          "video_orientation": "horizontal"
        },
        "next_title": "湖南农民画工，20多年临摹了10万张梵高的画，见到真迹后却沉默了",
        "kol_title": "湖南农民画工，20多年临摹了10万张梵高的画，见到真迹后却沉默了",
        "play_completion_actions": [
          {
            "type": "1",
            "icon": "https://h5.sinaimg.cn/upload/100/1413/2021/12/22/feed_video_icon_replay.png",
            "text": "重播",
            "link": "",
            "btn_code": 1000,
            "show_position": 1,
            "actionlog": {
              "oid": "2304444857848069554290",
              "act_code": 1221,
              "act_type": 0,
              "source": "video"
            }
          },
          {
            "type": 6,
            "icon": "https://tvax3.sinaimg.cn/crop.0.0.664.664.180/008l5vt8ly8gt83edy69vj30ig0igq3t.jpg?KID=imgbed,tva&Expires=1673704103&ssig=888YuVSFCP",
            "text": "",
            "display_starttime": 5,
            "display_endtime": 999999,
            "countdown_time": 5,
            "show_position": 48,
            "scheme": "",
            "link": "",
            "btn_code": 1009,
            "actionlog": {
              "oid": "2304444857848069554290",
              "act_code": 91,
              "act_type": 0,
              "source": "video",
              "ext": "mid:4857851275384530|oid:1034:4857848069554290|muid:7640678322|authorid:7640678322"
            },
            "ext": {
              "uid": "7640678322",
              "user_name": "贵妃醉影",
              "followers_count": 446237,
              "verified": True,
              "verified_type": 0,
              "verified_reason": "电影博主 微博原创视频博主",
              "level": 3
            },
            "display_mode": 2,
            "display_type": 0
          }
        ],
        "video_publish_time": 1673685229,
        "play_loop_type": 0,
        "author_mid": "4857851275384530",
        "author_name": "贵妃醉影",
        "is_playlist": 1,
        "get_playlist_id": 4654522329661517,
        "extra_info": {
          "sceneid": "profile_mb"
        },
        "has_recommend_video": 1,
        "video_download_strategy": {
          "abandon_download": 0
        },
        "jump_to": 6,
        "online_users": "1.5万次观看",
        "online_users_number": 15725,
        "guide_paster": {
          "recommend": {
            "time": 5,
            "type": "recommend",
            "action_log": [],
            "exposure_log": []
          }
        },
        "ttl": 3600,
        "storage_type": "oss",
        "is_keep_current_mblog": 0,
        "playback_list": [
          {
            "meta": {
              "label": "mp4_1080p",
              "quality_index": 1080,
              "quality_desc": "高清",
              "quality_label": "1080p",
              "quality_class": "HD",
              "type": 1,
              "quality_group": 1080,
              "is_hidden": False
            },
            "play_info": {
              "type": 1,
              "mime": "video/mp4",
              "protocol": "general",
              "label": "mp4_1080p",
              "url": "http://f.video.weibocdn.com/o0/3QLcw3Wclx082lwlDvmg0104120bAF6h0E050.mp4?label=mp4_1080p&template=1920x1080.25.0&media_id=4857848069554290&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=2&ot=h&lp=00002HVGNB&ps=mZ6WB&uid=8syIOL&ab=9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0&Expires=1673696960&ssig=hxcDcBHwbF&KID=unistore,video",
              "bitrate": 2307260,
              "prefetch_range": "0-1266437",
              "video_codecs": "avc1.640032",
              "fps": 24,
              "width": 1920,
              "height": 1080,
              "size": 171277497,
              "duration": 593.872,
              "sar": "0.0",
              "audio_codecs": "mp4a.40.5",
              "audio_sample_rate": 44100,
              "quality_label": "1080p",
              "quality_class": "HD",
              "quality_desc": "高清",
              "audio_channels": 2,
              "audio_sample_fmt": "fltp",
              "audio_bits_per_sample": 0,
              "watermark": "original",
              "extension": {
                "transcode_info": {
                  "pcdn_rule_id": 0,
                  "pcdn_jank": 0,
                  "origin_video_dr": "SDR",
                  "ab_strategies": "9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0"
                }
              },
              "video_decoder": "hard",
              "prefetch_enabled": True,
              "tcp_receive_buffer": 262144,
              "dolby_atmos": False,
              "dolby_vision": False
            }
          },
          {
            "meta": {
              "label": "mp4_720p",
              "quality_index": 720,
              "quality_desc": "高清",
              "quality_label": "720p",
              "quality_class": "HD",
              "type": 1,
              "quality_group": 720,
              "is_hidden": False
            },
            "play_info": {
              "type": 1,
              "mime": "video/mp4",
              "protocol": "general",
              "label": "mp4_720p",
              "url": "http://f.video.weibocdn.com/o0/NS2B1oKKlx082lwhoATu01041206FBsz0E030.mp4?label=mp4_720p&template=1280x720.25.0&media_id=4857848069554290&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=2&ot=h&lp=00002HVGNB&ps=mZ6WB&uid=8syIOL&ab=9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0&Expires=1673696960&ssig=udtiGO%2F3RB&KID=unistore,video",
              "bitrate": 1327872,
              "prefetch_range": "0-892453",
              "video_codecs": "avc1.64001f",
              "fps": 24,
              "width": 1280,
              "height": 720,
              "size": 98573463,
              "duration": 593.872,
              "sar": "0.0",
              "audio_codecs": "mp4a.40.5",
              "audio_sample_rate": 44100,
              "quality_label": "720p",
              "quality_class": "HD",
              "quality_desc": "高清",
              "audio_channels": 2,
              "audio_sample_fmt": "fltp",
              "audio_bits_per_sample": 0,
              "watermark": "original",
              "extension": {
                "transcode_info": {
                  "pcdn_rule_id": 0,
                  "pcdn_jank": 0,
                  "origin_video_dr": "SDR",
                  "ab_strategies": "9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0"
                }
              },
              "video_decoder": "hard",
              "prefetch_enabled": True,
              "tcp_receive_buffer": 262144,
              "dolby_atmos": False,
              "dolby_vision": False
            }
          },
          {
            "meta": {
              "label": "mp4_hd",
              "quality_index": 480,
              "quality_desc": "标清",
              "quality_label": "480p",
              "quality_class": "SD",
              "type": 1,
              "quality_group": 480,
              "is_hidden": False
            },
            "play_info": {
              "type": 1,
              "mime": "video/mp4",
              "protocol": "general",
              "label": "mp4_hd",
              "url": "http://f.video.weibocdn.com/o0/js1Hhn48lx082lwdUNxK01041203K9Zw0E020.mp4?label=mp4_hd&template=852x480.25.0&media_id=4857848069554290&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=2&ot=h&lp=00002HVGNB&ps=mZ6WB&uid=8syIOL&ab=9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0&Expires=1673696960&ssig=81OzH%2F5lZ8&KID=unistore,video",
              "bitrate": 745351,
              "prefetch_range": "0-651859",
              "video_codecs": "avc1.64001e",
              "fps": 24,
              "width": 852,
              "height": 480,
              "size": 55330506,
              "duration": 593.872,
              "sar": "0.0",
              "audio_codecs": "mp4a.40.5",
              "audio_sample_rate": 44100,
              "quality_label": "480p",
              "quality_class": "SD",
              "quality_desc": "标清",
              "audio_channels": 2,
              "audio_sample_fmt": "fltp",
              "audio_bits_per_sample": 0,
              "watermark": "original",
              "extension": {
                "transcode_info": {
                  "pcdn_rule_id": 0,
                  "pcdn_jank": 0,
                  "origin_video_dr": "SDR",
                  "ab_strategies": "9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0"
                }
              },
              "video_decoder": "hard",
              "prefetch_enabled": True,
              "tcp_receive_buffer": 262144,
              "dolby_atmos": False,
              "dolby_vision": False
            }
          },
          {
            "meta": {
              "label": "scrubber_hd",
              "quality_index": 480,
              "quality_desc": "标清",
              "quality_label": "480p",
              "quality_class": "SD",
              "type": 3,
              "quality_group": 480,
              "is_hidden": False
            },
            "play_info": {
              "type": 3,
              "mime": "image/jpeg",
              "protocol": "general",
              "label": "scrubber_hd",
              "url": "https://wx1.sinaimg.cn/large/008l5vt8ly1ha39mbf9hoj30qo460toz.jpg?media_id=4857848069554290&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=2&ot=h&lp=00002HVGNB&ps=mZ6WB&uid=8syIOL&ab=9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0&Expires=1673696960&ssig=Z0tKNM3%2BS%2B&KID=unistore,video",
              "prefetch_range": "0-512000",
              "width": 320,
              "height": 180,
              "quality_label": "480p",
              "quality_class": "SD",
              "quality_desc": "标清",
              "extension": {
                "transcode_info": {
                  "pcdn_rule_id": 0,
                  "pcdn_jank": 0,
                  "origin_video_dr": "SDR",
                  "ab_strategies": "9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0"
                }
              },
              "video_decoder": "hard",
              "prefetch_enabled": True,
              "tcp_receive_buffer": 262144,
              "col": 3,
              "row": 30,
              "interval": 2,
              "offset": 1,
              "urls": [
                "http://wx4.sinaimg.cn/large/008l5vt8ly1ha39mbf9hoj30qo460toz.jpg",
                "http://wx4.sinaimg.cn/large/008l5vt8ly1ha39mbsm75j30qo460x1e.jpg",
                "http://wx4.sinaimg.cn/large/008l5vt8ly1ha39mc3djoj30qo4604e6.jpg",
                "http://wx4.sinaimg.cn/large/008l5vt8ly1ha39mc9gtfj30qo460dmn.jpg"
              ]
            }
          },
          {
            "meta": {
              "label": "mp4_ld",
              "quality_index": 360,
              "quality_desc": "流畅",
              "quality_label": "360p",
              "quality_class": "SD",
              "type": 1,
              "quality_group": 360,
              "is_hidden": False
            },
            "play_info": {
              "type": 1,
              "mime": "video/mp4",
              "protocol": "general",
              "label": "mp4_ld",
              "url": "http://f.video.weibocdn.com/o0/W3laDNlslx082lwdp84801041202nz6k0E010.mp4?label=mp4_ld&template=640x360.25.0&media_id=4857848069554290&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=2&ot=h&lp=00002HVGNB&ps=mZ6WB&uid=8syIOL&ab=9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0&Expires=1673696960&ssig=MsUyLzQ709&KID=unistore,video",
              "bitrate": 473759,
              "prefetch_range": "0-540872",
              "video_codecs": "avc1.64001e",
              "fps": 24,
              "width": 640,
              "height": 360,
              "size": 35169148,
              "duration": 593.872,
              "sar": "0.0",
              "audio_codecs": "mp4a.40.5",
              "audio_sample_rate": 44100,
              "quality_label": "360p",
              "quality_class": "SD",
              "quality_desc": "流畅",
              "audio_channels": 2,
              "audio_sample_fmt": "fltp",
              "audio_bits_per_sample": 0,
              "watermark": "original",
              "extension": {
                "transcode_info": {
                  "pcdn_rule_id": 0,
                  "pcdn_jank": 0,
                  "origin_video_dr": "SDR",
                  "ab_strategies": "9298-g4,8224-g0,7397-g1,8012-g2,8143-g0,8013-g0,3601-g33,7598-g0"
                }
              },
              "video_decoder": "hard",
              "prefetch_enabled": True,
              "tcp_receive_buffer": 262144,
              "dolby_atmos": False,
              "dolby_vision": False
            }
          }
        ],
        "author_info": {
          "id": 7640678322,
          "idstr": "7640678322",
          "pc_new": 6,
          "screen_name": "贵妃醉影",
          "profile_image_url": "https://tvax3.sinaimg.cn/crop.0.0.664.664.50/008l5vt8ly8gt83edy69vj30ig0igq3t.jpg?KID=imgbed,tva&Expires=1673704160&ssig=IUSxqgiZrf",
          "profile_url": "/u/7640678322",
          "verified": True,
          "verified_type": 0,
          "domain": "",
          "weihao": "",
          "verified_type_ext": 0,
          "avatar_large": "https://tvax3.sinaimg.cn/crop.0.0.664.664.180/008l5vt8ly8gt83edy69vj30ig0igq3t.jpg?KID=imgbed,tva&Expires=1673704160&ssig=5w4a1K4ynM",
          "avatar_hd": "https://tvax3.sinaimg.cn/crop.0.0.664.664.1024/008l5vt8ly8gt83edy69vj30ig0igq3t.jpg?KID=imgbed,tva&Expires=1673704160&ssig=ePH0qEgvr%2B",
          "follow_me": False,
          "following": False,
          "mbrank": 4,
          "mbtype": 11,
          "v_plus": 0,
          "planet_video": False,
          "verified_reason": "电影博主 微博原创视频博主",
          "description": "素材来源网络，如有侵权，请联系删除",
          "location": "海外 罗马尼亚",
          "gender": "f",
          "followers_count": 446249,
          "followers_count_str": "44.6万",
          "friends_count": 60,
          "statuses_count": 45040,
          "url": "",
          "svip": 0,
          "cover_image_phone": "https://ww1.sinaimg.cn/crop.0.0.640.640.640/9d44112bjw1f1xl1c10tuj20hs0hs0tw.jpg"
        }
      },
      "page_pic": "https://wx4.sinaimg.cn/orj480/008l5vt8ly1ha3994tkyzj31hc0u0h0f.jpg",
      "page_title": "贵妃醉影的微博视频",
      "page_url": "sinaweibo://infopage?containerid=2304444857848069554290&containerid=2304444857848069554290&url_type=39&object_type=video&pos=2",
      "pic_info": {
        "pic_big": {
          "height": "480",
          "url": "https://wx4.sinaimg.cn/orj480/008l5vt8ly1ha3994tkyzj31hc0u0h0f.jpg",
          "width": "852"
        },
        "pic_small": {
          "height": "480",
          "url": "https://wx4.sinaimg.cn/orj480/008l5vt8ly1ha3994tkyzj31hc0u0h0f.jpg",
          "width": "852"
        },
        "pic_middle": {
          "url": "https://wx4.sinaimg.cn/orj480/008l5vt8ly1ha3994tkyzj31hc0u0h0f.jpg",
          "height": "480",
          "width": "852"
        }
      },
      "oid": "7640678322",
      "type_icon": "",
      "author_id": "7640678322",
      "authorid": "7640678322",
      "warn": "",
      "actionlog": {
        "act_type": 1,
        "act_code": 799,
        "lcardid": "",
        "fid": "1076031111681197_-_WEIBO_SECOND_PROFILE_WEIBO",
        "mid": "4857851275384530",
        "oid": "1034:4857848069554290",
        "uuid": 4857850303086609,
        "source": "video",
        "ext": "uid:7751075499|mid:4857883315410503|objectid:1034%3A4857848069554290|from:1|object_duration:593.872|miduid:1111681197|rootuid:7640678322|rootmid:4857851275384530|authorid:7640678322|video_orientation:horizontal|third_vid:|is_album:1|is_contribution:0|video_tags:|isfan:0|ua:|sceneid:profile_mb|uuid:4857850303086609|detail:native|contribution:0|short_video:1|st_video:0|author_mid:4857851275384530|cluster_type_status:c|is_ad_weibo:0|container_mid:4857883315410503|t_id:4857813298774091|t_name:%E5%90%88%E9%9B%86+%C2%B7+%E7%82%B9%E5%87%BB12|type:2|analysis_card:page_info"
      },
      "short_url": "http://t.cn/A69UcM1M"
    },
    "total": 120519,
    "since_id": "4857532763609089kp2",
    "timestamp": 1673693361296
  }
]
```

### ...其余接口略（可看源码注释-巨详细）

## 网页版账户操作重点接口

以上的开源数据采集接口大部分都跟上述示例相差无几，不再赘述（懒），下面是发布微博的主要接口详细介绍：

### 发布微博

使用：

```python
import time
from weibo import WeiBoClient
from weibo.consts import Visible, Video

client = WeiBoClient.load_from_file('cookies.yaml')

# 0.发布普通文字+表情微博,可见性为粉丝可见
ret = client.post_tweet("[作揖][兔子]新年快乐~", visible=Visible.FANS)

# 1.定时发布普通文字+表情微博
schedule_time = int(time.time() * 1000) + 30 * 60 * 1000  # 预定30分钟后发布此微博
ret01 = client.post_tweet("[作揖][兔子]新年快乐~", schedule=schedule_time)

# 2.发布图片微博
# 先上传需要插入到微博中的图片
picture_path = r'C:\Users\xxx\Pictures\1.jpg'  # 图片路径或二进制数据
watermark = "@saermart"  # 图片水印
upload_result = client.upload_picture(picture_path, watermark=watermark)
# 上传结果：{'ret': True, 'pic': {'rotated': False, 'pid': '008syIOLly1haxxxxxxxxxxx'}}
pic_pid = upload_result['pic']['pid']  # 已上传的图片的pid
# 发布带图片微博
ret02 = client.post_tweet("[作揖][兔子]新年快乐~", pid=pic_pid)

# 3.发布视频微博
# 先上传视频
video_path = r'C:\Users\xxx\Videos\1.mp4'  # 本地视频路径或者视频二进制数据
watermark = "@saermart"  # 视频水印
video_name = '这是一个测试视频'  # 视频标题
upload_threads = 10  # 上传视频的线程数，线程越多上传越快，失败率可能越高？建议默认
upload_result = client.upload_video(video_path, video_name=video_name, up_threads=upload_threads, watermark=watermark)
# 上传结果：{'result': True, 'upload_id': '142C46xxxxxxxxx', 'media_id': '48578xxxxxxx', 'auth': 'xxxx', 'request_id': 'req_31269c8exxxx', 'cover_pid': '008syIOLly1XXXXXXXXX'}
# 其中封面图片默认截取第一帧上传，如果想自定义封面可以自己上传图片后传入pid
video_mid = upload_result['media_id']  # 视频mid
cover_pid = upload_result['cover_pid']  # 视频封面pid，也可以是自己上传的图片的pid，如：008syIOLly1haxxxxxxxxxxx
# 发布视频微博
ret03 = client.post_tweet("[作揖][兔子]新年快乐~",
                          mid=video_mid,
                          pid=cover_pid,
                          video_down=True,  # 允许下载
                          schedule_time=schedule_time, #定时发布时间
                          video_title=video_name,  # 视频标题，可不写
                          video_type=Video.ORIGINAL, # 表示原创视频,详细可见weibo.consts的Video类
                          visible=Visible.FANS, #粉丝可见,详情可见函数注释
                          )
```
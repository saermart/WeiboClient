#!/usr/bin/python
# coding:utf-8


# 粉丝或是关注的采集模式
MODE_FANS = 10
MODE_FRIENDS = 11

# 接口模式
MODE_M = 12
MODE_WEB = 13

# mobile版本的接口
M_HOST = 'https://m.weibo.cn'
M_COMMON = f'{M_HOST}/api/container/getIndex?'
M_BLOG_DETAIL = f'{M_HOST}/statuses/extend?id='
M_BLOG_DETAILS = f'{M_HOST}/detail/'
M_BLOG_COMMENTS = f'{M_HOST}/comments/hotflow?'
M_BLOG_CHILD_COMMENTS = f'{M_HOST}/comments/hotFlowChild?'
M_BLOG_LIKES = f'{M_HOST}/api/attitudes/show?'
M_BLOG_REPOSTS = f'{M_HOST}/api/statuses/repostTimeline?'
# web版本的接口
WEB_HOST = 'https://weibo.com'
WEB_PASSPORT_HOST = 'https://passport.weibo.com'
WEB_USER_DETAIL = f'{WEB_HOST}/ajax/profile/detail?'
WEB_USER_INFO = f'{WEB_HOST}/ajax/profile/info?'
WEB_USER_BLOGS = f'{WEB_HOST}/ajax/statuses/mymblog?'
WEB_USER_COMMENTS = f'{WEB_HOST}/ajax/message/myCmt'
WEB_USER_FRIENDS = f'{WEB_HOST}/ajax/friendships/friends?page=3&uid=1669879400'
WEB_HOTS = f'{WEB_HOST}/ajax/side/hotSearch'
WEB_VISITOR_URL = f'{WEB_PASSPORT_HOST}/visitor/genvisitor'
WEB_TWEET_DETAILS = f'{WEB_HOST}/ajax/statuses/show?'
WEB_TWEET_COMMENTS = f'{WEB_HOST}/ajax/statuses/buildComments?'
WEB_TWEET_LIKES = f'{WEB_HOST}/ajax/statuses/likeShow?'
WEB_TWEET_REPOSTS = f'{WEB_HOST}/ajax/statuses/repostTimeline?'
WEB_TWEET_CHILD_COMMENTS = f'{WEB_HOST}/ajax/statuses/buildComments?'
WEB_HOT_TWEETS_FEED = f'{WEB_HOST}/ajax/feed/hottimeline?'
WEB_HOT_GROUPS = f'{WEB_HOST}/ajax/feed/allGroups?'
WEB_HOT_TOPICS = f'{WEB_HOST}/ajax/statuses/topic_band?'
WEB_VIDEO_BOARD = f'{WEB_HOST}/tv/api/component?'
WEB_SEARCH_PICS = 'https://s.weibo.com/ajax_pic/list?'
WEB_TWEET_REWARDS = 'https://reward.media.weibo.com/v1/public/h5/aj/reward/rewardlistnew?'
WEB_INCARNATE_URL = 'https://passport.weibo.com/visitor/visitor?a=incarnate&t={}&w={}&c={}&gc=&cb=cross_domain&from=weibo&_rand={}'
# 操作接口
WEB_UPLOAD_PIC = 'https://picupload.weibo.com/interface/upload.php?'
WEB_UPLOAD_INIT = 'https://fileplatform.api.weibo.com/2/fileplatform/init.json?'
WEB_UPLOAD_VIDEO = 'https://up.video.weibocdn.com/2/fileplatform/upload.json?'
WEB_CHECK_UPLOAD = 'https://fileplatform.api.weibo.com/2/fileplatform/check.json'
WEB_USER_COLLECTIONS = f'https://me.weibo.com/api/collection/details?'
WEB_USER_CREATE_COLLECTION = f'https://me.weibo.com/api/collection/create'
WEB_USER_PLAYLIST = f'{WEB_HOST}/ajax/multimedia/user_playlists_get?'
WEB_USER_STOPICS = f'{WEB_HOST}/ajax/stopic/list?'
WEB_FOLLOW_STOPICS = f'{WEB_HOST}/ajax/stopic/curl?'
WEB_USER_GROUPS = f'{WEB_HOST}/ajax/mblog/querygroup'
WEB_USER_TEAMS = f'{WEB_HOST}/ajax/feed/allGroups?'
WEB_USER_HOTS = f'{WEB_HOST}/ajax/profile/myhot?'
WEB_USER_VIDEOS = f'{WEB_HOST}/ajax/profile/getWaterFallContent?'
WEB_USER_PICS = f'{WEB_HOST}/ajax/profile/getImageWall?'
WEB_USER_ALBUM_PICS = f'{WEB_HOST}/ajax/profile/getAlbumDetail?'
WEB_FRIENDS_TWEETS = f'{WEB_HOST}/ajax/feed/unreadfriendstimeline?'
WEB_TWEET_MODIFY = f'{WEB_HOST}/ajax/statuses/modifyVisible'
WEB_UPDATE_TWEET = f'{WEB_HOST}/ajax/statuses/update'
WEB_LIKE_TWEET = f'{WEB_HOST}/ajax/statuses/setLike'
WEB_UNLIKE_TWEET = f'{WEB_HOST}/ajax/statuses/cancelLike'
WEB_SCHEDULE_POST = f'{WEB_HOST}/ajax/statuses/schedule/upload'
WEB_EMOTICONS = f'{WEB_HOST}/ajax/statuses/config'
WEB_DISPLAY_CHANNELS = f'{WEB_HOST}/ajax/multimedia/publish_display_config'
WEB_DELETE_TWEET = f'{WEB_HOST}/ajax/statuses/destroy'
WEB_UNFOLLOW_USER = f'{WEB_HOST}/ajax/friendships/destory'
WEB_FOLLOW_USER = f'{WEB_HOST}/ajax/friendships/create'
WEB_COMMENT_TWEET = f'{WEB_HOST}/ajax/comments/create'
WEB_COMMENT_REPLY = f'{WEB_HOST}/ajax/comments/reply'
WEB_QUICK_REPOST = f'{WEB_HOST}/ajax/statuses/repost'
WEB_REPOST = f'{WEB_HOST}/ajax/statuses/normal_repost'
WEB_AT_ME_TWEETS = f'{WEB_HOST}/ajax/statuses/mentions'
WEB_AT_ME_COMMENTS = f'{WEB_HOST}/ajax/comments/mentions'
WEB_COMMENT_DELETE = f'{WEB_HOST}/ajax/statuses/destroyComment'

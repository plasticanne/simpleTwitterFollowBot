import os,json,time,sys
from datetime import datetime,timezone
from dateutil.tz import tzlocal
from dateutil.parser import parse
import tweepy
import logging
import traceback
import pandas as pd
log_path='./log.txt'
stream=open(log_path, 'a', encoding='UTF-8')
logger = logging.getLogger()
handler=logging.StreamHandler(stream=stream)

logging_format = logging.Formatter('[%(asctime)s] [%(levelname)8s] -- %(message)s')
handler.setFormatter(logging_format)

logger.addHandler(handler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging_format)
logger.addHandler(consoleHandler)

logger.setLevel(logging.INFO)

def logger_print(msg):
    logging.info('------'+str(msg))
def logger_error(e,msg=None):
    error_class = e.__class__.__name__ #取得錯誤類型
    detail = e.args[0] #取得詳細內容
    cl, exc, tb = sys.exc_info() #取得Call Stack
    if msg!=None:
        logger.error((msg))
    logger.error(("---Error call stack start---"))
    logger.error(traceback.format_exc())
    logger.error(("---Error call stack end---"))

def utc_datetime_loaclzone_filename(timeN:datetime):
    return timeN.isoformat(timespec="milliseconds").replace(":","-")
def check_follower_ratio(user_d):
    #跟隨者
    followers_count=user_d["followers_count"]
    #跟隨中
    friends_count=user_d["friends_count"]
    r=friends_count/(followers_count+1)
    if r >= 0.7 and r <= 1.3:
        return True
    else:
        return False

class TweepyBot:
    def __init__(self,api_key,api_key_secret,access_token,access_token_secret):
        self.auth:tweepy.OAuthHandler = tweepy.OAuthHandler(api_key,api_key_secret)
        self.auth.set_access_token(access_token,access_token_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit_notify=True ,wait_on_rate_limit=True)
        
    def test_key(self):
        logger_print("測試金鑰...")
        try:
            self.api.verify_credentials()
            logger_print("正確")
        except:
            logger_print("錯誤")
        logger_print("執行完畢")
    def json_dumps(self,d):
        return json.dumps(d ,ensure_ascii=False)
    def load_processed(self,path):
        try: 
            with open(path,'r',encoding='utf-8') as f:
                return f.read().splitlines()
        except:
            return []


    def load_target_list(self,path):
        with open(path,'r',encoding='utf-8') as f:
            target_list=f.read().splitlines()
        return target_list
    def push_processed(self,id,path,push_list):
        with open(path,'a',encoding='utf-8') as f:
            f.write(id+ "\n")
        push_list.append(id)
    def get_user(self,user_id)-> dict:
        logger_print("取得目標用戶 {} 資料...".format(user_id))
        user  = self.api.get_user(user_id)
        return user
        
    def get_user_points(self,user):
        user_d=dict(user.__dict__)['_json']
        #跟隨者
        followers_count=user_d["followers_count"]
        #跟隨中
        friends_count=user_d["friends_count"]
        #正在關注
        following=user_d["following"]

        logger_print("{}個跟隨中, {}位跟隨者".format(friends_count,followers_count))
        logger_print("已在關注中" if following else "非關注中" )
        return followers_count,friends_count,following
    def do_follow(self,user,id,exclude_list_path,exclude_list,interval_min):
        try:
            user.follow()
            self.push_processed(id,exclude_list_path,exclude_list)
            logger_print("已執行關注")
            logger_print("等待 {} 分鐘執行下個名單".format(interval_min))
            time.sleep(interval_min*60)
            return True
        except Exception as e:
            logger_error(e)
            return False
    def do_unfollow(self,user,id,exclude_list_path,exclude_list,interval_min):
        try:
            user.unfollow()
            self.push_processed(id,exclude_list_path,exclude_list)
            logger_print("已執行取消關注")
            logger_print("等待 {} 分鐘執行下個名單".format(interval_min))
            time.sleep(interval_min*60)
            return True
        except Exception as e:
            logger_error(e)
            return False


    def process_batch_follow(self,target_list_path,exclude_list_path,interval_min=1,max_retry=2):
        exclude_list=self.load_processed(exclude_list_path)
        target_list=self.load_target_list(target_list_path)
        count=0
        logger_print("執行關注任務")
        for target in target_list:
            id=target.lower()
            if id in exclude_list:
                logger_print("已存在已執行名單中, 跳過")
                continue
            try:
                user=self.get_user(id)
            except Exception as e:
                logger_print("用戶 {} 資料取得錯誤, 跳過".format(id))
                logger_error(e)
                self.push_processed(id,exclude_list_path,exclude_list)
                continue  
            followers_count,friends_count,following=self.get_user_points(user)
            
            if not following:
                for i in range(max_retry+1):
                    isPass=self.do_follow(user,id,exclude_list_path,exclude_list,interval_min)
                    if isPass:
                        break
                    else:
                        min=15
                        logger_print("第 {} 次重新嘗試, 執行失敗".format(i))
                        if i ==max_retry+1:
                            logger_print("似乎被ban, 停止執行")
                            return
                        logger_print("{} 分鐘後再次重試".format(min))
                        time.sleep(min*60)

            else:
                self.push_processed(id,exclude_list_path,exclude_list)
                logger_print("跳過")
            # 15 min 300個用戶查找
            time.sleep(3)
        logger_print("全部名單執行完畢")
    def process_batch_unfollow(self,target_list_path,exclude_list_path,interval_min=1,max_retry=2):
        exclude_list=self.load_processed(exclude_list_path)
        target_list=self.load_target_list(target_list_path)
        count=0
        logger_print("執行取消關注任務")
        for target in target_list:
            id=target.lower()
            if id in exclude_list:
                logger_print("已存在排除名單中, 跳過")
                continue
            try:
                user=self.get_user(id)
            except Exception as e:
                logger_print("用戶 {} 資料取得錯誤, 跳過".format(id))
                logger_error(e)
                self.push_processed(id,exclude_list_path,exclude_list)
                continue  
            followers_count,friends_count,following=self.get_user_points(user)
            
            if following:
                for i in range(max_retry+1):
                    isPass=self.do_unfollow(user,id,exclude_list_path,exclude_list,interval_min)
                    if isPass:
                        break
                    else:
                        min=15
                        logger_print("第 {} 次重新嘗試, 執行失敗".format(i))
                        if i ==max_retry+1:
                            logger_print("似乎被ban, 停止執行")
                            return
                        logger_print("{} 分鐘後再次重試".format(min))
                        time.sleep(min*60)

            else:
                self.push_processed(id,exclude_list_path,exclude_list)
                logger_print("跳過")
            # 15 min 300個用戶查找
            time.sleep(3)
        logger_print("全部名單執行完畢")
    def process_search_no_effect_me(self,exclude_list_path,result_list_path,csv_folder):
        logger_print("執行查找未反追清單任務")
        exclude_list=self.load_processed(exclude_list_path)
        user=None
        try:
            user=self.api.me()
        except Exception as e:
            logger_print("用戶 {} 資料取得錯誤, 跳過".format(id))
            logger_error(e)
        followers_count,friends_count,following=self.get_user_points(user)  
        csv_path="03__me__{}.csv".format(utc_datetime_loaclzone_filename(datetime.now()))  
        try:
            logger_print("取得所有已關注id名單")
            friendsids=list( map(str, user._api.friends_ids(user_id=user.id) ))
            logger_print("{}".format(len(friendsids)))
            logger_print("取得所有跟隨者id名單}")
            followerids=list( map(str, user.followers_ids() ))
            logger_print("{}".format(len(followerids)))
            unfollowerids=list(set(friendsids) - set( followerids))
            logger_print("未反追id名單 {}".format(len(unfollowerids)))

        except Exception as e:
            logger_print("用戶 {} friends資料取得錯誤, 停止".format(id))
            logger_error(e)
        else:
            fullusers = self.get_usernames(unfollowerids,result_list_path,csv_path,csv_folder,lambda user_d: user_d["screen_name"] not in exclude_list)
            logger_print("全部名單執行完畢")
    def process_batch_search(self,search_root_list_path,search_exclude_root_list_path,search_exclude_id_list_path,search_result_list_path,csv_folder,interval_min=1,max_retry=2):
        logger_print("執行查找延伸名單任務")
        exclude_list=self.load_processed(search_exclude_root_list_path)
        exclude_id_list=self.load_processed(search_exclude_id_list_path)
        target_list=self.load_target_list(search_root_list_path)
        if not os.path.exists(csv_folder):
            os.makedirs(csv_folder)
        
        for target in target_list:
            id=target.lower()
            if id in exclude_list:
                logger_print("已存在已執行名單中, 跳過")
                continue
            
            try:
                user=self.get_user(id)
            except Exception as e:
                logger_print("用戶 {} 資料取得錯誤, 跳過".format(id))
                logger_error(e)
                self.push_processed(id,search_exclude_root_list_path,exclude_list)
                continue  
            self.push_processed(id,search_exclude_root_list_path,exclude_list)
            followers_count,friends_count,following=self.get_user_points(user)
            csv_path="01__{}__{}.csv".format(target,utc_datetime_loaclzone_filename(datetime.now()))
            try:
                followerids=self.get_followers(user,followers_count,search_exclude_id_list_path,exclude_id_list)
            except Exception as e:
                logger_print("用戶 {} followers資料取得錯誤, 跳過".format(id))
                logger_error(e)
                continue 
            #Calling the function below with the list of followeids and tweepy api connection details
            fullusers = self.get_usernames(followerids,search_result_list_path,csv_path,csv_folder,check_follower_ratio)
            
            # 15 min 300個用戶查找
            time.sleep(3)
        logger_print("全部名單執行完畢")

    def get_followers(self,user,followers_count,search_exclude_id_list_path,exclude_id_list):
        #followerids =[]
        #Below code will request for 5000 follower ids in one request and therefore will give 75K ids in every 15 minute window (as 15 requests could be made in each window).
        # for ids in tweepy.Cursor(user.followers_ids,count=5000).items():
        #     followerids.append(ids)    
        #     logger_print("取得id名單 {}/{}".format(len(followerids),followers_count))
        # followerids=list( map(str, followerids ))
        logger_print("取得所有follower id名單")
        followerids=list( map(str, user.followers_ids() ))
        x=set(followerids)
        y=set(exclude_id_list)
        nor_list= list(x.difference(y))
        logger_print("排除已搜過id, 新發現id有{}個".format(len(nor_list)))
        logger_print("更新已搜過id名單")
        with open(search_exclude_id_list_path,'a',encoding='utf-8') as f:
            f.write("\n".join(nor_list)+"\n")
        exclude_id_list.extend(nor_list)

        return nor_list
        
    def get_usernames(self,userids,search_result_list_path,csv_path,csv_folder,filter_fn):
        #Below function could be used to make lookup requests for ids 100 at a time leading to 18K lookups in each 15 minute window
        fullusers = []
        u_count = len(userids)
        
        for i in range(int(u_count/100) + 1):            
            end_loc = min((i + 1) * 100, u_count)
            try:
                users_d_list=[ dict(x.__dict__)['_json'] for x in self.api.lookup_users(user_ids=userids[i * 100:end_loc])  ]
                logger_print("進行id轉換成用戶名{}/{}".format(i*100+len(users_d_list),u_count))

                self.dump_csv(users_d_list,csv_path,csv_folder)
                filtered=[ x["screen_name"] for x in filter(filter_fn, users_d_list)]

                logger_print("篩選用戶後剩{}".format(len(filtered)))

                with open(search_result_list_path,'a',encoding='utf-8') as f:
                    f.write("\n".join(filtered)+"\n")
                fullusers.extend(filtered)
            except Exception as e:
                logger_error(e)
                logger_print('錯誤, 停止執行')

    def dump_csv(self,users_d_list,csv_path,csv_folder):
        path=os.path.join(csv_folder,csv_path)
        if os.path.isfile(path): 
            isHeader=False
            mode="a"
        else:
            isHeader=True
            mode="w"
        title = "screen_name,name,friends_count,followers_count,protected,location,id_str,description".split(",") # quick hack
        # with open(csv_path,mode,newline="",encoding='utf-8') as f:  
        #     
        #     cw = csv.DictWriter(f,title,delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL,extrasaction='ignore')
        #     if isHeader:
        #         cw.writeheader()
        #     cw.writerows(users_d_list)
        df=pd.DataFrame(users_d_list,columns =title )
        df.to_csv(path,mode=mode,header=isHeader)
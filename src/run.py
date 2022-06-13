import src.tweepyBot as tBot
import yaml

# Authenticate to Twitter
key_path='../key.yaml'
# 產生csv資料夾
csv_folder='../csv'


#任務1 
# 搜尋跟隨者根名單
search_root_list='../01_root_list.txt'
# 排除根名單 (已搜尋)
search_exclude_root_list='../01_exclude_root_list.txt'
# 排除ID (重複搜到ID)
search_exclude_id_list='../01_exclude_id_list.txt'
# 搜到名單
search_result_list='../01_result_list.txt'


#任務2 
# 關注目標名單
follow_target_list='../02_target_list.txt'
# 排除關注目標名單 (已關注)
follow_exclude_list='../02_exclude_list.txt'

#任務3
# 未反追結果名單
notfollowback_result_list='../03_result_list.txt'
# 未反追篩選排除名單
notfollowback_exclude_list='../03_exclude_list.txt'


#任務4 
# 取消關注目標名單
unfollow_target_list='../04_target_list.txt'
# 排除執行名單 
unfollow_exclude_list='../04_exclude_list.txt'


# 執行入口
def main():
    with open(key_path, 'r') as f:
        key_d = yaml.load(f)
    tb=tBot.TweepyBot(key_d["api_key"],key_d["api_key_secret"],key_d["access_token"],key_d["access_token_secret"])
    print("""任務選擇:
    0:測試金鑰
    1:執行查找延伸名單任務
    2:執行關注任務
    3:執行查找未反關注名單任務
    4:執行取消關注任務
    """)
    task=input("請輸入任務編號: ")
    
    if task=="0":
        tb.test_key()
    elif task=="1":
        tb.process_batch_search(search_root_list,search_exclude_root_list,search_exclude_id_list,search_result_list,csv_folder)
    elif task=="2":
        tb.process_batch_follow(follow_target_list,follow_exclude_list,interval_min=0.5)
    elif task=="3":
        tb.process_search_no_effect_me(notfollowback_exclude_list,notfollowback_result_list,csv_folder)
    elif task=="4":
        tb.process_batch_unfollow(unfollow_target_list,unfollow_exclude_list,interval_min=0.5)
    else:
        print("無此任務, 退出程式")
    

    

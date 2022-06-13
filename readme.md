
簡單推特跟隨機器人

* Key  
首先申請推特APP,  並且開啟可讀可寫權限  
然後在key.yaml內設定  

*打包exe
** 執行build.cmd打包

*打包後
** 執行run.cmd開始程式


** 0:測試金鑰任務  
測試key是否可用  

** 1:執行查找延伸名單任務  
***輸入  
# 搜尋跟隨者根名單, 會掃描這名單所有人的跟隨者  
search_root_list.txt   

***輸出  
# 排除根名單 (已搜尋過的根名單,避免重複搜尋)  
search_exclude_root_list.txt  
# 排除ID (已搜尋過的跟隨者ID,避免重複搜尋)  
search_exclude_id_list.txt  

***結果   
# 搜到名單, 已經過重複ID排除以及條件篩選後的結果  
search_result_list.txt  
# 詳細名單資訊, 已經過重複ID排除, 依照根目標產生的所有追隨者資料  
./csv/**.csv  



** 2:執行關注任務  
***輸入   
# 關注目標名單  
batch_follow_target_list.txt  

***輸出  
# 排除關注目標名單 (已經關注過的名單)
batch_follow_exclude_list.txt  


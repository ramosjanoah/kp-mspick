#!/bin/bash

def=(30)
sf=(1.4)
qpf=(linear)
tf=(sigmoid)
counter=0
for i in ${sf[@]}
do
	for j in ${def[@]}
	do
		for k in ${tf[@]}
		do
			for l in ${qpf[@]}
			do
				osascript -e 'tell application "Terminal" to do script "cd /Users/raudi/Documents/BukaLapak/DataScientist/MainSupplierPicker/\npython GridSearch.py -p -qpf '"${l}"' -tf '"${k}"' -sf '"${i}"' -df '"${j}"' -o result_p_'"${l}"'_tf_'"${k}"'_sf_'"${i}"'_df_'"${j}"'.csv"' &
				wait
				osascript -e 'tell application "Terminal" to do script "cd /Users/raudi/Documents/BukaLapak/DataScientist/MainSupplierPicker/\npython GridSearch.py -q -qpf '"${l}"' -tf '"${k}"' -sf '"${i}"' -df '"${j}"' -o result_q_'"${l}"'_tf_'"${k}"'_sf_'"${i}"'_df_'"${j}"'.csv"' &
				wait
				osascript -e 'tell application "Terminal" to do script "cd /Users/raudi/Documents/BukaLapak/DataScientist/MainSupplierPicker/\npython GridSearch.py -p -q -qpf '"${l}"' -tf '"${k}"' -sf '"${i}"' -df '"${j}"' -o result_p_q_'"${l}"'_tf_'"${k}"'_sf_'"${i}"'_df_'"${j}"'.csv"' &
				wait
			done
			osascript -e 'tell application "Terminal" to do script "cd /Users/raudi/Documents/BukaLapak/DataScientist/MainSupplierPicker/\npython GridSearch.py -tf '"${k}"' -sf '"${i}"' -df '"${j}"' -o result_tf_'"${k}"'_sf_'"${i}"'_df_'"${j}"'.csv"' &
		done
	done
done

# for j in ${def[@]}
# do
# 	for k in ${tf[@]}
# 	do
# 		for l in ${qpf[@]}
# 		do
# 			osascript -e 'tell application "Terminal" to do script "cd /Users/raudi/Documents/BukaLapak/DataScientist/MainSupplierPicker/\npython GridSearch.py -p -qpf '"${l}"' -tf '"${k}"' -df '"${j}"' -o result_p_'"${l}"'_tf_'"${k}"'_df_'"${j}"'.csv"'
# 			osascript -e 'tell application "Terminal" to do script "cd /Users/raudi/Documents/BukaLapak/DataScientist/MainSupplierPicker/\npython GridSearch.py -q -qpf '"${l}"' -tf '"${k}"' -df '"${j}"' -o result_q_'"${l}"'_tf_'"${k}"'_df_'"${j}"'.csv"'
# 			osascript -e 'tell application "Terminal" to do script "cd /Users/raudi/Documents/BukaLapak/DataScientist/MainSupplierPicker/\npython GridSearch.py -p -q -qpf '"${l}"' -tf '"${k}"' -df '"${j}"' -o result_p_q_'"${l}"'_tf_'"${k}"'_df_'"${j}"'.csv"'
# 			wait
# 		done
# 		osascript -e 'tell application "Terminal" to do script "cd /Users/raudi/Documents/BukaLapak/DataScientist/MainSupplierPicker/\npython GridSearch.py -tf '"${k}"' -df '"${j}"' -o result_tf_'"${k}"'_df_'"${j}"'.csv"'	
# 	done
# done
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
				(echo cd /Users/raudi/Documents/BukaLapak/Data$'\ 'Scientist/MainSupplierPicker/$'\n'python GridSearch.py -p -qpf ${l} -tf ${k} -sf ${i} -df ${j} -o result_p_${l}_tf_${k}_sf_${i}_df_${j}.csv > ${counter}.command; chmod +x ${counter}.command; open ${counter}.command) &&
				counter=$((counter+1)) &&
				(echo cd /Users/raudi/Documents/BukaLapak/Data$'\ 'Scientist/MainSupplierPicker/$'\n'python GridSearch.py -q -qpf ${l} -tf ${k} -sf ${i} -df ${j} -o result_q_${l}_tf_${k}_sf_${i}_df_${j}.csv > ${counter}.command; chmod +x ${counter}.command; open ${counter}.command) &&
				counter=$((counter+1)) &&
				(echo cd /Users/raudi/Documents/BukaLapak/Data$'\ 'Scientist/MainSupplierPicker/$'\n'python GridSearch.py -p -q -qpf ${l} -tf ${k} -sf ${i} -df ${j} -o result_p_q_${l}_tf_${k}_sf_${i}_df_${j}.csv > ${counter}.command; chmod +x ${counter}.command; open ${counter}.command) &&
				counter=$((counter+1)) &&
				wait
			done
			(echo cd /Users/raudi/Documents/BukaLapak/Data$'\ 'Scientist/MainSupplierPicker/$'\n'python GridSearch.py -tf ${k} -sf ${i} -df ${j} -o result_tf_${k}_sf_${i}_df_${j}.csv > ${counter}.command; chmod +x ${counter}.command; open ${counter}.command) &&
			counter=$((counter+1))
		done
	done
done

for j in ${def[@]}
do
	for k in ${tf[@]}
	do
		for l in ${qpf[@]}
		do
			(echo cd /Users/raudi/Documents/BukaLapak/Data$'\ 'Scientist/MainSupplierPicker/$'\n'python GridSearch.py -p -qpf ${l} -tf ${k} -df ${j} -o result_p_${l}_tf_${k}_df_${j}.csv > ${counter}.command; chmod +x ${counter}.command; open ${counter}.command) &
			counter=$((counter+1))
			(echo cd /Users/raudi/Documents/BukaLapak/Data$'\ 'Scientist/MainSupplierPicker/$'\n'python GridSearch.py -q -qpf ${l} -tf ${k} -df ${j} -o result_q_${l}_tf_${k}_df_${j}.csv > ${counter}.command; chmod +x ${counter}.command; open ${counter}.command) &
			counter=$((counter+1))
			(echo cd /Users/raudi/Documents/BukaLapak/Data$'\ 'Scientist/MainSupplierPicker/$'\n'python GridSearch.py -p -q -qpf ${l} -tf ${k} -df ${j} -o result_p_q_${l}_tf_${k}_df_${j}.csv > ${counter}.command; chmod +x ${counter}.command; open ${counter}.command) &
			counter=$((counter+1))
			wait
		done
		(echo cd /Users/raudi/Documents/BukaLapak/Data$'\ 'Scientist/MainSupplierPicker/$'\n'python GridSearch.py -tf ${k} -df ${j} -o result_tf_${k}_df_${j}.csv > ${counter}.command; chmod +x ${counter}.command; open ${counter}.command) &
		counter=$((counter+1))
	done
done

# open sayhi.command & open sayhi.command & 
# wait 
# open sayhi.command &

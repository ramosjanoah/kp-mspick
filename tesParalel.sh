#!/bin/bash

sf=(2.0)	
qpf=(nonlinear)
tf=(sigmoid)

for i in ${sf[@]}
do
	for k in ${tf[@]}
	do
		for l in ${qpf[@]}
		do
			xterm -title "App 1" -hold -e python gridding.py -p -sf -o result_p_${l}_tf_${k}_sf_${i}.csv &
			xterm -title "App 2" -e python gridding.py -q -sf -o result_q_${l}_tf_${k}_sf_${i}.csv &
			xterm -title "App 3" -e python gridding.py -p -q -sf -o result_p_q_${l}_tf_${k}_sf_${i}.csv &
			wait
		done
		xterm -title "App 4" -e python gridding.py -sf -o result_tf_${k}_sf_${i}.csv &
	done
done

for k in ${tf[@]}
do
	for l in ${qpf[@]}
	do
		xterm -title "App 1" -e python gridding.py -p -o result_p_${l}_tf_${k}.csv &
		xterm -title "App 2" -e python gridding.py -q -o result_q_${l}_tf_${k}.csv &
		xterm -title "App 3" -e python gridding.py -p -q -o result_p_q_${l}_tf_${k}.csv &
		wait
	done
	xterm -title "App 4" -e python gridding.py -o result_tf_${k}.csv &
done
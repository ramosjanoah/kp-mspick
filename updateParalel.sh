#!/bin/bash

xterm -title "Update P" -e ython updateDenGraph.py -p &
xterm -title "Update Q" -e python updateDenGraph.py -q &
xterm -title "Update S" -e python updateDenGraph.py -s &
xterm -title "Update D" -hold -e python updateDenGraph.py -d
xterm -title "Update PQ" -e python updateDenGraph.py -p -q &
xterm -title "Update PS" -e python updateDenGraph.py -p -s &
xterm -title "Update PD" -e python updateDenGraph.py -p -d &
xterm -title "Update QS" -hold -e python updateDenGraph.py -q -s 
xterm -title "Update QD" -e python updateDenGraph.py -q -d & 
xterm -title "Update SD" -e python updateDenGraph.py -s -d & 
xterm -title "Update PQS" -e python updateDenGraph.py -p -q -s &
xterm -title "Update PQD" -hold -e python updateDenGraph.py -p -q -d
xterm -title "Update PSD" -e python updateDenGraph.py -p -s -d &
xterm -title "Update QSD" -e python updateDenGraph.py -p -s -d &
xterm -title "Update PQSD" -e python updateDenGraph.py -p -q -s -d &
xterm -title "Update N" -e python updateDenGraph.py -n

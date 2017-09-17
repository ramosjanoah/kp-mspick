import pandas as pd
import dengraph_lib as dg

for Quantity in range(2):
    for Price in range(2):
        for SubsFactor in range(2):
            for usingDays in range(2):
                # hack
                if not usingDays:
                    continue
                # --
                universe = {}
                trx_file = "data/weight/weight"
                optimal_file = "data/optimalSearch/suffixOptimalSearch"
                suffix = ""
                if Price:
                    trx_file += "_price"
                    optimal_file += "_p"
                    suffix += "_p"
                if Quantity:
                    trx_file += "_quantity"
                    optimal_file += "_q"
                    suffix += "_q"
                if SubsFactor:
                    trx_file += "_subs"
                    subs_str = "2.0"
                    optimal_file += "_s"
                    suffix += "_s"
                else:
                    subs_str = "1.1"
                if usingDays:
                    optimal_file += "_d"
                    suffix += "_d"

                print "Making for suffix + " + suffix + ".."

                state_folder = "data/subs_"+subs_str+"_days_30"
                #state_folder = "subs_1.1_days_30"
                
                trx_file += ".csv"
                optimal_file+= ".csv"

                print "TRX FILE     : " + trx_file 
                print "OPTIMAL FILE : " + optimal_file  
                print "STATE FOLDER : " + state_folder
                
                dg.readMaxStateData(state_folder+"/maxStateWriterWeight.csv")
                dg.readStateData(state_folder+"/stateWriterWeight.csv")


                trx = pd.read_csv(trx_file)
                dg.inputTransactionDataFrameToGraph(df = trx, world = universe, Init=True, useDaysFactor=usingDays, sigmoid = True)

                optimal = pd.read_csv(optimal_file)                
                for index, row in optimal.iterrows():
                    if not row['Category'] == 1834.0:
                        continue
                    universe[row['Category']].MAX_DISTANCE = row['MD']
                    universe[row['Category']].MIN_NEIGHBOR = row['MN']
                    universe[row['Category']].MIN_HARMONIC = row['MH']
                    universe[row['Category']].denGraphClustering()
                    save_name = 'graph/' + str(row['Category']) + suffix
                    print save_name
                    universe[row['Category']].Save(save_name)

                #dg.writeMaxStateToFile(state_folder+"/maxStateWriterWeight.csv")
                #dg.writeStateToFile(state_folder+"/stateWriterWeight.csv")
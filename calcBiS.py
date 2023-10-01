import pandas as pd
import numpy as np

#constants
sheet_url = "https://docs.google.com/spreadsheets/d/1xo0kjlG319TQK2Zgz7Bx0HPuTU6iYA9fWA90oOQB87s/export?format=csv&gid=1672145508" #1672145508
cols = ["Item Name","Drops From","Item Type","Item LVL","Main Stat 1","MS 1 Value","Main Stat 2","MS 2 Value","Sec Stat 1","SS 1 Value","Sec Stat 2","SS 2 Value","Extra Stat","ES Value"]

stats_cols = ["Main Stat 1",
              "Main Stat 2",
              "Sec Stat 1",
              "Sec Stat 2",
              "Extra Stat"]

stats_prio = {"Health"     :10,
              "Utility"    :0,
              "Armor"      :7,
              "Spell Power":5,
              "Might"      :0,
              "Mastery"    :10,
              "Quickness"  :1,
              "Alacrity"   :0,
              "Crit Chance":0,
              "Crit Force" :0,
              "Versatility":1,
              "Resource"   :3,
              np.nan       :0}

min_stat_values = {"Health"     :800,
                   "Armor"      :15,
                   "Spell Power":55}


def calcBis(gsheet, stats_prio):
    df = gsheet.copy(deep=True)
    #set stat to stat prio, nan to 0 
    for stat in stats_cols:
        df[stat] = df[stat].apply(lambda x : stats_prio[x])

    # Sum up Prios    
    df["Sum"] = df[stats_cols].sum(axis=1)

    # magic
    bis_items = df.sort_values("Sum", ascending = False).drop_duplicates(subset=["Item Type"], keep="first")

    return bis_items


def calcStatValues(bis_items):
    # get original data for bis_items
    true_bis_items = gsheet.iloc[bis_items.index][["Main Stat 1","MS 1 Value","Main Stat 2","MS 2 Value","Sec Stat 1","SS 1 Value","Sec Stat 2","SS 2 Value","Extra Stat","ES Value"]]
    ms1 = true_bis_items.groupby(true_bis_items["Main Stat 1"]).aggregate({"MS 1 Value":"sum"})
    ms2 = true_bis_items.groupby(true_bis_items["Main Stat 2"]).aggregate({"MS 2 Value":"sum"})
    ss1 = true_bis_items.groupby(true_bis_items["Sec Stat 1"]).aggregate({"SS 1 Value":"sum"})
    ss2 = true_bis_items.groupby(true_bis_items["Sec Stat 2"]).aggregate({"SS 2 Value":"sum"})
    es1 = true_bis_items.groupby(true_bis_items["Extra Stat"]).aggregate({"ES Value":"sum"}).dropna()

    # yes
    true_bis_itemsStats = pd.concat([ms1, ms2, ss1, ss2, es1]) \
                          .fillna(0) \
                          .groupby(level=0) \
                          .aggregate({"MS 1 Value":"sum", "MS 2 Value":"sum",  "SS 1 Value":"sum", "SS 2 Value":"sum", "ES Value":"sum"}) \
                          .apply(pd.Series.sum, axis=1)
    
    return true_bis_itemsStats



# Prints out which Bosses to farm for BiS
if __name__ == "__main__":
    #read necessary cols
    gsheet = pd.read_csv(sheet_url, usecols=cols).dropna(subset = [cols[0]])
    #df[stats_cols].stack().dropna().drop_duplicates().reset_index(drop=True)
    
    user_sp = stats_prio
    user_mv = min_stat_values

    bis_items = calcBis(gsheet=gsheet, stats_prio=user_sp)
    true_bis_itemsStats = calcStatValues(bis_items=bis_items)
    search_bis = True
    while True:
        miss_min = False
        for k, v in user_mv.items():
            if true_bis_itemsStats.loc[k] < v:
                miss_min = True
                user_sp[k] += 1
                print(f"{k} is not > {v}")
                print(f"\n\n {user_sp}")
        
        if miss_min:
            bis_items = calcBis(gsheet=gsheet, stats_prio=user_sp)
            true_bis_itemsStats = calcStatValues(bis_items=bis_items)
        else:
            break

        


    print(bis_items[["Item Type", "Item LVL", "Item Name", "Drops From"]])
    print(f"\nTotal Stats from Items: \n{true_bis_itemsStats}")
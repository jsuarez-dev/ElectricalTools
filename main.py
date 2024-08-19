
import pandas as pd
import sys

CB_RULES = [
    {
        "low": 0,
        "high": 6,
        "value": "CB-C6"
    },
    {
        "low": 6,
        "high": 10,
        "value": "CB-C10"
    },
    {
        "low": 10,
        "high": 16,
        "value": "CB-C16"
    },
    {
        "low": 16,
        "high": 20,
        "value": "CB-C20"
    },
    {
        "low": 20,
        "high": 25,
        "value": "CB-C25"
    },
    {
        "low": 25,
        "high": 32,
        "value": "CB-C32"
    },
    {
        "low": 32,
        "high": 40,
        "value": "CB-C40"
    },
    {
        "low": 40,
        "high": 50,
        "value": "CB-C50"
    },
    {
        "low": 50,
        "high": 63,
        "value": "CB-C63"
    },
]



def calculate_cb(row):
    V = row["V"]
    I = row["I"]

    if V == "240V/1P":
        for rule in CB_RULES:
            if rule["low"] <= I and rule["high"] > I:
                return f"{rule['value']}-1P"
        
    elif V == "415V/3P":
        for rule in CB_RULES:
            if rule["low"] <= I and rule["high"] > I:
                return f"{rule['value']}-3P"



def main():
    # Read the CSV file
    df = pd.read_csv('data/elect_data.csv')
    #
    df = df.sort_values(by=['V', 'I(A)'], ascending=[False, False])


    value_counts = df['Name'].value_counts()

    
    repeated_values = value_counts[value_counts > 1]


    if len(repeated_values) > 0:
        print("error - name has to be unique")
        sys.exit(1)


    data = []

    l1, l2, l3 = (0,0,0)
    for _, row in df.iterrows():

        if row["V"] == "240V/1P":
            if l1 == 0 and l2 == 0 and l3 == 0:
                l1 = row["I(A)"]
            elif l1 > 0:
                l2 = row["I(A)"]
                l1 = 0
            elif l2 > 0:
                l3 = row["I(A)"]
                l2 = 0
            elif l3 > 0:
                l1 = row["I(A)"]
                l3 = 0
            
            new_row = {
                "Name": row["Name"],
                "Designation":row["Designation"], 
                "L1": l1, 
                "L2": l2,
                "L3": l3,
                "I": row["I(A)"],
                "V": row["V"],
                "P": row["Power(kw)"]

            }
            data.append(new_row)
        elif row["V"] == "415V/3P":
            new_row = {
                "Name": row["Name"],
                "Designation":row["Designation"], 
                "L1": row["I(A)"], 
                "L2": row["I(A)"],
                "L3": row["I(A)"],
                "I": row["I(A)"],
                "V": row["V"],
                "P": row["Power(kw)"]

            }
            data.append(new_row)

    db_df = pd.DataFrame(data)

    db_df["CB"] = db_df.apply(calculate_cb,axis=1)

    db_acs = db_df[(db_df["Designation"].str.contains(r".*AC.*", regex=True))]


    db_acs.reset_index(inplace=True)

    data = []

    l1, l2, l3 = (0,0,0)
    current_AC_count = 0 
    count = 0
    name=""
    for index , row in db_acs.iterrows():

        print(index)
        if row["V"] == "240V/1P":

            if current_AC_count > 16 or index == len(db_acs.index)-1:
                count += 1
                if l1 == 0 and l2 == 0 and l3 == 0:
                    l1 = current_AC_count
                elif l1 > 0:
                    l2 = current_AC_count
                    l1 = 0
                elif l2 > 0:
                    l3 = current_AC_count
                    l2 = 0
                elif l3 > 0:
                    l1 = current_AC_count
                    l3 = 0
                
                new_row = {
                    "Name": name,
                    "Designation": f"Group {count} of AC", 
                    "L1": l1, 
                    "L2": l2,
                    "L3": l3,
                    "I": current_AC_count,
                    "V": row["V"],
                    "P": row["P"]

                }
                data.append(new_row)
                current_AC_count = 0
                name = ""
            else:
                name += f"{row['Name']}--"
                current_AC_count += row["I"]

        elif row["V"] == "415V/3P":
            new_row = {
                "Name": row["Name"],
                "Designation":row["Designation"], 
                "L1": row["I"], 
                "L2": row["I"],
                "L3": row["I"],
                "I": row["I"],
                "V": row["V"],
                "P": row["P"]

            }
            data.append(new_row)

    db_acs_t = pd.DataFrame(data)

    db_acs = db_df[(db_df["Designation"].str.contains(r".*CU.*", regex=True))]


    print(pd.concat([db_acs,db_acs_t], ignore_index=True))


if __name__ == "__main__":
    main()




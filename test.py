import pandasai as pai

df = pai.read_csv("bmc_sample.csv")
res = df.chat("Could you give a summary of the torque trend in the past 24 hrs?")
print(res)

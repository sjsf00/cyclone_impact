import pandas as pd

tc_china_from_2025 = pd.read_excel('tc_china_from_2015.xlsx',header=None).ffill()

tc_china_from_2025.columns = [tc_china_from_2025.iloc[0, i] if tc_china_from_2025.iloc[0, i] == tc_china_from_2025.iloc[1, i] else str(tc_china_from_2025.iloc[0, i]) + str(tc_china_from_2025.iloc[1, i]) for i in range(tc_china_from_2025.shape[1])]

tc_china_from_2025 = tc_china_from_2025.iloc[2:].reset_index(drop=True)


tc_china_from_2025_cleaned = tc_china_from_2025.loc[(tc_china_from_2025['登陆时强度等级'] != 'TD') & (tc_china_from_2025['登陆省份'] != '台湾'),:]
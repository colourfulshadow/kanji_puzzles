from functions import read_sheet
import pandas as pd

grade6 = read_sheet('kanji_database1.xlsx', 6)
grade6 = grade6.loc[:, 'grade']
print(grade6)

writer = pd.ExcelWriter('kanji_database_new.xlsx')
grade6.to_excel(writer)
writer.save()

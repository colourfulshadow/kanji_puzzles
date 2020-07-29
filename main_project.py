import functions

functions.printing(functions.create_puzzle(*functions.choose_reading_and_writings(
    functions.transform_dataframe(functions.read_excel('kanji_database_new.xlsx')))))


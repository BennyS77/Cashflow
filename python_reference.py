## LISTS
list1 = ['a','b']
list2 = ['c','d']
my_list = list1 + list2
print(my_list)


## DATAFRAMES
# GROUPING
df_1 = 'a_dataframe'
df_1 = df_1.groupby(['Cost_Item']).apply(lambda x: x.sum())
df_1 = df_1.groupby(['cost_item']).agg({'EAC':['sum'],'Division':['first'],'Cost_Item_Description':['first']})

# DROP A COLUMN (ie axis=1) LABEL LEVEL
df_1 = df_1.droplevel(level=1, axis=1)

# RESET ROW INDEX TO BE A COLUMN
df_1.reset_index(level=0, inplace=True)

# DROP DUPLICATES - returns dataframe with unique rows based on 'cost_item'
df_1.drop_duplicates(subset = 'cost_item', inplace=True)

# SHOWS THE INDEX VALUES OF THE DATAFRAME
df_1.index
# SHOWS THE COLUMN NAME VALUES OF THE DATAFRAME
df_1.columns


## DICTIONARY
dict_1 = {'a':1}
dict_1.update({'b':2, 'c':3})
print(dict_1)

# ITERATE THROUGH DICTIONARY
for key in dict_1:
    print(key, dict_1[key])
for item in dict_1.items():
    print(item)  # a tuple
for key, value in dict_1.items():
    print(key, value)

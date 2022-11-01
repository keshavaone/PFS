import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
import datetime as dt
import math

original_values_plot = False
INCOME_BANK = 'SBI Bank'
json_file_path = r'C:\Users\iamke\OneDrive\Important\Codes\Python Scripts\iPynbs\Practice\EXPENSES.json'
import_file_location = r"C:\Users\iamke\OneDrive\Important\Codes\Python Scripts\iPynbs\Practice\Personal Financial Analysis.xlsx"
index_data = ['Category','Category Sub Type(CST)']
category_transaction_pivot = 'category_transaction_pivot.xlsx'
Expense_Analysis = 'CTGRY and CST Analysis.xlsx'
sheet_names = ['ctgry','cst']
sub_cols_names = ['Amount','Total Visits','Amount Per Visit','Quantity','Amount Per Quantity','Total Days','Amount Per Day','Visit/s Per Day','Quantity Per Day']
path = "C:\\Users\\iamke\\OneDrive\\Important\\Codes\\Python Scripts\\iPynbs\\Practice\\"+Expense_Analysis
writer = pd.ExcelWriter(path, engine = 'xlsxwriter')


##data pre-processing
df = pd.read_excel(import_file_location,"Expense Sheet") # sheet import and import only one sheet: Expense Sheet
df = df.iloc[:,0:8] #slicing the data to specific columns

borrow_lend_transactions = df[df['Payment Through'] == 'LB Wallet']
lend_transactions = borrow_lend_transactions[borrow_lend_transactions['Expenses']=='Lend']
borrow_transactions = borrow_lend_transactions[borrow_lend_transactions['Expenses']=='Borrow']
lend_transactions_cleared = borrow_lend_transactions[borrow_lend_transactions['Expenses']=='Lend - Clear']
borrow_transactions_cleared = borrow_lend_transactions[borrow_lend_transactions['Expenses']=='Borrow - Clear']

TOTAL_DAYS = (df.iloc[-1,0]-df.iloc[0,0]).days #last date - first date
payment_throughs = np.unique(df.iloc[0:-1,-1]) # last column

transaction_types = np.unique(df.iloc[0:-1,1]) # second column
transaction_categories = np.unique(df.iloc[0:-1,4]) # 5th column

all_incomes = df[df['Payment Through']==INCOME_BANK] #all incomes
all_incomes = pd.DataFrame(all_incomes)

all_expenses = df[df['Payment Through'].str.startswith('Paytm')==True]
all_expenses = pd.concat([all_expenses,df[df['Payment Through']=='Cash']])
all_expenses = all_expenses.sort_values(['Date'])

#data processing and visualize
#frequency of transactions by Days
all_expenses['Date'].value_counts().hist(bins = 20)
plt.title('1. Expense Frequency Distribution')
plt.xlabel('Expense Frequency')
plt.ylabel('Days')
plt.grid(False)
plt.figtext(.4,.5,'Expense Frequency Per Day is '+str(round(pd.DataFrame(all_expenses['Date'].value_counts()).mean()[0],2)))
plt.show()

#frequency of transactions by Category
#creating dataframe for the expense category value counts
PIE_COLUMNS = ['Category','Category Sub Type(CST)','Expenses']
TITLE_NAMES = ['2.1 Expense Category Distribution', '2.2 Expense by Visit Distribution','2.3 Expenses by Expense Type Distribution']
for i in range(len(PIE_COLUMNS)):
    category_frquencies = pd.DataFrame(all_expenses[PIE_COLUMNS[i]].value_counts().head(8))
    category_frquencies.plot(kind='pie',subplots=True,figsize=(8,8),legend=False,autopct='%1.0f%%')
    plt.title(TITLE_NAMES[i])
    plt.show()

GROUPBY_COLUMN = 'Category'

#Weekend  and Weekday Transactions
weekend_dates = [i for i in all_expenses['Date'] if i.weekday() >= 5]
weekday_dates = [i for i in all_expenses['Date'] if i.weekday() < 5]
weekend_expenses = pd.DataFrame()
weekday_expenses = pd.DataFrame()

for i in range(len(weekend_dates)):
    weekend_expenses =pd.concat([weekend_expenses,all_expenses[all_expenses['Date'] == weekend_dates[i]]])
for i in range(len(weekday_dates)):
    weekday_expenses = pd.concat([weekday_expenses,all_expenses[all_expenses['Date'] == weekday_dates[i]]])
    
weekday_expenses = weekday_expenses.drop_duplicates()
weekend_expenses = weekend_expenses.drop_duplicates()

#Highest Weekend-Week Day Expense Category Contribution
weekend_category_expenses = pd.DataFrame(weekend_expenses.groupby([GROUPBY_COLUMN])['Amount'].sum()).sort_values(['Amount'],ascending=False)
weekday_category_expenses = pd.DataFrame(weekday_expenses.groupby([GROUPBY_COLUMN])['Amount'].sum()).sort_values(['Amount'],ascending=False)

weekend_category_expenses= weekend_category_expenses.rename(columns={'Amount':'Weekend'})
weekday_category_expenses= weekday_category_expenses.rename(columns={'Amount':'Weekday'})

#concatenating both weekend and weekday category expenses
weekendday_category_expenses = pd.concat([weekend_category_expenses,weekday_category_expenses],axis=1)

#highest category expenditure on weekend
HIGHEST_EXPENDITURE_WEEKEND = weekendday_category_expenses.sort_values(['Weekend'],ascending=False).index[0]

#highest category expenditure on weekday
HIGHEST_EXPENDITURE_WEEKDAY = weekendday_category_expenses.sort_values(['Weekday'],ascending=False).index[0]

#Week Day vs Weekend Transactions
print('--------------------------------------------------------------------------------------')
print('3. Categorical Expenses on Weekday vs Weekend\n',weekendday_category_expenses.describe())
print('\nLegend: \nCount - Total Categories\nMean,std,min,25%,50%,75%,max - Amount in Categories')
print('--------------------------------------------------------------------------------------')

all_expenses_count_df = pd.DataFrame(all_expenses['Date'].value_counts(sort=False)).rename(columns={'Date':'Count'})
NO_EXPENSE_DAYS = TOTAL_DAYS - len(all_expenses_count_df)
EXPENSE_DAYS = TOTAL_DAYS - NO_EXPENSE_DAYS

EXPENSE_MEAN = pd.DataFrame(all_expenses['Date'].value_counts()).mean()[0]
INCOME_MEAN = pd.DataFrame(all_incomes['Date'].value_counts()).mean()[0]

if INCOME_MEAN <=0:
    INCOME_HEALTH_STATUS = "Dead"
elif INCOME_MEAN == 1:
    INCOME_HEALTH_STATUS = "Surviving"
elif INCOME_MEAN >= 2 and INCOME_MEAN <= EXPENSE_MEAN:
    INCOME_HEALTH_STATUS = "Growing and Thrving -- Middle Class"
elif INCOME_MEAN > EXPENSE_MEAN and INCOME_MEAN <= (EXPENSE_MEAN+(EXPENSE_MEAN/2)):
    INCOME_HEALTH_STATUS = "Highly Growing and Recovering -- Upper Middle Class"
else:
    INCOME_HEALTH_STATUS = "Rapid Growth and Completely Healthy -- Rich Class"

print('\n4. Expense Heart Rate Graph is Daily Expense Transactions Activity')
all_expenses_count_df.plot(figsize=(40,10))
plt.title('Expense Heart Rate')
plt.xlabel('Date')
plt.figtext(.4,0.8,'Expense Frequency Per Day is '+str(round(EXPENSE_MEAN,2)))
plt.ylabel('Expense Rate')
plt.show()

all_expenses_reindexed = all_expenses.copy()
all_expenses_reindexed.index = all_expenses['Date']
all_expenses_reindexed.resample('M')['Amount'].mean().plot(figsize=(12,7))
for i in range(len(all_expenses_reindexed.resample('M')['Amount'].mean().index)):
    plt.text(all_expenses_reindexed.resample('M')['Amount'].mean().index[i],all_expenses_reindexed.resample('M')['Amount'].mean().values[i],round(all_expenses_reindexed.resample('M')['Amount'].mean().values[i]))
plt.title('Expenses Mean by Amount')
plt.ylabel('Amount')
plt.show()

only_transactions = df[df['Payment Through'] != 'Time'] # removing the data that column have Time
only_transactions = only_transactions[only_transactions['Expenses']!='Success-NPS'] # also removing data that data having Success-NPS
only_transactions_expenses = all_expenses[all_expenses['Expenses']!='Success-NPS']
only_transactions_expenses = only_transactions_expenses.sort_index()
only_transactions = only_transactions.sort_index()


# only_transactions_expenses['Amount'].resample('M').mean().plot(style="-o", figsize=(10, 5))
only_transactions_expenses_dateindex = only_transactions_expenses.copy()
only_transactions_expenses_dateindex.index = only_transactions_expenses['Date']
only_transactions_expenses_dateindex.resample('M')['Amount'].sum().plot(style="-o", figsize=(12, 7))
for i in range(len(only_transactions_expenses_dateindex.resample('M')['Amount'].sum().values)):
    plt.text(only_transactions_expenses_dateindex.resample('M')['Amount'].sum().index[i],only_transactions_expenses_dateindex.resample('M')['Amount'].sum().values[i],round(only_transactions_expenses_dateindex.resample('M')['Amount'].sum().values[i]))
plt.figtext(0.45,0.35,'Expense Mean Per Month: '+str(round(only_transactions_expenses_dateindex.resample('M')['Amount'].sum().mean(),2)))
plt.xlabel('Month')
plt.ylabel('Amount')
plt.title('Expense Amount Per Month')
plt.show()
print('Expense Mean per Month:',round(only_transactions_expenses_dateindex.resample('M')['Amount'].sum().mean()))


all_incomes_count_df = pd.DataFrame(all_incomes['Date'].value_counts(sort=False)).rename(columns={'Date':'Count'})
print('\n5. Income Heart Rate Graph is Daily Income Transactions Activity')
all_incomes_count_df.plot(figsize=(40,10))
plt.title('Income Heart Rate')
plt.figtext(.4,0.8,'Income Frequency per day is '+(str(round(INCOME_MEAN,2)))+' and your income is '+INCOME_HEALTH_STATUS)
plt.xlabel('Date')
plt.ylabel('Income Rate')
plt.show()
print('--------------------------------------------------------------------------------------')
def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


print('--------------------------------------------------------------------------------------')
print('|6. Cross Tab Analysis on Expenses, Quantity, CST, Category with Amount has Started...')
column_data = 'Expenses'
for i in range(len(index_data)):
    
    print('|\tStep 1: Creating Pivot Tables...',index_data[i])
    #Step 1: Creating Pivot Tables
    #pivoting the cst vs transactions keeping amount as values
    cst_vs_transactions_pivot = pd.crosstab(index=[only_transactions[index_data[i]]],columns=only_transactions[column_data],values=only_transactions[sub_cols_names[0]],aggfunc=sum,margins=True).fillna("")
    #pivoting cst and expenses keeping amount as values
    cst_vs_only_expenses_pivot = pd.crosstab(index=[only_transactions_expenses[index_data[i]]],columns=only_transactions_expenses[column_data],values=only_transactions_expenses[sub_cols_names[0]],aggfunc=sum,margins=True).fillna("")
    #pivoting the cst count (No of Visits) with expenses
    cst_vs_only_expenses_pivot_count_df = pd.crosstab(index=[only_transactions_expenses[index_data[i]]],columns=only_transactions_expenses[column_data],margins=True).fillna("")
    # concatenating both pivot and count
    cst_pivot_final = pd.concat([cst_vs_only_expenses_pivot_count_df,cst_vs_only_expenses_pivot],axis=1,join='inner')
    #pivoting the expenses with cst keeping Quantity as values
    cst_vs_only_expenses_pivot_quantity = pd.crosstab(index=[only_transactions_expenses[index_data[i]]],columns=only_transactions_expenses[column_data],values=only_transactions_expenses[sub_cols_names[3]],aggfunc=sum,margins=True).fillna("")
    cst_vs_only_expenses_pivot_date = pd.crosstab(index=[only_transactions_expenses[index_data[i]]],columns=only_transactions_expenses[column_data],values=only_transactions_expenses['Date'],aggfunc=set,margins=True).fillna("")
    for l in cst_vs_only_expenses_pivot_date:
        for p in cst_vs_only_expenses_pivot_date.index:
            cst_vs_only_expenses_pivot_date.loc[p,l] = len(cst_vs_only_expenses_pivot_date.loc[p,l])
    cst_vs_only_expenses_pivot_date = cst_vs_only_expenses_pivot_date.replace(0,"")
    print('|\tStep 2: Creating multi indexes...',end="")
    #Step 2: creating multi index for sub_cols_names
    cols_and_subcols1 = pd.MultiIndex.from_product([cst_vs_only_expenses_pivot, [sub_cols_names[0]]]) #multiindex cols created - Amount
    cols_and_subcols2 = pd.MultiIndex.from_product([cst_vs_only_expenses_pivot_count_df, [sub_cols_names[1]]]) #multiindex cols created - Count
    cols_and_subcols3 = pd.MultiIndex.from_product([cst_vs_only_expenses_pivot_count_df, [sub_cols_names[2]]]) #multiindex cols created -  Per Day
    cols_and_subcols4 = pd.MultiIndex.from_product([cst_vs_only_expenses_pivot_quantity, [sub_cols_names[3]]]) #multiindex cols created - Quantity
    cols_and_subcols5 = pd.MultiIndex.from_product([cst_vs_only_expenses_pivot_count_df, [sub_cols_names[4]]]) #multiindex cols created - Per Quantity
    cols_and_subcols6 = pd.MultiIndex.from_product([cst_vs_only_expenses_pivot_date,[sub_cols_names[5]]])
    cols_and_subcols7 = pd.MultiIndex.from_product([cst_vs_only_expenses_pivot_date,[sub_cols_names[6]]])
    cols_and_subcols8 = pd.MultiIndex.from_product([cst_vs_only_expenses_pivot_date,[sub_cols_names[7]]])
    print('Done')
   
    print('|\tStep 3: Creating DataFrames using both Step 1 and Step 2...',end="")
    #Step 3: Creating DataFrames for all step 1 pivot tables with step 2 cols
    df1 =  pd.DataFrame(cst_vs_only_expenses_pivot.values,columns=cols_and_subcols1,index=cst_vs_only_expenses_pivot.index)
    df2 =  pd.DataFrame(cst_vs_only_expenses_pivot_count_df.values,columns=cols_and_subcols2,index=cst_vs_only_expenses_pivot.index)
    df3 = pd.DataFrame("",columns=cols_and_subcols3,index=cst_vs_only_expenses_pivot.index)
    df4 = pd.DataFrame(cst_vs_only_expenses_pivot_quantity.values,columns=cols_and_subcols4,index=cst_vs_only_expenses_pivot.index)
    df5 = pd.DataFrame("",columns=cols_and_subcols5,index=cst_vs_only_expenses_pivot.index)
    df6 = pd.DataFrame(cst_vs_only_expenses_pivot_date,columns=cols_and_subcols6,index=cst_vs_only_expenses_pivot.index)
    df7 = pd.DataFrame("",columns=cols_and_subcols7,index=cst_vs_only_expenses_pivot.index)
    df8 = pd.DataFrame("",columns=cols_and_subcols8,index=cst_vs_only_expenses_pivot.index)
    final_df = df1+df2+df3+df4+df5+df6+df7+df8
    print('Done')
    print('|\tStep 4: Adding data to final DataFrame...',end="")
    #Step 4: adding data to each main column(loop start) and adding data to each sub column(Per Quantity, Amount,Count,Per Day) at a time.
    for j in list(cst_pivot_final.columns):
        final_df[j,sub_cols_names[0]] = cst_vs_only_expenses_pivot[j].values #Amount
        final_df[j,sub_cols_names[1]] = cst_vs_only_expenses_pivot_count_df[j].values #total visits
        final_df[j,sub_cols_names[2]] = round(final_df[j,sub_cols_names[0]].replace("",0).astype(float)/final_df[j,sub_cols_names[1]].replace("",1).astype(float),2) #Per Visit
        final_df[j,sub_cols_names[3]] = cst_vs_only_expenses_pivot_quantity[j].values # Quantity
        final_df[j,sub_cols_names[4]] = round(final_df[j,sub_cols_names[0]].replace("",0).astype(float)/final_df[j,sub_cols_names[3]].replace("",1).astype(float),2) #APPQ
        final_df[j,sub_cols_names[5]] = cst_vs_only_expenses_pivot_date[j].values # total days
        final_df[j,sub_cols_names[6]] = round(final_df[j,sub_cols_names[0]].replace("",0).astype(float)/final_df[j,sub_cols_names[5]].replace("",1).astype(float),2) # Amount Per Day 
        final_df[j,sub_cols_names[7]] = round(final_df[j,sub_cols_names[1]].replace("",0).astype(float)/final_df[j,sub_cols_names[5]].replace("",1).astype(float),2) # Visit Per Day
        final_df[j,sub_cols_names[8]] = round(final_df[j,sub_cols_names[3]].replace("",0).astype(float)/final_df[j,sub_cols_names[5]].replace("",1).astype(float),2) # Quantity Per Day
    final_df = final_df.fillna("").replace(0,"")
    print('Done')
    final_df.rename(columns={'Amount':'Cost','Amount Per Day':'Cost Per Day','Amount Per Quantity':'Cost Per Quantity','Amount Per Visit':'Cost Per Visit'},inplace=True)
    #Step 5: writing data to excel
    print('|\tStep 5: Writing Data into Excel...',end='')
    final_df.to_excel(writer,sheet_name=sheet_names[i]+" vs Expenses",columns=final_df.columns)
    print('Done')
    print('|'+str(i+1)+"/"+str(len(index_data))+" is Done")
writer.save()
writer.close()

print('|Excel File Name: ',Expense_Analysis,'and',category_transaction_pivot,' are created successfully')
print('--------------------------------------------------------------------------------------')

print('Creating Expenses JSON as EXPENSES.json')
JSON_df = df.copy()
for i in range(len(JSON_df)):
    Date = 'new Date('+str(JSON_df.Date[i].year)+','+str(JSON_df.Date[i].month)+','+str(JSON_df.Date[i].day)+')'
    JSON_df['Date'][i] = Date
JSON_df_expenses = JSON_df[(JSON_df['Payment Through']!='SBI Bank') & (JSON_df['Payment Through']!='LB Bank')]
file_path = r'C:\Users\iamke\OneDrive\Important\Codes\Python Scripts\iPynbs\Practice\NEW_DATA.json'
JSON_df_expenses['title'] = JSON_df_expenses['Expenses']+" => "+JSON_df_expenses['Quantity Name']+" => "+JSON_df_expenses['Category Sub Type(CST)']
JSON_df_expenses = JSON_df_expenses.rename(columns=({"Amount":'amount',"Date":'date'})).drop(['Quantity Name','Category','Category Sub Type(CST)','Payment Through','Expenses','Quantity'],axis=1)
JSON_df_expenses['id'] = JSON_df_expenses.index
JSON_df_expenses.to_json(json_file_path,date_format="iso",orient='records',index=True)
print('JSON File has been Created')
for i in only_transactions_expenses_dateindex.resample('W').mean().columns:
    only_transactions_expenses_dateindex.resample('W').mean()[i].plot(figsize=(15,4))
    for j in range(len(only_transactions_expenses_dateindex.resample('W').mean()[i].index)):
        plt.text(only_transactions_expenses_dateindex.resample('W').mean()[i].index[j],only_transactions_expenses_dateindex.resample('W').mean()[i].values[j],round(only_transactions_expenses_dateindex.resample('W').mean()[i].values[j]))
    plt.title('Weekly Mean Expenses by '+i)
    plt.ylabel(i)
    plt.show()
    
# expenses made based on DAY
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
expenses_by_day = only_transactions_expenses.groupby([only_transactions_expenses["Date"].dt.weekday])["Amount"].mean()
expenses_by_day.index = days
expenses_by_day = expenses_by_day.to_frame()
week_day_df = only_transactions_expenses.copy()
week_day_df['Week Day'] = only_transactions_expenses['Date'].dt.weekday
week_day_df = week_day_df.sort_values('Week Day')
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
for i in range(len(np.unique(week_day_df['Week Day']))):
    globals()[days[i]+'_Expenses'] = week_day_df[week_day_df['Week Day']==np.unique(week_day_df['Week Day'])[i]]
    globals()[days[i]+'_Expenses'].index = globals()[days[i]+'_Expenses']['Date']
    del globals()[days[i]+'_Expenses']['Date']
    globals()[days[i]+'_Expenses'].resample('M')['Amount'].mean().plot(style="-o", figsize=(10, 5))
    plt.title(days[i]+' Monthly Mean Expenses')
    plt.xlabel('Month')
    plt.ylabel('Amount')
    for j in range(len(globals()[days[i]+'_Expenses'].resample('M')['Amount'].mean().index)):
        plt.text(globals()[days[i]+'_Expenses'].resample('M')['Amount'].mean().index[j],globals()[days[i]+'_Expenses'].resample('M')['Amount'].mean().values[j],round(globals()[days[i]+'_Expenses'].resample('M')['Amount'].mean().values[j]))
    plt.show()
    if original_values_plot:
        unique_day_df = (globals()[days[i]+'_Expenses']['Amount'].resample('M').count()*globals()[days[i]+'_Expenses']['Amount'].resample('M').mean())
        unique_day_df.plot(style="-o", figsize=(10, 5))
        plt.title(days[i]+' Monthly Expenses by Amount')
        plt.xlabel('Month')
        plt.ylabel('Amount')
        for j in range(len(unique_day_df.index)):
            plt.text(unique_day_df.index[j],unique_day_df.values[j],round(unique_day_df.values[j]))
        plt.show()
        print('-'*72)
    
print('Expense Analysis by Day')
expenses_by_day['Amount'] = round(expenses_by_day['Amount'])
print(expenses_by_day)
print("Expense Per Week on Avg =",round(expenses_by_day['Amount'].sum()))
print('\n')

x = expenses_by_day.index
y = expenses_by_day.values
tickvalues = df.index
plt.figure(figsize = (15,4))
for i in range(len(expenses_by_day.index)):
    plt.text(expenses_by_day.index[i],expenses_by_day.values[i][0],expenses_by_day.values[i][0])
plt.plot(x,y)
plt.title('Expenses by Day')
plt.xlabel('Days')
plt.ylabel('Mean Amount')
plt.show()

FROM_DATE = '2022-04-01'
TO_DATE = '2022-05-01'
print('Describing expenses from',FROM_DATE,'to',TO_DATE)
expenses_pivoted = pd.crosstab(index=only_transactions_expenses['Date'],columns=only_transactions_expenses['Expenses'],values=only_transactions_expenses['Amount'],aggfunc='sum').fillna(0)
# to understand the expenses between the dates
print(expenses_pivoted[FROM_DATE:TO_DATE].describe())

quantity_expenses_pivoted = pd.crosstab(values = all_expenses['Amount'],index=all_expenses['Quantity Name'],columns=all_expenses['Expenses'],aggfunc='sum')
quantity_expenses_pivoted_count = pd.crosstab(index=all_expenses['Quantity Name'],columns=all_expenses['Expenses'])

# expenses pivoted by monthly expenses.
for s in expenses_pivoted.columns:
    print('-'*28)
    expenses_pivoted.resample('M')[s].mean().plot(style="-o", figsize=(10, 5))
    plt.title(s+" Mean by Month")
    plt.xlabel('Month')
    plt.ylabel('Amount')
    for v in range(len(expenses_pivoted.resample('M')[s].mean())):
        plt.text(expenses_pivoted.resample('M')[s].mean().index[v],expenses_pivoted.resample('M')[s].mean().values[v],round(expenses_pivoted.resample('M')[s].mean().values[v]))
    plt.show()
    temp_df_1 = pd.DataFrame(quantity_expenses_pivoted[s].sort_values(ascending=False).dropna().head())
    temp_df_1 = temp_df_1.rename_axis(s+'(Top 5)')
    temp_df_1 = temp_df_1.rename(columns={s:'Amount'})
    data  = []
    for j in list(temp_df_1.index):
        data.append(quantity_expenses_pivoted_count.loc[j,s])
    temp_df_1['Total Visit'] = data
    temp_df_1['Per Visit(Amount)'] = temp_df_1['Amount']/temp_df_1['Total Visit']
    print(temp_df_1)
    print('-'*28)

monthly_df = only_transactions_expenses_dateindex.resample('M').sum()
monthly_df['A/Q'] = round(monthly_df['Amount']/monthly_df['Quantity'],2)
monthly_df['Count'] = all_expenses_count_df.resample('M').sum()
monthly_df['A/C'] = round(monthly_df['Amount']/monthly_df['Count'],2)
monthly_df['Q/C'] = round(monthly_df['Quantity']/monthly_df['Count'],2)

weekly_df = only_transactions_expenses_dateindex.resample('W').sum()
weekly_df['A/Q'] = round(weekly_df['Amount']/weekly_df['Quantity'],2)
weekly_df['Count'] = all_expenses_count_df.resample('W').sum()
weekly_df['A/C'] = round(weekly_df['Amount']/weekly_df['Count'],2)
weekly_df['Q/C'] = round(weekly_df['Quantity']/weekly_df['Count'],2)
# - NEW SHEET - #
other_payment_keywords = ['Rent','Fee','Grocer']

#TOP_EXPENSE is the top most expense on all the categories.
TOP_EXPENSE = only_transactions_expenses.loc[only_transactions_expenses['Amount']==only_transactions_expenses['Amount'].max()]
#average expense is total expense amount by only expense days ( NO EXPENSE DAYS ARE subtracted)
print('Avg Expense Per Day =',round(only_transactions_expenses['Amount'].sum()/EXPENSE_DAYS,2))
print('Total Expense Days:',EXPENSE_DAYS)
print('Total Days:',TOTAL_DAYS)
print('Non Expense Days:',NO_EXPENSE_DAYS)
#expense rate means chance of expense happening per day
print('Expense Rate:',round((EXPENSE_DAYS/TOTAL_DAYS)*100,2),'%')
#chances of no expenses per day
print('Non Expense Rate:',round((NO_EXPENSE_DAYS/TOTAL_DAYS)*100,2),'%')
print('Highest Expense Made Till Now:',str(TOP_EXPENSE['Quantity Name'].values).replace('[','').replace(']','').replace('\'',''),'=',int(TOP_EXPENSE['Amount']))
print('Mean Expense Per Day:',round(only_transactions_expenses['Amount'].mean()))
print('Median Expense Per Day:',round(only_transactions_expenses['Amount'].median()))
print('STD Expense Per Day:',round(only_transactions_expenses['Amount'].std()))
print('-'*28)
price_per_quantity = round(np.divide(only_transactions_expenses.agg(x=('Amount',np.mean)).values,only_transactions_expenses.agg(x=('Quantity',np.mean)).values)[0,0],2)
#difference_from_expense is amount to be removed as an outstanding amount. [ the moment invested in stocks but then removed which returned as an investment amount]
difference_from_expense = 35928.77 + 1541.72
ranking_df = only_transactions_expenses.copy()
print('Total Income -',round(all_incomes['Amount'].sum()))
print('Total Expense -',round(only_transactions_expenses['Amount'].sum()-difference_from_expense))
remaining_amount = all_incomes['Amount'].sum()-only_transactions_expenses[only_transactions_expenses['Category']!='Gold']['Amount'].sum()+difference_from_expense
print('Remaining -',round(remaining_amount,2),'-',round((remaining_amount/(all_incomes['Amount'].sum()))*100,2),'%')
print('Expense Per Quantity:',price_per_quantity)
print('Most Repetitive Amounts by Ranks')
print('\tNo:','Amnt:','AggCount:','Total')
#ranking the top most repetitive expenses made by amount.
for i in range(5):
    print('\t',i+1,':',ranking_df.mode()['Amount'].values[0],':',len(ranking_df.loc[ranking_df['Amount']==ranking_df.mode()['Amount'].values[0]]),':',ranking_df.mode()['Amount'].values[0]*len(ranking_df.loc[ranking_df['Amount']==ranking_df.mode()['Amount'].values[0]]))
    ranking_df = ranking_df.loc[ranking_df['Amount']!=ranking_df.mode()['Amount'].values[0]]


print('Most Repetitive Item by Ranks')
print('\tNo:','Amnt:','AggCount:','Each Purchase:','Total')

ranking_df = only_transactions_expenses.copy()
for i in range(5):
    print('\t',i+1,':',ranking_df.mode()['Quantity Name'].values[0],':',len(ranking_df.loc[ranking_df['Quantity Name']==ranking_df.mode()['Quantity Name'].values[0]]),':',round(ranking_df[ranking_df['Quantity Name'] == ranking_df.mode()['Quantity Name'].values[0]]['Amount'].mean(),2),':',round(ranking_df[ranking_df['Quantity Name'] == ranking_df.mode()['Quantity Name'].values[0]]['Amount'].mean()*len(ranking_df.loc[ranking_df['Quantity Name']==ranking_df.mode()['Quantity Name'].values[0]]),2))
    ranking_df = ranking_df.loc[ranking_df['Quantity Name']!=ranking_df.mode()['Quantity Name'].values[0]]
print('-'*28)

#General Subscriptions that you subscribed as a service.
total_subscriptions = list(np.unique(only_transactions_expenses[only_transactions_expenses['Category'].str.contains('Subs')]['Quantity Name']))
inactive_subscriptions = ['Subscription - Eat.Fit','Ullu Subscription']
active_subscriptions = total_subscriptions
for i in inactive_subscriptions:
    active_subscriptions.remove(i)
#other payments that you are paying other than subscriptions

other_payments =  []
category_lowers = only_transactions_expenses['Quantity Name'].str.lower()

for i in other_payment_keywords:
    other_payments.extend(list(np.unique(only_transactions_expenses[only_transactions_expenses.astype('str').sum(axis=1).str.contains(i)]['Quantity Name'])))
other_active_payments = list(np.unique(other_payments))

active_payments = []
indirect_expenses = []
indirect_expenses_days = []
per_day_indirect_expenses = []
active_subscriptions_final_data = []
other_active_payments_final_data = []
indirect_expenses_per_day = []
indirect_expenses_amount = 0
other_active_payments_final_data_sum = 0
active_subscriptions_final_data_sum = 0
active_subscriptions_final_data_amount = 0
other_active_payments_final_data_amount = 0

active_payments.extend(active_subscriptions+other_active_payments)
for o in active_payments:
    indirect_expenses.append([o,only_transactions_expenses[only_transactions_expenses['Quantity Name']==o]['Amount'].sum(),only_transactions_expenses[only_transactions_expenses['Quantity Name']==o]['Quantity'].sum(),only_transactions_expenses[only_transactions_expenses['Quantity Name']==o]['Quantity'].count()])
    indirect_expenses_amount += only_transactions_expenses[only_transactions_expenses['Quantity Name']==o]['Amount'].sum()
    indirect_expenses_days.append([o,only_transactions_expenses[only_transactions_expenses['Quantity Name']==o]['Quantity'].sum()])
for ie in indirect_expenses:
    if ie[0] in active_subscriptions:
        active_subscriptions_final_data.append([ie[0],ie[1],ie[2],round(ie[1]/ie[2],2),ie[3]])
        active_subscriptions_final_data_amount += ie[1]/ie[2]
        active_subscriptions_final_data_sum += ie[1]
    else:
        other_active_payments_final_data.append([ie[0],ie[1],ie[2],round(ie[1]/ie[2],2),ie[3]])
        other_active_payments_final_data_amount += ie[1]/ie[2]
        other_active_payments_final_data_sum += ie[1]
    per_day_indirect_expenses.append(ie[1]/ie[2])
    
indirect_expenses_per_day.extend(active_subscriptions_final_data+other_active_payments_final_data)
per_day_expense_amount = sum(per_day_indirect_expenses)

print('PDIE - Per Day Indirect Expenses')
print('PDIE - ',round(per_day_expense_amount,2))
print('Item Name - Amount Paid / Total subscribing days = subscribe price per Day - % indirect expenses amount per Day - total paid Time/s')
print('\nActive/Inactive Subscription Payments -',round(active_subscriptions_final_data_sum,2))
print('Total Active Subscriptions: ',len(active_subscriptions))
for iep in active_subscriptions_final_data:
    print('\n ->',iep[0],'-',round(iep[1],2),'/',iep[2],'days=',iep[3],'Per Day -',round((iep[3]/per_day_expense_amount)*100,2),'% of PDIE -',iep[4],'Time/s')
print('\nOther Active/Inactive Payments -',round(other_active_payments_final_data_sum,2))
for iep in other_active_payments_final_data:
    print('\n ->',iep[0],'-',round(iep[1],2),'/',iep[2],'Days (or) Items =',iep[3],'Per Day (or) Item -',round((iep[3]/per_day_expense_amount)*100,2),'% of PDIE -',iep[4],'Time/s')
print('\nTotal Per Day Amount on Subscriptions -',round(active_subscriptions_final_data_amount,2),' -',round(((active_subscriptions_final_data_amount/per_day_expense_amount)*100),2),'%')
print('Total Per Day Amount on other Payments -',round(other_active_payments_final_data_amount,2),' -',round(((other_active_payments_final_data_amount/per_day_expense_amount)*100),2),'%')
print('\nTotal Per Day on Indirect Expenses - ',round(per_day_expense_amount,2))

maximum_avg_expense_per_day = round(only_transactions_expenses['Amount'].sum()/EXPENSE_DAYS,2)
minimum_avg_expense_per_day = round(per_day_expense_amount,2)
print('\nYour Minimum Avg Expense Amount Per Day -',round(minimum_avg_expense_per_day,2))
print('it means your minimum Survivability Expense is be at',round(minimum_avg_expense_per_day*31+minimum_avg_expense_per_day*0.20,2))
print('Your Maximum Avg Expense Amount Per Day -',round(maximum_avg_expense_per_day,2))
print('it means your current maximum survivability Expense is at',round(maximum_avg_expense_per_day*31,2))
print('Extra Expenses Per Day -',round(maximum_avg_expense_per_day-minimum_avg_expense_per_day,2))
#############
path = path.split('\\')[0:-1]
path.append('Keshava Balance Sheet1.xlsx')
path = '\\'.join(path)
writer = pd.ExcelWriter(path, engine = 'xlsxwriter')
only_transactions_expenses_powebi = only_transactions_expenses[only_transactions_expenses.Category != 'Gold']
only_transactions_expenses_powebi.to_excel(writer,sheet_name='Expense Sheet',columns=only_transactions_expenses_powebi.columns,index=False)
writer.save()
writer.close()

## - NEW SHEET - ##

# to use multiple use, // in between
column_name = 'Quantity Name'
main_query = 'BM'

def capitalise(i,split):
    return ' '.join([i.capitalize() for i in i.split(split)])

amount = []
splitted_items = []
unique_splitted_items = []
final_amounts = []
import re
multi_expenses_final = pd.DataFrame()
for q in main_query.split(' // '):
    query = r''+q.lower()
    amount = []
    pd.options.mode.chained_assignment = None
    only_transactions_expenses_lowers = only_transactions_expenses.copy()
    only_transactions_expenses_lowers[column_name] = only_transactions_expenses_lowers[column_name].str.lower()
    multi_expenses = only_transactions_expenses[only_transactions_expenses_lowers[column_name].str.contains(query)==True] # gets row data that has + in quantity column
    multi_expenses[column_name] = multi_expenses[column_name].str.lower()
    for i in multi_expenses[column_name].value_counts().index:
        amount.append(multi_expenses[multi_expenses[column_name]==i]['Amount'].sum())
    values = pd.DataFrame(data = multi_expenses[column_name].value_counts().values,index= multi_expenses[column_name].value_counts().index,columns=['Count'])
    values['Amount'] = amount
    for i in values.index:
        for j in i.split('+'):
            if re.findall(query,j):
                splitted_items.append([j.strip(),round(only_transactions_expenses_lowers[only_transactions_expenses_lowers[column_name]==i]['Amount'].sum()/only_transactions_expenses_lowers[only_transactions_expenses_lowers[column_name]==i]['Quantity'].sum(),2)])
                unique_splitted_items.append(j.strip())
    multi_expenses_final = multi_expenses_final.append(multi_expenses,ignore_index=True)
unique_splitted_items = list(set(unique_splitted_items))
final_splitted_values = pd.DataFrame(data = splitted_items,columns=[column_name,'Amount'])
print('Item Name: Mean Price /Q [ Count of Item ]#Note: "/Q" mean price Per '+column_name+'\n')
for i in unique_splitted_items:
    print(capitalise(i,' '),':',round(final_splitted_values[final_splitted_values[column_name]==i]['Amount'].mean(),2),'/Q [',len(multi_expenses[multi_expenses[column_name].str.contains(i)==True]),']')
    final_amounts.append(final_splitted_values[final_splitted_values[column_name]==i]['Amount'].mean())
occurences = len(multi_expenses_final)
print('\nMedian Value:',round(np.median(final_amounts),2))
print('Total Purchases:',occurences)
print('Total Amount:',round(multi_expenses['Amount'].sum(),2))
print('Total Quantities:',round(multi_expenses['Quantity'].sum(),2))
print('Total Items:',np.unique(multi_expenses['Quantity Name']).size)
multi_expenses_final.index = multi_expenses_final['Date']
multi_expenses_final.resample('M').Date.count().plot()
print(round(multi_expenses_final.resample('M').Date.count().mean(),2),'expense/s per month')
for i in range(len(multi_expenses_final.resample('M').Date.count().values)):
    plt.text(multi_expenses_final.resample('M').Date.count().index[i],multi_expenses_final.resample('M').Date.count().values[i],round(multi_expenses_final.resample('M').Date.count().values[i],2))
plt.xlabel('Month')
plt.ylabel('Count')
plt.title('Expenditure on '+capitalise(main_query,' ')+' Frequency')
plt.show()

amounts_of_query = pd.DataFrame(multi_expenses_final.resample('M').count()['Date']*multi_expenses_final.resample('M').mean()['Amount']).fillna(0)
amounts_of_query.plot(legend=False)
for i in range(len(amounts_of_query.values)):
    plt.text(amounts_of_query.index[i],amounts_of_query.values[i],'₹'+str(round(amounts_of_query.values[i][0],2)))
plt.xlabel('Month')
plt.ylabel('Amount')
plt.title(capitalise(main_query, ' ')+' Expenses on Amount by Month')
plt.show()

## - NEW SHEET - ##
column_name = 'Quantity Name'
split_for_and_condition = ['BM']
split_value = 1
#date format = YYYY-MM-DD
start_date = ""
to_date = ""
period_check = 'M'
##################
split_for_and_condition = [i.lower() for i in split_for_and_condition]

def permutations_and_combinations(split_for_and_condition,split_value):
    split_for_and_condition = [r'\b'+i+r'\b' for i in split_for_and_condition]
    from itertools import combinations,permutations
    permutations_combinations = []
    total_joining_combinations = ''
    if len(split_for_and_condition) <= 2:
        permutations_combinations.append(list(permutations(split_for_and_condition)))
    else:
        for i in range(len(split_for_and_condition)):
            if i >= split_value:
                combinations_list = list(combinations(split_for_and_condition,i))
                for k in combinations_list:
                    permutations_combinations.append(list(permutations(list(k))))
            else:
                pass
        permutations_combinations.append(list(permutations(split_for_and_condition)))
    total_joining_combinations = ''
    for i in permutations_combinations:
        for j in i:
            joining_combinations = '.*'.join(j)
            total_joining_combinations += joining_combinations
            total_joining_combinations += '|'
    total_joining_combinations = total_joining_combinations[:-1]
    return total_joining_combinations

only_transactions_expenses_lowers_and = only_transactions_expenses.copy()

only_transactions_expenses_lowers_and[column_name] = only_transactions_expenses_lowers_and[column_name].str.lower()
    
filtered_df = only_transactions_expenses_lowers_and[only_transactions_expenses_lowers_and[column_name].str.contains(permutations_and_combinations(split_for_and_condition,split_value),regex=True)==True]

if start_date != "" and to_date != "":
    filtered_df = filtered_df[(filtered_df.Date >= start_date) & (filtered_df.Date <= to_date)]
elif start_date != "" and to_date == "":
    filtered_df = filtered_df[filtered_df.Date >= start_date]
elif start_date == "" and to_date != "":
    filtered_df = filtered_df[filtered_df.Date <= to_date]
else:
    pass

print('Item Name:',split_for_and_condition,'\n')
print('Total Amount:',filtered_df['Amount'].sum())
print('Total Quantity:',filtered_df['Quantity'].sum())
print('Total Times:',len(filtered_df))
filtered_df.index = filtered_df['Date']
for i in range(len(filtered_df.select_dtypes('float').mean())):
    print('\nMean',filtered_df.select_dtypes('float').mean().index[i],':',round(filtered_df.select_dtypes('float').mean()[i],2))
    print('Median',filtered_df.select_dtypes('float').mean().index[i],':',round(filtered_df.select_dtypes('float').median()[i],2))
    filtered_df.resample(period_check)[filtered_df.select_dtypes('float').mean().index[i]].mean().fillna(0).plot()
    plt.title('Mean '+str(filtered_df.select_dtypes('float').mean().index[i])+' Distribution')
    plt.ylabel(filtered_df.select_dtypes('float').sum().index[i])
    filtered_df_types = filtered_df.resample(period_check)[filtered_df.select_dtypes('float').mean().index[i]].mean().fillna(0)
    for j in range(len(filtered_df_types)):
        plt.text(filtered_df_types.index[j],filtered_df_types.values[j],'₹'+str(round(filtered_df_types.values[j],2)))
    plt.show()
print('Deep Analysis on your Purchase Choices:')
filtered_df['Amount'].groupby(filtered_df.Category).agg(func=sum).head(8).plot(kind='pie',subplots=True,figsize=(6,6),legend=False,autopct='%1.0f%%')
plt.show()
filtered_df['Category'].value_counts().head(8).plot(kind='pie',subplots=True,figsize=(6,6),legend=False,autopct='%1.0f%%')
plt.show()
filtered_df['Date'].to_period(period_check).groupby('Date').count().plot()
for i in range(len(filtered_df['Date'].to_period(period_check).groupby('Date').count())):
    plt.text(filtered_df['Date'].to_period(period_check).groupby('Date').count().index[i],filtered_df['Date'].to_period(period_check).groupby('Date').count().values[i],filtered_df['Date'].to_period(period_check).groupby('Date').count().values[i])
plt.title(','.join(j for j in split_for_and_condition)+' Frequency')
plt.ylabel('Expense Frequency')
plt.show()
print('Period Check:',period_check)
print('Mean Frequency on Expenses',round(filtered_df['Date'].to_period(period_check).groupby('Date').count().mean(),2))
# filtered_df

## - NEW SHEET - ##
weekly_change_df = pd.DataFrame(only_transactions_expenses_dateindex.resample('W')['Amount'].sum())
monthly_change_df = pd.DataFrame(only_transactions_expenses_dateindex.resample('M')['Amount'].sum())
change_calc = [weekly_change_df,monthly_change_df]
weekly_change,monthly_change = [],[]
weekly_monthly_change = [weekly_change,monthly_change]
for h in range(len(change_calc)):
    for i in range(len(change_calc[h])):
        if i == 0:
            weekly_monthly_change[h].append(change_calc[h]['Amount'][i])
        else:
            weekly_monthly_change[h].append(change_calc[h]['Amount'][i] - change_calc[h]['Amount'][i-1])
            
weekly_change_df['7-Day Change'] = weekly_change
weekly_change_df['7-Day Change %'] = round((weekly_change_df['7-Day Change']/weekly_change_df['Amount'])*100,2)

monthly_change_df['Monthly Change'] = monthly_change
monthly_change_df['Monthly Change %'] = round((monthly_change_df['Monthly Change']/monthly_change_df['Amount'])*100,2)

fig, axes = plt.subplots(2,1,figsize=(21,11))
axes[0].plot(weekly_change_df.index,weekly_change_df['7-Day Change'].values,label='Weekly Change')
axes[1].plot(monthly_change_df.index,monthly_change_df['Monthly Change'].values,label='Monthly Change',color='orange')
axes[0].legend()
axes[0].text(weekly_change_df.index[0],20000,'Mean Change Amount: ±'+str(round(abs(weekly_change_df['7-Day Change']).mean(),2))+'\n'+'Median Change Amount: ±'+str(round(abs(weekly_change_df['7-Day Change']).median(),2)))
axes[0].set_title('Weekly Change Analysis')
axes[1].text(monthly_change_df.index[0],-20000,'Mean Change Amount: ±'+str(round(abs(monthly_change_df['Monthly Change']).mean(),2))+'\n'+'Median Change Amount: ±'+str(round(abs(monthly_change_df['Monthly Change']).median(),2)))
axes[1].set_title('Monthly Change Analysis')
axes[1].legend()

for i in range(len(monthly_change_df.index)):
    axes[1].text(monthly_change_df.index[i],monthly_change_df['Monthly Change'].values[i],'₹'+str(round(monthly_change_df['Monthly Change'].values[i])))

plt.show()

## - NEW SHEET - ##

normalizes_list = ['monthly_df','weekly_df','monthly_change_df','weekly_change_df']
scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
for j in normalizes_list:
    d = scaler.fit_transform(globals()[j])
    globals()['normalize_'+j] = pd.DataFrame(d, columns=globals()[j].columns,index=globals()[j].index)
columns_names = ['Monthly Road Way','Weekly Road Way']
current_position = 0
for j  in ['monthly_df','weekly_df']:
    globals()['normalize_'+j]['Amount'].plot(figsize=(16,4))
    for v in range(len(globals()['normalize_'+j].index)):
        plt.text(globals()['normalize_'+j].index[v],globals()['normalize_'+j]['Amount'].values[v],round(globals()['normalize_'+j]['Amount'].values[v],2))
    plt.title(columns_names[current_position])
    current_position += 1
    plt.show()
    
columns_names = ['Monthly Change','7-Day Change']
current_position = 0
for j  in ['monthly_change_df','weekly_change_df']:
    globals()['normalize_'+j][columns_names[current_position]].plot(figsize=(16,4))
    for v in range(len(globals()['normalize_'+j].index)):
        plt.text(globals()['normalize_'+j].index[v],globals()['normalize_'+j][columns_names[current_position]].values[v],round(globals()['normalize_'+j][columns_names[current_position]].values[v],2))
    plt.title(columns_names[current_position])
    plt.show()
    current_position += 1

quarter_level_df = only_transactions_expenses_dateindex.resample('Q')['Amount'].sum()
quarter_level_df.plot(title='Quarter Plot',xlabel='Quarter',ylabel='Amount',figsize=(12,4))
for i in range(len(quarter_level_df)):
    plt.text(quarter_level_df.index[i],quarter_level_df.values[i],'₹'+str(round(quarter_level_df.values[i])))
plt.show()


math.ceil(((only_transactions_expenses_dateindex.resample('Q')['Amount'].sum().index[-1]-only_transactions_expenses_dateindex.resample('Q')['Amount'].sum().index[-2]).days-(only_transactions_expenses_dateindex.resample('Q')['Amount'].sum().index[-1]-dt.datetime.today()).days)/30)

for i in only_transactions_expenses_dateindex.resample('Q')['Amount'].sum().index[:-1]:
    print(i)
    
quarter_df_actual = pd.DataFrame(index = only_transactions_expenses_dateindex.resample('Q')['Amount'].sum().index, data = list(only_transactions_expenses_dateindex.resample('Q')['Amount'].sum().values),columns=['Amount'])
quarter_df_actual['Date'] = quarter_df_actual.index
quarter_df_actual_1 = quarter_df_actual.diff()
x = quarter_df_actual['Amount'][1:-1]/quarter_df_actual_1.Date[1:-1].dt.days
x[quarter_df_actual.Date[-1]] = quarter_df_actual.Amount[-1]/((dt.datetime.now() - quarter_df_actual['Date'][-2]).days+1)
x.plot()
x[quarter_df_actual['Date'][0]] = quarter_df_actual['Amount'][0]/((quarter_df_actual['Date'][0] - only_transactions_expenses_dateindex.index[0]).days+1)
x[quarter_df_actual['Date'][0]] = quarter_df_actual['Amount'][0]/((quarter_df_actual['Date'][0] - only_transactions_expenses_dateindex.index[0]).days+1)
x.plot()

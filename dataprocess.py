import pandas as pd
import json
import pickle

def get_country_code():  # 返回国家名和对应的编码

    df = pd.read_csv('./dataset/summerOly_athletes.csv')
    countries = df['NOC'].unique()
    countries = [country for country in countries if '\xa0' not in country]
    # 按照字母顺序排序
    countries.sort()
    country_mapping = {country: i for i, country in enumerate(countries)}

    with open('./dataset/country_mapping.json', 'w') as f:
        json.dump(country_mapping, f, indent=4)

    return

def get_discipline_code():  # 返回体育项目名和对应的编码
    
    df = pd.read_csv('./dataset/summerOly_programs.csv')
    disciplines = df['Discipline'].iloc[:55]
    discipline_mapping = {discipline: i for i, discipline in enumerate(disciplines)}

    with open('./dataset/discipline_mapping.json', 'w') as f:
        json.dump(discipline_mapping, f, indent=4)

    return

def get_medals_num():
    # 读取数据并过滤掉没有奖牌的记录
    df = pd.read_csv('./dataset/summerOly_athletes.csv')
    df = df[df['Medal'] != 'No medal']

    # 去重，确保每个团体项目的奖牌只计入一次
    df = df.drop_duplicates(subset=['Year', 'NOC', 'Sport', 'Event', 'Medal'])

    # 按照年份、国家和运动项目进行分组，并统计每个奖牌的数量
    result = df.groupby(['Year', 'NOC', 'Sport', 'Medal']).size().unstack(fill_value=0)

    # 计算每个国家每个运动项目的金牌数和总奖牌数
    gold_results = result.get('Gold', 0)
    total_results = result.sum(axis=1)

    final_results = pd.DataFrame({
        'Gold': gold_results,
        'Total': total_results
    })

    return final_results

def get_winning_rate():  # 得到每个国家每个体育项目的胜率

    df = pd.read_csv("./dataset/summerOly_programs.csv")
    df_filtered = df[['Discipline'] + list(df.columns[4:])]
    df_filtered = df_filtered.iloc[:55, 0:]
    df_filtered.rename(columns={'1906*': '1906'}, inplace = True)
    df_medals = get_medals_num()
    olympic_years = df_medals.columns
    with open('./dataset/discipline_mapping.json', 'r') as file:
                    discipline_mapping = json.load(file)
    reverse_discipline_dict = {value: key for key, value in discipline_mapping.items()}
    with open('./dataset/country_mapping.json', 'r') as file:
                    country_mapping = json.load(file)

    probability_matrices = {}

    for year in df_medals.index.get_level_values('Year').unique():
        probability_matrix_year = pd.DataFrame(index=country_mapping.keys(), 
                    columns=discipline_mapping.keys())

        for country in df_medals.index.get_level_values('NOC').unique():
            for discipline in df_medals.index.get_level_values('Sport').unique():
                country_total_medals = df_medals.loc[(year, country, discipline), 'Total'] if (year, country, discipline) in df_medals.index else 0
                country_gold_medals = df_medals.loc[(year, country, discipline), 'Gold'] if (year, country, discipline) in df_medals.index else 0
                discipline = discipline_mapping[discipline]
                total_gold_medals = df_filtered.loc[discipline][str(year)]
                total_medals = total_gold_medals * 3
                discipline = reverse_discipline_dict[discipline]
                # Calculate the winning probability (gold medals / total medals)
                probability_matrix_year.loc[country, discipline] = (country_gold_medals / total_gold_medals) if total_medals > 0 else 0
        
        # Store the probability matrix for this year
        probability_matrices[year] = probability_matrix_year

    with open('./dataset/probability_matrices.pkl', 'wb') as f:
        pickle.dump(probability_matrices, f)

    return

def get_player_number():  # 得到每个国家每个体育项目的运动员数

    df = pd.read_csv('./dataset/summerOly_athletes.csv')
    result = df.groupby(['Year', 'NOC', 'Sport']).size()

    # 转换为字典，key为年份，value为dataframe，index为国家，columns为体育项目
    result = result.unstack(level=-1)
    result = result.fillna(0)

    with open('./dataset/discipline_mapping.json', 'r') as file:
                    discipline_mapping = json.load(file)
    with open('./dataset/country_mapping.json', 'r') as file:
                    country_mapping = json.load(file)

    number_matrices = {}

    for year in result.index.get_level_values('Year').unique():
        number_matrix_year = pd.DataFrame(index=country_mapping.keys(), 
                columns=discipline_mapping.keys())

        for country in country_mapping.keys():
            for discipline in discipline_mapping.keys():
                try:
                    number_matrix_year.loc[country, discipline] = result.loc[(year, country)][discipline] if discipline in result.loc[(year, country)].index else 0
                except KeyError:
                    number_matrix_year.loc[country, discipline] = 0
        
        # Store the probability matrix for this year
        number_matrices[year] = number_matrix_year
    
    with open('./dataset/number_matrices.pkl', 'wb') as f:
        pickle.dump(number_matrices, f)

    return result

def get_programms_num():
    df = pd.read_csv('./dataset/summerOly_programs.csv')
    df_filtered = df[['Discipline'] + list(df.columns[4:])]
    df_filtered = df_filtered.iloc[:55, 0:]
    df_filtered.rename(columns={'1906*': '1906'}, inplace = True)
    df_filtered = df_filtered.set_index('Discipline')

    return df_filtered        


if __name__ == '__main__':
    get_country_code()
    get_discipline_code()
    get_medals_num()
    get_winning_rate()
    get_player_number()
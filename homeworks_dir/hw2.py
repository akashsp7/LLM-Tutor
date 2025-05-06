# Christina Georgiades
# Final Project
# 12/1/2024

# NOTES: I used a lot from my EX08.py file to complete this assignment
#        All numbers used are from the URLs
#        Some overlapping in the income areas pie chart because it is very small spacing

# Imports the required libraries
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
from collections import Counter
from spacy.lang.en.stop_words import STOP_WORDS
import matplotlib.pyplot as plt
import bs4 as bs
import requests
import pandas as pd
import seaborn as sns

# This is the basic cleaning for the list of words
# Used EX08 as reference
def txt_clean(word_list, min_len, stopwords_list):
    clean_words = []
    for line in word_list:
        parts = line.strip().split() # splits up lines to make them into individual words
        for word in parts:
            word_l = word.lower().strip()
            if word_l.isalpha(): # checks if word is alphabetical
                if len(word_l) > min_len: # Filters the short words
                    if word_l not in stopwords_list: # Makes sure to not include stopwords
                        clean_words.append(word_l)
    return clean_words

# URL 1: Global Migration Trends
# Used EX08 as reference
url_1 = 'https://www.migrationdataportal.org/themes/international-migrant-stocks#data-sources-amp-measurement'
# Minimum word length is 3 used when filtering
min_word = 3

# Used EX08 as reference
# Looks at the URL provided parses HTML and then prints the title of the page
body_1 = requests.get(url_1)
soup_1 = bs.BeautifulSoup(body_1.content, 'html.parser')
print('URL 1', soup_1.title.string)

# Used EX08 as reference
# Extracts paragraph text and makes them all into a string
for paragraph_1 in soup_1.find_all('p'):
    text_1 = " ".join([p.text for p in soup_1.find_all('p')])

# Used EX08 as reference
# Updates stopwords list ot include words that could be frequent but not necessary in both URLs
stopwords = set(STOP_WORDS)
stopwords.update(['migration', 'immigration', 'migrant', 'europe', 'countries', 'issued', 'international', 'europeans', 'data', 'stocks', 'stock', 'migrants', 'country', 'person', 'number', 'time', 'year', 'market', '.', '"', ','])

# Used EX08 as reference
# Cleans text
clean_text_1 = txt_clean(text_1.splitlines(), min_word, stopwords)

# Used EX08 as reference
# Sentiment analysis on the updated clean text
analyzer = SentimentIntensityAnalyzer()
clean_text_str_1 = ' '.join(clean_text_1)
vad_sentiment_1 = analyzer.polarity_scores(clean_text_str_1)

# Used EX08 as reference
# Does the positive, negative, and neutral sentiment percents
pos_1 = vad_sentiment_1['pos']
neg_1 = vad_sentiment_1['neg']
neu_1 = vad_sentiment_1['neu']

# Used EX08 as reference
# Prints the positive, negative, and neutral sentiment percents
print('\nIt is positive for URL 1:', '{:.1%}'.format(pos_1))
print('\nIt is negative for URL 1:', '{:.1%}'.format(neg_1))
print('\nIt is neutral for URL 1:', '{:.1%}'.format(neu_1), '\n')

# Used EX08 as reference
# Calculates lexical diversity and prints
def lexical_diversity(tokens):
    return len(set(tokens)) / len(tokens) if tokens else 0
ld_1 = lexical_diversity(clean_text_1)
print('\nURL 1 Lexical Diversity is:', (round(ld_1, 3) * 100), '%')

# Used EX08 as reference
# Loads NLP and processes clean text
nlp = spacy.load("en_core_web_sm")
process_1 = nlp(clean_text_str_1)

# Used EX08 as reference
# Extracts tokens from the text and filters it by length while not including the punctuation and numbers
tokens_1 = [token.text for token in process_1 if not token.is_punct and not token.like_num and len(token.text) > 3]

# Used EX08 as reference
# Gets two most frequent words and prints
freqdist_1 = Counter(tokens_1).most_common(2)
print('\nThe 2 most frequent words in URL 1 are:', freqdist_1)

# Used EX08 as reference
# Generates bigrams
bigrams_1 = [(tokens_1[i], tokens_1[i + 1]) for i in range(len(tokens_1) - 1)]
print('\nThe following are the bigrams extracted from URL 1:', bigrams_1)

#VISUALIZATIONS for URL 1
# Bar Chart for the Migration Flows to OECD Countries
# Used link below for reference to make the best bar plot possible
#https://seaborn.pydata.org/generated/seaborn.barplot.html
oecd_migration_flows = pd.DataFrame({
    'Country': ['United States', 'United Kingdom', 'Germany', 'Canada', 'Spain',
                'Australia', 'France', 'Finland', 'Japan', 'Korea', 'Luxembourg', 'Switzerland',
                'Estonia', 'Lithuania', 'New Zealand', 'Israel'],
    'Migrants': [1200000, 750000, 700000, 470000, 360000,
                 'Record', 'Record', 'Record', 'Record', 'Record', 'Record', 'Record',
                 -36000, -32000, -23000, -38000],
    'Change (%)': [None, 52, 4, 7.8, 12,
                   'Record', 'Record', 'Record', 'Record', 'Record', 'Record', 'Record',
                   -36, -32, -23, -38]
})

# Creates the bar chart and formats it
plt.figure(figsize=(10, 6))
sns.barplot(data=oecd_migration_flows[:5], x='Country', y='Migrants')  # Top 5 countries
plt.title('Major Migration Flows to OECD Countries (2023)')
plt.xlabel('Country')
plt.ylabel('Number of Migrants')
plt.xticks(rotation=45)
plt.show()

# Pie chart for Migration from developed regions
# Used Link Below for Reference:
#https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html
migration_categories = pd.DataFrame({
    'Category': ['Family Migration', 'Labor Migration', 'Free Circulation', 'Humanitarian'],
    'Percentage': [43, 20, 19, 11]
})
# Formats the pie chart
plt.figure(figsize=(8, 8))
plt.pie(migration_categories['Percentage'], labels=migration_categories['Category'], autopct='%1.1f%%', startangle=140)
plt.title('Migration Categories (2023)')
plt.show()

# Bar Plot for Changes in migration trends
# Used link below for reference to make the best bar plot possible
#https://seaborn.pydata.org/generated/seaborn.barplot.html
migration_trends = pd.DataFrame({
    'Country': ['United States', 'United Kingdom', 'Germany', 'Canada', 'Spain', 'Estonia', 'Lithuania', 'New Zealand', 'Israel'],
    'Change (%)': [10, 52, 4, 7.8, 12, -36, -32, -23, -38]
})
# Format for the bar plot
plt.figure(figsize=(10, 6))
sns.barplot(data=migration_trends, x='Country', y='Change (%)', dodge=False)
plt.title('Changes in Migration Trends (2022-2023)', fontsize=14, weight='bold')
plt.xlabel('Country', fontsize=12)
plt.ylabel('Percentage Change', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Dynamics by income and geographic region
# Data for Pie Chart
# Used Link Below for Reference:
#https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html
income_region_data = pd.DataFrame({'Region': ['High Income', 'Middle Income', 'Low Income'], 'Migrants': [6500000, 16632, 0]})
# Format for the Pie Chart
plt.figure(figsize=(10, 8))
plt.pie( income_region_data['Migrants'], labels=income_region_data['Region'], autopct='%1.1f%%', startangle=140)
plt.title('Migration Dynamics by Income Region (2023)', fontsize=14, weight='bold')
plt.legend(labels=income_region_data['Region'], title='Income Region', loc='upper right')
plt.tight_layout()
plt.show()

# Bar Plot for Migration by OECD Geographic Regions
# Used link below for reference to make the best bar plot possible
#https://seaborn.pydata.org/generated/seaborn.barplot.html
region_migration = pd.DataFrame({'Region': ['North America', 'Europe', 'Asia-Pacific', 'Middle East'], 'Migrants': [1670000, 2810000, 750000, 16632]})
# Format of the Bar Plot
plt.figure(figsize=(10, 6))
sns.barplot(data=region_migration, x='Region', y='Migrants')
plt.title('Migration Dynamics by Geographic Region (2023)')
plt.xlabel('Region')
plt.ylabel('Number of Migrants')
plt.xticks(rotation=45)
plt.show()

# URL 2: Migration in Europe
# Used EX08 as reference
url_2 = 'https://home-affairs.ec.europa.eu/policies/migration-and-asylum/statistics-migration-europe_en#:~:text=In%202023%20there%20was%20an,%2C%2060%2C800)%20compared%20to%202022.'

# Used EX08 as reference
# Looks at the URL provided parses HTML and then prints the title of the page
body_2 = requests.get(url_2)
soup_2 = bs.BeautifulSoup(body_2.content, 'html.parser')
print('URL 2:', soup_2.title.string)

# Used EX08 as reference
# Extracts paragraph text and makes them all into a string
for paragraph_2 in soup_2.find_all('p'):
    text_2 = " ".join([p.text for p in soup_2.find_all('p')])

# Used EX08 as reference
# Cleans text
clean_text_2 = txt_clean(text_2.splitlines(), min_word, stopwords)

# Used EX08 as reference
# Sentiment analysis on the updated clean text
clean_text_str_2 = ' '.join(clean_text_2)
vad_sentiment_2 = analyzer.polarity_scores(clean_text_str_2)

# Used EX08 as reference
# Does the positive, negative, and neutral sentiment percents
pos_2 = vad_sentiment_2['pos']
neg_2 = vad_sentiment_2['neg']
neu_2 = vad_sentiment_2['neu']

# Used EX08 as reference
# Prints the positive, negative, and neutral sentiment percents
print('\nIt is positive for URL 2:', '{:.1%}'.format(pos_2))
print('\nIt is negative for URL 2:', '{:.1%}'.format(neg_2))
print('\nIt is neutral for URL 2:', '{:.1%}'.format(neu_2), '\n')

# Used EX08 as reference
# Calculates lexical diversity and prints
ld_2 = lexical_diversity(clean_text_2)
print('\nURL 2 Lexical Diversity is:', (round(ld_2, 3) * 100), '%')

# Used EX08 as reference
# Processes Clean Text
process_2 = nlp(clean_text_str_2)

# Used EX08 as reference
# Extracts tokens from the text and filters it by length while not including the punctuation and numbers
tokens_2 = [token.text for token in process_2 if not token.is_punct and not token.like_num and len(token.text) > 3]

# Used EX08 as reference
# Gets two most frequent words and prints
freqdist_2 = Counter(tokens_2).most_common(2)
print('\nThe 2 most frequent words in URL 2 are:', freqdist_2)

# Used EX08 as reference
# Generates bigrams
bigrams_2 = [(tokens_2[i], tokens_2[i + 1]) for i in range(len(tokens_2) - 1)]
print('\nThe following are the bigrams extracted from URL 2:', bigrams_2)

#VISUALIZATIONS for URL 2
# Line Plot Data for Migration Flows
# Used link below for reference to create line plot (New visualization I tried to do because thought it was best in order to show plot)
#https://seaborn.pydata.org/generated/seaborn.lineplot.html
migration_flows = pd.DataFrame({
    'Year': ['2021', '2022', '2023'],
    'Immigrants (Million)': [6.85, 7.03, 7.10],
    'Emigrants (Million)': [2.50, 2.73, 2.80],
    'Net Immigration (Million)': [4.35, 4.30, 4.30]
})
# Format and creation of the actual line plot
plt.figure(figsize=(10, 6))
sns.lineplot(data=migration_flows, x='Year', y='Immigrants (Million)', marker='o', label='Immigrants')
sns.lineplot(data=migration_flows, x='Year', y='Emigrants (Million)', marker='o', label='Emigrants')
sns.lineplot(data=migration_flows, x='Year', y='Net Immigration (Million)', marker='o', label='Net Immigration')
plt.title('EU Migration Flows (2021-2023)', fontsize=14, weight='bold')
plt.xlabel('Year', fontsize=12)
plt.ylabel('Population (Million)', fontsize=12)
plt.legend(title='Flow Type')
plt.tight_layout()
plt.show()

# Pie chart data for Reasons for Staying in Europe
# Used Link Below for Reference:
#https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html
residence_permits = pd.DataFrame({'Reason': ['Family', 'Work', 'Other'], 'Percentage': [34, 21, 26], 'People': [8393260, 5157584, 6448534]})
# Format and creates pie chart
plt.figure(figsize=(8, 6))
plt.pie(residence_permits['People'], labels=residence_permits['Reason'], autopct='%1.1f%%', startangle=140)
plt.title('Reasons for Staying in Europe (2023)', fontsize=14, weight='bold')
plt.tight_layout()
plt.show()

# Bar Plot data for Asylum Applications by Country
# Used link below for reference to make the best bar plot possible
#https://seaborn.pydata.org/generated/seaborn.barplot.html
asylum_applications = pd.DataFrame({'Country': ['Germany', 'Spain', 'Italy', 'France', 'Greece'], 'Applications (Thousands)': [139.9, 99.0, 94.6, 75.7, 33.0]})
# Formats and creates bar plot
plt.figure(figsize=(10, 6))
sns.barplot(data=asylum_applications, x='Country', y='Applications (Thousands)')
plt.title('Asylum Applications by Country (2024)', fontsize=14, weight='bold')
plt.xlabel('Country', fontsize=12)
plt.ylabel('Applications (Thousands)', fontsize=12)
plt.tight_layout()
plt.show()

# Bar Plot data for Refugees in Europe
# Used link below for reference to make the best bar plot possible
#https://seaborn.pydata.org/generated/seaborn.barplot.html
refugee_population = pd.DataFrame({'Category': ['Global Refugees', 'Internally Displaced People', 'EU Refugees'], 'Population (Million)': [37.6, 68.3, 8.0]})
# Format and create the bar plot
plt.figure(figsize=(10, 6))
sns.barplot(data=refugee_population, x='Category', y='Population (Million)')
plt.title('Refugee Population Trends (2023)', fontsize=14, weight='bold')
plt.xlabel('Category', fontsize=12)
plt.ylabel('Population (Million)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Bar plot data for Dynamics by Geographic Regions
# Used link below for reference to make the best bar plot possible
#https://seaborn.pydata.org/generated/seaborn.barplot.html
irregular_border_crossings = pd.DataFrame({'Route': ['Central Mediterranean', 'Eastern Mediterranean', 'Western Mediterranean', 'Atlantic Route'], 'Crossings (Thousands)': [162.7, 60.8, 16.9, 39.7]})
# Format and Create bar plot
plt.figure(figsize=(10, 6))
sns.barplot(data=irregular_border_crossings, x='Route', y='Crossings (Thousands)')
plt.title('Irregular Border Crossings by Route (2023)', fontsize=14, weight='bold')
plt.xlabel('Route', fontsize=12)
plt.ylabel('Crossings (Thousands)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
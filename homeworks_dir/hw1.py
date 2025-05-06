import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from textblob import TextBlob
import matplotlib.pyplot as plt

# Path to the stopwords file
stopwords_path = 'stopwords_en.txt'

# Load custom stopwords from the .txt file
with open(stopwords_path, 'r') as f:
    custom_stopwords = set(f.read().splitlines())

# List of URLs
urls = [
    "https://world-nuclear.org/information-library/current-and-future-generation/nuclear-power-in-the-world-today",
    "https://www.pewresearch.org/short-reads/2024/08/05/majority-of-americans-support-more-nuclear-power-in-the-country/",
    "https://www.iea.org/reports/nuclear-power-in-a-clean-energy-system",
    "https://ourworldindata.org/what-was-the-death-toll-from-chernobyl-and-fukushima"
]

# Function to scrape content and save to individual files
def scrape_and_save_content(url, index):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from all paragraphs
        content = soup.find_all('p')
        text_content = "\n".join([paragraph.get_text() for paragraph in content])

        # Save content to a .txt file
        filename = f"article_{index + 1}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"Content from URL: {url}\n\n")
            file.write(text_content)
        print(f"Content from {url} saved to {filename}")
        return text_content
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""

# Combine content from all articles
combined_text = ""
for index, url in enumerate(urls):
    combined_text += scrape_and_save_content(url, index)

# Ensure there's content for analysis
if not combined_text.strip():
    print("No content retrieved for analysis.")
    exit()

# 1. Generate a Word Cloud using custom stopwords
plt.figure(figsize=(10, 6))
plt.imshow(WordCloud(width=800, height=400, background_color='white', stopwords=custom_stopwords).generate(combined_text), interpolation='bilinear')
plt.axis('off')
plt.title('Figure 1: Word Cloud of Combined Articles', fontsize=16)
# plt.show()

# 2. Sentiment Analysis of the Combined Text
blob = TextBlob(combined_text)
sentiment_polarity = blob.sentiment.polarity
sentiment_subjectivity = blob.sentiment.subjectivity
print(f"Sentiment Analysis Results:")
print(f"Polarity: {sentiment_polarity:.2f} (Scale: -1 [negative] to +1 [positive])")
print(f"Subjectivity: {sentiment_subjectivity:.2f} (Scale: 0 [objective] to 1 [subjective])")

# 3. Sentiment Polarity Across Paragraphs
paragraphs = combined_text.split('\n\n')
polarity_scores = [TextBlob(p).sentiment.polarity for p in paragraphs]

plt.figure(figsize=(10, 6))
plt.plot(range(len(polarity_scores)), polarity_scores, marker='o', linestyle='-', color='purple')
plt.title('Figure 2: Sentiment Polarity Across Paragraphs', fontsize=16)
plt.xlabel('Paragraph Index')
plt.ylabel('Polarity (Scale: -1 to +1)')
plt.grid(True)
# plt.show()

# 4. Trends in Nuclear Energy Production Over Time
years = list(range(1970, 2024))
production = [100, 200, 300, 500, 800, 1000, 1200, 1500, 1800, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2602]

plt.figure(figsize=(10, 6))
plt.plot(years[-len(production):], production, marker='o', linestyle='-', color='b')
plt.title('Figure 3: Global Nuclear Electricity Production Over Time', fontsize=16)
plt.xlabel('Year')
plt.ylabel('Electricity Production (TWh)')
plt.grid(True)
# plt.show()

# 5. Comparison of Low-Carbon Electricity Sources
years = [2000, 2005, 2010, 2015, 2020]
nuclear = [2500, 2600, 2700, 2650, 2600]
hydro = [3000, 3200, 3400, 3600, 3800]
wind = [100, 200, 400, 800, 1200]
solar = [50, 100, 200, 500, 1000]

plt.figure(figsize=(10, 6))
plt.stackplot(years, nuclear, hydro, wind, solar, labels=['Nuclear', 'Hydro', 'Wind', 'Solar'], alpha=0.8)
plt.title('Figure 4: Global Low-Carbon Electricity Generation by Source', fontsize=16)
plt.xlabel('Year')
plt.ylabel('Electricity Generation (TWh)')
plt.legend(loc='upper left')
plt.grid(True)
# plt.show()

# 6. Timeline of Immediate Fatalities Following Nuclear Disasters
time_after_disaster = [0, 1, 7, 30, 60, 90]
chernobyl_deaths = [2, 4, 28, 30, 30, 30]
fukushima_deaths = [0, 0, 0, 0, 0, 0]

plt.figure(figsize=(10, 6))
plt.plot(time_after_disaster, chernobyl_deaths, marker='o', label='Chernobyl', color='r')
plt.plot(time_after_disaster, fukushima_deaths, marker='x', label='Fukushima', color='b')
plt.title('Figure 5: Immediate Fatalities Following Nuclear Disasters', fontsize=16)
plt.xlabel('Days After Disaster')
plt.ylabel('Cumulative Number of Deaths')
plt.legend()
plt.grid(True)
# plt.show()

# 7. Public Perception of Nuclear Energy Over Time
perception_years = [2020, 2021, 2022, 2023]
perception_scores = [0.3, 0.35, 0.4, 0.45]  # Example sentiment polarity scores from public surveys

plt.figure(figsize=(10, 6))
plt.plot(perception_years, perception_scores, marker='o', linestyle='-', color='g')
plt.title('Figure 6: Public Perception of Nuclear Energy Over Time', fontsize=16)
plt.xlabel('Year')
plt.ylabel('Sentiment Polarity Score (Scale: -1 to +1)')
plt.grid(True)
# plt.show()

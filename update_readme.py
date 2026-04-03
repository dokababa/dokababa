"""
Daily Dataset Spotlight updater for GitHub profile README.
Picks a dataset based on day-of-year so it changes every day
but is consistent for all visitors on the same day.
"""
import re
from datetime import datetime

DATASETS = [
    {
        "name": "Iris",
        "samples": 150, "features": "4 (sepal/petal length & width)", "classes": "3 — Setosa · Versicolor · Virginica",
        "year": "1936 · Ronald Fisher",
        "fun_fact": "Still the \"hello world\" of ML — used in virtually every intro course, 88 years later",
        "dist": [("Setosa", 33), ("Versicolor", 33), ("Virginica", 33)],
    },
    {
        "name": "MNIST Handwritten Digits",
        "samples": 70000, "features": "784 (28×28 pixels)", "classes": "10 (digits 0–9)",
        "year": "1998 · LeCun et al.",
        "fun_fact": "Trained on US census forms & high-school student writing; became the de-facto CNN benchmark for 20 years",
        "dist": [("0-4", 50), ("5-9", 50)],
    },
    {
        "name": "Titanic Survival",
        "samples": 891, "features": "12 (age, class, fare, sex…)", "classes": "2 — Survived / Did not survive",
        "year": "2012 · Kaggle",
        "fun_fact": "The most-submitted Kaggle dataset ever — 1st-class passengers had a 63% survival rate vs 24% in 3rd class",
        "dist": [("Survived", 38), ("Did not survive", 62)],
    },
    {
        "name": "CIFAR-10",
        "samples": 60000, "features": "3072 (32×32×3 RGB)", "classes": "10 (airplane, car, bird…)",
        "year": "2009 · Krizhevsky & Hinton",
        "fun_fact": "AlexNet's 2012 win on ImageNet used techniques first validated on CIFAR-10, kicking off the deep learning revolution",
        "dist": [("Each class", 10)] * 10,
    },
    {
        "name": "Breast Cancer Wisconsin",
        "samples": 569, "features": "30 (tumor geometry)", "classes": "2 — Malignant · Benign",
        "year": "1995 · UCI ML Repository",
        "fun_fact": "Features were computed from digitized FNA biopsy images — one of the earliest clinical ML datasets",
        "dist": [("Benign", 63), ("Malignant", 37)],
    },
    {
        "name": "Adult Income (Census)",
        "samples": 48842, "features": "14 (age, education, occupation…)", "classes": "2 — >$50K / ≤$50K",
        "year": "1996 · UCI (1994 US Census)",
        "fun_fact": "A foundational fairness benchmark — income correlates with race & sex in ways ML models can amplify",
        "dist": [(">$50K", 24), ("≤$50K", 76)],
    },
    {
        "name": "Fashion-MNIST",
        "samples": 70000, "features": "784 (28×28 pixels)", "classes": "10 (T-shirt, trouser, dress…)",
        "year": "2017 · Zalando Research",
        "fun_fact": "Created as a harder drop-in replacement for MNIST after researchers noted MNIST was \"too easy\" for modern CNNs",
        "dist": [("Each class", 10)] * 10,
    },
    {
        "name": "Wine Quality",
        "samples": 6497, "features": "11 (acidity, sulphates, alcohol…)", "classes": "10 quality scores (3–9)",
        "year": "2009 · UCI · Cortez et al.",
        "fun_fact": "Physicochemical tests alone can predict wine quality — no sommelier required (though accuracy tops out ~65%)",
        "dist": [("Score ≤5", 46), ("Score 6", 40), ("Score ≥7", 14)],
    },
    {
        "name": "ImageNet (ILSVRC)",
        "samples": 1200000, "features": "Variable (high-res RGB images)", "classes": "1,000 object categories",
        "year": "2010 · Fei-Fei Li et al.",
        "fun_fact": "AlexNet halved the error rate on ImageNet in 2012 — the moment the deep learning era officially began",
        "dist": [("~1,200 imgs/class", 100)],
    },
    {
        "name": "IMDB Movie Reviews",
        "samples": 50000, "features": "Variable-length text reviews", "classes": "2 — Positive · Negative",
        "year": "2011 · Maas et al. (Stanford)",
        "fun_fact": "One of the earliest large-scale sentiment datasets; still a top benchmark for NLP transfer learning",
        "dist": [("Positive", 50), ("Negative", 50)],
    },
    {
        "name": "Boston Housing",
        "samples": 506, "features": "13 (crime rate, rooms, accessibility…)", "classes": "Continuous (median home value)",
        "year": "1978 · Harrison & Rubinfeld",
        "fun_fact": "Retired from scikit-learn in 2021 — the dataset contains a racial proxy variable that encodes discriminatory assumptions",
        "dist": [("<$20K", 34), ("$20–30K", 36), (">$30K", 30)],
    },
    {
        "name": "California Housing",
        "samples": 20640, "features": "8 (income, rooms, location…)", "classes": "Continuous (median house value)",
        "year": "1997 · Pace & Barry",
        "fun_fact": "Based on 1990 US Census data — it replaced Boston Housing as scikit-learn's default regression demo dataset",
        "dist": [("<$150K", 30), ("$150–250K", 40), (">$250K", 30)],
    },
    {
        "name": "Diabetes (Pima Indians)",
        "samples": 768, "features": "8 (glucose, BMI, age…)", "classes": "2 — Diabetic · Non-diabetic",
        "year": "1988 · National Institute of Diabetes",
        "fun_fact": "Collected from Pima Native American women in Arizona — the community has one of the highest type-2 diabetes prevalence rates worldwide",
        "dist": [("Non-diabetic", 65), ("Diabetic", 35)],
    },
    {
        "name": "Credit Card Fraud Detection",
        "samples": 284807, "features": "30 (PCA-transformed transactions)", "classes": "2 — Fraud · Legitimate",
        "year": "2013 · ULB (anonymized)",
        "fun_fact": "Only 0.17% of transactions are fraudulent — the ultimate class imbalance challenge; SMOTE was popularized on datasets like this",
        "dist": [("Legitimate", 99.83), ("Fraud", 0.17)],
    },
    {
        "name": "ETTh (Electricity Transformer Temperature)",
        "samples": 17420, "features": "7 (load, oil temp, time features)", "classes": "Continuous (oil temperature)",
        "year": "2021 · Zhou et al. (Informer paper)",
        "fun_fact": "Introduced alongside the Informer transformer — now a standard benchmark for long-sequence time-series forecasting",
        "dist": [("Train", 60), ("Val", 20), ("Test", 20)],
    },
    {
        "name": "Spam Email (Enron)",
        "samples": 33702, "features": "Variable-length email text", "classes": "2 — Spam · Ham",
        "year": "2004 · Metsis et al.",
        "fun_fact": "Built from real Enron employee emails released during the 2001 scandal — the largest public email corpus of its time",
        "dist": [("Ham", 75), ("Spam", 25)],
    },
    {
        "name": "Amazon Product Reviews",
        "samples": 233100000, "features": "Rating + text review", "classes": "5-star scale",
        "year": "2018 · McAuley et al.",
        "fun_fact": "233M+ reviews spanning 1996–2018 — more text than the entire Wikipedia, making it a major pretraining corpus",
        "dist": [("5★", 53), ("4★", 19), ("3★", 9), ("1-2★", 19)],
    },
    {
        "name": "MS COCO",
        "samples": 330000, "features": "High-res images + 5 captions each", "classes": "80 object categories",
        "year": "2014 · Microsoft Research",
        "fun_fact": "Every image has 5 human-written captions — it's the gold standard for image captioning and object detection benchmarks",
        "dist": [("Train", 83), ("Val+Test", 17)],
    },
    {
        "name": "NYC Taxi Trips",
        "samples": 1000000000, "features": "18 (pickup/dropoff, fare, tip…)", "classes": "Continuous (fare / duration)",
        "year": "2009–present · NYC TLC",
        "fun_fact": "1B+ trips since 2009 — researchers used it to expose driver identity from supposedly anonymised medallion IDs",
        "dist": [("Manhattan", 65), ("Outer boroughs", 35)],
    },
    {
        "name": "AWA2 (Animals with Attributes)",
        "samples": 37322, "features": "85 semantic attributes + images", "classes": "50 animal species",
        "year": "2018 · Xian et al.",
        "fun_fact": "Designed for zero-shot learning — the semantic attributes let models reason about animals they've never seen before",
        "dist": [("Seen (40)", 80), ("Unseen (10)", 20)],
    },
    {
        "name": "Reuters-21578",
        "samples": 21578, "features": "Variable-length news text", "classes": "90 categories (multi-label)",
        "year": "1987 · Reuters Ltd.",
        "fun_fact": "One of the first multi-label text datasets — many articles belong to multiple topics simultaneously",
        "dist": [("Earn", 40), ("Acq", 14), ("Other", 46)],
    },
    {
        "name": "Heart Disease (Cleveland)",
        "samples": 303, "features": "13 (age, cholesterol, ECG…)", "classes": "2 (presence/absence)",
        "year": "1988 · UCI · Detrano et al.",
        "fun_fact": "Despite only 303 samples, it's been cited 3,000+ times — proof that a tiny but well-curated dataset can outlast massive ones",
        "dist": [("No disease", 54), ("Disease", 46)],
    },
    {
        "name": "Car Evaluation",
        "samples": 1728, "features": "6 (buying, maint, doors, safety…)", "classes": "4 — unacc · acc · good · vgood",
        "year": "1997 · Bohanec · UCI",
        "fun_fact": "All 1,728 samples are synthetically generated from a hierarchical decision model — perfect for testing rule-induction algorithms",
        "dist": [("unacc", 70), ("acc", 22), ("good", 5), ("vgood", 3)],
    },
    {
        "name": "Bank Marketing",
        "samples": 45211, "features": "16 (age, job, balance, contact…)", "classes": "2 — subscribed / not subscribed",
        "year": "2012 · Moro et al. · UCI",
        "fun_fact": "Based on real Portuguese bank telemarketing calls (2008–2013) — hit rate was only 11.7%, showing how hard cold outreach is",
        "dist": [("Not subscribed", 88), ("Subscribed", 12)],
    },
    {
        "name": "Air Quality (UCI)",
        "samples": 9358, "features": "15 (CO, NOx, O3, humidity, temp…)", "classes": "Continuous (pollutant concentration)",
        "year": "2004–2005 · De Vito et al.",
        "fun_fact": "Collected hourly by a multisensor device in an Italian city — popular for studying sensor drift in IoT applications",
        "dist": [("Winter", 25), ("Spring", 25), ("Summer", 25), ("Autumn", 25)],
    },
    {
        "name": "Mushroom",
        "samples": 8124, "features": "22 (cap shape, odor, gill color…)", "classes": "2 — Edible · Poisonous",
        "year": "1987 · Schlimmer · UCI",
        "fun_fact": "\"Odor\" alone predicts edibility with 98.5% accuracy — the strongest single-feature predictor in any UCI dataset",
        "dist": [("Edible", 52), ("Poisonous", 48)],
    },
    {
        "name": "CIFAR-100",
        "samples": 60000, "features": "3072 (32×32×3 RGB)", "classes": "100 fine / 20 coarse",
        "year": "2009 · Krizhevsky",
        "fun_fact": "100 fine-grained classes grouped into 20 superclasses — \"baby\", \"boy\", \"girl\" are all subclasses of \"people\"",
        "dist": [("Each class", 1)] * 10,
    },
    {
        "name": "Twitter Sentiment140",
        "samples": 1600000, "features": "Variable-length tweets", "classes": "2 — Positive · Negative",
        "year": "2009 · Go et al. (Stanford)",
        "fun_fact": "Labels were automatically assigned using emoticons as proxies — :) = positive, :( = negative. No human annotation needed",
        "dist": [("Positive", 50), ("Negative", 50)],
    },
    {
        "name": "Solar Energy (Alabama)",
        "samples": 52560, "features": "137 (solar plant sensors)", "classes": "Continuous (energy output)",
        "year": "2015 · LSTNet paper",
        "fun_fact": "Hourly solar power readings across 137 stations — used to benchmark multivariate time-series forecasting models",
        "dist": [("Day (active)", 50), ("Night (zero)", 50)],
    },
    {
        "name": "Fake News (LIAR)",
        "samples": 12836, "features": "12 (speaker, context, history…)", "classes": "6 (pants-fire → true)",
        "year": "2017 · Wang · ACL",
        "fun_fact": "Sourced from PolitiFact fact-checks — speaker history (past lie count) is actually one of the best predictors of veracity",
        "dist": [("False/Mostly false", 43), ("Half-true", 21), ("True/Mostly true", 36)],
    },
    {
        "name": "Open Images V7",
        "samples": 9000000, "features": "Multi-res RGB + bounding boxes", "classes": "600 object categories",
        "year": "2022 · Google",
        "fun_fact": "9M images with 40M bounding boxes — the annotations took 15M human-hours to produce",
        "dist": [("Train", 89), ("Val", 6), ("Test", 5)],
    },
]


def make_bar(label: str, pct: float, width: int = 20) -> str:
    filled = round(pct / 100 * width)
    return f"{label:<14} {'█' * filled}{'░' * (width - filled)} {pct:.0f}%"


def build_spotlight(dataset: dict) -> str:
    rows = "\n".join(make_bar(lbl, pct) for lbl, pct in dataset["dist"][:4])
    return (
        f'| | **{dataset["name"]}** |\n'
        f"|:--|:--|\n"
        f'| 📁 Samples | {dataset["samples"]:,} |\n'
        f'| 🏷️ Features | {dataset["features"]} |\n'
        f'| 🎯 Classes | {dataset["classes"]} |\n'
        f'| 📅 Introduced | {dataset["year"]} |\n'
        f'| 💡 Fun fact | {dataset["fun_fact"]} |\n'
        f"\n```\n{rows}\n```"
    )


def main():
    day_of_year = datetime.now().timetuple().tm_yday
    dataset = DATASETS[day_of_year % len(DATASETS)]
    spotlight = build_spotlight(dataset)

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- DATASET_SPOTLIGHT_START -->).*?(<!-- DATASET_SPOTLIGHT_END -->)"
    replacement = f"<!-- DATASET_SPOTLIGHT_START -->\n{spotlight}\n<!-- DATASET_SPOTLIGHT_END -->"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Updated: {dataset['name']}")


if __name__ == "__main__":
    main()

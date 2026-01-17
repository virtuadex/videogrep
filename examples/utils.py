import os
import sys

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# Shared stop words
STOPWORDS_EN = ["i", "we're", "you're", "that's", "it's", "us", "i'm", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
STOPWORDS_PT = ["a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "até", "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles", "depois", "do", "dos", "e", "é", "ela", "elas", "ele", "eles", "em", "entre", "era", "eram", "éramos", "essa", "essas", "esse", "esses", "esta", "está", "estamos", "estão", "estas", "estava", "estavam", "estávamos", "este", "esteja", "estejam", "estejamos", "estes", "esteve", "estive", "estivemos", "estivera", "estiveram", "estivéramos", "estiverem", "estivermos", "estivesse", "estivessem", "estivéssemos", "estou", "eu", "foi", "fomos", "for", "fora", "foram", "fôramos", "forem", "formos", "fosse", "fossem", "fôssemos", "fui", "há", "haja", "hajam", "hajamos", "hão", "haver", "havia", "haviam", "havíamos", "houve", "houvemos", "houvera", "houveram", "houvéramos", "houverei", "houverem", "houveremos", "houveria", "houveriam", "houveríamos", "houvermos", "houvesse", "houvessem", "houvéssemos", "isso", "isto", "já", "lhe", "lhes", "mais", "mas", "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "na", "nas", "nem", "no", "nos", "nós", "nossa", "nossas", "nosso", "nossos", "num", "numa", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual", "quando", "que", "quem", "são", "se", "seja", "sejam", "sejamos", "sem", "ser", "será", "serão", "serei", "seremos", "seria", "seriam", "seríamos", "seu", "seus", "só", "somos", "sou", "sua", "suas", "também", "te", "tem", "tém", "temos", "tenha", "tenham", "tenhamos", "tenho", "terá", "terão", "terei", "teremos", "teria", "teriam", "teríamos", "teu", "teus", "teve", "tinha", "tinham", "tínhamos", "tive", "tivemos", "tivera", "tiveram", "tivéramos", "tiverem", "tivermos", "tivesse", "tivessem", "tivéssemos", "tu", "tua", "tuas", "um", "uma", "você", "vocês", "vos"]
STOPWORDS = set(STOPWORDS_EN + STOPWORDS_PT)

def load_spacy_model(lang):
    """Tries to load the best available model for the language."""
    if not SPACY_AVAILABLE:
        print("Error: Spacy is not installed. Please run: pip install spacy")
        sys.exit(1)

    if spacy.prefer_gpu():
        print("GPU detected! Using GPU for spacy processing.")
    else:
        print("No GPU detected or spacy-transformers not configured for GPU. Using CPU.")

    if lang == "en":
        models = ["en_core_web_trf", "en_core_web_lg", "en_core_web_sm"]
    else:
        models = ["pt_core_news_lg", "pt_core_news_sm"]

    for model in models:
        try:
            print(f"Attempting to load spacy model: {model}")
            return spacy.load(model)
        except OSError:
            continue
    
    print(f"Error: No spacy models found for language '{lang}'.")
    print(f"Please run: python -m spacy download {models[0]}")
    sys.exit(1)

def calculate_silences(timestamps, filename, min_duration=0.5, max_duration=None, adjuster=0.0):
    """
    Calculates silences (gaps) between words or sentences.
    Returns a list of dicts with 'start', 'end', and 'file'.
    """
    items = []
    if "words" in timestamps[0]:
        for sentence in timestamps:
            items += sentence["words"]
    else:
        items = timestamps

    silences = []
    for item1, item2 in zip(items[:-1], items[1:]):
        start = item1["end"]
        end = item2["start"] - adjuster
        duration = end - start
        
        if duration >= min_duration:
            if max_duration is None or duration <= max_duration:
                silences.append({"start": start, "end": end, "file": filename})
    
    return silences


def merge_clips(items, filename, min_silence_duration=1.0):
    """
    Merges segments if the gap between them is less than min_silence_duration.
    """
    if not items:
        return []

    clips = []
    current_clip = {"start": items[0]["start"], "end": items[0]["end"], "file": filename}

    for item in items[1:]:
        gap = item["start"] - current_clip["end"]
        if gap < min_silence_duration:
            current_clip["end"] = item["end"]
        else:
            clips.append(current_clip)
            current_clip = {"start": item["start"], "end": item["end"], "file": filename}
    
    clips.append(current_clip)
    return clips

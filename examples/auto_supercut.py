import sys
import os
import videogrep
from videogrep import transcribe
from collections import Counter
import random

stopwords_en = ["i", "we're", "you're", "that's", "it's", "us", "i'm", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
stopwords_pt = ["a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "até", "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles", "depois", "do", "dos", "e", "é", "ela", "elas", "ele", "eles", "em", "entre", "era", "eram", "éramos", "essa", "essas", "esse", "esses", "esta", "está", "estamos", "estão", "estas", "estava", "estavam", "estávamos", "este", "esteja", "estejam", "estejamos", "estes", "esteve", "estive", "estivemos", "estivera", "estiveram", "estivéramos", "estiverem", "estivermos", "estivesse", "estivessem", "estivéssemos", "estou", "eu", "foi", "fomos", "for", "fora", "foram", "fôramos", "forem", "formos", "fosse", "fossem", "fôssemos", "fui", "há", "haja", "hajam", "hajamos", "hão", "haver", "havia", "haviam", "havíamos", "houve", "houvemos", "houvera", "houveram", "houvéramos", "houverei", "houverem", "houveremos", "houveria", "houveriam", "houveríamos", "houvermos", "houvesse", "houvessem", "houvéssemos", "isso", "isto", "já", "lhe", "lhes", "mais", "mas", "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "na", "nas", "nem", "no", "nos", "nós", "nossa", "nossas", "nosso", "nossos", "num", "numa", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual", "quando", "que", "quem", "são", "se", "seja", "sejam", "sejamos", "sem", "ser", "será", "serão", "serei", "seremos", "seria", "seriam", "seríamos", "seu", "seus", "só", "somos", "sou", "sua", "suas", "também", "te", "tem", "tém", "temos", "tenha", "tenham", "tenhamos", "tenho", "terá", "terão", "terei", "teremos", "teria", "teriam", "teríamos", "teu", "teus", "teve", "tinha", "tinham", "tínhamos", "tive", "tivemos", "tivera", "tiveram", "tivéramos", "tiverem", "tivermos", "tivesse", "tivessem", "tivéssemos", "tu", "tua", "tuas", "um", "uma", "você", "vocês", "vos"]

stopwords = set(stopwords_en + stopwords_pt)

def auto_supercut(vidfile, total_words=3):
    """automatically creates a supercut from a video by selecting three random words"""

    # ensure transcript exists
    if not videogrep.find_transcript(vidfile):
        print(f"Transcript not found for {vidfile}. Transcribing with Whisper...")
        transcribe.transcribe(vidfile, method="whisper")

    # grab all the words from the transcript
    unigrams = videogrep.get_ngrams(vidfile)

    # remove stop words
    unigrams = [w for w in unigrams if w[0] not in stopwords]

    # get the most common 10 words
    most_common = Counter(unigrams).most_common(10)

    # transform the list into just the words
    words = [w[0][0] for w in most_common]

    # randomize the list
    random.shuffle(words)

    # select the first N words
    words = words[0:total_words]

    # create a query
    query = "|".join(words)

    # create the video
    videogrep.videogrep(vidfile, query, search_type="fragment", output="auto_supercut.mp4")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_supercut.py <video_file>")
        sys.exit(1)
    vidfile = sys.argv[1]
    auto_supercut(vidfile)

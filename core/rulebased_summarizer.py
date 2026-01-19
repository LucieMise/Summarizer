from collections import Counter
import re
from loaders.url_loader import fetch_text_from_url

class RuleBasedSummarizer:
    def __init__(self, min_sentence_length=5, max_sentence_length=30, summary_sentences=3, max_summary_words=150):
        """
        Era 1: Rule-Based / Extractive Summarization with concise output.

        Args:
            min_sentence_length: ignore sentences shorter than this
            max_sentence_length: truncate sentences longer than this
            summary_sentences: max number of top sentences to pick
            max_summary_words: max total words in the final summary
        """
        self.min_sentence_length = min_sentence_length
        self.max_sentence_length = max_sentence_length
        self.summary_sentences = summary_sentences
        self.max_summary_words = max_summary_words

    def _split_sentences(self, text):
        # Simple sentence splitter using punctuation
        sentences = re.split(r'(?<=[.!?]) +', text)
        # Filter sentences that are too short
        sentences = [
            s.strip() for s in sentences
            if len(s.split()) >= self.min_sentence_length
        ]
        return sentences

    def _score_sentences(self, sentences):
        # Count word frequencies (ignoring punctuation, lowercase)
        words = []
        for sentence in sentences:
            words.extend(re.findall(r'\w+', sentence.lower()))
        freq = Counter(words)

        # Score sentences by sum of word frequencies
        sentence_scores = {}
        for sentence in sentences:
            sentence_words = re.findall(r'\w+', sentence.lower())
            score = sum(freq[word] for word in sentence_words)
            sentence_scores[sentence] = score
        return sentence_scores

    def summarize(self, text):
        sentences = self._split_sentences(text)
        if not sentences:
            return "Text too short to summarize."

        sentence_scores = self._score_sentences(sentences)
        # Pick top N sentences by score
        top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:self.summary_sentences]

        # Keep original order and truncate long sentences
        top_sentences_sorted = []
        for s in sentences:
            if s in top_sentences:
                words = s.split()
                if len(words) > self.max_sentence_length:
                    s = " ".join(words[:self.max_sentence_length]) + "..."
                top_sentences_sorted.append(s)

        # Join sentences and truncate overall summary if needed
        summary_words = " ".join(top_sentences_sorted).split()
        if len(summary_words) > self.max_summary_words:
            summary_words = summary_words[:self.max_summary_words]
            summary = " ".join(summary_words) + "..."
        else:
            summary = " ".join(summary_words)

        return summary


if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    print("Fetching article...")
    text = fetch_text_from_url(url)
    print("Article fetched. Summarizing with Era 1 rule-based method...")

    summarizer = RuleBasedSummarizer(summary_sentences=5, max_summary_words=150)
    summary = summarizer.summarize(text)

    print("\nSUMMARY:\n")
    print(summary)
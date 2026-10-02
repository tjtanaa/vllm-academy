"""A count-based baseline. The corpus and query are synthetic, not benchmarks."""
from collections import Counter, defaultdict
import json

class Bigram:
    def __init__(self, sentences: list[list[str]], alpha: float = 1.0):
        if alpha <= 0 or not sentences or any(not s for s in sentences):
            raise ValueError("Supply nonempty sentences and positive smoothing")
        self.alpha = alpha
        self.vocab = sorted({w for s in sentences for w in s})
        self.counts = defaultdict(Counter)
        for sentence in sentences:
            for left, right in zip(sentence, sentence[1:]):
                self.counts[left][right] += 1

    def predict(self, history: list[str]) -> dict[str, float]:
        if not history:
            raise ValueError("History must not be empty")
        counts = self.counts.get(history[-1], Counter())
        total = sum(counts.values()) + self.alpha * len(self.vocab)
        return {w: (counts[w] + self.alpha) / total for w in self.vocab}

if __name__ == '__main__':
    m = Bigram([['cats', 'eat', 'fish'], ['dogs', 'eat', 'food']])
    a, b = m.predict(['cats', 'eat']), m.predict(['dogs', 'eat'])
    print(json.dumps({'cats_eat': a, 'dogs_eat': b,
                      'same_last_word_same_distribution': a == b}, indent=2))

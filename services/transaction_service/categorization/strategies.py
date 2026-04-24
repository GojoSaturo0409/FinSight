from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import os
import logging

logger = logging.getLogger(__name__)


class CategorizationStrategy(ABC):
    """Abstract base class for transaction categorization strategies (Strategy Pattern)."""

    @abstractmethod
    def categorize(self, transaction: Dict[str, Any]) -> str:
        pass


class RuleBasedStrategy(CategorizationStrategy):
    """
    Rule-based categorization using a keyword dictionary.
    Runs with low latency — instant lookup against merchant names.
    """

    def __init__(self):
        # Comprehensive keyword -> category mapping
        self.rules: Dict[str, str] = {
            # Transport
            "uber": "Transport",
            "lyft": "Transport",
            "ola": "Transport",
            "grab": "Transport",
            "taxi": "Transport",
            "metro": "Transport",
            "gas station": "Transport",
            "shell": "Transport",
            "bp": "Transport",
            "parking": "Transport",

            # Food & Dining
            "mcdonalds": "Food",
            "starbucks": "Food",
            "dominos": "Food",
            "pizza": "Food",
            "restaurant": "Food",
            "cafe": "Food",
            "grubhub": "Food",
            "doordash": "Food",
            "ubereats": "Food",
            "zomato": "Food",
            "swiggy": "Food",
            "chipotle": "Food",
            "subway": "Food",
            "burger": "Food",
            "bakery": "Food",
            "grocery": "Food",
            "walmart": "Food",
            "whole foods": "Food",
            "trader joe": "Food",

            # Subscriptions
            "netflix": "Subscriptions",
            "spotify": "Subscriptions",
            "hulu": "Subscriptions",
            "disney+": "Subscriptions",
            "apple music": "Subscriptions",
            "youtube premium": "Subscriptions",
            "hbo": "Subscriptions",
            "icloud": "Subscriptions",
            "adobe": "Subscriptions",
            "dropbox": "Subscriptions",
            "microsoft 365": "Subscriptions",

            # Housing
            "rent": "Housing",
            "mortgage": "Housing",
            "lease": "Housing",
            "property": "Housing",
            "zillow": "Housing",
            "airbnb": "Housing",

            # Utilities
            "electric": "Utilities",
            "water bill": "Utilities",
            "internet": "Utilities",
            "comcast": "Utilities",
            "at&t": "Utilities",
            "verizon": "Utilities",
            "t-mobile": "Utilities",
            "gas bill": "Utilities",
            "power": "Utilities",

            # Shopping
            "amazon": "Shopping",
            "flipkart": "Shopping",
            "ebay": "Shopping",
            "target": "Shopping",
            "costco": "Shopping",
            "ikea": "Shopping",
            "nike": "Shopping",
            "zara": "Shopping",
            "h&m": "Shopping",

            # Entertainment
            "cinema": "Entertainment",
            "theater": "Entertainment",
            "concert": "Entertainment",
            "ticketmaster": "Entertainment",
            "steam": "Entertainment",
            "playstation": "Entertainment",
            "xbox": "Entertainment",
            "arcade": "Entertainment",

            # Healthcare
            "pharmacy": "Healthcare",
            "hospital": "Healthcare",
            "doctor": "Healthcare",
            "dental": "Healthcare",
            "cvs": "Healthcare",
            "walgreens": "Healthcare",
            "clinic": "Healthcare",
            "medical": "Healthcare",

            # Education
            "university": "Education",
            "tuition": "Education",
            "coursera": "Education",
            "udemy": "Education",
            "bookstore": "Education",
            "school": "Education",

            # Income
            "salary": "Income",
            "payroll": "Income",
            "deposit": "Income",
            "freelance": "Income",
            "dividend": "Income",
            "interest": "Income",
        }

    def categorize(self, transaction: Dict[str, Any]) -> str:
        merchant = transaction.get("merchant", "").lower()
        for keyword, category in self.rules.items():
            if keyword in merchant:
                return category
        return "Miscellaneous"


class MLStrategy(CategorizationStrategy):
    """
    ML-based categorization using a Naive Bayes classifier with TF-IDF features.
    Trains on a built-in keyword dataset at initialization.
    Falls back to RuleBasedStrategy when sklearn is unavailable or confidence is low.
    """

    def __init__(self):
        self._model = None
        self._vectorizer = None
        self._fallback = RuleBasedStrategy()
        self._categories: List[str] = []
        self._trained = False
        self._model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
        self._load_or_train()

    def _load_or_train(self):
        """Load from pickle if exists, otherwise train and save."""
        import pickle
        if os.path.exists(self._model_path):
            try:
                with open(self._model_path, 'rb') as f:
                    data = pickle.load(f)
                self._model = data['model']
                self._vectorizer = data['vectorizer']
                self._categories = data['categories']
                self._trained = True
                logger.info("MLStrategy: Successfully loaded model from %s", self._model_path)
                return
            except Exception as e:
                logger.error("MLStrategy: Failed to load pickle file: %s. Re-training.", str(e))
        
        self._train()

    def _train(self):
        """Train the Naive Bayes model on a bundled keyword dataset."""
        try:
            from sklearn.naive_bayes import MultinomialNB
            from sklearn.feature_extraction.text import TfidfVectorizer

            # Training dataset: (merchant_keyword, category)
            training_data: List[Tuple[str, str]] = [
                # Transport
                ("uber ride", "Transport"), ("lyft driver", "Transport"),
                ("taxi fare", "Transport"), ("gas station fuel", "Transport"),
                ("metro transit", "Transport"), ("parking lot", "Transport"),
                ("ola cab", "Transport"), ("shell petroleum", "Transport"),

                # Food
                ("mcdonalds burger", "Food"), ("starbucks coffee", "Food"),
                ("dominos pizza delivery", "Food"), ("restaurant dining", "Food"),
                ("grubhub order", "Food"), ("doordash delivery", "Food"),
                ("grocery store", "Food"), ("walmart supermarket", "Food"),
                ("whole foods market", "Food"), ("trader joe organic", "Food"),
                ("chipotle mexican grill", "Food"), ("subway sandwich", "Food"),
                ("cafe latte", "Food"), ("bakery bread", "Food"),
                ("zomato food", "Food"), ("swiggy delivery", "Food"),

                # Subscriptions
                ("netflix streaming", "Subscriptions"), ("spotify music", "Subscriptions"),
                ("hulu subscription", "Subscriptions"), ("disney plus", "Subscriptions"),
                ("apple music", "Subscriptions"), ("youtube premium", "Subscriptions"),
                ("hbo max", "Subscriptions"), ("adobe creative cloud", "Subscriptions"),
                ("icloud storage", "Subscriptions"), ("microsoft 365 office", "Subscriptions"),

                # Housing
                ("rent payment apartment", "Housing"), ("mortgage home loan", "Housing"),
                ("lease property", "Housing"), ("airbnb rental", "Housing"),
                ("zillow rent", "Housing"),

                # Utilities
                ("electric bill power", "Utilities"), ("water bill utility", "Utilities"),
                ("internet comcast broadband", "Utilities"), ("phone bill at&t", "Utilities"),
                ("verizon wireless bill", "Utilities"), ("t-mobile phone", "Utilities"),
                ("gas bill heating", "Utilities"),

                # Shopping
                ("amazon purchase", "Shopping"), ("ebay auction buy", "Shopping"),
                ("target store", "Shopping"), ("costco wholesale", "Shopping"),
                ("ikea furniture", "Shopping"), ("nike shoes", "Shopping"),
                ("zara clothing", "Shopping"), ("flipkart online", "Shopping"),

                # Entertainment
                ("cinema movie ticket", "Entertainment"), ("concert ticket", "Entertainment"),
                ("ticketmaster event", "Entertainment"), ("steam game", "Entertainment"),
                ("playstation store", "Entertainment"), ("xbox live", "Entertainment"),
                ("theater show", "Entertainment"), ("arcade gaming", "Entertainment"),

                # Healthcare
                ("pharmacy prescription", "Healthcare"), ("hospital medical", "Healthcare"),
                ("doctor appointment", "Healthcare"), ("dental clinic", "Healthcare"),
                ("cvs health", "Healthcare"), ("walgreens drug", "Healthcare"),

                # Education
                ("university tuition", "Education"), ("coursera course", "Education"),
                ("udemy online class", "Education"), ("bookstore textbook", "Education"),
                ("school fee", "Education"),

                # Income
                ("salary payroll deposit", "Income"), ("freelance payment", "Income"),
                ("dividend income", "Income"), ("interest earned", "Income"),
            ]

            merchants = [item[0] for item in training_data]
            labels = [item[1] for item in training_data]

            self._vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
            X = self._vectorizer.fit_transform(merchants)

            self._model = MultinomialNB(alpha=0.1)
            self._model.fit(X, labels)

            self._categories = list(set(labels))
            self._trained = True
            logger.info("MLStrategy: Naive Bayes classifier trained successfully on %d samples", len(training_data))

            # Save to pickle
            import pickle
            try:
                with open(self._model_path, 'wb') as f:
                    pickle.dump({
                        'model': self._model,
                        'vectorizer': self._vectorizer,
                        'categories': self._categories
                    }, f)
                logger.info("MLStrategy: Successfully saved model to %s", self._model_path)
            except Exception as e:
                logger.error("MLStrategy: Failed to save model to pickle: %s", str(e))

        except ImportError:
            logger.warning("MLStrategy: scikit-learn not installed, falling back to RuleBasedStrategy")
            self._trained = False
        except Exception as e:
            logger.error("MLStrategy: Training failed: %s, falling back to RuleBasedStrategy", str(e))
            self._trained = False

    def categorize(self, transaction: Dict[str, Any]) -> str:
        if not self._trained or self._model is None or self._vectorizer is None:
            return self._fallback.categorize(transaction)

        merchant = transaction.get("merchant", "")
        if not merchant:
            return self._fallback.categorize(transaction)

        try:
            import numpy as np

            X = self._vectorizer.transform([merchant.lower()])
            probabilities = self._model.predict_proba(X)[0]
            max_prob = np.max(probabilities)
            prediction = self._model.predict(X)[0]

            # If confidence is below 40%, fall back to rule-based
            if max_prob < 0.4:
                rule_result = self._fallback.categorize(transaction)
                if rule_result != "Miscellaneous":
                    return rule_result
                # Even rule-based didn't match, use ML prediction with suffix
                return f"{prediction} - ML Predicted"

            return f"{prediction} - ML Predicted"

        except Exception as e:
            logger.error("MLStrategy: Prediction failed: %s", str(e))
            return self._fallback.categorize(transaction)

    def update_model(self, merchant: str, correct_category: str):
        """Active learning feedback loop to incrementally update the model weights."""
        if not self._trained or self._model is None or self._vectorizer is None:
            logger.warning("MLStrategy: Model not trained, skipping feedback update.")
            return

        try:
            X = self._vectorizer.transform([merchant.lower()])
            # partial_fit updates weights incrementally in Naive Bayes
            self._model.partial_fit(X, [correct_category], classes=self._model.classes_)
            
            # Save the updated model back to pickle
            import pickle
            with open(self._model_path, 'wb') as f:
                pickle.dump({
                    'model': self._model,
                    'vectorizer': self._vectorizer,
                    'categories': self._categories
                }, f)
            logger.info("MLStrategy: Successfully active-learned merchant %s -> %s", merchant, correct_category)
        except Exception as e:
            logger.error("MLStrategy: Feedback loop partial_fit failed: %s", str(e))

import re
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, AutoModelForSequenceClassification, AutoTokenizer
from config import CONFIG

class AssistantModel:
    def __init__(self):
        # Загрузка основной модели и токенизатора
        self.tokenizer = GPT2Tokenizer.from_pretrained("sberbank-ai/rugpt3medium_based_on_gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("sberbank-ai/rugpt3medium_based_on_gpt2")
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
            self.model.resize_token_embeddings(len(self.tokenizer))

        # Загрузка модели токсичности
        self.toxicity_tokenizer = AutoTokenizer.from_pretrained("SkolkovoInstitute/russian_toxicity_classifier")
        self.toxicity_model = AutoModelForSequenceClassification.from_pretrained("SkolkovoInstitute/russian_toxicity_classifier")

        self.forbidden_words = self.load_forbidden_words(CONFIG['forbidden_words_path'])

    @staticmethod
    def load_forbidden_words(file_path):
        """Загружает список запрещенных слов из файла."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f.readlines()]

    def is_appropriate(self, response):
        """Проверяет, является ли ответ подходящим по заданным критериям."""
        response_lower = response.lower()
        
        # Проверка на запрещенные слова
        for word in self.forbidden_words:
            if re.search(r'\b' + re.escape(word) + r'\b', response_lower):
                return False

        # Проверка на токсичность
        inputs = self.toxicity_tokenizer(response, return_tensors="pt")
        with torch.no_grad():
            outputs = self.toxicity_model(**inputs)
        scores = torch.softmax(outputs.logits, dim=1)
        toxic_score = scores[0][1].item()
        
        return toxic_score < 0.7

    def generate_response(self, prompt):
        """Генерирует ответ на основе входного промпта и предустановленного префикса."""
        pre_prompt = CONFIG['pre_prompt'] + "\n" + \
    "Пожалуйста, отвечайте на вопросы, связанные с учебой и повседневной жизнью. Если вы не уверены, старайтесь дать полезную и общую рекомендацию. Не отвечайте на вопросы, которые могут привести к вредным последствиям.\n\n"

        full_prompt = f"{pre_prompt}\nПользователь: {prompt}\nАссистент:"

        input_ids = self.tokenizer.encode(full_prompt, return_tensors='pt')
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_length=150,
                do_sample=True,
                top_k=40,
                top_p=0.9,
                temperature=0.7,
                no_repeat_ngram_size=3,
                pad_token_id=self.tokenizer.eos_token_id
            )
        response = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        response = response[len(full_prompt):].strip()

        if not self.is_coherent(response):
            return "Извините, я не могу ответить на этот вопрос, так как он выходит за рамки моей компетенции."

        return response if self.is_appropriate(response) else "Извините, я не могу ответить на этот вопрос."

    def is_coherent(self, response):
        """Проверяет, является ли ответ осмысленным и логичным."""
        sentences = response.split(". ")
        if len(sentences) < 2:
            return False
        
        words = response.split()
        word_counts = {word: words.count(word) for word in set(words)}
        if any(count > len(words) / 3 for count in word_counts.values()):
            return False

        return True

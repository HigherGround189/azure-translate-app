from transformers import MarianMTModel, MarianTokenizer

class MarianManager:
    def __init__(self):
        self.english_model_name = "Helsinki-NLP/opus-mt-zh-en"
        self.english_tokenizer = MarianTokenizer.from_pretrained(self.english_model_name)
        self.english_output = MarianMTModel.from_pretrained(self.english_model_name)

        self.chinese_model_name = "Helsinki-NLP/opus-mt-en-zh"
        self.chinese_tokenizer = MarianTokenizer.from_pretrained(self.chinese_model_name)
        self.chinese_output = MarianMTModel.from_pretrained(self.chinese_model_name)

    def english_to_chinese(self, src_text: str) -> str:
        translated = self.chinese_output.generate(**self.chinese_tokenizer(text=src_text, return_tensors="pt", padding=True))
        tgt_text = [self.chinese_tokenizer.decode(t, skip_special_tokens=True) for t in translated]
        return tgt_text

    def chinese_to_english(self, src_text: str) -> str:
        translated = self.english_output.generate(**self.english_tokenizer(text=src_text, return_tensors="pt", padding=True))
        tgt_text = [self.english_tokenizer.decode(t, skip_special_tokens=True) for t in translated]
        return tgt_text
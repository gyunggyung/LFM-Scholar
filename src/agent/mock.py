class MockLlama:
    """Fallback class to demonstrate agent flow without heavy model loading."""
    def __call__(self, prompt, **kwargs):
        print("[MockLlama] Generating dummy text based on prompt...")
        return {
            'choices': [{
                'text': "\n\nBased on the retrieved papers, we identify three key themes. First, [Vaswani2017Attention] introduced the Transformer architecture, revolutionizing sequence modeling. Second, [Devlin2018BERT] applied bidirectional training for better context understanding. Third, [Brown2020Language] demonstrated the few-shot capabilities of large language models. These works collectively establish the foundation of modern NLP.\n"
            }]
        }

class Config:
    def __init__(self, batch_size=300, input_size=31, max_length=8, hidden_size=10, static_size = 5):
        self.batch_size = batch_size
        self.input_size = input_size
        self.max_length = max_length
        self.hidden_size = hidden_size
        self.static_size = static_size
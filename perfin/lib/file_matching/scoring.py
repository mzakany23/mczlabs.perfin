from .base import Base




class ScoreResult(Base):
    def __init__(self, *args, **kwargs):
        super(ScoreResult, self).__init__(*args, **kwargs)
        self.validate(['match'])
        match = kwargs.get('match')
        self.score = match.total_score
        self.domain = match.domain
        self.match = match
    
    @property
    def __info__(self):
        self.header_print('Score Result')
        self.match.__info__

    @property
    def confidence(self):
        score = self.score
        confidence = 'very poor'

        if score >= 200:
            confidence = 'very likely'
        elif score > 150:
            confidence = 'likely'
        elif score > 100:
            confidence = 'marginal'
        elif score > 90:
            confidence = 'poor'
        return confidence

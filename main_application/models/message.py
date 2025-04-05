from pydantic import BaseModel

class KafkaMessage(BaseModel):
    bucket: str
    key: str
    candidate_id: str
from pydantic import BaseModel,Field



class StartStreamRequestSchema(BaseModel):
    url:str = Field(...)
    
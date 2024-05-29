import duckdb

from typing import Optional, List
from instructor import llm_validator
from typing_extensions import Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator


class Decomposition(BaseModel):
    '''
    Breaks down a user's natural language query into components of a sql query.
    * Price data is in item_file
    * Sales data is in item_movement
    '''
    understanding: str = Field(description='Explain your understanding of users query. Think in select / from / where terms')
    table: str = Field(description='Identify what table to query')
    
    @field_validator('table')
    @classmethod
    def validate_table(cls, v):
        if v not in ['item_file', 'sale_batch']:
            raise ValueError('table must be in available tables')
        return v

    def intent_mapping(self):
        return self.intent.name
    
    def generate_next_prompt(self):
        return f"Help me {self.understanding} by querying {self.table}"


class GenerateQuery(BaseModel):
    query: str = Field(description='A syntactically correct duckdb sql query to get data user is asking for')
    sql_confidence: str = Field(description='How confident are you that this query is syntactically correct')
    intent_confidence: str = Field(description='How confident are you that this query is matches what user wants')

    def execute_query(self):
        with duckdb.connect('./data/duckdb.db') as conn:
            return conn.query(self.query).df()
        

class Inspection(BaseModel):
    alignment_score: int = Field(description='Score for alignment of question and query intent. Scale of 1 (totally different intents) to 10 (perfectly aligned intent)')
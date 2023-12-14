import torch
import sys
import os
from tqdm import tqdm
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, MapReduceDocumentsChain, ReduceDocumentsChain, StuffDocumentsChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from tqdm import tqdm
import transformers
import pandas as pd
import numpy as np
import logging
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from huggingface_hub import hf_hub_download
from langchain.llms import HuggingFacePipeline
from torch import  bfloat16
import transformers


def load_intel_model():
    sample_generation = True

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path='Intel/neural-chat-7b-v3-1',
    )
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_8bit=False,
        load_in_4bit=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=bfloat16
    )
    model_config = transformers.AutoConfig.from_pretrained(
        pretrained_model_name_or_path='Intel/neural-chat-7b-v3-1',
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path='Intel/neural-chat-7b-v3-1',
        resume_download=True,
        trust_remote_code=True,
        config=model_config,
        quantization_config=bnb_config,
        device_map='auto'
    )
    model.eval()
    pipeline_args = {}
    if sample_generation:
        pipeline_args['top_k'] = 20
        pipeline_args['top_p'] = 0.95
        pipeline_args['temperature'] = 0.1
    generate_text = transformers.pipeline(
        model=model,
        tokenizer=tokenizer,
        return_full_text=True,
        task='text-generation',
        do_sample=sample_generation,
        max_new_tokens=4095,
        repetition_penalty=1.1,
        **pipeline_args
    )
    generate_text.model.config.pad_token_id = generate_text.model.config.eos_token_id

    llm = HuggingFacePipeline(pipeline=generate_text)

    return llm

def get_candidate_info(agent_prompts, cv, llm):
    """_summary_

    Args:
        agent_prompts (list): list of prompts to get info
        cv (str): imput CV variable
        llm (hugging face pipeline):llm used 

    Returns:
        _type_: full structured info about candidate
    """

    candidate_dict = {}

    for i, prompt_part in enumerate(tqdm(agent_prompts)):
        prompt = PromptTemplate(
            input_variables=['texts'],
            template=prompt_part
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(cv)
        candidate_dict[i] = response

    candidate_info = (f"LEVEL:\n{candidate_dict[0]}\n"
                f"EXPERIENCE:\n{candidate_dict[1]}\n"
                f"SKILLS:\n{candidate_dict[2]}\n"
                 f"EDUCATION:\n{candidate_dict[3]}")
    
    return candidate_info

def get_vacancy_info(vacancy_prompt, vacancy, llm):
    prompt = PromptTemplate(
      input_variables=['texts'],
      template=vacancy_prompt
  )
    chain = LLMChain(llm=llm, prompt=prompt)
    key_vacancy = chain.run(vacancy)

    return key_vacancy

def get_recs(recs_prompt, candidate_info, key_vacancy, llm):
    prompt = PromptTemplate(
      input_variables=["resume", "recs","vacancy"],
      template=recs_prompt
  )
    chain = LLMChain(llm=llm, prompt=prompt)
    recs = chain.run({'resume': candidate_info, 'vacancy': key_vacancy})

    return recs

def get_score(score_prompt, candidate_info, key_vacancy, llm):
    prompt = PromptTemplate(
      input_variables=["resume", "recs",  "vacancy"],
      template=score_prompt
  )
    chain = LLMChain(llm=llm, prompt=prompt)
    score = chain.run({'resume': candidate_info, 'recs': recs, 'vacancy': key_vacancy})

    return score






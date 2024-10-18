import logging
import requests
import json
import re
import os
from decouple import config

logger = logging.getLogger(__name__)
OLLAMA_API_URL = config('OLLAMA_API_URL', default='http://localhost:11434/api/generate')

def extract_json(response_text):
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(response_text):
        try:
            obj, pos = decoder.raw_decode(response_text, pos)
            return obj
        except json.JSONDecodeError:
            pos += 1
    return None


def analyze_writing_sample(writing_sample):
    encoding_prompt = f'''
Please analyze the writing style and personality of the given writing sample. Provide a detailed assessment of their characteristics using the following template. Rate each applicable characteristic on a scale of 1-10 where relevant, or provide a descriptive value. Return the results in a JSON format.


 "name": "[Author/Character Name]",
 "vocabulary_complexity": [1-10],
 "sentence_structure": "[simple/complex/varied]",
 "paragraph_organization": "[structured/loose/stream-of-consciousness]",
 "idiom_usage": [1-10],
 "metaphor_frequency": [1-10],
 "simile_frequency": [1-10],
 "tone": "[formal/informal/academic/conversational/etc.]",
 "punctuation_style": "[minimal/heavy/unconventional]",
 "contraction_usage": [1-10],
 "pronoun_preference": "[first-person/third-person/etc.]",
 "passive_voice_frequency": [1-10],
 "rhetorical_question_usage": [1-10],
 "list_usage_tendency": [1-10],
 "personal_anecdote_inclusion": [1-10],
 "pop_culture_reference_frequency": [1-10],
 "technical_jargon_usage": [1-10],
 "parenthetical_aside_frequency": [1-10],
 "humor_sarcasm_usage": [1-10],
 "emotional_expressiveness": [1-10],
 "emphatic_device_usage": [1-10],
 "quotation_frequency": [1-10],
 "analogy_usage": [1-10],
 "sensory_detail_inclusion": [1-10],
 "onomatopoeia_usage": [1-10],
 "alliteration_frequency": [1-10],
 "word_length_preference": "[short/long/varied]",
 "foreign_phrase_usage": [1-10],
 "rhetorical_device_usage": [1-10],
 "statistical_data_usage": [1-10],
 "personal_opinion_inclusion": [1-10],
 "transition_usage": [1-10],
 "reader_question_frequency": [1-10],
 "imperative_sentence_usage": [1-10],
 "dialogue_inclusion": [1-10],
 "regional_dialect_usage": [1-10],
 "hedging_language_frequency": [1-10],
 "language_abstraction": "[concrete/abstract/mixed]",
 "personal_belief_inclusion": [1-10],
 "repetition_usage": [1-10],
 "subordinate_clause_frequency": [1-10],
 "verb_type_preference": "[active/stative/mixed]",
 "sensory_imagery_usage": [1-10],
 "symbolism_usage": [1-10],
 "digression_frequency": [1-10],
 "formality_level": [1-10],
 "reflection_inclusion": [1-10],
 "irony_usage": [1-10],
 "neologism_frequency": [1-10],
 "ellipsis_usage": [1-10],
 "cultural_reference_inclusion": [1-10],
 "stream_of_consciousness_usage": [1-10],
 "openness_to_experience": [1-10],
 "conscientiousness": [1-10],
 "extraversion": [1-10],
 "agreeableness": [1-10],
 "emotional_stability": [1-10],
 "dominant_motivations": "[achievement/affiliation/power/etc.]",
 "core_values": "[integrity/freedom/knowledge/etc.]",
 "decision_making_style": "[analytical/intuitive/spontaneous/etc.]",
 "empathy_level": [1-10],
 "self_confidence": [1-10],
 "risk_taking_tendency": [1-10],
 "idealism_vs_realism": "[idealistic/realistic/mixed]",
 "conflict_resolution_style": "[assertive/collaborative/avoidant/etc.]",
"relationship_orientation": "[independent/communal/mixed]",
"emotional_response_tendency": "[calm/reactive/intense]",
"creativity_level": [1-10],
"age": "[age or age range]",
 "gender": "[gender]",
 "education_level": "[highest level of education]",
 "professional_background": "[brief description]",
 "cultural_background": "[brief description]",
 "primary_language": "[language]",
 "language_fluency": "[native/fluent/intermediate/beginner]",
 "background": "[A brief paragraph describing the author's context, major influences, and any other relevant information not captured above]"


Writing Sample:
{writing_sample}
'''

    payload = {
        'model': 'llama3.2',  # Replace with your Ollama model name
        'prompt': encoding_prompt,
        'stream': False
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        json_str = re.search(r'\{.*?\}', response.text, re.DOTALL).group()
        analyzed_data = extract_json(response.text)
        if analyzed_data is None:
            logger.error("No JSON object found in the response.")
            return None
        return analyzed_data
    except (requests.RequestException, json.JSONDecodeError, AttributeError) as e:
        logger.error(f"Error during analyze_writing_sample: {str(e)}")
        return None

def generate_content(persona_data, prompt):
    decoding_prompt = f'''
You are to write a blog post in the style of {persona_data.get('name', 'Unknown Author')}, a writer with the following characteristics:

{json.dumps(persona_data, indent=2)}

Now, please write a response in this style about the following topic:
"{prompt}"
Begin with a compelling title that reflects the content of the post.
'''

    payload = {
        'model': 'llama3.2',  # Replace with your Ollama model name
        'prompt': decoding_prompt,
        'stream': False
    }
    headers = {'Content-Type': 'application/json'}

    try:
        logger.info(f"Sending request to OLLAMA API at {OLLAMA_API_URL} with payload: {payload}")
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
        logger.info(f"Received response from OLLAMA API: Status Code {response.status_code}")

        response.raise_for_status()

        response_json = response.json()
        response_content = response_json.get('response', '').strip()
        if not response_content:
            logger.error("OLLAMA API response 'response' field is empty.")
            return ''

        return response_content

    except requests.RequestException as e:
        logger.error(f"Error during generate_content: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Ollama Response Status: {e.response.status_code}")
            logger.error(f"Ollama Response Body: {e.response.text}")
        return ''

def save_blog_post(blog_post, title):
    # Implement if needed
    pass


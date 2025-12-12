import os
import json
import logging

MODEL = "gpt-4o"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_openai_client():
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
        return None

MEDICATIONS_DB = [
    {"medication": "Tretinoína 0,025% creme", "type": "topical", "instructions": "Aplicar uma fina camada à noite sobre a pele limpa e seca"},
    {"medication": "Tretinoína 0,05% creme", "type": "topical", "instructions": "Aplicar uma fina camada à noite sobre a pele limpa e seca"},
    {"medication": "Adapaleno 0,1% gel", "type": "topical", "instructions": "Aplicar uma fina camada à noite sobre a pele limpa e seca"},
    {"medication": "Cetoconazol 2% creme", "type": "topical", "instructions": "Aplicar na área afetada 1 vez ao dia por 2-4 semanas"},
    {"medication": "Dipropionato de Betametasona 0,05% pomada", "type": "topical", "instructions": "Aplicar uma fina camada 1-2 vezes ao dia nas áreas afetadas"},
    {"medication": "Clindamicina 1% solução tópica", "type": "topical", "instructions": "Aplicar 2 vezes ao dia nas áreas afetadas"},
    {"medication": "Metronidazol 0,75% gel", "type": "topical", "instructions": "Aplicar uma camada fina nas áreas afetadas 2 vezes ao dia"},
    {"medication": "Peróxido de Benzoíla 5% gel", "type": "topical", "instructions": "Aplicar uma fina camada nas áreas afetadas 1 vez ao dia"},
    {"medication": "Ácido Salicílico 2% loção", "type": "topical", "instructions": "Aplicar nas áreas afetadas 1-2 vezes ao dia"},
    {"medication": "Isotretinoína 20mg cápsulas", "type": "oral", "instructions": "Tomar 1 cápsula por dia com alimento por 15-20 semanas"},
    {"medication": "Isotretinoína 10mg cápsulas", "type": "oral", "instructions": "Tomar 1 cápsula por dia com alimento por 15-20 semanas"},
    {"medication": "Doxiciclina 100mg comprimidos", "type": "oral", "instructions": "Tomar 1 comprimido a cada 12 horas por 14 dias"},
    {"medication": "Fluconazol 150mg comprimidos", "type": "oral", "instructions": "Tomar 1 comprimido por semana por 2-4 semanas"},
    {"medication": "Minoxidil 5% solução capilar", "type": "topical", "instructions": "Aplicar 1mL na área afetada do couro cabeludo 2 vezes ao dia"},
    {"medication": "Tacrolimo 0,1% pomada", "type": "topical", "instructions": "Aplicar uma fina camada nas áreas afetadas 2 vezes ao dia"},
    {"medication": "Hidroquinona 4% creme", "type": "topical", "instructions": "Aplicar uma fina camada nas manchas 2 vezes ao dia"},
    {"medication": "Prednisolona 20mg comprimidos", "type": "oral", "instructions": "Tomar conforme prescrito, com redução gradual da dose"},
    {"medication": "Azitromicina 500mg comprimidos", "type": "oral", "instructions": "Tomar 1 comprimido por dia durante 3 dias"}
]

def suggest_medications(partial_input):
    logging.debug(f"Generating suggestions for: {partial_input}")
    
    try:
        client = get_openai_client()
        if client:
            try:
                prompt = f"""
                I am a dermatologist creating a prescription. Based on the partial input "{partial_input}", 
                suggest up to 5 potential dermatological medications or formulations.
                
                For each suggestion, classify it as either "topical" (creams, gels, ointments) or "oral" (pills, tablets, capsules).
                
                Return your response as a JSON object with a "suggestions" key containing an array:
                {{"suggestions": [
                    {{
                        "medication": "Full medication name with strength and form",
                        "type": "topical or oral",
                        "instructions": "Brief usage instructions"
                    }}
                ]}}
                
                Only include dermatological medications that are commonly prescribed.
                """
                
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                    max_tokens=500
                )
                
                content = response.choices[0].message.content
                logging.debug(f"OpenAI response: {content}")
                
                result = json.loads(content)
                
                if "suggestions" in result:
                    return result["suggestions"]
                elif isinstance(result, list):
                    return result
                else:
                    values = list(result.values())
                    return values[0] if values and isinstance(values[0], list) else []
                    
            except Exception as e:
                logging.error(f"Error in OpenAI API call: {str(e)}")
        
        logging.info("Using fallback medication database for suggestions")
        
        partial_lower = partial_input.lower()
        
        suggestions = [
            med for med in MEDICATIONS_DB 
            if partial_lower in med["medication"].lower()
        ]
        
        return suggestions[:5]
            
    except Exception as e:
        logging.error(f"Error while generating suggestions: {str(e)}")
        return [{"error": f"Failed to get suggestions: {str(e)}"}]

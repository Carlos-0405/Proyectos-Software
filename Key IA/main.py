import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
import re
import json
from datetime import datetime

class KeylaChatbot:
    def __init__(self):
        # Datos de entrenamiento expandidos y mejor estructurados
        self.data = {
            "saludos": {
                "Hola": ["¡Hola! Soy Keylx, ¿en qué puedo ayudarte?", "¡Hola! Es un gusto saludarte", "¡Hola! ¿Cómo estás?"],
                "Buenos días": ["¡Buenos días! ¿En qué puedo ayudarte?", "¡Buenos días! Espero que tengas un excelente día"],
                "Buenas tardes": ["¡Buenas tardes! ¿En qué puedo ayudarte?"],
                "Buenas noches": ["¡Buenas noches! ¿En qué puedo ayudarte?"]
            },
            "preguntas_personales": {
                "¿Cómo estás?": ["Estoy bien, gracias por preguntar. ¿Y tú?", "¡Muy bien! ¿Qué tal tú?"],
                "¿Cuál es tu nombre?": ["Me llamo Keylx, un gusto conocerte", "Soy Keylx, ¿en qué puedo ayudarte?"],
                "¿Qué puedes hacer?": ["Puedo ayudarte con preguntas generales, mantener una conversación y aprender de nuestras interacciones"]
            },
            "despedidas": {
                "Adiós": ["¡Hasta luego! Que tengas un excelente día", "¡Adiós! Espero volver a charlar pronto"],
                "Hasta luego": ["¡Hasta pronto! Fue un gusto charlar contigo", "¡Nos vemos! Cuídate mucho"],
                "Chao": ["¡Chao! Que tengas un excelente día"]
            }
        }
        
        self.context = {}
        self.setup_model()

    def preprocess_text(self, text):
        """Preprocesa el texto para normalizarlo"""
        text = text.lower()
        text = re.sub(r'[^\w\s¿?¡!áéíóúñ]', '', text)
        return text.strip()

    def setup_model(self):
        """Configura y entrena el modelo"""
        # Aplanamos los datos para el entrenamiento
        self.training_sentences = []
        self.training_labels = []
        
        for category in self.data.values():
            for question, answers in category.items():
                self.training_sentences.append(self.preprocess_text(question))
                # Usamos la primera respuesta como respuesta principal
                self.training_labels.append(answers[0])

        # Configuración del tokenizador
        self.tokenizer = keras.preprocessing.text.Tokenizer()
        self.tokenizer.fit_on_texts(self.training_sentences)
        
        # Preparación de secuencias
        sequences = self.tokenizer.texts_to_sequences(self.training_sentences)
        self.max_sequence_length = max(len(s) for s in sequences)
        X = keras.preprocessing.sequence.pad_sequences(sequences, maxlen=self.max_sequence_length)

        # Tokenizador para respuestas
        self.response_tokenizer = keras.preprocessing.text.Tokenizer()
        self.response_tokenizer.fit_on_texts(self.training_labels)
        response_sequences = self.response_tokenizer.texts_to_sequences(self.training_labels)
        y = keras.preprocessing.sequence.pad_sequences(response_sequences)

        # Modelo mejorado
        self.model = keras.Sequential([
            layers.Embedding(len(self.tokenizer.word_index) + 1, 16, input_length=self.max_sequence_length),
            layers.Bidirectional(layers.LSTM(32, return_sequences=True)),
            layers.Bidirectional(layers.LSTM(16)),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(len(self.response_tokenizer.word_index) + 1, activation='softmax')
        ])

        self.model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        # Entrenamiento con early stopping
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='loss',
            patience=10,
            restore_best_weights=True
        )

        self.model.fit(
            X, 
            np.argmax(y, axis=1),
            epochs=100,
            batch_size=32,
            callbacks=[early_stopping],
            verbose=0
        )

    def get_response(self, message, user_id):
        """Genera una respuesta para el mensaje del usuario"""
        # Preprocesar el mensaje
        processed_message = self.preprocess_text(message)

        # Buscar coincidencia exacta en el dataset
        for category in self.data.values():
            if processed_message in [self.preprocess_text(q) for q in category.keys()]:
                responses = category[list(category.keys())[list(map(lambda x: self.preprocess_text(x), category.keys())).index(processed_message)]]
                return np.random.choice(responses)

        # Si no hay coincidencia exacta, usar el modelo
        sequence = self.tokenizer.texts_to_sequences([processed_message])
        padded = keras.preprocessing.sequence.pad_sequences(sequence, maxlen=self.max_sequence_length)
        
        try:
            prediction = self.model.predict(padded, verbose=0)
            response_index = np.argmax(prediction)
            response = self.response_tokenizer.sequences_to_texts([[response_index]])[0]
            
            if not response or response.isspace():
                raise ValueError("Respuesta vacía generada")
                
            # Actualizar contexto
            self.context[user_id] = {
                'last_message': message,
                'timestamp': datetime.now(),
                'interaction_count': self.context.get(user_id, {}).get('interaction_count', 0) + 1
            }
            
            return response
            
        except Exception as e:
            print(f"Error al generar respuesta: {str(e)}")
            return "Lo siento, no entiendo bien esa pregunta. ¿Podrías reformularla?"

    def save_model(self, path):
        """Guarda el modelo y los tokenizadores"""
        self.model.save(f"{path}/keylx_model")
        
        # Guardar configuración de tokenizadores
        with open(f"{path}/tokenizer_config.json", 'w', encoding='utf-8') as f:
            json.dump({
                'tokenizer': self.tokenizer.to_json(),
                'response_tokenizer': self.response_tokenizer.to_json()
            }, f)

    def load_model(self, path):
        """Carga el modelo y los tokenizadores"""
        self.model = keras.models.load_model(f"{path}/keyla_model")
        
        with open(f"{path}/tokenizer_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.tokenizer = keras.preprocessing.text.tokenizer_from_json(config['tokenizer'])
            self.response_tokenizer = keras.preprocessing.text.tokenizer_from_json(config['response_tokenizer'])

# Ejemplo de uso
if __name__ == "__main__":
    chatbot = KeylaChatbot()
    print("¡Hola! Soy Keylx. Puedes hablarme. Escribe 'salir' para terminar.")
    
    user_id = "user_1"
    while True:
        try:
            user_input = input("Tú: ").strip()
            if user_input.lower() in ['salir', 'adiós', 'chao']:
                print("Keylx: ¡Hasta luego! Fue un gusto charlar contigo.")
                break
            
            if not user_input:
                print("Keylx: No he recibido ningún mensaje. ¿Podrías escribir algo?")
                continue
                
            response = chatbot.get_response(user_input, user_id)
            print(f"Keylx: {response}")
            
        except KeyboardInterrupt:
            print("\nKeylx: ¡Hasta luego! Fue un gusto charlar contigo.")
            break
        except Exception as e:
            print(f"Keylx: Lo siento, ha ocurrido un error. ¿Podrías intentarlo de nuevo?")
            print(f"Error: {str(e)}")
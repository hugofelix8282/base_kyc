import boto3
import os
from typing import Dict, Tuple
from dotenv import load_dotenv

load_dotenv()


class RekognitionClient:

    def __init__(self):
        self.client = boto3.client(
            "rekognition",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        self.threshold = float(os.getenv("SIMILARITY_THRESHOLD", "85.0"))

    def compare_faces(
        self, source_image_path: str, target_image_path: str
    ) -> Dict[str, any]:
        
        try:
            with open(source_image_path, "rb") as source_file:
                source_bytes = source_file.read()

            with open(target_image_path, "rb") as target_file:
                target_bytes = target_file.read()

            response = self.client.compare_faces(
                SourceImage={"Bytes": source_bytes},
                TargetImage={"Bytes": target_bytes},
                SimilarityThreshold=self.threshold,
            )

            if not response["FaceMatches"]:
                return {
                    "match": False,
                    "similarity": 0.0,
                    "confidence": 0.0,
                    "message": "Faces não correspondem - Pessoas diferentes detectadas",
                }

            face_match = response["FaceMatches"][0]
            similarity = face_match["Similarity"]

            return {
                "match": similarity >= self.threshold,
                "similarity": round(similarity, 2),
                "confidence": round(face_match["Face"]["Confidence"], 2),
                "message": self._get_message(similarity),
                "raw_response": response,
            }

        except self.client.exceptions.InvalidParameterException as e:
            return {"match": False, "error": f"Imagem inválida: {str(e)}"}
        except self.client.exceptions.ImageTooLargeException:
            return {"match": False, "error": "Imagem muito grande (max 5MB)"}
        except Exception as e:
            return {"match": False, "error": f"Erro inesperado: {str(e)}"}

    def _get_message(self, similarity: float) -> str:
        if similarity >= 95:
            return "Correspondência excelente"
        elif similarity >= 85:
            return "Correspondência alta"
        elif similarity >= 70:
            return "Correspondência moderada - requer análise manual"
        else:
            return "Correspondência baixa - rejeitado"

    def detect_faces(self, image_path: str) -> Dict[str, any]:
        try:
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()

            response = self.client.detect_faces(
                Image={"Bytes": image_bytes}, Attributes=["ALL"]
            )

            return {
                "faces_count": len(response["FaceDetails"]),
                "faces": response["FaceDetails"],
            }

        except Exception as e:
            return {"error": f"Erro ao detectar faces: {str(e)}"}

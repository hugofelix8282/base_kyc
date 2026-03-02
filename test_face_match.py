import argparse
import json
from pathlib import Path
from datetime import datetime
from rekognition_client import RekognitionClient
from pdf_utils import extract_image_from_pdf


def print_result(result: dict):
    print("\n" + "=" * 60)
    print(" RESULTADO DA COMPARAÇÃO FACIAL")
    print("=" * 60)

    if "error" in result:
        print(f" ERRO: {result['error']}")
        return

    match_icon = "v" if result["match"] else "x"
    print(f"\n{match_icon} Match: {result['match']}")
    print(f"Similaridade: {result['similarity']}%")
    print(f" Confiança: {result['confidence']}%")
    print(f" Mensagem: {result['message']}")
    print("\n" + "=" * 60)


def save_result(result: dict, output_dir: Path):
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"result_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"\n Resultado salvo em: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Teste de Face Match com AWS Rekognition"
    )
    parser.add_argument(
        "--selfie",
        type=str,
        default="samples/selfie.jpg",
        help="Caminho da selfie",
    )
    parser.add_argument(
        "--cnh", type=str, default="samples/cnh.pdf", help="Caminho da foto da CNH"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        default=True,
        help="Salvar resultado em arquivo JSON",
    )

    args = parser.parse_args()

    selfie_path = Path(args.selfie)
    cnh_path = Path(args.cnh)

    if not selfie_path.exists():
        print(f" Erro: Arquivo não encontrado: {selfie_path}")
        return

    if not cnh_path.exists():
        print(f" Erro: Arquivo não encontrado: {cnh_path}")
        return

    if cnh_path.suffix.lower() == ".pdf":
        print(" Detectado PDF - Extraindo imagem...")
        try:
            cnh_path = extract_image_from_pdf(str(cnh_path))
        except Exception as e:
            print(f" Erro ao extrair imagem do PDF: {e}")
            return

    print("Iniciando comparação facial...")
    print(f" Selfie: {selfie_path}")
    print(f" CNH: {cnh_path}")

    client = RekognitionClient()
    result = client.compare_faces(str(selfie_path), str(cnh_path))
    print_result(result)

    if args.save:
        save_result(result, Path("results"))


if __name__ == "__main__":
    main()

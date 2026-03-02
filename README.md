# KYC - Biometria Facial (AWS Rekognition)

POC para validação de identidade via comparação facial usando AWS Rekognition.

## 🎯 Objetivo

Testar e validar a integração com AWS Rekognition para comparação facial entre selfie e documento (CNH) antes de integrar ao projeto principal.

## 📋 Pré-requisitos

1. **Conta AWS**
2. **Credenciais AWS** (Access Key + Secret Key)
3. **Python 3.11+**

## 🚀 Setup

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Instalar poppler (necessário para PDF)
sudo apt-get install -y poppler-utils  # Linux
# brew install poppler  # macOS

# 4. Configurar credenciais AWS
cp .env.example .env
# Editar .env com suas credenciais
```

## 📁 Estrutura

```
kyc/
├── README.md              # Este arquivo
├── requirements.txt       # Dependências Python
├── .env.example          # Template de configuração
├── .env                  # Credenciais (não commitar)
├── rekognition_client.py # Cliente AWS Rekognition
├── pdf_utils.py          # Utilitário para extrair imagem de PDF
├── test_face_match.py    # Script de teste principal
├── check_faces.py        # Script para verificar detecção de faces
├── download_gdrive.py    # Script para baixar arquivos do Google Drive
├── samples/              # Imagens de teste
│   ├── selfie.jpg
│   └── cnh.pdf          # Suporta PDF e imagens
└── results/              # Resultados dos testes (JSON)
```

## 🧪 Testes

```bash
# Teste básico de comparação (resultados salvos automaticamente)
python test_face_match.py

# Teste com imagens customizadas
python test_face_match.py --selfie samples/selfie.jpg --cnh samples/cnh.jpg

# Suporte a PDF (extração automática) aplicar imagens salvas na pasta samples.
python test_face_match.py --selfie samples/selfie.jpg --cnh samples/cnh.pdf


## 📊 Métricas e Resultados

- **Similarity Score**: 0-100%
- **Threshold Recomendado**: 85% (alta confiança)
- **Tempo Médio**: ~500ms por comparação

### Interpretação dos Resultados

- **≥ 95%**: Correspondência excelente
- **85-94%**: Correspondência alta (aprovado)
- **70-84%**: Correspondência moderada (requer análise manual)
- **< 70%**: Correspondência baixa (rejeitado)
- **0%**: Pessoas diferentes detectadas

### Formato do Resultado

```json
{
  "match": true,
  "similarity": 92.5,
  "confidence": 99.8,
  "message": "Correspondência alta"
}
```


## 🔧 Troubleshooting

### Erro: "Unable to get page count"
```bash
sudo apt-get install -y poppler-utils
```

### Erro: "Cannot retrieve the public link" (Google Drive)
- Ajuste permissões para "Qualquer pessoa com o link"
- Ou baixe manualmente e coloque em `samples/`

## 🔄 Próximos Passos

Após validação bem-sucedida:
1. Integrar ao módulo `modules/verification/`
2. Criar `BiometryService` interface
3. Implementar `AWSRekognitionProvider`
4. Adicionar task Celery assíncrona
5. Criar endpoints de verificação

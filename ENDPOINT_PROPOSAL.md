# Proposta de Atualização - Endpoint de Cadastro de Instrutor

## Request Atual vs Request Proposto

### ❌ Request Atual (Sem Biometria)

```json
{
  "cpf": "123456789",
  "first_name": "tomnj",
  "last_name": "Andrade",
  "birth_date": "1998-05-03",
  "gender": "male",
  "email": "hugofelix560@gmail.com",
  "phone": "81995797560",
  "password": "SenhaSegura123!",
  "address": {
    "street": "rua osorio",
    "number": "320",
    "complement": "apt107",
    "neighborhood": "marlay",
    "city": "recife",
    "state": "PE",
    "zip_code": "54000000"
  },
  "licenses": [
    {
      "license_type": "A",
      "experience_years": 10,
      "usage_frequency": "daily",
      "hourly_rate": 10,
      "cnh_front_url": "https://...",
      "cnh_back_url": "https://...",
      "cnh_selfie_url": "https://..."
    }
  ],
  "specialties": ["muitas especialidades"],
  "vehicles": [
    {
      "brand": "Toyota",
      "model": "Corolla",
      "year": 2020,
      "license_category": "B",
      "transmission_type": "manual"
    }
  ],
  "avatar_url": "string",
  "google_id": "string"
}
```

---

## ✅ Request Proposto (Com Biometria)

### Opção 1: Manter Estrutura Atual + Adicionar Validação Biométrica

**Endpoint:** `POST /api/v1/instructors/register`

```json
{
  "cpf": "12345678900",
  "first_name": "Tom",
  "last_name": "Andrade",
  "birth_date": "1998-05-03",
  "gender": "male",
  "email": "hugofelix560@gmail.com",
  "phone": "81995797560",
  "password": "SenhaSegura123!",
  "address": {
    "street": "rua osorio",
    "number": "320",
    "complement": "apt107",
    "neighborhood": "marlay",
    "city": "recife",
    "state": "PE",
    "zip_code": "54000000"
  },
  "licenses": [
    {
      "license_type": "A",
      "experience_years": 10,
      "usage_frequency": "daily",
      "hourly_rate": 10,
      
      // ✨ NOVO: Documentos para validação biométrica
      "cnh_front": "base64_string_or_file",  // Frente da CNH (PDF ou imagem)
      "cnh_back": "base64_string_or_file",   // Verso da CNH (PDF ou imagem)
      "cnh_selfie": "base64_string_or_file"  // Selfie do instrutor
    }
  ],
  "specialties": ["muitas especialidades"],
  "vehicles": [
    {
      "brand": "Toyota",
      "model": "Corolla",
      "year": 2020,
      "license_category": "B",
      "transmission_type": "manual"
    }
  ],
  
  // ✨ NOVO: Documentos adicionais (OBRIGATÓRIO)
  "additional_documents": [
    {
      "type": "certification",
      "description": "Certificado de Instrutor DETRAN",
      "file": "base64_string_or_file"
    },
    {
      "type": "diploma",
      "description": "Diploma de Ensino Superior",
      "file": "base64_string_or_file"
    }
  ],
  
  "avatar_url": "string",
  "google_id": "string"
}
```

**Response:**
```json
{
  "instructor_id": "uuid",
  "status": "pending_verification",
  "message": "Cadastro criado com sucesso. Aguardando validação de documentos.",
  "verification": {
    "submission_id": "uuid",
    "status": "pending_admin_review",
    "estimated_review_time": "24-48h"
  },
  "access": {
    "can_login": true,
    "can_create_classes": false,
    "can_start_classes": false,
    "restrictions": [
      "Aguardando aprovação de documentos",
      "Aguardando validação biométrica"
    ]
  }
}
```

---

### Opção 2: Separar Cadastro Básico + Upload de Documentos (Recomendado)

#### Passo 1: Cadastro Básico
**Endpoint:** `POST /api/v1/instructors/register`

```json
{
  "cpf": "12345678900",
  "first_name": "Tom",
  "last_name": "Andrade",
  "birth_date": "1998-05-03",
  "gender": "male",
  "email": "hugofelix560@gmail.com",
  "phone": "81995797560",
  "password": "SenhaSegura123!",
  "address": {
    "street": "rua osorio",
    "number": "320",
    "complement": "apt107",
    "neighborhood": "marlay",
    "city": "recife",
    "state": "PE",
    "zip_code": "54000000"
  },
  "licenses": [
    {
      "license_type": "A",
      "experience_years": 10,
      "usage_frequency": "daily",
      "hourly_rate": 10
    }
  ],
  "specialties": ["muitas especialidades"],
  "vehicles": [
    {
      "brand": "Toyota",
      "model": "Corolla",
      "year": 2020,
      "license_category": "B",
      "transmission_type": "manual"
    }
  ],
  "avatar_url": "string",
  "google_id": "string"
}
```

**Response:**
```json
{
  "instructor_id": "uuid",
  "status": "pending_documents",
  "message": "Cadastro criado. Por favor, envie seus documentos para validação.",
  "next_step": {
    "action": "upload_documents",
    "endpoint": "/api/v1/instructors/{instructor_id}/documents",
    "required_documents": [
      "selfie",
      "cnh",  // Aceita PDF único OU frente+verso separados
      "additional_documents"  // Certificações obrigatórias
    ],
    "accepted_formats": {
      "selfie": ["jpg", "jpeg", "png"],
      "cnh": ["pdf", "jpg", "jpeg", "png"]
    },
    "upload_options": {
      "option_1": "Enviar campo 'cnh' com PDF único contendo frente e verso",
      "option_2": "Enviar campos 'cnh_front' e 'cnh_back' com imagens separadas"
    }
  }
}
```

#### Passo 2: Upload de Documentos
**Endpoint:** `POST /api/v1/instructors/{instructor_id}/documents`

**Opção A: CNH em PDF único (frente e verso)**
```json
{
  "selfie": "base64_string_or_file",
  "cnh": "base64_string_or_file",  // PDF com frente e verso
  "additional_documents": [  // OBRIGATÓRIO
    {
      "type": "certification",
      "description": "Certificado de Instrutor DETRAN",
      "file": "base64_string_or_file"
    }
  ]
}
```

**Opção B: CNH em imagens separadas (frente e verso)**
```json
{
  "selfie": "base64_string_or_file",
  "cnh_front": "base64_string_or_file",  // Frente da CNH
  "cnh_back": "base64_string_or_file",   // Verso da CNH
  "additional_documents": [  // OBRIGATÓRIO
    {
      "type": "certification",
      "description": "Certificado de Instrutor DETRAN",
      "file": "base64_string_or_file"
    }
  ]
}
```

**Response:**
```json
{
  "submission_id": "uuid",
  "status": "pending_admin_review",
  "message": "Documentos enviados com sucesso. Aguardando análise.",
  "estimated_review_time": "24-48h",
  "documents_received": [
    {
      "type": "selfie",
      "status": "received",
      "url": "https://storage.../selfie.jpg"
    },
    {
      "type": "cnh",
      "status": "received",
      "format": "pdf",  // ou "images"
      "files": [
        {
          "side": "front",
          "url": "https://storage.../cnh_front.jpg"
        },
        {
          "side": "back",
          "url": "https://storage.../cnh_back.jpg"
        }
      ]
    }
  ]
}
```

---

## 🔄 Fluxo Completo Proposto

### Opção 1 (Tudo de uma vez):
```
1. POST /api/v1/instructors/register (com todos os dados + documentos)
   ↓
2. Sistema cria instrutor + armazena documentos
   ↓
3. Status: pending_admin_review
   ↓
4. Admin aprova documentos
   ↓
5. Sistema executa validação biométrica automática
   ↓
6. Status: active (se aprovado) ou rejected (se rejeitado)
```

### Opção 2 (Separado - Recomendado):
```
1. POST /api/v1/instructors/register (dados básicos)
   ↓
2. Sistema cria instrutor
   ↓
3. Status: pending_documents
   ↓
4. POST /api/v1/instructors/{id}/documents (upload de documentos)
   ↓
5. Status: pending_admin_review
   ↓
6. Admin aprova documentos
   ↓
7. Sistema executa validação biométrica automática
   ↓
8. Status: active (se aprovado) ou rejected (se rejeitado)
```

---

## 📋 Mudanças Necessárias no Backend

### 1. Atualizar Model `Instructor`

```python
class Instructor(Base):
    # ... campos existentes ...
    
    # Novos campos
    biometry_verified = Column(Boolean, default=False)
    biometry_status = Column(
        Enum('pending', 'approved', 'rejected', 'manual_review'),
        default='pending'
    )
    submission_id = Column(UUID, ForeignKey('instructor_submissions.id'))
    verification_status = Column(
        Enum('pending_documents', 'pending_admin_review', 
             'documents_approved', 'biometry_processing', 
             'active', 'rejected'),
        default='pending_documents'
    )
```

### 2. Atualizar Endpoint de Cadastro

```python
@router.post("/instructors/{instructor_id}/documents")
async def upload_documents(instructor_id: UUID, files: DocumentsUpload):
    # Detectar formato de envio
    if files.cnh:  # PDF único
        cnh_files = process_pdf_cnh(files.cnh)
    elif files.cnh_front and files.cnh_back:  # Imagens separadas
        cnh_files = {
            "front": files.cnh_front,
            "back": files.cnh_back
        }
    else:
        raise ValidationError("CNH deve ser enviada como PDF ou frente+verso")
    
    # Armazenar documentos
    submission = create_submission(
        instructor_id=instructor_id,
        selfie=files.selfie,
        cnh_files=cnh_files
    )
    
    # Notificar admin
    notify_admin_new_submission(submission.id)
    
    return {
        "submission_id": submission.id,
        "status": "pending_admin_review"
    }
```

### 3. Criar Novos Endpoints

```python
# Upload de documentos (se separado)
@router.post("/instructors/{instructor_id}/documents")
async def upload_documents(instructor_id: UUID, files: DocumentsUpload):
    # Armazenar documentos
    # Criar submission
    # Notificar admin
    pass

# Status da verificação
@router.get("/instructors/{instructor_id}/verification-status")
async def get_verification_status(instructor_id: UUID):
    # Retornar status completo da verificação
    pass
```

---

## 🎯 Recomendação

**Opção 2 (Separado)** é a melhor escolha porque:

✅ **Melhor UX**: Usuário não precisa ter todos os documentos prontos no momento do cadastro  
✅ **Mais flexível**: Permite retry de upload de documentos sem reenviar tudo  
✅ **Menor payload**: Requisição inicial mais leve  
✅ **Melhor tratamento de erros**: Falha no upload não impede cadastro básico  
✅ **Progressive disclosure**: Mostra informações gradualmente  

---

## 📝 Validações Necessárias

### No Frontend:
- Validar formato de arquivo (JPG, PNG, PDF)
- Validar tamanho máximo (5MB por arquivo)
- Validar qualidade da selfie (iluminação, foco)
- Preview antes do envio
- **CNH**: Permitir escolha entre PDF único ou frente+verso separados
- Validar que ao menos uma opção de CNH foi enviada

### No Backend:
- Validar formato e tamanho
- Validar se selfie contém face detectável
- **CNH PDF**: Validar se tem pelo menos 1 página
- **CNH PDF**: Extrair foto automaticamente da primeira página
- **CNH Imagens**: Validar que ambas (frente e verso) foram enviadas
- **CNH Imagens**: Extrair foto da frente
- Validar que apenas uma opção foi enviada (PDF OU imagens, não ambos)
- Validar se CNH é legível
- Sanitizar arquivos (antivírus)
- Armazenar com criptografia

### Lógica de Validação:
```python
def validate_cnh_upload(cnh, cnh_front, cnh_back):
    if cnh and (cnh_front or cnh_back):
        raise ValidationError("Envie CNH como PDF OU frente+verso, não ambos")
    
    if not cnh and not (cnh_front and cnh_back):
        raise ValidationError("CNH obrigatória: envie PDF ou frente+verso")
    
    if cnh_front and not cnh_back:
        raise ValidationError("Envie frente E verso da CNH")
    
    if cnh_back and not cnh_front:
        raise ValidationError("Envie frente E verso da CNH")
    
    return True

def validate_additional_documents(additional_documents):
    if not additional_documents or len(additional_documents) == 0:
        raise ValidationError("Documentos adicionais obrigatórios (certificações, diplomas)")
    
    # Validar que pelo menos uma certificação foi enviada
    has_certification = any(
        doc['type'] == 'certification' 
        for doc in additional_documents
    )
    
    if not has_certification:
        raise ValidationError("Pelo menos uma certificação de instrutor é obrigatória")
    
    return True
```

---

## 🔐 Segurança

- Armazenar documentos em S3 com criptografia
- URLs assinadas com expiração (24h)
- Acesso restrito (apenas admin e próprio instrutor)
- Logs de acesso aos documentos
- Retenção de 5 anos para auditoria
- LGPD compliance (direito ao esquecimento)

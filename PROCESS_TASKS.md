# TASKS JIRA - Sistema de Biometria Facial

---

## EPIC: Implementação de Biometria Facial para Validação de Identidade

**Descrição:** Implementar sistema completo de validação biométrica para instrutores e alunos, incluindo cadastro inicial e validação no início de aulas.

---

## TASK 1: [BACKEND] Criar Serviço Base de Biometria Facial

**Tipo:** Task  
**Prioridade:** Alta  
**Story Points:** 8

### Descrição
Criar infraestrutura base para integração com provedores de biometria facial (AWS Rekognition, Unico, CAF, Truora, Serpro), permitindo comparação entre selfie e documento de identidade.

### Contexto de Negócio
Sistema precisa validar identidade de instrutores e alunos através de biometria facial para garantir autenticidade e segurança na plataforma.

### Objetivos
- Criar interface abstrata para provedores de biometria
- Implementar provider AWS Rekognition (POC validada)
- Configurar armazenamento de evidências
- Implementar sistema de retry e timeout

### Implementação Técnica

**Componentes a Desenvolver:**

1. **BiometryService** (Interface)
```python
- compare_faces(selfie_url, document_url) -> BiometryResult
- detect_face(image_url) -> FaceDetectionResult
- get_similarity_score() -> float
```

2. **AWSRekognitionProvider** (Implementação)
```python
- Integração com AWS Rekognition
- Suporte a PDF (extração automática)
- Tratamento de erros específicos
- Logs detalhados
```

3. **BiometryRepository**
```python
- save_verification_result()
- get_verification_history()
- update_verification_status()
```

4. **Configurações**
```python
- BIOMETRY_PROVIDER = "aws_rekognition"
- SIMILARITY_THRESHOLD = 85.0
- BIOMETRY_TIMEOUT = 30
- BIOMETRY_MAX_RETRIES = 3
```

### Estrutura de Dados

**Tabela: `biometry_verifications`**
```sql
- id (uuid, PK)
- user_id (uuid, FK)
- user_type (enum: 'instructor', 'student')
- verification_type (enum: 'registration', 'class_start')
- selfie_url (string)
- document_url (string)
- document_type (enum: 'cnh', 'rg', 'cnh_digital')
- biometry_score (float)
- biometry_provider (string)
- biometry_result (jsonb)
- status (enum: 'approved', 'rejected', 'manual_review')
- verified_at (timestamp)
- created_at (timestamp)
- updated_at (timestamp)
```

### Regras de Negócio
- Score >= 85%: Aprovação automática
- Score 70-84%: Análise manual obrigatória
- Score < 70%: Rejeição automática
- Timeout de 30s na chamada ao provedor
- Retry automático (3 tentativas) em caso de falha
- Logs completos para auditoria

### Critérios de Aceite
- [ ] Interface BiometryService criada e documentada
- [ ] AWSRekognitionProvider implementado e testado
- [ ] Suporte a PDF e imagens (JPG, PNG)
- [ ] Sistema de retry funcionando
- [ ] Timeout configurado e testado
- [ ] Tabela biometry_verifications criada
- [ ] Logs de auditoria implementados
- [ ] Testes unitários com cobertura >= 80%

### Dependências
- POC AWS Rekognition (concluída)
- Credenciais AWS configuradas

### Documentação Técnica
- Repositório POC: https://github.com/hugofelix8282/base_kyc
- AWS Rekognition Docs: https://docs.aws.amazon.com/rekognition/

---

## TASK 2: [BACKEND] Implementar Validação Biométrica no Cadastro de Instrutor (Fluxo Manual)

**Tipo:** Task  
**Prioridade:** Alta  
**Story Points:** 8

### Descrição
Implementar fluxo de validação biométrica para cadastro de instrutores com aprovação manual de documentos pelo admin, seguido de validação biométrica automática.

### Contexto de Negócio
Atualmente não existe API para validar a veracidade de documentos de credenciamento de instrutores. Por isso, o processo será híbrido:
1. **Admin valida manualmente** se o documento é válido (CNH, certificações, etc)
2. **Sistema valida automaticamente via biometria** se a selfie corresponde à foto do documento

Isso garante que a pessoa é realmente quem diz ser, mesmo sem API de validação de credenciais.

### Objetivos
- Criar fluxo de upload de selfie + documentos pelo instrutor
- Processar validação biométrica após aprovação manual
- Notificar instrutor sobre status da validação
- Bloquear acesso até aprovação completa

### Implementação Técnica

**Endpoints:**

1. **POST /api/v1/instructors/registration/documents**
```json
Request:
{
  "instructor_id": "uuid",
  "selfie": "base64|file",
  
  // Opção A: CNH em PDF único
  "cnh": "base64|file",
  
  // Opção B: CNH em imagens separadas
  "cnh_front": "base64|file",
  "cnh_back": "base64|file",
  
  // OBRIGATÓRIO:
  "additional_documents": [
    {
      "type": "certification",
      "file": "base64|file",
      "description": "Certificado de Instrutor DETRAN"
    }
  ]
}

Response:
{
  "submission_id": "uuid",
  "status": "pending_admin_review",
  "message": "Documentos enviados para análise",
  "estimated_review_time": "24-48h"
}
```

2. **GET /api/v1/instructors/registration/status/{instructor_id}**
```json
Response:
{
  "instructor_id": "uuid",
  "submission_id": "uuid",
  "status": "pending_admin_review|documents_approved|biometry_processing|approved|rejected",
  "admin_review": {
    "reviewed": true,
    "approved": true,
    "reviewed_by": "admin_name",
    "reviewed_at": "2024-03-02T10:30:00Z",
    "comments": "Documentos válidos"
  },
  "biometry_verification": {
    "verified": true,
    "similarity_score": 92.5,
    "verified_at": "2024-03-02T10:35:00Z",
    "message": "Correspondência alta"
  }
}
```

**Endpoints Admin:**

3. **GET /api/v1/admin/instructors/pending-review**
```json
Response:
{
  "total": 15,
  "items": [
    {
      "submission_id": "uuid",
      "instructor_id": "uuid",
      "instructor_name": "João Silva",
      "selfie_url": "url",
      "documents": [
        {
          "type": "cnh",
          "url": "url",
          "description": "CNH Categoria B"
        }
      ],
      "submitted_at": "2024-03-02T09:00:00Z"
    }
  ]
}
```

4. **POST /api/v1/admin/instructors/{submission_id}/review**
```json
Request:
{
  "decision": "approved|rejected",
  "comments": "Documentos válidos e em conformidade",
  "reviewed_by": "admin_user_id",
  "documents_validation": [
    {
      "document_type": "cnh",
      "valid": true,
      "notes": "CNH válida até 2028"
    }
  ]
}

Response:
{
  "submission_id": "uuid",
  "status": "documents_approved",
  "biometry_verification_triggered": true,
  "message": "Documentos aprovados. Validação biométrica iniciada."
}
```

**Task Celery:**
```python
@celery.task(bind=True, max_retries=3)
def verify_instructor_biometry_after_approval(self, submission_id):
    """
    Executado automaticamente após admin aprovar documentos
    - Busca selfie e foto do documento (CNH/RG)
    - Chama BiometryService para comparação
    - Atualiza status do instrutor
    - Envia notificação
    """
    submission = get_submission(submission_id)
    
    # Extrai foto do documento (CNH/RG)
    document_photo = extract_photo_from_document(
        submission.documents[0].url
    )
    
    # Compara com selfie
    result = BiometryService.compare_faces(
        submission.selfie_url,
        document_photo
    )
    
    # Atualiza status
    if result.similarity >= 85:
        approve_instructor(submission.instructor_id)
        notify_instructor("approved")
    elif result.similarity >= 70:
        flag_for_manual_biometry_review(submission_id)
        notify_admin("biometry_manual_review")
    else:
        reject_instructor(submission.instructor_id)
        notify_instructor("rejected_biometry")
```

### Fluxo Completo de Cadastro do Instrutor

**Fase 1: Envio de Documentos (Instrutor)**
1. Instrutor preenche dados pessoais
2. Instrutor tira selfie
3. Instrutor faz upload de documentos:
   - **CNH (obrigatório)**: PDF único OU frente+verso separados
   - **Certificações (OBRIGATÓRIO)**:  certificação de credencial instrutor 
4. Sistema armazena e cria `instructor_submission`
5. Status: `pending_admin_review`
6. Notificação enviada ao admin

**Fase 2: Validação Manual (Admin)**
7. Admin acessa dashboard de pendências
8. Admin visualiza:
   - Selfie do instrutor
   - Documentos enviados
   - Dados cadastrais
9. Admin valida manualmente:
   - ✅ Documento é autêntico?
   - ✅ Documento está válido (não vencido)?
   - ✅ Certificações são válidas?
   - ✅ Dados conferem?
10. Admin aprova ou rejeita com justificativa
11. Se rejeitado: Instrutor notificado + processo encerrado
12. Se aprovado: Trigger automático da validação biométrica

**Fase 3: Validação Biométrica Automática (Sistema)**
13. Task Celery executada automaticamente
14. Sistema extrai foto do documento (CNH/RG)
15. Sistema compara selfie com foto do documento
16. Resultado:
    - **Score ≥ 85%**: Aprovação automática
      - `instructor.is_status = 'active'`
      - `instructor.biometry_verified = True`
      - Notificação: "Cadastro aprovado!"
    - **Score 70-84%**: Análise manual biométrica
      - Admin revisa comparação lado a lado
      - Admin decide aprovação final
    - **Score < 70%**: Rejeição automática
      - `instructor.status = 'rejected'`
      - Notificação: "Selfie não corresponde ao documento"

### Estrutura de Dados

**Tabela: `instructor_submissions`**
```sql
- id (uuid, PK)
- instructor_id (uuid, FK)
- selfie_url (string)
- status (enum: 'pending_admin_review', 'documents_approved', 'documents_rejected', 'biometry_processing', 'biometry_approved', 'biometry_rejected', 'approved', 'rejected')
- submitted_at (timestamp)
- created_at (timestamp)
- updated_at (timestamp)
```

**Tabela: `instructor_documents`**
```sql
- id (uuid, PK)
- submission_id (uuid, FK)
- document_type (enum: 'cnh', 'certification')
- document_url (string)
- description (string)
- admin_validated (boolean)
- admin_notes (text)
- created_at (timestamp)
```

**Tabela: `admin_reviews`**
```sql
- id (uuid, PK)
- submission_id (uuid, FK)
- reviewed_by (uuid, FK -> users)
- decision (enum: 'approved', 'rejected')
- comments (text)
- documents_validation (jsonb)
- reviewed_at (timestamp)
- created_at (timestamp)
```

### Regras de Negócio

**Upload de Documentos:**
- Selfie obrigatória
- **CNH obrigatória**: PDF único OU frente+verso separados
- **Certificações obrigatórias**:  certificação de instrutor
- Diplomas opcionais
- Tamanho máximo: 5MB por arquivo
- Formatos aceitos: JPG, PNG, PDF
- Máximo 3 documentos por submissão

**Validações de CNH:**
- Aceitar PDF único (frente e verso juntos)
- OU aceitar frente+verso em imagens separadas
- Não aceitar ambos formatos simultaneamente
- Se imagens separadas: ambas (frente E verso) obrigatórias

**Validação Manual (Admin):**
- SLA: 24-48h para análise
- Justificativa obrigatória para rejeição
- Histórico de revisões armazenado

**Validação Biométrica:**
- Executada automaticamente após aprovação admin
- Score ≥ 85%: Aprovação automática
- Score 70-84%: Análise manual biométrica
- Score < 70%: Rejeição automática
- Retry automático (3 tentativas) em caso de falha

**Bloqueios:**
- Instrutor bloqueado até aprovação completa
- Não pode criar aulas
- Pode acessar sistema, porém com acesso limitado.
- Pode visualizar status da submissão

**Notificações:**
- Instrutor: Ao enviar documentos
- Admin: Quando nova submissão chega
- Instrutor: Quando admin aprova/rejeita documentos
- Instrutor: Quando biometria aprova/rejeita
- Admin: Quando biometria precisa de análise manual

### Critérios de Aceite
- [ ] Endpoint de upload de documentos funcionando
- [ ] Endpoint de status funcionando
- [ ] Dashboard admin de pendências funcionando
- [ ] Endpoint de revisão admin funcionando
- [ ] Task Celery de validação biométrica funcionando
- [ ] Trigger automático após aprovação admin
- [ ] Suporte a CNH em PDF único
- [ ] Suporte a CNH em frente+verso separados
- [ ] Validação de formato de CNH (PDF OU imagens, não ambos)
- [ ] Validação de certificações obrigatórias
- [ ] Extração de foto do documento funcionando (PDF e imagens)
- [ ] Comparação biométrica funcionando
- [ ] Tabelas criadas e relacionadas corretamente
- [ ] Notificações enviadas em cada etapa
- [ ] Bloqueio de acesso até aprovação
- [ ] Logs de auditoria completos
- [ ] Testes de integração end-to-end
- [ ] Teste: admin aprova + biometria aprova
- [ ] Teste: admin aprova + biometria rejeita
- [ ] Teste: admin rejeita (sem biometria)
- [ ] Teste: upload CNH em PDF
- [ ] Teste: upload CNH em imagens separadas
- [ ] Teste: rejeição por falta de certificações

### Dependências
- TASK 1 concluída
- Sistema de storage configurado (S3/MinIO)
- Sistema de notificações funcionando
- Dashboard admin existente

---

## TASK 2B: [BACKEND] Implementar Validação Biométrica no Início de Aula (Selfie em Tempo Real)

**Tipo:** Task  
**Prioridade:** Alta  
**Story Points:** 3

### Descrição
Implementar validação biométrica rápida comparando selfie em tempo real com documento já armazenado no cadastro.

### Contexto de Negócio
Instrutor e aluno já têm documentos validados no cadastro (TASK 2). No início da **aula prática de direção** (1 instrutor + 1 aluno), ambos precisam tirar selfie em tempo real para confirmar identidade antes de iniciar.

### Objetivos
- Capturar selfie em tempo real via frontend
- Comparar com foto do documento já armazenado
- Validação rápida (< 5s)
- Marcar presença automaticamente

### Implementação Técnica

**Endpoint:**

**POST /api/v1/biometry/verify-realtime**
```json
Request:
{
  "user_id": "uuid",
  "user_type": "instructor|student",
  "selfie": "base64",  // Selfie capturada em tempo real
  "context": "class_start",
  "class_id": "uuid"  // Opcional: para marcar presença
}

Response:
{
  "verification_id": "uuid",
  "status": "approved|rejected",
  "similarity_score": 94.2,
  "verified": true,
  "message": "Identidade confirmada",
  "processing_time": "2.3s"
}
```

**Arquitetura Híbrida: Celery + Redis Pub/Sub + WebSocket**

```python
# 1. Task Celery para processamento pesado
@celery.task(bind=True, max_retries=2, time_limit=10)
def verify_realtime_biometry(self, verification_id, user_id, selfie_url, class_id=None):
    """
    Processamento pesado (AWS Rekognition)
    - Busca documento já armazenado
    - Comparação facial
    - Retry automático
    - Persistência garantida
    """
    user_document = get_user_document(user_id)
    
    if not user_document:
        return {"error": "Documento não encontrado"}
    
    # Comparação biométrica (pesada)
    result = BiometryService.compare_faces(
        selfie_url,
        user_document.photo_extracted_url
    )
    
    # Atualizar verificação no banco
    update_verification(verification_id, result)
    
    # Publicar evento no Redis Pub/Sub (leve e instantâneo)
    if class_id and result.verified:
        publish_verification_event(
            class_id=class_id,
            user_id=user_id,
            user_type=get_user_type(user_id),
            verified=True,
            similarity_score=result.similarity
        )
    
    return result


# 2. Redis Pub/Sub para eventos em tempo real
def publish_verification_event(class_id, user_id, user_type, verified, similarity_score):
    """
    Publica evento de verificação no Redis
    - Instantâneo (< 10ms)
    - Notifica todos os listeners
    """
    redis_client.publish(
        f'class:{class_id}:verifications',
        json.dumps({
            'event': 'verification_complete',
            'user_id': user_id,
            'user_type': user_type,
            'verified': verified,
            'similarity_score': similarity_score,
            'timestamp': datetime.now().isoformat()
        })
    )


# 3. Task Celery para verificar requisitos
@celery.task(bind=True)
def check_class_start_requirements(self, class_id):
    """
    Verifica requisitos para aula prática (1 instrutor + 1 aluno)
    - Instrutor validado?
    - Aluno validado?
    - Se AMBOS: Habilita início da aula
    """
    instructor_verified = check_instructor_verification(class_id)
    student_verified = check_student_verification(class_id)
    
    # Aula prática: AMBOS devem estar validados
    can_start = instructor_verified and student_verified
    
    # Atualizar banco
    update_class_session(
        class_id=class_id,
        can_start=can_start,
        instructor_verified=instructor_verified,
        student_verified=student_verified
    )
    
    # Publicar evento no Redis
    redis_client.publish(
        f'class:{class_id}:status',
        json.dumps({
            'event': 'class_status_update',
            'can_start': can_start,
            'instructor_verified': instructor_verified,
            'student_verified': student_verified,
            'timestamp': datetime.now().isoformat()
        })
    )
    
    return {
        "class_id": class_id,
        "can_start": can_start,
        "instructor_verified": instructor_verified,
        "student_verified": student_verified
    }


# 4. SSE (Server-Sent Events) para frontend
@app.get("/api/v1/classes/{class_id}/events")
async def class_events_stream(class_id: str):
    """
    Stream de eventos via SSE (mais simples que WebSocket)
    - Ideal para 1 instrutor + 1 aluno
    - Reconexão automática
    - HTTP padrão
    """
    async def event_generator():
        # Subscribe no Redis Pub/Sub
        pubsub = redis_client.pubsub()
        pubsub.subscribe(
            f'class:{class_id}:verifications',
            f'class:{class_id}:status'
        )
        
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    
                    # Enviar evento para frontend
                    yield {
                        "event": data['event'],
                        "data": json.dumps(data)
                    }
                    
                    # Se aula pode iniciar, enviar evento especial
                    if data.get('event') == 'class_status_update':
                        if data.get('can_start'):
                            yield {
                                "event": "class_ready",
                                "data": json.dumps({
                                    "message": "Aula prática liberada para início! "
                                })
                            }
        finally:
            pubsub.unsubscribe()
    
    return EventSourceResponse(event_generator())


# Frontend: JavaScript nativo (sem bibliotecas)
const eventSource = new EventSource(`/api/v1/classes/${classId}/events`);

// Escutar verificações
eventSource.addEventListener('verification_complete', (e) => {
    const data = JSON.parse(e.data);
    updateUI({
        userId: data.user_id,
        userType: data.user_type,
        verified: data.verified,
        score: data.similarity_score
    });
});

// Escutar quando aula pode iniciar
eventSource.addEventListener('class_ready', (e) => {
    const data = JSON.parse(e.data);
    showNotification(data.message);
    enableStartButton();
});

// Reconexão automática (nativa do SSE)
eventSource.onerror = (error) => {
    console.log('Reconectando...');
    // SSE reconecta automaticamente
};
```

### Fluxo de Validação em Tempo Real (Arquitetura Híbrida: Celery + Redis + SSE)

```
1. Frontend captura selfie
   ↓
2. POST /api/v1/biometry/verify-realtime
   ↓
3. Celery Task: verify_realtime_biometry
   - Comparação facial (AWS Rekognition) [PESADO]
   - Retry automático
   - Persistência no banco
   ↓
4. Redis Pub/Sub: publish_verification_event
   - Publica evento [LEVE - < 10ms]
   - Canal: class:{class_id}:verifications
   ↓
5. SSE Stream: /api/v1/classes/{class_id}/events
   - Escuta eventos do Redis
   - Envia para frontend [INSTANTÂNEO]
   - Reconexão automática
   ↓
6. Frontend atualiza UI em tempo real
   - "Instrutor João Silva validado ✅"
   - "Aguardando aluno..."
   ↓
7. Celery Task: check_class_start_requirements
   - Verifica: Instrutor ✅ + Aluno ✅
   - Publica resultado no Redis
   ↓
8. SSE envia notificação
   - "Aula prática liberada para início! "
   - Botão "Iniciar Aula" habilitado
```

### Estrutura de Dados

**Reutiliza tabela existente:**
```sql
-- biometry_verifications (já criada na TASK 1)
- verification_type = 'class_start'  // Diferencia do cadastro
- selfie_url (nova selfie em tempo real)
- document_url (referência ao documento do cadastro)
```

**Cache de fotos extraídas:**
```sql
-- user_documents (já criada na TASK 2)
- photo_extracted_url (string)  // Foto já extraída e em cache
- photo_extracted_at (timestamp)
```

### Regras de Negócio

**Aula Prática de Direção:**
- ⚠️ **1 Instrutor + 1 Aluno** (aula individual)
- **AMBOS** devem estar validados para iniciar
- Validação obrigatória a cada aula

**Validação em Tempo Real:**
- Selfie obrigatória em tempo real
- Documento já deve estar no cadastro
- Score mínimo: 80% (mais flexível que cadastro)
- Timeout: 10s (mais rápido)
- Retry: 2 tentativas
- Cache de foto do documento (evita reprocessamento)

**Performance:**
- Foto do documento já extraída no cadastro
- Cache em Redis/Memcached
- Resposta em < 5s
- Processamento assíncrono

**Segurança:**
- Selfie em tempo real (não pode ser foto antiga)
- Validação de timestamp (máx 30s de diferença)
- Detecção de liveness (opcional)

### Critérios de Aceite
- [ ] Endpoint de verificação em tempo real funcionando
- [ ] Busca documento do cadastro automaticamente
- [ ] Comparação com foto em cache
- [ ] Resposta em < 5s
- [ ] Cache de fotos extraídas implementado
- [ ] Validação de timestamp da selfie
- [ ] Retry automático (2 tentativas)
- [ ] ⚠️ **Celery Task para processamento pesado**
- [ ] ⚠️ **Redis Pub/Sub para eventos em tempo real**
- [ ] ⚠️ **SSE (Server-Sent Events) para atualização instantânea do frontend**
- [ ] ⚠️ **Task `check_class_start_requirements` funcionando**
- [ ] ⚠️ **Verificação de 1 instrutor + 1 aluno validados**
- [ ] ⚠️ **Habilita início apenas se AMBOS validados**
- [ ] Notificação em tempo real quando aula pode iniciar
- [ ] Notificação quando aguardando validações
- [ ] Reconexão automática do SSE
- [ ] Logs de auditoria
- [ ] Testes de performance (< 5s)
- [ ] Teste: instrutor validado, aluno não (bloqueado)
- [ ] Teste: aluno validado, instrutor não (bloqueado)
- [ ] Teste: ambos validados (liberado)
- [ ] Teste: SSE recebe eventos em tempo real
- [ ] Teste: Redis Pub/Sub funcionando
- [ ] Teste: Reconexão SSE após desconexão

### Dependências
- TASK 1 concluída
- TASK 2 concluída (documentos já armazenados)
- **Redis configurado** (Pub/Sub + Cache)
- **Celery configurado** (Workers)
- **SSE suportado** (FastAPI com sse-starlette)

---

## TASK 3: [BACKEND] Implementar Validação Biométrica no Início de Aula

**Tipo:** Task  
**Prioridade:** Alta  
**Story Points:** 8

### Descrição
Implementar validação biométrica em tempo real no início de cada aula, onde instrutor e alunos tiram selfie para confirmar presença e identidade.

### Contexto de Negócio
Garantir que o instrutor e estudante ao qual será iniciado aula é realmente quem está cadastrado, evitando fraudes de presença e garantindo conformidade legal.

### Objetivos
- Validar identidade do instrutor antes de iniciar aula
- Validar identidade dos alunos ao entrar na aula
- Comparar selfie em tempo real com foto do cadastro
- Registrar presença automaticamente após validação
- Bloquear acesso em caso de falha na validação

### Implementação Técnica

**Endpoints:**

1. **POST /api/v1/classes/{class_id}/biometry/verify-instructor**
```json
Request:
{
  "instructor_id": "uuid",
  "selfie": "base64",
  "class_id": "uuid"
}

Response:
{
  "verification_id": "uuid",
  "status": "approved|rejected",
  "similarity_score": 94.2,
  "can_start_class": true,
  "message": "Identidade confirmada"
}
```

2. **POST /api/v1/classes/{class_id}/biometry/verify-student**
```json
Request:
{
  "student_id": "uuid",
  "selfie": "base64",
  "class_id": "uuid"
}

Response:
{
  "verification_id": "uuid",
  "status": "approved|rejected",
  "similarity_score": 89.7,
  "can_join_class": true,
  "attendance_marked": true,
  "message": "Presença confirmada"
}
```

3. **GET /api/v1/classes/{class_id}/biometry/status**
```json
Response:
{
  "class_id": "uuid",
  "can_start_class": true,
  "instructor_verified": true,
  "instructor_verified_at": "2024-03-02T10:30:00Z",
  "students_verified": [
    {
      "student_id": "uuid",
      "student_name": "João Silva",
      "verified": true,
      "verified_at": "2024-03-02T10:30:00Z"
    }
  ],
  "total_students": 25,
  "verified_students": 23,
  "pending_students": 2,
  "minimum_requirements_met": true
}
```

4. **POST /api/v1/classes/{class_id}/start**
```json
Request:
{
  "instructor_id": "uuid"
}

Response:
{
  "class_id": "uuid",
  "status": "started|blocked",
  "can_start": true,
  "message": "Aula iniciada com sucesso",
  "instructor_verified": true,
  "students_verified_count": 23,
  "started_at": "2024-03-02T10:35:00Z"
}
```

**Task Celery:**
```python
@celery.task(bind=True, max_retries=2, time_limit=15)
def verify_class_start_biometry(self, verification_id, class_id, user_id, user_type):
    """
    Validação rápida para início de aula
    - Compara selfie com foto do cadastro
    - Timeout reduzido (15s)
    - Marca presença automaticamente
    - Libera acesso à aula
    """
```

### Fluxo de Início de Aula

**Pré-requisito: Aula só inicia quando AMBOS (instrutor E alunos) estiverem validados**

**Instrutor:**
1. Instrutor clica em "Iniciar Aula"
2. Sistema solicita selfie do instrutor
3. Validação biométrica em tempo real (< 15s)
4. Se aprovado: Sistema aguarda validação dos alunos
5. Se rejeitado: Bloqueio + notificação ao admin
6. Aula só inicia quando instrutor E pelo menos 1 aluno estiverem validados
7. Registro de tentativa para auditoria

**Aluno:**
1. Aluno entra na sala de aula virtual
2. Sistema solicita selfie (obrigatório no início da aula)
3. Validação biométrica em tempo real (< 15s)
4. Se aprovado: Acesso liberado + presença marcada + notifica sistema
5. Se rejeitado: Acesso negado + notificação ao instrutor
6. Sistema verifica se instrutor já foi validado
7. Se ambos validados: Aula é liberada para início
8. Registro de tentativa para auditoria

**Lógica de Liberação da Aula:**
```python
def can_start_class(class_id):
    instructor_verified = check_instructor_verification(class_id)
    students_verified = get_verified_students_count(class_id)
    
    # Aula só inicia se:
    # 1. Instrutor validado
    # 2. Pelo menos 1 aluno validado
    return instructor_verified and students_verified >= 1
```

### Estrutura de Dados

**Tabela: `class_attendance_verifications`**
```sql
- id (uuid, PK)
- class_id (uuid, FK)
- user_id (uuid, FK)
- user_type (enum: 'instructor', 'student')
- verification_id (uuid, FK -> biometry_verifications)
- attendance_marked (boolean)
- verified_at (timestamp)
- created_at (timestamp)
```

**Tabela: `class_sessions`**
```sql
- id (uuid, PK)
- class_id (uuid, FK)
- instructor_verification_id (uuid, FK)
- can_start (boolean)
- started_at (timestamp, nullable)
- minimum_students_verified (integer, default: 1)
- created_at (timestamp)
- updated_at (timestamp)
```

### Regras de Negócio

**Início de Aula:**
- ⚠️ **CRÍTICO**: Aula só inicia quando instrutor E pelo menos 1 aluno estiverem validados
- Sistema bloqueia botão "Iniciar Aula" até requisitos mínimos serem atendidos
- Notificação em tempo real quando requisitos são atendidos
- Timeout de 30 minutos: se requisitos não forem atendidos, aula é cancelada

**Instrutor:**
- Validação obrigatória a cada aula
- Score mínimo: 85%
- Timeout: 15s
- Retry: 2 tentativas
- Falha bloqueia início da aula
- Admin notificado em caso de falha

**Aluno:**
- Validação obrigatória no início da aula (todos os alunos)
- Alunos que chegarem atrasados também precisam validar
- Score mínimo: 80% (mais flexível)
- Timeout: 15s
- Retry: 2 tentativas
- Falha impede entrada + notifica instrutor
- Presença marcada automaticamente após aprovação
- Mínimo de 1 aluno validado para iniciar aula

**Auditoria:**
- Todas as tentativas registradas
- Selfies armazenadas por 90 dias
- Logs detalhados de cada validação
- Relatório de anomalias para admin
- Registro de horário exato de validação de cada participante

### Critérios de Aceite
- [ ] Endpoint de validação do instrutor funcionando
- [ ] Endpoint de validação do aluno funcionando
- [ ] Endpoint de status da turma funcionando
- [ ] Endpoint de início de aula com validação de requisitos
- [ ] ⚠️ **Aula só inicia quando instrutor E aluno(s) validados**
- [ ] Validação em tempo real (< 15s)
- [ ] Presença marcada automaticamente
- [ ] Bloqueio de acesso em caso de falha
- [ ] Notificações em tempo real sobre status de validação
- [ ] Botão "Iniciar Aula" desabilitado até requisitos atendidos
- [ ] Timeout de 30min para cancelamento automático
- [ ] Tabelas class_attendance_verifications e class_sessions criadas
- [ ] Selfies armazenadas temporariamente
- [ ] Logs de auditoria completos
- [ ] Testes de carga (100 alunos simultâneos)
- [ ] Testes de integração end-to-end
- [ ] Teste de cenário: instrutor validado mas nenhum aluno
- [ ] Teste de cenário: alunos validados mas instrutor não

### Dependências
- TASK 1 e TASK 2 concluídas
- Sistema de aulas funcionando
- Sistema de presença implementado

---

## TASK 4: [BACKEND] Implementar Suporte a Múltiplos Documentos Brasileiros

**Tipo:** Task  
**Prioridade:** Média  
**Story Points:** 5

### Descrição
Expandir sistema para aceitar e validar múltiplos tipos de documentos de identidade brasileiros (CNH, RG, CNH Digital, RNE).

### Contexto de Negócio
Alunos e instrutores podem ter diferentes documentos de identidade. Sistema precisa aceitar documentos válidos no Brasil para inclusão e conformidade legal.

### Objetivos
- Suportar CNH física e digital
- Suportar RG (frente e verso)
- Suportar CNH Digital (QR Code)
- Suportar RNE (estrangeiros)
- Validar formato e autenticidade do documento

### Implementação Técnica

**Tipos de Documentos:**

1. **CNH Física**
   - Formato: PDF ou imagem
   - Extração automática da foto
   - Validação de campos obrigatórios

2. **CNH Digital**
   - Formato: PDF com QR Code
   - Validação do QR Code (opcional)
   - Extração da foto

3. **RG**
   - Formato: Frente + Verso (2 imagens)
   - Extração da foto da frente
   - Validação de campos (CPF, data nascimento)

4. **RNE (Registro Nacional de Estrangeiro)**
   - Formato: PDF ou imagem
   - Extração da foto
   - Validação de campos específicos

**Componente: DocumentProcessor**
```python
class DocumentProcessor:
    def extract_photo(document_type, file) -> Image
    def validate_document(document_type, file) -> ValidationResult
    def extract_metadata(document_type, file) -> DocumentMetadata
```

**Estrutura de Dados:**

**Tabela: `user_documents`**
```sql
- id (uuid, PK)
- user_id (uuid, FK)
- document_type (enum: 'cnh', 'cnh_digital', 'rg', 'rne')
- document_number (string)
- document_url (string)
- document_back_url (string, nullable) -- Para RG
- photo_extracted_url (string)
- metadata (jsonb)
- validated (boolean)
- validated_at (timestamp)
- created_at (timestamp)
```

### Regras de Negócio
- CNH: Aceitar física ou digital
- RG: Obrigatório frente e verso
- RNE: Aceitar para estrangeiros
- Validação de formato antes do upload
- Extração automática da foto do documento
- Armazenamento seguro (criptografado)
- Retenção de 5 anos para auditoria

### Critérios de Aceite
- [ ] Suporte a CNH física e digital
- [ ] Suporte a RG (frente + verso)
- [ ] Suporte a RNE
- [ ] Extração automática de foto funcionando
- [ ] Validação de formato implementada
- [ ] Tabela user_documents criada
- [ ] Metadata extraída e armazenada
- [ ] Testes com documentos reais
- [ ] Documentação de tipos aceitos

### Dependências
- TASK 1 concluída
- Biblioteca de OCR configurada (opcional)

---

## TASK 5: [BACKEND] Implementar Dashboard Admin para Análise Manual

**Tipo:** Task  
**Prioridade:** Média  
**Story Points:** 5

### Descrição
Criar dashboard administrativo para análise manual de casos duvidosos (score 70-84%) e visualização de histórico de validações.

### Objetivos
- Visualizar casos pendentes de análise manual
- Aprovar/rejeitar manualmente com justificativa
- Visualizar histórico completo de validações
- Gerar relatórios de auditoria
- Monitorar taxa de aprovação/rejeição

### Implementação Técnica

**Endpoints:**

1. **GET /api/v1/admin/biometry/pending-review**
```json
Response:
{
  "total": 15,
  "items": [
    {
      "verification_id": "uuid",
      "user_id": "uuid",
      "user_name": "João Silva",
      "user_type": "instructor",
      "similarity_score": 78.5,
      "selfie_url": "url",
      "document_url": "url",
      "created_at": "2024-03-02T10:30:00Z"
    }
  ]
}
```

2. **POST /api/v1/admin/biometry/{verification_id}/review**
```json
Request:
{
  "decision": "approved|rejected",
  "justification": "string",
  "reviewed_by": "admin_user_id"
}

Response:
{
  "verification_id": "uuid",
  "status": "approved",
  "reviewed_at": "2024-03-02T11:00:00Z"
}
```

3. **GET /api/v1/admin/biometry/reports**
```json
Response:
{
  "period": "last_30_days",
  "total_verifications": 1250,
  "auto_approved": 1100,
  "auto_rejected": 50,
  "manual_review": 100,
  "approval_rate": 92.0,
  "average_score": 89.5
}
```

### Funcionalidades do Dashboard
- Lista de casos pendentes (score 70-84%)
- Visualização lado a lado (selfie vs documento)
- Histórico de validações do usuário
- Filtros (data, tipo, status, score)
- Exportação de relatórios (CSV/PDF)
- Métricas em tempo real

### Critérios de Aceite
- [ ] Endpoint de casos pendentes funcionando
- [ ] Endpoint de revisão manual funcionando
- [ ] Endpoint de relatórios funcionando
- [ ] Justificativa obrigatória para decisões
- [ ] Histórico de revisões armazenado
- [ ] Notificação ao usuário após revisão
- [ ] Métricas calculadas corretamente
- [ ] Exportação de relatórios funcionando

### Dependências
- TASK 1, 2 e 3 concluídas
- Sistema de permissões admin configurado

---

## TASK 6: [FRONTEND] Implementar Interface de Upload de Biometria

**Tipo:** Task  
**Prioridade:** Alta  
**Story Points:** 5

### Descrição
Criar interface amigável para captura de selfie e upload de documento durante cadastro e início de aula.

### Objetivos
- Captura de selfie via webcam/câmera
- Upload de documento (arrastar e soltar)
- Preview das imagens antes do envio
- Feedback visual do processo de validação
- Tratamento de erros amigável

### Componentes

1. **SelfieCapture Component**
   - Acesso à câmera
   - Captura de foto
   - Preview e retake
   - Validação de qualidade (iluminação, foco)

2. **DocumentUpload Component**
   - Drag and drop
   - Seleção de arquivo
   - Preview do documento
   - Validação de formato e tamanho

3. **BiometryStatus Component**
   - Loading state
   - Resultado da validação
   - Mensagens de erro/sucesso
   - Ações de retry

### Critérios de Aceite
- [ ] Captura de selfie funcionando
- [ ] Upload de documento funcionando
- [ ] Preview das imagens implementado
- [ ] Validação client-side de formato/tamanho
- [ ] Feedback visual durante processamento
- [ ] Tratamento de erros amigável
- [ ] Responsivo (mobile e desktop)
- [ ] Acessibilidade (WCAG 2.1)

---

## Estimativa Total
- **Story Points:** 36
- **Tempo Estimado:** 4-5 sprints (8-10 semanas)
- **Equipe Sugerida:** 2 backend + 1 frontend + 1 QA

## Ordem de Implementação Recomendada
1. TASK 1 (Base do sistema)
2. TASK 2 (Cadastro)
3. TASK 6 (Interface)
4. TASK 3 (Início de aula)
5. TASK 4 (Múltiplos documentos)
6. TASK 5 (Dashboard admin)

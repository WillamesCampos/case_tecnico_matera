# Developer Notes

Aqui estão alguns pontos levantados na arquitetura do projeto e construção da API, que pontos foram considerados em relação a outros, para dar melhor contexto em como pensei na construção do projeto.

## Por que não usar diretamente o django.contrib.auth.User?

Eu fiz a escolha de get_user_model() porque vai buscar o model definido para User diretamente do settings do django. Com isso, se futuramente ou ainda, optar por um model de User customizado, a aplicação vai detectar, pois é necessário passar a informação no settings.

## Por que optar por annotations e não por armazenar o valor restante do empréstimo?
Para o cenário do case, usar annotations vai fazer com que eu gere uma query que já traz o resultado, sem riscos de inconsistência (porque o cálculo é feito na hora). Armazenar acarreta no risco de verificar se a quantia está correta e é mais adequado para quantidades muito maiores de pagamentos, pois a query perderia performance.

## PaymentAggregatorService: Uso de aggregate() vs cache do prefetch

O `PaymentAggregatorService` utiliza `aggregate()` para calcular o total pago, mesmo quando há `prefetch_related("payments")` no ViewSet.

**Decisão de design:**
- O `LoanSerializer` (que usa este serviço) é utilizado apenas em `retrieve`, `create` e `update` (nunca em `list`)
- Como sempre trabalhamos com 1 objeto por vez, não há problema de N+1 queries
- A query `aggregate()` é simples e eficiente para este cenário
- Manter o código mais simples e direto, sem lógica condicional de cache

**Otimização futura (se necessário):**
Se no futuro houver necessidade de otimizar ainda mais, é possível verificar se os payments estão em cache (`loan._prefetched_objects_cache`) e somar em Python, evitando a query `aggregate()`. Porém, para o escopo atual do projeto, essa otimização não é necessária.

## Race Condition na Validação de Pagamentos

O `PaymentValidatorService` valida se o valor do pagamento não excede o saldo devedor calculando o saldo no momento da validação. Isso pode causar uma race condition em cenários de alta concorrência.

**O problema:**
Quando duas requisições simultâneas tentam criar pagamentos para o mesmo empréstimo:
1. Ambas leem o mesmo saldo devedor (ex: R$ 10.250)
2. Ambas passam na validação (ex: R$ 6.000 <= R$ 10.250)
3. Ambas são salvas
4. Resultado: overpayment (total pago = R$ 12.000, excedendo o saldo)

**Decisão de design:**
Para o escopo deste projeto (case técnico), foi decidido não implementar locks ou validações adicionais no banco de dados, mantendo a solução mais simples. Em um ambiente de produção com alta concorrência, seria necessário implementar uma das seguintes soluções:

1. **Lock pessimista**: Usar `select_for_update()` para bloquear a linha do loan durante a validação e criação do pagamento
2. **Validação no banco**: Adicionar constraints ou triggers no banco de dados
3. **Validação otimista**: Implementar retry logic com tratamento de erros de constraint

**Impacto:**
- Em cenários normais (baixa concorrência), o problema é raro
- Em alta concorrência, pode permitir overpayment
- Para produção, recomenda-se implementar lock pessimista

## Proteção de Campos Críticos do Loan Após Pagamentos

O `LoanSerializer` implementa uma proteção dinâmica que torna campos críticos `read_only` quando o empréstimo já possui pagamentos associados.

**O problema:**
Alterar campos críticos de um empréstimo após pagamentos terem sido criados pode causar inconsistências nos cálculos financeiros:

1. **`amount`**: Alterar o valor do empréstimo quebra o cálculo de saldo devedor, pois os pagamentos foram feitos com base no valor original
2. **`interest_rate`**: Alterar a taxa de juros quebra o cálculo de juros compostos, pois os pagamentos foram validados com base na taxa original
3. **`owner`**: Alterar o dono do empréstimo quebra o isolamento de dados e pode permitir acesso não autorizado
4. **`bank`**: Embora seja informativo, manter consistência dos dados é importante para auditoria

**Solução implementada:**
No `__init__` do serializer, verifico dinamicamente:
- Se é uma operação de UPDATE (`self.instance` existe)
- Se o empréstimo possui pagamentos (`self.instance.payments.exists()`)
- Se ambas condições forem verdadeiras, os campos críticos são tornados `read_only = True`

**Comportamento:**
- **CREATE**: Todos os campos podem ser preenchidos normalmente
- **UPDATE sem pagamentos**: Campos podem ser alterados
- **UPDATE com pagamentos**: Campos críticos ficam `read_only` (não podem ser alterados)

**Benefícios:**
- Mantém a integridade dos cálculos financeiros
- Evita inconsistências entre pagamentos e dados do empréstimo
- Protege dados históricos para auditoria
- Usa funcionalidade nativa do DRF (`read_only`), sem necessidade de validações customizadas

## IOFCalculatorService: Cálculo de IOF em Empréstimos

O `IOFCalculatorService` implementa o cálculo do Imposto sobre Operações Financeiras (IOF) conforme regras brasileiras para pessoa física.

**Componentes do IOF:**
1. **Alíquota Fixa**: 0,38% sobre o valor original do empréstimo (calculado uma vez)
2. **Alíquota Diária**: 0,0082% ao dia sobre o valor original, limitada a 3% ao ano

**Decisões de design:**
- IOF diário é calculado sobre o valor original (`loan.amount`), não sobre o saldo devedor atual
- O limite de 3% ao ano é aplicado por empréstimo (não globalmente)
- IOF é incluído no cálculo do saldo devedor: `(Principal + Juros + IOF) - Pagamentos`
- Cálculo é feito dinamicamente com base na data de referência (hoje ou data específica)

**Integração:**
- `OutstandingBalanceCalculatorService` injeta e usa o `IOFCalculatorService` para incluir IOF no saldo
- `LoanSerializer` expõe o campo `iof` no retrieve para transparência ao usuário

## Uso do pacote python-dotenv

O projeto utiliza `python-dotenv` para gerenciar variáveis de ambiente através do arquivo `.env`.

**Decisão de design:**
- Centraliza configurações sensíveis (SECRET_KEY, etc.) fora do código
- Facilita diferentes ambientes (dev, staging, production) sem alterar código
- Carregado no `settings.py` via `dotenv.load_dotenv()`

## Arquitetura de Serviços e Use Cases

O projeto segue uma arquitetura em camadas separando responsabilidades:

**Camada de Serviços (`services/`):**
- Contém lógica de negócio reutilizável e testável
- Exemplos: `InterestCalculatorService`, `PaymentAggregatorService`, `IOFCalculatorService`
- Herdam de `BaseService` para logging consistente
- Podem ser injetados como dependências para facilitar testes

**Camada de Use Cases (`use_cases/`):**
- Orquestram serviços para executar casos de uso específicos
- Exemplos: `CalculateLoanOutstandingBalanceUseCase`, `ValidatePaymentUseCase`
- Herdam de `BaseUseCase` com método abstrato `execute()`
- Abstraem a lógica de aplicação da lógica de domínio

**Benefícios:**
- Separação clara de responsabilidades
- Facilita testes isolados (mocks de dependências)
- Código mais manutenível e extensível
- Reutilização de serviços em diferentes contextos

## Logging em Serviços e Use Cases

Todos os serviços e use cases herdam de classes base (`BaseService`, `BaseUseCase`) que fornecem um logger configurado.

**Decisão de design:**
- Logger centralizado em `credit_track.settings` com handlers para console e arquivo
- Nível DEBUG em desenvolvimento, INFO em produção
- Logs estruturados com informações relevantes (UUIDs, valores, datas)
- Facilita debugging e auditoria sem poluir o código com prints

**Uso:**
- Serviços logam cálculos importantes (juros, IOF, saldo devedor)
- Use cases logam início e fim de execução
- Mensagens incluem contexto suficiente para rastreamento
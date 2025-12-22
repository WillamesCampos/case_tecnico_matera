# Regras de Cálculo do IOF em Empréstimos

## Alíquotas (Pessoa Física)

### 1. Alíquota Fixa
- **Valor**: 0,38% sobre o valor total do empréstimo
- **Cálculo**: `loan.amount * 0.0038`
- **Quando**: Calculado uma única vez sobre o valor principal

### 2. Alíquota Diária
- **Valor**: 0,0082% ao dia
- **Base de cálculo**: Valor original do empréstimo (`loan.amount`)
- **Período**: Dias entre `request_date` e `reference_date` (hoje ou data específica)
- **Limite**: Máximo de 3% ao ano (365 dias)
- **Cálculo**: `loan.amount * 0.000082 * days`
- **Limite aplicado**: `min(iof_daily, loan.amount * 0.03)`

### 3. IOF Total
- **Cálculo**: `IOF Fixo + IOF Diário`
- **Fórmula completa**: 
  ```
  IOF = (loan.amount * 0.0038) + min(loan.amount * 0.000082 * days, loan.amount * 0.03)
  ```

## Observações Importantes

1. **Base de cálculo**: O IOF diário é calculado sobre o **valor original do empréstimo** (`loan.amount`), **não sobre o saldo devedor atual**
2. **Não incide sobre juros**: O IOF incide apenas sobre o valor principal, não sobre os juros
3. **Cobrança**: O IOF é cobrado no momento da liberação do crédito (mas calculamos dinamicamente)
4. **Limite anual**: O limite de 3% é aplicado por empréstimo, não globalmente

## Exemplo de Cálculo

**Empréstimo**: R$ 10.000,00
**Data de solicitação**: 01/01/2024
**Data de referência**: 01/07/2024 (180 dias)

- **IOF Fixo**: R$ 10.000,00 × 0,38% = R$ 38,00
- **IOF Diário**: R$ 10.000,00 × 0,0082% × 180 dias = R$ 147,60
- **Total de IOF**: R$ 38,00 + R$ 147,60 = R$ 185,60

**Cenário com limite** (ex: 400 dias):
- **IOF Fixo**: R$ 10.000,00 × 0,38% = R$ 38,00
- **IOF Diário (sem limite)**: R$ 10.000,00 × 0,0082% × 400 = R$ 328,00
- **IOF Diário (com limite)**: min(R$ 328,00, R$ 10.000,00 × 3%) = R$ 300,00
- **Total de IOF**: R$ 38,00 + R$ 300,00 = R$ 338,00

## Integração no Saldo Devedor

O IOF será incluído no cálculo do saldo devedor:

```
Saldo Devedor = (Principal + Juros Compostos + IOF) - Total Pago
```

Onde:
- **Principal**: `loan.amount`
- **Juros Compostos**: Calculado mensalmente sobre o principal
- **IOF**: IOF fixo + IOF diário (calculado sobre o principal original)
- **Total Pago**: Soma de todos os pagamentos realizados


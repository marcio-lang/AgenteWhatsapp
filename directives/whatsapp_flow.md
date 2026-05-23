# WhatsApp Flow Directive

## Goal
Automate customer service via WhatsApp using the Evolution API. The agent acts as a "AutoResponder" based on defined rules.

## Config
- **Offers Directory**: `ofertas/`
- **Flow Rules**: Based on `AutoResponder_WA_Rules_.csv`

## Flow Logic

### 1. Default / Start (Pattern: `*` or Welcome)
**Trigger**: Any message that doesn't match other rules, or new conversation.
**Action**: Send Menu.
**Message**:
> Olá, tudo bem?
> O que podemos fazer por você hoje? Vamos tentar sanar suas dúvidas através do nosso atendimento automático.
> Qual é a sua dúvida? (Digite apenas o número correspondente à opção desejada!)
> 1 - Ofertas
> 2 - Formas de Pagamento
> 3 - Entregas
> 4 - Venda via Whatsapp
> 5 - Parcelamento
> 6 - Dúvidas Sobre Preços
> 7 - Falar com Atendente
> 8 - Trabalhe conosco
> 9 - Encerrar Atendimento

### 2. Option "1" - Ofertas
**Trigger**: Message "1"
**Action**:
1. Send Intro Text: "Aguarde enquanto preparamos as ofertas..."
2. **List files** in `ofertas/` directory.
3. **Send each file** found in `ofertas/` (Image/PDF).
4. If no files, send: "No momento não temos ofertas cadastradas."

### 3. Option "Eu Quero"
**Trigger**: Message "eu quero" (case insensitive)
**Action**: Send Success Message.
**Message**: "Agora você receberá nossas ofertas em primeira mão sempre!..."

### 4. Specific Options (Static Text)
- **"2" (Start/Pagamento)**: Lists payment methods (MaxxCard, Visa, Pix, etc.).
- **"3" (Entregas)**: Explains delivery policy (Taguatinga/Samambaia only).
- **"4" (Venda Whatsapp)**: Explains how to buy, asks for address details.
- **"5" (Parcelamento)**: Explains installments (2x > R$100).
- **"6" (Preços)**: Explains no access to stock/prices.
- **"7" (Atendente)**: "Em breve um atendente entrará em contato".
- **"8" (Trabalho)**: Email for resume (envieecurriculo@gmail.com).
- **"9" (Encerrar)**: "Obrigado e até breve!".
- **"obrigado"**: "Nós que agradecemos...".

## APIs
Use `execution/evolution_api.py` to send messages.

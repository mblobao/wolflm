[PAPEL]: Atue como um secretário de assembleias experiente e meticuloso. Sua especialidade é transformar discussões corridas e informais em um registro formal, claro, objetivo e imparcial para a ata oficial.

[CONTEXTO]: Você receberá um trecho de texto bruto ou áudio, que é uma transcrição ou anotação de uma discussão ocorrida durante uma assembleia de condomínio. Sua tarefa é processar especificamente a discussão relacionada ao tópico da pauta informada, criando um extrato da ata que seja claro e fiel aos fatos apresentados no texto.

[TAREFA]: Analise o texto fornecido, que corresponde à discussão de um tópico da pauta, e estruture-o em um formato de ata de reunião. Siga estes passos:

1.  Declare claramente qual é o "Tópico da Pauta" em discussão.
2.  Resuma a "Apresentação do Tópico", explicando a proposta ou o problema inicial.

3.  Sintetize os "Principais Pontos da Discussão", listando os argumentos a favor e contra, ou as diferentes opiniões levantadas pelos participantes. Seja conciso e agrupe ideias similares.
3.1. Atribua cada argumento à pessoa que o apresentou, sempre que o texto original a identificar (ex: "O Sr. João disse...", "A síndica Maria explicou..."). Se o texto não identificar o orador, apresente o argumento de forma impessoal (ex: "Foi sugerido que...", "Argumentou-se que...").

4.  Identifique se houve uma "Votação e Deliberação". Se sim, descreva a proposta votada, o resultado da votação (ex: aprovado por maioria, unanimidade) e a deliberação final. Se não houve votação, indique que "Não houve deliberação registrada".

Estruture a saída de forma limpa e profissional, seguindo o formato especificado.

[FORMATO]: Organize a saída usando a seguinte estrutura de Markdown, com os títulos em negrito:

**Tópico da Pauta:** [Nome do tópico discutido]

**Apresentação do Tópico:**
[Parágrafo único resumindo a apresentação inicial do tema.]

**Principais Pontos da Discussão:**
*   [Ponto 1: Resumo do primeiro argumento ou opinião principal.]
*   [Ponto 2: Resumo do segundo argumento ou contraponto.]
*   [Continue com quantos pontos forem necessários para cobrir a discussão.]

**Votação e Deliberação:**
[Descreva aqui o resultado. Ex: "Após a discussão, a proposta de [descrever proposta] foi colocada em votação. A deliberação foi [aprovada/rejeitada] por [maioria simples/unanimidade/contagem de votos, se disponível]. Ficou decidido que [descrever a ação a ser tomada]."]

[RESTRIÇÕES]:
* Seja estritamente objetivo e imparcial. Não adicione opiniões ou interpretações que não estejam explicitamente no texto original.
* Mantenha a imparcialidade. Não use adjetivos ou linguagem que sugira um juízo de valor.
* Seja conciso, focando nos pontos principais de cada argumento sem transcrever literalmente falas longas.
* Remova repetições, gaguejos, interrupções e frases coloquiais (ex: "tipo assim", "né", "aí").
* Concentre-se nos fatos, propostas e decisões. Evite registrar ataques pessoais ou comentários fora de tópico.
* O texto final deve ser claro e conciso.
* Foque exclusivamente no conteúdo relacionado ao [TÓPICO DA PAUTA] informado.
* O objetivo do resultado é a utilização direta do texto com parte da ata de reunião, então não faça introduções ou conclusões ou exemplos ou ou perguntas adicionais. responda apenas o prompt de resultado

[PÚBLICO]: A ata será lida por todos os condôminos, incluindo os que não estavam presentes na assembleia, pelo síndico, conselhos e eventualmente por oficiais de cartório.
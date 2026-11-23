# Rony-e-Gui-pygame

Jogo da Memória

Integrantes
- Rony Frid
- Guilherme Hutzler

Como rodar o jogo
1. Instale o Python 3.
2. Instale o PyGame com o comando: pip install pygame
3. Execute o arquivo principal com o comando: python jogo_da_memoria.py
O arquivo ranking.txt é criado ou atualizado automaticamente quando alguém vence uma partida.

Como jogar

Objetivo: encontrar todos os pares de cartas usando o menor número de tentativas possível.

1. Digite seu nome no menu. Se deixar o campo vazio, o jogo usará o nome “Anônimo”.

2. Escolha um nível de dificuldade:
   - Fácil: 12 cartas e 5 segundos para memorizar.
   - Médio: 16 cartas e 4 segundos para memorizar.
   - Difícil: 24 cartas e 3 segundos para memorizar.

3. No começo da partida, todas as cartas ficam viradas para cima durante alguns segundos. Tente memorizar a posição das figuras.

4. Quando as cartas virarem, clique em duas para tentar encontrar um par. Se forem iguais, ficam marcadas com uma borda verde e aparecem partículas. Se forem diferentes, aparece a mensagem “Não é par!” e elas viram de volta após um instante. Cada par de cartas escolhido conta como uma tentativa.

5. Ao encontrar todos os pares, a tela mostra suas tentativas, seu tempo e sua colocação no Top 5 do nível. O ranking considera o menor número de tentativas.

Controles

- Clique do mouse: vira uma carta ou seleciona um botão.
- Teclado no menu: digita o nome, usando letras e números.
- Backspace no menu: apaga o último caractere do nome.
- Botão “Ranking”: mostra o Top 5 de cada nível.
- R: reinicia a partida.
- ESC durante o jogo: volta ao menu.
- ESC no menu: sai do jogo.
- Clique na tela de vitória: volta ao menu.

Funcionalidades

- Menu, partida, tela de ranking e tela de vitória.
- Três níveis de dificuldade, com diferentes quantidades de cartas e tempos para memorização.
- Ranking Top 5 separado por nível e salvo em arquivo de texto.
- Cronômetro e contador de tentativas.
- Cartas e partículas implementadas com pygame.sprite.Sprite.
- Música de fundo e efeitos sonoros gerados pelo próprio código, sem arquivos de áudio externos.

Uso de inteligência artificial

Parte do código foi desenvolvida com auxílio de inteligência artificial (Claude). Não calculamos um percentual exato do código gerado com esse auxílio. A IA ajudou principalmente na estrutura inicial do programa e em ideias para organizar as telas, a lógica das cartas, o ranking e os sons. Depois, adaptamos essas sugestões às regras e ao funcionamento que queríamos para o jogo.



Link vídeo : https://youtube.com/shorts/wYuC7fM-NQk?is=sxxOzBdP19hTsH3D





Esta conversa está sendo útil até agora?

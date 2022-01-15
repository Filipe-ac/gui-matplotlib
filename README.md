# gui-matplotlib
Interface grafica usando a biblioteca Kivy para manipular gráficos através da biblioteca matplotlib

# Introdução

Muitas vezes um único código é usado tanto para o processamento e análise dos dados quanto para gerar as visualizações, o que pode tornar inconveniente futuras manipulações nos gráficos gerados, que devem ser localizadas no código e compiladas após cada modificação.
Portanto, é conveniente uma interface gráfica para manipular visualizações geradas com a biblioteca matplotlib em tempo real, sem a necessadida de compilar o codigo a cada alteração, bem como salvar as alterações feitas em um arquivo independente do código principal.

Com esse objetivo a biblioteca 'fp_ig2' implementa uma interface grafica baseada em Kivy que permite manipular graficamente os métodos pertinentes de várias instancias da biblioteca matplotlib, como 'Lines', 'Axes', 'Texts' etc, e implementa algumas funcionalidades como posicionar textos na figura com o mouse, ajuste de zoom, manipular dados, entre outros.

Alem disso, o arquivo 'fp_load' permite salvar e carregar um objeto 'Figure' em um arquivo independente com extensão definidad como .plt

Os códigos estão em fase de revisão, pois as funcionalidades vem sendo elaboradas a alguns anos, e as mais antigas, foram escritas em fases iniciais do meu aprendizado em Python e programação.

# Uso

## Carregando um objeto 'Figure'

'fp_ig(Figure).run()'

## Carregando um arquivo previamente salvo

No terminal:

'python fp_ig2.py foo.plt'

# Exemplos

Manipulando atributos de uma Line:

![image](https://user-images.githubusercontent.com/78453361/149636207-eaa21cb1-f23a-49cc-8424-86a664cf71da.png)

![image](https://user-images.githubusercontent.com/78453361/149636267-01863269-d6ea-4984-b752-5727c412dc88.png)


# Dependencias

- python 3
- numpy
- kivy
- matplotlib versão 3.1.0

# Documentação

Em construção

import matplotlib.pyplot as plt
import numpy as np
from erros2 import *
import os
import subprocess
from funcoes import *
from PIL import Image
import pandas as pd
from time import time
from threading import Thread
from matplotlib.ticker import FixedLocator, FixedFormatter, AutoLocator, FuncFormatter
from matplotlib.ticker import ScalarFormatter
from inspect import getfullargspec
from matplotlib.colorbar import _ColorbarAutoLocator
from matplotlib.axes import Axes
import matplotlib
from matplotlib.collections import QuadMesh
from matplotlib.patches import Rectangle
from matplotlib.container import BarContainer
from matplotlib.collections import PolyCollection
#from fp_load import *
plt.switch_backend('TkAgg')

#load_lists: get/set methods
#load_list_gui: attributes (obj.attr) may or may not native from matplotlib

def separa_repetidos(x,y = None):
    if isinstance(x,pd.DataFrame) == True:
        df = x.dropna()
    else:
        df = pd.DataFrame(y,x).dropna()

    bm = df.index.duplicated()
    if sum(bm) == 0:
        return None
    duplicates = df.index[bm]
    
    N = max([len(df.loc[i]) for i in duplicates])
    #uma copia do dataframe para cada repeticao
    m = [df.loc[~bm].copy() for i in range(N)]
    for d in duplicates:
        dfd = df.loc[d]
        for i in range(1,N):
            if i < len(dfd):
                m[i].loc[d] = dfd.iloc[i]

        
    
    return m


def to_cp(*args):
    '''insere no clipboard as listas, ou matriz, em forma de tabela'''
    import pyperclip
    tamanho = len(args[0])
    s = '' 
    for p in range(tamanho):
        
        for i in args:
            
            s += str(i[p]) + '\t'
        s += '\n'

    pyperclip.copy(s)
    
def salva_dados(nome,*args):
    arq = open(nome,'w')
    s = ''
    tamanho = len(args[0])
    for p in range(tamanho):
        
        for i in args:
            
            s += str(i[p]) + '\t'
        s += '\n'
    arq.write(s)
    arq.close()


def __read2__(data,verbose = False):

    m = data
    m.reverse()
    nan = np.nan

    for i in ['','\n']:

        while (i in m) == True:
            m.remove(i)

    arruma_linha = lambda x: x.replace('%','').replace('$','').replace('i','j').strip()
    arruma_linha2 = lambda x: x.replace('%','').replace('$','').replace('i','j').replace(',','.').strip()
    arruma_col = lambda x: [i.strip('\n').strip() for i in x if i.strip('\n').strip() != '']

    lista = ['\t',',',';',None,' ','   ']
    data = []
    ini = 0

    #encontrar separador
    for i in range(len(m)):
        for separador in lista:
            try:
                if separador == ',':
                    linha = arruma_linha2(m[ini])
                else:
                    linha = arruma_linha(m[ini])
                l = [eval(i) for i in linha.split(separador)]
                dados = True
                break
                
            except Exception as ex:
                pass
        if dados == True:
            break
        else:
            n += 1

    if verbose == True:
        print('separador: %s, ini: %s'%(separador,ini))

    while True:
        try:
            if separador == ',':
                linha = arruma_linha2(m[ini])
            else:
                linha = arruma_linha(m[ini])
            l = [eval(i) for i in linha.split(separador)]
            data.append(l)
            ini += 1

        except Exception as ex:
            break
        
    data.reverse()
    columns = None
    if ini >= len(m):
        return pd.DataFrame(data = data,columns = columns)
    else:
        if verbose == True:
            print('estimar coluna')
            print(m[ini])
        for sep in [separador] + lista:
            col = arruma_col(m[ini].split(sep))
            if len(col) == len(data[0]):
                columns = col
                if verbose == True:
                    print('sep: %s\ncoluna: %s'%(sep,col))
                break
    #comsol:
    if columns == None:
        col = arruma_col(m[ini].replace(')',')   ').split('  '))
        #print(col)
        if len(col) == len(data[0]):
            columns = col
    return pd.DataFrame(data = data,columns = columns)   
        
#m = open('/home/filipe/Dropbox/Usp_2021_1/dd/simulacoes_filipe/ressonador_py/tabela_ressondor').readlines()
#df = __read2__(m,1)

def __read__(data = 'Nao se aplica',inicio_data = 'auto', columns = 'auto',
           separador = 'auto'):
    
    m = data
    nan = np.nan

    for i in range(len(m)):
        m[i] = m[i].replace('%','').replace('$','')

    for i in ['','\n']:

        while (i in m) == True:
            m.remove(i)
    
    if columns != 'auto':
        columns = m[columns].split(separador)


    else:
        #estimar inicio dos dados

        #estimar o separador
        if separador == 'auto':
            lista = ['\t',',',';',None,' ']
        else:
            lista = [separador]
                
        data = []
        ini = 0
        for i in range(len(m)):
            for separador in lista:
                #print(separador)
                dados = False
                if separador == ' ':
                    #print(m[ini].strip().split(separador))
                    try:
                        #print('asd',m[ini].strip().split(separador))
                        l = [eval(i) for i in m[ini].replace('i','j').strip().split(separador)]
                        
                        dados = True
                        break
                        
                    except Exception as ex:
                        pass
                else:
                    
                    try:
                        #print('asd',m[ini].strip().split(separador))
                        l = [eval(i) for i in m[ini].replace('i','j').strip().split(separador)]
                        dados = True
                        
                        break
                    except Exception as ex:
                        #print(ex)
                        pass

            if dados == False:
                ini += 1
            else:
                break
        if separador != ',':
            for i in range(len(m)):
                m[i] = m[i].replace(',','.')

        #print(separador)
        if ini == 0:
            columns = None
            print('aa',m[ini])
            print('bb',m[ini].replace('i','j').replace('nan','np.nan').strip().split(separador))
            data = [[eval(i) for i in l.replace('i','j').replace('nan','np.nan').strip().split(separador)] for l in m]
        
        else:
##            for l in m[ini:]:
##                print(l.replace('i','j').strip().split(separador))
            
            data = [[eval(i) for i in l.replace('i','j').strip().split(separador)] for l in m[ini:]]
            if ini == 1:
                columns = m[ini-1].strip().split(separador)
                if len(columns) != len(data[0]):
                    columns = None
            
            else:
                for i in range(1,ini):
                    columns = m[ini-i].strip().split(separador)
                    if len(columns) == len(data[0]):
                        break
                if len(columns) != len(data[0]):
                    columns = None
        #correct columns with same name
        if columns != None:
            for i in range(len(columns)):
                if columns.count(columns[i]) > 1:
                    columns[i] = new_name_func(columns[i],columns)
    if inicio_data != 'auto':
        data = [[eval(i) for i in l.replace('i','j').split()] for l in m[inicio_data:]]
    return pd.DataFrame(data = data,columns = columns)

def read_c(data = 'Nao se aplica',inicio_data = 'auto', columns = 'auto',
           separador = 'auto'):
    
    import pyperclip
    m = pyperclip.paste().lower().replace(',','.').split('\n')
    return __read__(data = m,inicio_data = inicio_data,
                    columns = columns,separador = separador)
    
def read_a0(file,verbose = False):
    #return read_a(file,0,None,'\t')
    arq = open(file)
    m = arq.readlines()
    arq.close()
    return __read2__(data = m, verbose = verbose)

def read_a(file,inicio_data = 1,columns = 0, sep = '\t'):
    
    arq = open(file)
    l = arq.readlines()
    arq.close()
    m = []
    for line in l[inicio_data:]:
        m.append([eval(i.replace(',','.').replace('nan','np.nan').lower().strip('\n').strip(sep).strip()) for i in line.strip('\n').replace(';',sep).strip().split(sep)])

    if columns == None:
        return pd.DataFrame(np.array(m))

    if type(columns) == str:
        columns = eval(columns)
        
    if type(columns) == list:
        return pd.DataFrame(np.array(m),
                        columns = columns)
    if type(columns) == int:
        if '"' in l[columns]:
            #tentar separar pelo " 
            cl = l[columns].split('"')
            #pegar apenas os impares
            ind = [i for i in range(len(cl)) if i%2 != 0]
            cl = [cl[i] for i in ind]
            return pd.DataFrame(np.array(m),
                        columns = cl)
        else:
            return pd.DataFrame(np.array(m),
                columns = l[columns].split(sep))



def read_comsol(file):

    #print(os.getcwd())

    arq = open(file);m = arq.readlines();arq.close()
    #print(m[4])
    columns = m[4].replace(')',')   ').strip('\n').split('   ')
    while True:
        if '' in columns:
            columns.remove('')
        else:
            break

    df = pd.DataFrame(columns = columns)
    #print(columns)
    ind = 0
    for line in m[5:]:
        df.loc[ind] = [float(i) for i in line.strip('\n').split()]
        ind += 1
    return df

def tradus_terminal(s):

    lista = [' ','$','(',')']
    s2 = ''
        
    for i in s:
        if i in lista:
            i = '\%s'%i
        s2 += i
            

    return s2


def seleciona_listas(lim1 = -np.inf,lim2 = np.inf,*args):
    '''seleciona as listas apenas entre os valores contidos entre lim1 e lim2
        na PRIMEIRA lista'''
    
    if args == ():
        return None
    l1 = np.array(args[0])
    bm = (l1 >= lim1) & (l1 <= lim2)

    return [np.array(i)[bm] for i in args]

class FuncFormatter(FuncFormatter):
    def __init__(self,string):
        self.string = string
        super().__init__(lambda x,*args: eval(string))

#implementar legenda 'get_legend'
#implementar funcao para modificar a line


#methods that return native python types (bool, int, str..)

def set_ax_id(ax,_id):
    ax.id = _id
    
def cria_id_axes(fig):
    '''cria ou atualiza o dict com os axes relacionados por uma id unica'''
    if 'ax_ids' not in fig.__dict__:
        fig.ax_ids = []
        
    ids_atuais = []
    for ax in fig.axes:
        
        if 'id' not in ax.__dict__:
            if fig.ax_ids == []:
                ax.id = 1
                fig.ax_ids.append(1)
            else:
                ax.id = fig.ax_ids[-1] + 1
                fig.ax_ids.append(ax.id)

        ids_atuais.append(ax.id)

    #excluir as ids cujos ax nao existem mais
    for id_ in fig.ax_ids:
        if id_ not in ids_atuais:
            fig.ax_ids.remove(id_)
            

def localiza_ax(fig,id_):
    if isinstance(id_,Axes) == True:
        return id_
    cria_id_axes(fig)
    for i in fig.axes:
        
        if i.id == id_:
            return i
    print('ax nao encontrado')
    return None
        
def new_name_func(name,lista):
    if name not in lista:
        return name
    n = 1
    while '%s%i'%(name,n) in lista:
        n += 1
    return '%s%i'%(name,n)

def new_name_line(name,line):
    return new_name_func(name,[i.get_label() for i in line.axes.lines])

def acha_dir(objeto,nome):
    for i in dir(objeto):
        if nome in i:
            print(i)

def twin_ax(ax,axis = 'x'):
    if axis == 'x':
        if ax.twiny_ax != None:
            return
        ax2 = ax.twiny()
        ax2.set_label(ax.get_label() + '_x2')
        ax.twiny_ax = ax2
    else:
        if ax.twinx_ax != None:
            return
        ax2 = ax.twinx()
        ax2.set_label(ax.get_label() + '_y2')
        ax.twinx_ax = ax2
        
    ax2.parent_ax = ax
    
    ax.figure.canvas.draw()
    
    return ax2


def sort_line(line,sort = True):

    if 'original_data' not in line.__dict__:
        x,y = line.get_data()
        line.original_data = [x.copy(),y.copy()]
    if sort == True:  
        x,y = line.original_data
        line.argsort = np.argsort(x)
    else:
        line.argsort = None
    func_line(line)

        
def suavisa(x,y,passo,erro = False):
    xmedia, ymedia = [],[]
    pos = 0
    if erro == True:
        while pos + passo < len(x):
            xmedia.append(media(x[pos:pos+passo+1]))
            ymedia.append(media(y[pos:pos+passo+1]))
            pos += passo
        if pos != len(x):
            xmedia.append(media(x[pos:]))
            ymedia.append(media(y[pos:]))
    else:
        while pos + passo < len(x):
            xmedia.append(media(x[pos:pos+passo+1]).valor)
            ymedia.append(media(y[pos:pos+passo+1]).valor)
            pos += passo
        if pos != len(x):
            xmedia.append(media(x[pos:]).valor)
            ymedia.append(media(y[pos:]).valor)


    return xmedia,ymedia

def suavisa_line(line,passo,erro = False):
    line.suavisa = passo
    func_line(line)

def savgol(line,window_lenght,polyorder):
    try:
        from scipy.signal import savgol_filter
        x,y = line.original_data
        x,y = savgol_filter([x,y],window_lenght,polyorder)
        line.set_data(x,y)
        line.window_lenght = window_lenght
        line.polyorder = polyorder
        line.figure.canvas.draw()
    except Exception as ex:
        print(ex)
        
    
def busca(l,valor):

   
    if len(l) == 0 or len(l) == 1:
        return 0

    try:
        iter(valor)
        df = pd.DataFrame(data = list(l),columns = ['l'])
        for i in valor:
            df[i] = df['l'] - i
        
        res = abs(df).agg(np.argmin).drop('l').values

        return res    
            

    except Exception as ex:
    
        df  = pd.DataFrame(np.array(l).transpose())
        exato = df[df[0] == valor]
        if len(exato) != 0:
            return exato.index[0]
        else:
            baixo = df[df[0] < valor][0]
            alto = df[df[0] > valor][0]

            if len(baixo) == 0:
                return alto.idxmin()
            if len(alto) == 0:
                return baixo.idxmax()

            baixo = df[df[0] < valor][0].idxmax()
            alto = df[df[0] > valor][0].idxmin()

            l = [(abs(valor - l[alto]),alto),(abs(valor - l[baixo]),baixo)]
            return min(l)[1]

def get_line(label,ax):
    for line in ax.lines:
        if line.get_label() == label:
            return line
    return None

def get_text(label,ax):
    for text in ax.texts:
        if text.get_label() == label:
            return text
    return None

def load_img(img,ax,**args):
    im = ax.imshow(Image.open(img),**args)
    im.set_label(new_name_func('_'+img,[i.get_label() for i in ax.images]))
    return im




def fit_curva(x,y,x0,fwhm,intensidade,y0 = 0,alfa_assimetria = 0,offset = 0,
                  tol_x0 = 1,tol_fwhm = 1,tol_intensidade = 1,tol_y0 = 0, tol_alfa_assimetria = 0,tol_offset = 0,
              funcao = 'lorentziana',
              retorna_func = False,
              individuais = False,
              **kargs):

    '''Se tolerancia for == 0, nao vai fitar o parametros '''
    funcao_nome = funcao
    if funcao == 'lorentziana':
        funcao = lorentziana
    if funcao == 'gaussiana':
        funcao = gaussiana

    #padronizar tudo em array
    dic = {}
    for i in ['x0','fwhm','intensidade','y0','alfa_assimetria','offset']:
        var = locals()[i]
        if isinstance(var, np.ndarray) == False and isinstance(var,list) == False:
            var = np.array([var])
        else:
            var = np.array(var)
        dic[i] = var
            
    x0 = dic['x0']
    fwhm = dic['fwhm']
    intensidade = dic['intensidade']
    y0 = dic['y0']
    alfa_assimetria = dic['alfa_assimetria']
    offset = dic['offset']

    #definir o chute inicial e bounds
    bounds1 = []; bounds2 = []; p0 = []
    inicio = 0
    parametros_fit = []

    for i in ['x0','fwhm','intensidade','y0','alfa_assimetria','offset']:
        valor = locals()[i]
        tol = locals()['tol_%s'%i]

        if tol != 0:
            parametros_fit.append(i)
            p0 = np.concatenate([p0,valor])
            if i == 'fwhm':
                bounds = valor - tol
                bounds[bounds < 0] = 0
                bounds1 = np.concatenate([bounds1,bounds])
                bounds2 = np.concatenate([bounds2,valor + tol])
            else:
                if type(tol) == tuple:
                    bounds1 = np.concatenate([bounds1,[tol[0] for v in valor]])
                    bounds2 = np.concatenate([bounds2,[tol[1] for v in valor]])
                else:
                    bounds1 = np.concatenate([bounds1,valor - tol])
                    bounds2 = np.concatenate([bounds2,valor + tol])
            inicio += len(valor)

    #definir a funcao a ser fitada
    def func(x,*args):
        
        #cuidado para nao subistituir as variaveis da funcao principal
        inicio = 0
        nu0 = list(args[:len(x0)]) if tol_x0 != 0 else x0
        inicio = inicio + len(x0) if tol_x0 != 0 else inicio

        sigma = list(args[inicio:inicio+len(fwhm)]) if tol_fwhm != 0 else fwhm
        inicio = inicio + len(fwhm) if tol_fwhm != 0 else inicio

        i0 = list(args[inicio:inicio+len(intensidade)]) if tol_intensidade != 0 else intensidade
        inicio = inicio + len(intensidade) if tol_intensidade != 0 else inicio
        
        y0_ = list(args[inicio:inicio+len(y0)]) if tol_y0 != 0 else y0
        inicio = inicio + len(y0) if tol_y0 != 0 else inicio

        alfa = list(args[inicio:inicio+len(alfa_assimetria)]) if tol_alfa_assimetria != 0 else alfa_assimetria
        inicio = inicio + len(alfa) if alfa != 0 else inicio
        
        ofset = list(args[inicio:inicio+len(offset)]) if tol_offset != 0 else offset
        inicio = inicio + len(offset) if tol_offset != 0 else inicio

        return funcao(x,nu0,sigma,i0,y0_,alfa,ofset)

   #remover nan
    xnan = ~np.isnan(x)
    ynan = ~np.isnan(y)
    ind_nan = xnan*ynan

    x = np.array(x)[ind_nan]
    y = np.array(y)[ind_nan]
    
   
    #ordenar os dados
    ind = np.argsort(x)
    x = x[ind]; y = y[ind]
##
##    print(parametros_fit)
##    print('p0: ',p0)
##    print('bounds1: ',bounds1)
##    print('bounds2: ',bounds2)
##    
    from scipy.optimize import curve_fit
    res, erros = curve_fit(func,x,y,p0 = p0,
                                        bounds = (bounds1,bounds2),**kargs)
    err = np.sqrt(np.diag(erros))
    
    
    df = pd.DataFrame(index = np.arange(0,len(x0)),
                      columns = ['x0','x0_err','fwhm','fwhm_err','intensidade','intensidade_err',
                                'y0','y0_err',
                                          'alfa_assimetria','alfa_assimetria_err',
                                 'offset','offset_err'])

    inicio = 0    
    for i in ['x0','fwhm','intensidade','y0','alfa_assimetria','offset']:
        valor = locals()[i]
        tol = locals()['tol_%s'%i]
        if tol != 0:
            #print(inicio,res,len(valor))
            if len(res[inicio:inicio+len(valor)]) == len(x0):
                df[i] = res[inicio:inicio+len(valor)]
                df['%s_err'%i] = err[inicio:inicio+len(valor)]
            else:
                df[i] = res[inicio:inicio+len(valor)][0]
                df['%s_err'%i] = err[inicio:inicio+len(valor)][0]           
            inicio += len(valor)
        else:
            
            if len(valor) > 1:
                df[i] = valor
                df['%s_err'%i] = np.repeat(0,len(valor))
            else:
                df[i] = valor[0]
                df['%s_err'%i] = 0
    df.index.name = funcao_nome
            
    return res,err,df



def plot_fit_curvas(df,lim1,lim2,resolucao = 10000,ax = None,
                    unidadex = '',
                    unidadey = '',simbolox = 'x',simboloy = 'y',
                    legenda = False):



    lista_lines = []

    dic = {'x0':'$%s_0 = $'%simbolox,
           'fwhm':'$\Delta %s$'%simbolox,
           'intensidade': '$I_0$',
           'y0':'$%s_0$'%simboloy,
           'alfa_assimetria':'$\\alpha$',
           'offset':'offset'}

    if ax == None:
        fig,ax = plt.subplots()

    if df.index.name == 'lorentziana':
        func = lorentziana
    if df.index.name == 'gaussiana':
        func = gaussiana

    xpoints = np.linspace(lim1,lim2,resolucao)

    #parciais:
    for i in df.index:
        
        dfa = df.loc[i]
        xp = np.linspace(dfa['x0'] - 3*dfa['fwhm'],dfa['x0'] + 3*dfa['fwhm'],int(resolucao/10))
        y = func(xp,nu0 = dfa['x0'],
                        deltanu = dfa['fwhm'],
                        intensidade = dfa['intensidade'],
                        y0 = dfa['y0'],
                        alfa = dfa['alfa_assimetria'],
                        offset = dfa['offset'])
        lista_lines.append(ax.plot(xp,y,'--')[0])

    #total
    y = func(xpoints,nu0 = df['x0'].values,
                    deltanu = df['fwhm'].values,
                    intensidade = df['intensidade'].values,
                    y0 = df['y0'].values,
                    alfa = df['alfa_assimetria'].values,
                    offset = df['offset'].values)
    lista_lines.append(ax.plot(xpoints,y,'--',color = 'black')[0])
    
    if legenda == True:
        ax.legend(loc = 'upper right')

    return lista_lines


def teste_fit_curva_parametros():
    x = np.linspace(-10,10,1000)
    y = lorentziana(x,nu0 = [-2,2],
                    deltanu = 1,
                    intensidade = 1,
                    y0 = 0,
                    alfa = [3,6])
    
    res,err,df = fit_curva(x,y,x0 = [-1,2],
              fwhm = 1,
              intensidade = 0.5,
              y0 = 0,
              alfa_assimetria = [4,6],
              tol_x0 = 3,
              tol_fwhm = 0,
              tol_intensidade = 1,
              tol_y0 = 0,
              tol_alfa_assimetria = 1)
    fig,ax = plt.subplots()
    ax.plot(x,y)
##    ax.plot(x,lorentziana(x,nu0 = res[0:2],
##                          deltanu = 1,
##                          intensidade = res[2],
##                          y0 = 0,
##                          alfa = res[3:]),'--')
##    fig.show()
    plot_fit_curvas(df,-10,10,ax=ax)
    fig.show()
    return res,err,df

#res,err,df = teste_fit_curva_parametros()

def legend(ax):
    if type(ax.get_legend()) == type(None):
        return
    loc = ax.get_legend()._get_loc()
    ax.legend(loc = loc)
    #ax.figure.canvas.draw()

def legend_line(line,leg):
    line.set_label(leg)
    legend(line.axes)
    line.figure.canvas.draw()
    

def visible(line,v):
    lb = line.get_label()
    line.set_visible(v)
    if v == 0:
        line.set_label('_' + lb)
    else:
        line.set_label(lb[1:]) 
    legend(line.axes)

def str2func(string):
    '''a partir de uma string onde a variavel independente e X,
        separa os parametros e retorna uma funcao'''
    if string in dir():
        pass
    #separar parametros
    import funcoes
    lista_funcoes = dir(funcoes)
    parametros = []
    numeros = '1234567890.'
    l = string.replace(')','').split('(')
    for i in l:
        i = i.replace('*','+').replace('-','+').replace('/','+')
        i = i.replace('**','+').replace(' ','').replace('X','').split('+')
        for para in i:
            for par in para.split(','):
                if par != '' and par not in lista_funcoes and par not in numeros:

                    #testar se o parametro nao e um numero
                    for num in par:
                        if num not in numeros and par not in parametros: #nao e numero
                            parametros.append(par)
                            break
                        else: #se for numero nao e adicionado na lista
                            pass
                

    funcao = eval('lambda X, %s: %s'%(','.join(parametros),string))
    print(parametros,type(parametros))
    return funcao,parametros

def create_disepertion(Y):
    '''return two arrays with the highest and lowest
        value for all points on Y matrix'''
    
    return Y.min(axis = 0), Y.max(axis = 0)

#Y = create_disepertion(np.ramdom.radom(

def shadow_error(line, error_down,error_up = None,
                 alpha = 0.5,**args):

    if error_up is None:
        try:
            #if is a list/array
            iter(error_down)
            err = np.array(error_down)
            error_down = y - err
            error_up = y + err
        except:
            #if it is a number
            error_up = y + error_down
            error_down = y - error_down


    if 'df_err' not in line.__dict__:
        line.df_err = pd.DataFrame(np.array([error_down,error_up]).T,
                        columns = ['error_down','error_up'])
        ed,eu = ['error_down','error_up']
    else:
        ed = new_name_func('error_down',line.df_err.columns)
        eu = new_name_func('error_up',line.df_err.columns)
        line.df_err[ed] = error_down
        line.df_err[eu] = error_up
        
    line.list_erry = [ed,eu]
    
    fb = line.axes.fill_between(line.get_xdata(),error_up,error_down,alpha = alpha,
                                color = line.get_color(),**args)
    checa_id(line)
    fb.id = line.id
    fb.tipo = 'erro'


def checa_id(line):
    if 'id' not in line.__dict__:
        line.id = new_name_func('id1',[i.id for i in line.axes.lines if 'id' in i.__dict__])

 
def salva(fig,file):

    if '.plt' not in file:
        file = file + '.plt'
    from fp_load import load_fig
    dic = load_fig(fig)
    dic['df_dict'] = {}
    dic['conteiners'] = []
    pd.DataFrame({'graf':dic}).to_hdf(file,mode = 'w',key = 'df')

    fig.savefig('.'+file+'_icone.png')
    pasta = tradus_terminal(os.getcwd())
    
    #arrumar icone
    
    os.system('gio set -t string %s/%s metadata::custom-icon file://%s/%s'%\
                              (pasta,file,pasta,'.'+file+'_icone.png'))
    
#aqui ta a treta
def func_line(line):

    if 'original_data' not in line.__dict__:
        x,y = line.get_data()
        line.original_data = [x.copy(),y.copy()]

    X,Y = line.original_data
    X = np.array(X); Y = np.array(Y)

    if 'argsort' in line.__dict__ and type(line.argsort) != type(None):
        X = X[line.argsort]; Y = Y[line.argsort]

    if 'funcao_eixox' not in line.__dict__ or line.funcao_eixox == 'x':
        line.funcao_eixox = 'X'
    if 'ratiox' not in line.__dict__:
        line.ratiox = 1
    if 'deltax' not in line.__dict__:
        line.deltax = 0

    if 'funcao_eixoy' not in line.__dict__ or line.funcao_eixoy == 'y':
        line.funcao_eixoy = 'Y'
    if 'ratioy' not in line.__dict__:
        line.ratioy = 1
    if 'deltay' not in line.__dict__:
        line.deltay = 0

    #min_y = min(Y)
##    #min_x = min(X)
##    X = eval('('+line.funcao_eixox +' - %s)*%s + %s + %s'%(min_x,line.ratiox , line.deltax,min_x))
##    Y = eval('('+line.funcao_eixoy +' - %s)*%s + %s + %s'%(min_y,line.ratioy , line.deltay,min_y))
##    #print('('+line.funcao_eixoy +' - %s)*%s + %s + %s'%(min_y,line.ratioy , line.deltay,min_y))

    X = eval(line.funcao_eixox +'*%s + %s'%(line.ratiox , line.deltax))
    Y = eval(line.funcao_eixoy +'*%s + %s'%(line.ratioy , line.deltay))
        
    if 'suavisa' not in line.__dict__:
        line.suavisa = 1
    if line.suavisa != 1:

        X,Y = suavisa(X,Y,line.suavisa)

    line.set_data(X,Y)

    
    #shadow erro
    if 'id' in line.__dict__:
        for col in line.axes.collections:
            if 'id' in col.__dict__ and col.id == line.id:
                if 'tipo' in col.__dict__ and col.tipo == 'erro':
                    if 'original_data' not in col.__dict__:
                        mxy = col.get_paths()[0].vertices.copy()
                        col.original_data = mxy
                    else:
                        mxy = col.original_data
                        
                    X = mxy.T[0]; Y = mxy.T[1]
       
                    col.get_paths()[0].vertices.T[0] = eval(line.funcao_eixox +'*%s + %s'%(line.ratiox , line.deltax))
                    col.get_paths()[0].vertices.T[1] = eval(line.funcao_eixoy +'*%s + %s'%(line.ratioy , line.deltay))
        
    
    line.figure.canvas.draw()
#df = read_comsol('/home/filipe/Desktop/Link to projetos/fp_ig2/heatmap_alpha_d32_12000_16000.txt')


def heatmap_df(hm,ax = None,*args):


    if ax is None:
        fig,ax = plt.subplots()
        
    hm = hm.sort_index().T.sort_index().T

    y0 = hm.index.sort_values()[-1]
    dy = np.diff(hm.index.sort_values())[0]

    x0 = hm.columns.sort_values()[-1]
    dx = np.diff(hm.columns.sort_values())[0]
    
    quad = ax.pcolormesh(np.append(hm.columns,x0+dx) - dx/2
         ,np.append(hm.index,y0+dy) - dy/2,
         hm.values,
        cmap = 'RdYlBu_r')

    ax.set_xlim(hm.columns.min()-dx/2,hm.columns.max()+dx/2)
    ax.set_ylim(hm.index.min()-dy/2,hm.index.max()+dy/2)
    
    cb = ax.figure.colorbar(quad)
    
    return ax,quad,cb


def eixos_proporcionais(ax):

    x1,x2 = ax.get_xlim()
    y1,y2 = ax.get_ylim()

    mi = min(x1,y1)
    ma = max(x2,y2)

    distancia = ma - mi

    dist = x2-x1
    delta = (x1 + x2 - mi - ma)/2
    ax.set_xlim(mi+delta,ma-delta)

    dist = y2-y1
    delta = (y1 + y2 - mi - ma)/2
    ax.set_ylim(mi+delta,ma-delta)

    return ax


def add_axis2(ax,funcao,axis = 'y'):
    '''Cria um segundo eixo com valores dados pela funcao
        e travado com os mesmos limites do eixo principal'''

    if axis == 'y':
        twin = ax.twinx()
        axis = twin.yaxis
        ax.twin_travada_y = twin
    else:
        twin = ax.twiny()
        axis = twin.xaxis
        ax.twin_travada_x = twin
        

    axis.set_major_formatter(FuncFormatter(funcao))
    draw = ax.figure.canvas.draw
    

    def draw2():
        if 'twin_travada_x' in ax.__dict__:
            ax.twin_travada_x.set_xlim(ax.get_xlim())
        if 'twin_travada_y' in ax.__dict__:
            ax.twin_travada_y.set_ylim(ax.get_ylim())
        draw()
    
    ax.figure.canvas.draw = draw2

    return ax

def set_funcoes_acopladas(ax,axes_filhos,eixo = 'x'):
    
    if 'x' in eixo:
        xlim = ax.set_xlim
        def xlim2(x,y = None,**args):
            if y is None:
                x,y = x
            for i in ax.axes_travados_x:
                
                if (ax.id is i) == False:
                    ax2 = localiza_ax(ax.figure,i)
                    if ax2 != None:
                        ax2.set_xlim(x,y,**args)
            xlim(x,y,**args)

        ax.set_xlim = xlim2

    if 'y' in eixo:
        ylim = ax.set_ylim
        def ylim2(x,y = None,**args):
            if y is None:
                x,y = x
            for i in ax.axes_travados_y:
                
                if (ax.id is i) == False:
                    ax2 = localiza_ax(ax.figure,i)
                    if ax2 != None:
                        ax2.set_ylim(x,y,**args)
            ylim(x,y,**args)

        
        ax.set_ylim = ylim2

def centraliza_ax(ax,eixo = 'x'):
    bbox = ax.get_position(0)
    
    for a in ax.figure.axes:

        if (a is ax) == False:

            if eixo == 'x':
                #mesmo x e arrumar a altura
                bbox2 = a.get_position(0)
                y2 = bbox2.y0 + bbox.y1 - bbox.y0
                
                print(bbox.y0,bbox.y1,y2)
                
                bbox2.x0 = bbox.x0
                bbox2.x1 = bbox.x1
                bbox2.y1 = y2
                #print([bbox.x0,bbox2.y0,bbox.x1,bbox2.y1])
                a.set_position(bbox2,
                               which = 'both')

            if eixo == 'y':
                #mesmo y e arrumar x
                pass
    ax.figure.canvas.draw()

def desacopla_axis(ax,fig = None,eixo = 'x',*args):
    if isinstance(ax,Axes) == True:
        fig = ax.figure
        cria_id_axes(fig)
        
    else:
        cria_id_axes(fig)
        ax = localiza_ax(fig,ax)

    if 'x' in eixo:
        ax.axes_travados_x = []
    if 'y' in eixo:
        ax.axes_travados_y = []

def acopla_axis(ax_pai,axes_filhos = [],fig = None,eixo = 'x',*args):
    print(ax_pai)
    if isinstance(ax_pai,Axes) == True:
        ax = ax_pai
        fig = ax.figure

        cria_id_axes(fig)
        
    else:
        cria_id_axes(fig)
        ax = localiza_ax(fig,ax_pai)
    if 'axes_travados_x' not in ax.__dict__:
        ax.axes_travados_x = []
    if 'axes_travados_y' not in ax.__dict__:
        ax.axes_travados_y = []
        
    if axes_filhos == []:
        axes_filhos = [i for i in args]
    if type(axes_filhos) != list:
        axes_filhos = [axes_filhos]
    for i in axes_filhos:
        if 'x' in eixo:
            if isinstance(i,Axes) == True:
                __id = i.id
            else:
                __id = i
            if __id not in ax.axes_travados_x:
                ax.axes_travados_x.append(__id)
                
        set_funcoes_acopladas(ax,ax.axes_travados_x,eixo = 'x')
        
        if 'y' in eixo:
            if isinstance(i,Axes) == True:
                __id = i.id
            else:
                __id = i
            if __id not in ax.axes_travados_y:
                ax.axes_travados_y.append(__id)

        set_funcoes_acopladas(ax,ax.axes_travados_y,eixo = 'y')
               


def teste_acopla_axis():
    fig,ax = plt.subplots(2)
    ax1,ax2 = ax
    cria_id_axes(fig)
    localiza_ax(fig,1)

    acopla_axis(ax1,ax2,fig)
    #fig.show()
    return fig,ax1,ax2
#fig,ax1,ax2 = teste_acopla_axis()

def intersection(l1,l2,tolerance = None):
    if tolerance == None:
        tolerance = np.abs(l1 - l2).mean()

    idx = np.argwhere((np.diff(np.sign(l1 - l2)) != 0) &\
                      (np.abs(np.diff(l1 - l2)) <= tolerance)).flatten()
    return idx

def isfabryperot(lista_maximos,convert_to_thz = True,
                 unidade = 1e9):
    if convert_to_thz == True:
        lista_maximos = nm2thz(np.array(lista_maximos))


    dif = np.sort(np.diff(lista_maximos))
    delta_medio = abs(np.mean(dif))
    delta_std = abs(np.std(dif))
    nd = (vluz)/(2*delta_medio*10**12)
    return nd*unidade

def teste_isfabryperot():
    l = [434.72297756, 560.66086068, 685.19934596,
       809.43852767, 934.27663475]
    nd = isfrabyperot(thz2nm(np.array(l)))
    print(nd)

def resolve_ressonancia(x,Y,funcao,limite = 30):

    #passo 2: organizar as listas
    idx = x.argsort()
    x = x[idx]; Y = Y[idx]

    #passo 3: decidir deltay minimo

    dy_min = abs(max(Y)-min(Y))/10

    #passo 4: checar quais pontos em y não satisfazem o dy_min
    pontos = abs(np.diff(Y)) > dy_min

    iteracao = 0
    while pontos.sum() > 0:
        #passo 5: para cada ponto == True (nao satisfaz dy_min), acrescentar um ponto
            #entre os dois pontos x

        index = np.argwhere(pontos == True)[0]
        x_novos = x[index] + (x[index + 1] - x[index])/2


        #Resolver plato no ponto maximo:

        #procurar plato:
        pos = np.argwhere(Y == Y.max()).flatten()
        if len(pos) > 1:
            platos = np.argwhere(np.diff(pos) == 1).flatten()
            index = pos[platos]
            if len(platos) != 0:
                x_platos = x[index] + (x[index + 1] - x[index])/2
                print(x_platos)
                x_novos = np.append(x_novos,x_platos)

        #passo 6: acrescentar os novos potnos

        Y = np.append(Y,funcao(x_novos))
        x = np.append(x,x_novos)    

        #refazer do passo 2:
        
        #passo 2: organizar as listas
        idx = x.argsort()
        x = x[idx]; Y = Y[idx]

        #passo 3: decidir deltay minimo

        dy_min = abs(max(Y)-min(Y))/10

        #passo 4: checar quais pontos em y não satisfazem o dy_min
        pontos = abs(np.diff(Y)) > dy_min
        iteracao += 1
        if iteracao >= limite:
            break

    return x, Y

def teste_resolve_ressonancia():
    fig,ax = plt.subplots()
    y = lambda x: lorentziana(x,0,0.01,1)


    #passo 1: fazer a curva com dada resolucao
    x = np.linspace(-1,1,10)
    Y = y(x)
    ax.plot(x,Y,'-o')

    x,Y = resolve_ressonancia(x,Y,y)

    ax.plot(x,Y,'-o')
    fig.show()

def plot_bg(ax,list_bg,unidade,exp = 1e9,
            color = 'yellow',alpha = 0.5,**args):
    #converter para comprimento de onda
    for bg in list_bg:
        l1 = u2lambda(bg[0],unidade)*exp
        l2 = u2lambda(bg[1],unidade)*exp
        ax.fill_between([l1,l2],1,0,color = color,
                        alpha = alpha,
                        **args)


class fiting2:
    def __init__ (self,x,y,funcao = 'alfa*X**2 + beta',
                  chutes = None,aplica = True,
                  escalax = 'linear',
                  escalay = 'linear',
                  offset = None,
                  **kwargs):
        
        self.offset = offset
        self.kwargs = kwargs
        import funcoes as fc
        if escalax == 'linear':
            self.x = np.array(x)
        elif escalay == 'log':
            self.x = np.log(self.lx)
        if escalay == 'linear':
            self.y = y
        elif escalay == 'log':
            self.y = np.log(self.y)
            
        self.chutes = chutes
        self.string = funcao

        self.escalax = escalax
        self.escalay = escalay
        
        if type(funcao) != str:

            self.funcao = funcao
            from inspect import getfullargspec
            self.parametros = getfullargspec(self.funcao).args[1:]
            self.funcao_latex = '$y(x) = $'
            
        else:
            
            if funcao.split()[0] == 'FUNCAO':
                    self.funcao = globals()[funcao.split()[-1]]
                    from inspect import getfullargspec
                    self.parametros = getfullargspec(self.funcao).args[1:]
                    self.funcao_latex = '$y(x) = $'
            else:
                if funcao in dir(fc):
                
                    self.funcao = fc.__dict__[funcao]
                    from inspect import getfullargspec
                    self.parametros = getfullargspec(self.funcao).args[1:]


                    if '%s_string'%funcao in fc.__dict__:
                        self.funcao_latex = fc.__dict__['%s_string'%funcao]
                    else:
                        self.funcao_latex = '$y(x) = $'
                    
                else:
                    self.separa_parametros()
                    #print(self.parametros)
                    self.f = self.cria_funcao()
                    exec(self.cria_funcao())
                    self.funcao = locals()['___funcao___fiting___']
                    self.funcao_latex = '$y(x) = $%s'%str2latex(funcao).final


        
        if aplica == True:
            self.fit()

    def exporta_dados(self,nome):
        nome = ajusta_nome(nome)
        s = 'parâmetro\tvalor\terro\n'
        for i in range(len(self.parametros)):
            v = self.resultados[i]
            s += '\t'.join([self.parametros[i],str(v.valor),str(v.erro)]) + '\n'
        if self.offset != None:
            s += '\t'.join(['offset',str(self.offset),str(0)])
            

        arq = open(nome,'w')
        arq.write(s)
        arq.close()

    def fit(self,**args):
        if args == {}:
            kargs = self.kwargs
        else:
            kargs = args
        print(kargs)
        from scipy.optimize import curve_fit
        self.lista_resultados, erros = curve_fit(self.funcao,
                                               self.x,self.y,
                                                 self.chutes,**kargs)
        
        self.lista_erros = np.sqrt(np.diag(erros))
        self.resultados = []
        for i in range(len(self.lista_resultados)):
            self.resultados.append(ne(self.lista_resultados[i],
                                      self.lista_erros[i]))

    def cria_funcao(self):
        #print(self.parametros)
        s = 'def ___funcao___fiting___(X,'
        for i in self.parametros:
            s += '%s,'%i
        s = s.strip()
        s += '):'
        s += '\n\t return %s'%self.string
        #print(s)
        return s

    def funcao_fitada(self):
        args = [i.valor for i in self.resultados]
        
        def f(x):
            return self.funcao(x,*args)

        return f


    def separa_parametros(self):
        import funcoes
        lista_funcoes = dir(funcoes)
        parametros = []
        numeros = '1234567890.'
        l = self.string.replace(')','').split('(')
        for i in l:
            i = i.replace('*','+').replace('-','+').replace('/','+')
            i = i.replace('**','+').replace(' ','').replace('X','').split('+')
            for par in i:
                if par != '' and par not in lista_funcoes and par not in numeros:

                    #testar se o parametro nao e um numero
                    for num in par:
                        if num not in numeros and par not in parametros: #nao e numero
                            parametros.append(par)
                            break
                        else: #se for numero nao e adicionado na lista
                            pass
        
        self.parametros = parametros
        
        #print(parametros)
    def cria_legenda(self,leg = '',funcao = False,
                     simbolos = True,unidades = None):
        '''sibols = None - nada; simbolos = True - usa os parametros,
            se for lista usa a lista'''

        if simbolos == None:
            simbolos = [None for i in self.parametros]
        if simbolos == True:
            simbolos = self.parametros
        if leg == '':
            self.legenda = ''
            n = 0
            for i in self.resultados:
                i.simbolo = simbolos[n]; n += 1
                self.legenda += i.legenda(simbolo = True) + '\n'
                #print(i.legenda(),i.legenda(simbolo = True),i.valor)
                
            if funcao == True:
                self.legenda += self.funcao_latex
            self.legenda = self.legenda.strip('\n')
        
        #print(self.legenda)    
        return self.legenda

    def plot(self,ax,legenda = True,lim1 = None,lim2 = None,
             resolucao = 1000,**kwargs):
        #p.plot(self.x,self.y,tipo = 'o')
        import funcoes as fc
        if legenda == True:
            legenda = self.cria_legenda()
        if lim1 == None:
            lim1 = min(self.x)
        if lim2 == None:
            lim2 = max(self.x)
        x = np.linspace(lim1,lim2,resolucao)
        if self.escalay == 'log':
            y = np.exp(self.funcao(y,*self.lista_resultados))
        if self.escalay == 'linear':
            try:
                y = self.funcao(y,*self.lista_resultados)
            except Exception as ex:
                '''nao foi possivel aplicar funcao na arrau
                fiting2 - l4049'''
                y = [self.funcao(i,*self.lista_resultados) for i in x]
        if self.escalax == 'log':
            x = np.exp(x)
        if self.escalax == 'linaer':
            x = x
        ax.plot(x,y,'--',label = legenda,
               color = 'black',**kwargs)

    def add_legenda(self,p,**kwargs):
        self.cria_legenda(**kwargs)
        p.set_legenda(self.legenda)


    def salva_antigo(self,line,*args):

        dic = {}
        dic['par'] = {}
        dic['string'] = self.string
        dic['escalax'] = self.escalax
        dic['escalay'] = self.escalay

        n = 0
        for i in self.parametros:
            
            dic['par'][i] = {}
            
            
            dic['par'][i]['chutes'] = self.resultados[n].valor
            dic['par'][i]['bounds'] = (0.5*self.resultados[n].valor,
                                       1.5*self.resultados[n].valor)
            
            n += 1
            
        dic['resultados'] = [(i.valor,i.erro) for i in self.resultados]
           
           
        if 'lista_fits' not in line.__dict__:
                line.lista_fits = [dic]
        else:
            line.lista_fits.append(dic)

def separa_picos(x,y,picos):
    
    idx = np.argsort(x)
    x = np.array(x)[idx]
    y = np.array(y)[idx]

    picos_idx = busca(x,picos)
    
    meios = picos_idx[:-1] + (picos_idx[1:] - picos_idx[:-1])/2
    esquerda = np.append([0] , meios)
    direita = np.append(meios , [len(x)])
    
    return esquerda.astype('int'),direita.astype('int')

def estima_fwhm(x,y,picos):
    esquerda,direita = separa_picos(x,y,picos)
    lfwhm = []
    picos_idx = busca(x,picos)
    lista_x = []
    lista_y = []
    lmeio = []
    from scipy.interpolate import interp1d
    for i in range(len(picos)):
        X = np.array(x[esquerda[i]:direita[i]])
        Y = np.array(y[esquerda[i]:direita[i]])
        func = interp1d(X,Y)
        pico = y[picos_idx[i]]
        if pico > np.mean(Y):
            meio = min(Y) + (pico - min(Y))/2
        else:
            meio = max(Y) - (max(Y)-pico)/2
        bm1 = X < X[int(len(X)/2)]
        bm2 = X > X[int(len(X)/2)]
        x1 = X[bm1][busca(Y[bm1],meio)]
        x2 = X[bm2][busca(Y[bm2],meio)]

        lfwhm.append((x1,x2))
        lista_x.append(X)
        lista_y.append(Y)
        lmeio.append(meio)
    return lfwhm,lmeio,lista_x,lista_y,picos_idx


def teste_estima_fwhm():
    df = read_a0('/home/filipe/Dropbox/Usp_2021_1/dd/simulacoes_filipe/ressonador_py/Ressonadores/analise_artigo_go/dados_artigo_nat/teste_1')
    
    picos = read_a0('/home/filipe/Dropbox/Usp_2021_1/dd/simulacoes_filipe/ressonador_py/Ressonadores/analise_artigo_go/dados_artigo_nat/picos')[0]
    fwhm,meio,X,Y,picos_idx = estima_fwhm(df[0],df[1],picos.values)


##    fig,ax = plt.subplots()
##    for i in range(len(X)):
##        ax.plot(X[i],Y[i])
##        ax.plot(list(fwhm[i]),[meio[i],meio[i]],'o')
##    fig.show()


def fit_individuais(x,y,picos,y0,funcao = 'lorentziana',df = None,
                    bounds = [0.1,10,0.5,500,0.3]):
    '''bounds:  x0 +- bounds_x0
                sigma 0 - bounds sigma
                i0: i0 +- bounds
                alfa: alfa +- bounds
                y0: +- bounds'''

    
    fwhm,meio,X,Y,picos_idx = estima_fwhm(x,y,picos)
    list_idx = []
    
    if df is None:
        df = pd.DataFrame(columns = ['u','u_err','sigma','sigma_err','intensidade','intensidade_err',
                                      'alfa_assimetria','alfa_assimetria_err',
                                     'y0','y0_err'])

    if funcao == 'lorentziana':
        func = lambda lda,X0,f,i0,a,y0: y0 + lorentziana_assimetrica(lda,X0,f,i0,a)

    for i in range(len(X)):
        fw = abs(fwhm[i][0] - abs(fwhm[i][1]))
        alfa = 0
        x0 = picos[i]
        xi,yi = X[i],Y[i]
        i0 = y[picos_idx[i]]-1
        from scipy.optimize import curve_fit


        
        try:
            #print(len(y))
            
            res, erros = curve_fit(func,xi,yi,p0 = [x0,fw,i0,alfa,y0],
                               bounds = [[x0-bounds[0], #x0
                                          0,            #fw 
                                          i0 - bounds[2],#i0 
                                          alfa - bounds[3],      #alfa
                                          y0 - bounds[4]],         #y0
                                         [x0+bounds[0], #x0
                                          fw + bounds[1],    #fw
                                          i0 + bounds[2],#i0
                                          alfa + bounds[3],       #lfa
                                          y0 + bounds[4]]])        #y0
            erros = np.sqrt(np.diag(erros))
            
            if len(df.index) == 0:
                idx = 0
            else:
                idx = max(df.index)
            list_idx.append(idx)
            df.loc[idx+1,'u'] = res[0]; df.loc[idx+1,'u_err'] = erros[0]
            df.loc[idx+1,'sigma'] = res[1]; df.loc[idx+1,'sigma_err'] = erros[1]
            df.loc[idx+1,'intensidade'] = res[2]; df.loc[idx+1,'intensidade_err'] = erros[2]
            df.loc[idx+1,'alfa_assimetria'] = res[3]; df.loc[idx+1,'alfa_assimetria_err'] = erros[3]
            df.loc[idx+1,'y0'] = res[4]; df.loc[idx+1,'y0_err'] = erros[4]
            
        except Exception as ex:
            print('erro',ex)
    return df,X,Y,func

def plot_fits_individuais(df,X,Y,func,ax = None):

    llines = []
    if ax is None:
        fig,ax = plt.subplots()
    for i in range(len(X)):
        l = ax.plot(X[i],Y[i])[0]
        llines.append(l)
    for i in df.index:
        x0 = df.loc[i,'u']
        sigma = df.loc[i,'sigma']
        intens = df.loc[i,'intensidade']
        alfa = df.loc[i,'alfa_assimetria']
        y0 = df.loc[i,'y0']

        x = np.linspace(x0 - 3*sigma,x0 + 3*sigma,1000)
        l = ax.plot(x,func(x,x0,sigma,intens,alfa,y0),'--',color = 'black')[0]
        llines.append(l)
    
    return llines


def fit_curva_df(x,y,df,funcao,
                  off_set = None, y0 = None,regulariza = False,
               tol_nu0 = 5,tol_sigma = 10,
              tol_intensidade = np.inf,tol_y0 = np.inf,
              tol_alfa_assimetria = np.inf,
              arruma_sinal = True,retorna_func = False
                 ,**kargs):
    


    return fit_curva(x,y,df['u'].values,df['sigma'].values,
                    df['intensidade'].values,funcao = funcao,
                     inicio = None, fim = None,
              off_set = off_set, y0 = y0, regulariza = regulariza,
           tol_nu0 = tol_nu0,tol_sigma = tol_sigma,
          tol_intensidade = tol_intensidade,tol_y0 = tol_y0,
          alfa_assimetria = df['alfa_assimetria'].values,
                     tol_alfa_assimetria = tol_alfa_assimetria,
          arruma_sinal = arruma_sinal,retorna_func = retorna_func,
          individuais = False,**kargs)

def derivada_3pontos(x,y):
    #(f(x + h) - f(x - h))/2
    y = np.array(y)
    h = np.diff(x).mean()
    der = (y[2:] - y[0:-2])/(2*h)
    return (y[2:] - y[0:-2])/(2*h)

def derivada2_3pontos(x,y):
    #(f(x + h) = 2f(x) - f(x - h))/h^2
    y = np.array(y)
    h = np.diff(x).mean()
    return (y[2:]  -2*y[1:-1] + y[0:-2])/(h**2)


#plotar os picos individualmente experimentais e os fits
#fazer a funcao para plotar as curvas convoluidas usando os parâmetros do df como x0 (bounds ainda colocar manual)

##df = read_a0('/home/filipe/Dropbox/Usp_2021_1/dd/simulacoes_filipe/ressonador_py/Ressonadores/analise_artigo_go/dados_artigo_nat/teste_1')
##picos = read_a0('/home/filipe/Dropbox/Usp_2021_1/dd/simulacoes_filipe/ressonador_py/Ressonadores/analise_artigo_go/dados_artigo_nat/picos')[0]
##        
##df,X,Y,func = fit_individuais(df[0],df[1],picos.values,y0 = 1)
##plot_fits_individuais(df,X,Y,func)

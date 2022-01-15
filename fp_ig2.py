#!/home/filipe/anaconda3/bin/python
from scipy.signal import savgol_filter

from kivy.config import Config

Config.set('kivy', 'exit_on_escape', '0')
from funcoes import *
from numpy import nan,array,ndarray,float64,uint8
from time import time
from threading import Thread
import requests
from fp_ig2_tools import *
from kivyplt import *
import pandas as pd
from fp_load import *
from fplot3 import *
from inspect import getfullargspec,signature
import sys
import os
from funcoes import *
#menu para carregar
#abrir quando ja esta carregada
#ig para cada coluna (lugar/botao para selecionar)
#escolher index, colunas, ax
#plotar sempre substituindo. Botao para salvar

#menu for pandas interface



lateral_args = {'size_hint_x':1,'size_hint_y':None,'size':(0,30)}

def group_conteiner(lista):
    dic = {'__none__':[]}
    for i in lista:
        if 'conteiner' in i.__dict__:
            if i.conteiner in dic:
                dic[i.conteiner].append(i)
            else:
                dic[i.conteiner] = [i]
        else:
            dic['__none__'].append(i)
    return dic

def names_lines_conteiners(axes,pai):
    return [i.get_label() for i in axes.lines] + pai.conteiners
        

setattr(pd,'read_comsol',read_comsol)
setattr(pd,'read_a',read_a)
setattr(pd,'read_a0',read_a0)
setattr(pd,'read_c',read_c)


class obj_operations(lateral_menu):
    '''operacoes com lines ou ax'''
    
    def __init__(self,pai,obj = 'line',**args):
        super().__init__(pai,text = '%s operations'%obj,**lateral_args)
        self.lines_selecionadas = []
        self.dic = {}
        self.obj = obj
        
    def funcao1(self,*args):
        self.new_list(True)
        self.pai.bl_lateral.lista.append(Button(text = 'add %s'%self.obj,
                                                on_release = self.add_line,
                                                **lateral_args))
        n = 1
        for line in self.lines_selecionadas:
            self.labelti(self.change_line,
                         'obj%i'%n,line.get_label())
            self.dic['obj%i'%n] = line
            n += 1

        self.labelti(self.exec_func,
                     'execute_function',
                     'obj1')
            
        self.pai.bl_lateral.cria()

    def exec_func(self,*args):
        try:
            
            for i in self.dic:
                ln = self.dic[i]
                locals()[i] = ln
            eval(args[0].text)
            
            self.pai.fig.canvas.draw()
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex) + ',' + str(ex.__traceback__.tb_lineno)        
    
    def add_line(self,*args):
        self.new_list()
        self.pai.bl_lateral.lista.append(botao_deleta(self.funcao1,
                                                      text = 'PRONTO',
                                                      **lateral_args))

        lista = []
        if self.obj == 'line':
            for ax in self.pai.fig.axes:
                for ln in ax.lines:
                    lista.append(ln)
        if self.obj == 'ax':
            for ax in self.pai.fig.axes:
                lista.append(ax)

        for obj in lista:

            bdel = botao_deleta(self.seleciona_line,text = obj.get_label(),
                                                          **lateral_args)
            bdel.line = obj
            self.pai.bl_lateral.lista.append(bdel)
                
        self.pai.bl_lateral.cria()
    
    def seleciona_line(self,*args):
        self.pai.bl_lateral.lista.remove(args[0])
        self.lines_selecionadas.append(args[0].line)
        self.pai.bl_lateral.cria()

    def change_line(self,*args):
        self.lines_selecionadas.remove(self.dic[args[0].label.text])
        self.dic.__delitem__(args[0].label.text)
        self.funcao1()
        
        
    



class line_operations(obj_operations):
    '''eixo x da primeira line selecionada'''
    
    def __init__(self,pai,obj = 'line',**args):
        super().__init__(pai,obj = obj,text = 'line operations',**lateral_args)

        
  
    def exec_func(self,*args):
        try:
            from scipy.interpolate import interp1d
            
            xdata = self.dic['obj1'].get_xdata()
            for i in self.dic:
                ln = self.dic[i]
                interp = interp1d(ln.get_xdata(),ln.get_ydata(),
                                  bounds_error = False)
                locals()[i] = interp(xdata)
            ydata = eval(args[0].text)
            line = self.pai.ax.plot(xdata,ydata)[0]

            label = args[0].text
            for i in self.dic:
                label = label.replace(i,self.dic[i].get_label())
            line.set_label(label)
            
            self.pai.fig.canvas.draw()
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex) + ',' + str(ex.__traceback__.tb_lineno)        
    

class execute_func(lateral_menu):
    def __init__(self,pai,**args):
        super().__init__(pai,text = 'execute func',**lateral_args)

    def funcao1(self,*args):
        self.new_list(True)
        self.func = self.labelti(self.open_menu,'Func name','')
        self.pai.bl_lateral.cria()

    def open_menu(self,*args):
        try:
            func = self.func.text
            self.new_list(True)
            
            #create labels and ti for all args and dfaults for the method
            method = eval(func)
            a = signature(method)
            args = [i for i in a.parameters]
            defaults = [a.parameters[i].default for i in args]
            self.wg_args = []
            
            if len(args) > 0:
                wg = self.labelti(lambda x: None,args[0],args[0])
                self.wg_args.append(wg)
                
            for n in range(1,len(args[1:])+1):
                if args[n] not in ['args','kwargs']:
                    wg = self.labelti(lambda x: None, args[n],
                                  str(defaults[n]))
                    self.wg_args.append(wg)

            self.pai.bl_lateral.lista.append(botao_deleta(self.run_func,
                                                          text = 'Run',**lateral_args))
                
            self.pai.bl_lateral.cria()

        except Exception as ex:
            self.pai.ti_baixo.text = str(ex) + ',' + str(ex.__traceback__.tb_lineno)

        
    def run_func(self,*args):
        args = {}
        for wg in self.wg_args:
            try:
                args[wg.label.text] = eval(wg.text)
            except:
                args[wg.label.text] = wg.text
        
        try:
            eval(self.func.text)(**args)

        except Exception as ex:
            self.pai.ti_baixo.text = str(ex) + ',' + str(ex.__traceback__.tb_lineno)

class add_fill_between(lateral_menu):
    def __init__(self,pai,**args):
        super().__init__(pai,text = 'add fill between',**args)

    def funcao1(self,*args):

        self.new_list(True)
        self.lx = self.labelti(lambda *args: None,'x','')
        self.ly1 = self.labelti(lambda *args: None,'y1','')
        self.ly2 = self.labelti(lambda *args: None,'y2','0')
        self.cor = self.labelti(lambda *args: None,'cor','yellow')
        self.alfa = self.labelti(lambda *args: None,'alpha','0.2')

        self.pai.bl_lateral.lista.append(botao_deleta(self.aplica,text = 'aplica',
                                                      **lateral_args))
        
        self.pai.bl_lateral.cria()

    def aplica(self,*args):
        pontos = []
        try:
            for l in [self.lx,self.ly1,self.ly2]:

                if ',' in l.text:
                    p = [eval(i) for i in l.text.split(',')]
                else:
                    p = [eval(i) for i in l.text.split()]
                pontos.append(p)

            fb = self.pai.ax.fill_between(x = pontos[0],y1 = pontos[1],y2 = pontos[2],
                                          color = self.cor.text,alpha = eval(self.alfa.text))
            self.pai.atualiza()
            
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex) + ',' + str(ex.__traceback__.tb_lineno)


class plot_funcao_menu(lateral_menu):
    def __init__(self,pai,text = 'Funcoes'):
        super().__init__(pai,text = text,
                         **lateral_args)

    def funcao1(self,*args):
        self.new_list(True)
        self.labelti(self.add_func,'f(X,a1,...,an)','a*X + b')

        for line in self.pai.ax.lines:
            if 'plot_funcao' in line.__dict__:
                for pf in line.plot_funcao:
                    plot_funcao_ig(self.pai,pf)

        self.pai.bl_lateral.cria()

    def add_func(self,*args):
        plot_funcao_ig(self.pai,args[0].text).muda_cor()

class plot_funcao_ig(lateral_menu):
    def __init__(self,pai,funcao_dict):
        
        self.funcao_str = funcao_dict if type(funcao_dict) == str else funcao_dict['funcao']
        self.dict = {} if type(funcao_dict) == str else funcao_dict


        super().__init__(pai,text = self.funcao_str,**lateral_args)

    def funcao1(self,*args):
        self.new_list(True)
        self.line_plot = self.pai.ax.plot([],[])[0]
        self.ti_funcao = self.labelti(self.cria_sliders,'f(X,a1,...,an)',self.funcao_str)             

        for i in [('resolucao',10000),('lim1',0),('lim2',1)]:

            #criar chave no dicionario se nao existir
            if i[0] not in self.dict:
                self.dict[i[0]] = i[1]

        self.cria_sliders()
        self.cria_padroes()

        self.pai.bl_lateral.cria()

    def cria_dic_args(self,*args):
        pass

    def cria_padroes(self,*args):
       
        for i in [('resolucao',10000),('lim1',0),('lim2',1)]:

            #criar chave no dicionario se nao existir
            if i[0] not in self.dict:
                self.dict[i[0]] = i[1]

            #criar o labelti com valor padrao se nao existir
            if i[0] + '_ti' not in self.__dict__:
                self.__dict__[i[0] + '_ti'] = self.labelti(self.cria_padroes,i[0],str(i[1]))
            #atualizar o dict com o valor do labelti
            else:
                self.dict[i[0]] = eval(self.__dict__[i[0] + '_ti'].text)

        self.pai.bl_lateral.cria()

        try:
            self.aplica()
        except Exception as ex:
            print(ex)
        
    def cria_sliders(self,*args):

        #remover sliders antigos
        if 'list_sliders' in self.__dict__:
            for s in self.list_sliders:
                self.pai.bl_lateral.lista.remove(s)
        else:
            self.list_sliders = []

        import funcoes as fc
        if self.ti_funcao.text not in fc.__dict__:
            self.funcao,self.args = str2func(self.ti_funcao.text)
        else:
            self.funcao = fc.__dict__[self.ti_funcao.text]
            from inspect import getfullargspec
            self.args = getfullargspec(self.funcao).args[1:]
        #argumentos e limites
        print(self.args,'d')
        if 'arguments' not in self.dict:
            self.dict['arguments'] = {'X':np.linspace(self.dict['lim1'],self.dict['lim2'],self.dict['resolucao'])}
        if 'slider_lims' not in self.dict:
            self.dict['slider_lims'] = {}
        for a in self.args:
            if a not in self.dict['arguments']:
                self.dict['arguments'][a] = 1
                self.dict['lims'] = (-100,100)
            bl = self.labeltislider(chave = a, dic = self.dict['arguments'],funcao = self.aplica,
                                    textolb = a, textoti = str(self.dict['arguments'][a]),
                                    valor = self.dict['arguments'][a],
                                    lim1 = self.dict['lims'][0],lim2 = self.dict['lims'][1])
            self.list_sliders.append(bl)


        #remover argumentos nao usados
        for a in self.dict['arguments'].copy():
            if a not in self.args:
                self.dict['arguments'].__delitem__(a)
        

        print(self.dict['lim2'])
                
              

        self.pai.bl_lateral.cria()
        
    def aplica(self,*args):
        x = np.linspace(self.dict['lim1'],self.dict['lim2'],self.dict['resolucao'])
        y = self.funcao(x,**self.dict['arguments'])
        self.line_plot.set_data(x,y)
        #self.pai.res_zoom()
        self.pai.atualiza()

class fit_funcao_menu(plot_funcao_menu):
    def __init__(self,pai,line,dic = {}):
        super().__init__(pai,text = 'fit funcao')

        self.line = line
        self.dic = dic

    def add_func(self,*args):
        self.pfig = plot_funcao_ig(self.pai,args[0].text)
        self.pfig.muda_cor()

        self.pai.bl_lateral.lista.append(botao_deleta(self.aplica_fit,
                                                      text = 'FIT',
                                                      **lateral_args))

        self.pai.bl_lateral.lista.append(botao_deleta(self.salva_fit,
                                                      text = 'SALVA',
                                                      **lateral_args))
        self.pai.bl_lateral.cria()

    def aplica_fit(self,*args):
        #self.pfig.aplica()
        if 'line_fit' not in self.__dict__:
            self.line_fit = self.pai.ax.plot([],[],'--')[0]
        else:
            self.line_fit.set_data([],[])
            
        x0 = list(self.pfig.dict['arguments'].values())
        bounds1 = []
        bounds2 = []
        for i in self.pfig.list_sliders:
            bounds1.append(i.slider.minimo)
            bounds2.append(i.slider.maximo)
        lim1 = self.pfig.dict['lim1']; lim2 = self.pfig.dict['lim2']

        x,y = seleciona_listas(lim1,lim2,*self.line.get_data())
        from scipy.optimize import curve_fit
        res, erros = curve_fit(self.pfig.funcao,x,y,p0 = x0,
                                            bounds = (bounds1,bounds2))
        err = np.sqrt(np.diag(erros))

        legend = ''
        for i in range(len(res)):
            neo = ne(res[i],err[i])
            legend += list(self.pfig.dict['arguments'].keys())[i] + ' = ' + neo.legenda() + '\n'
        x = np.linspace(lim1,lim2,self.pfig.dict['resolucao'])
        y = self.pfig.funcao(x,*res)
        self.line_fit.set_data(x,y)
        self.line_fit.set_label(legend)
        self.pai.ax.legend()

        self.pai.atualiza()

        #bounds1 = list(self.pfig.dict[

    def salva_fit(self,*args):
        print('asd')
    
class fit_menu(lateral_menu):
    def __init__(self,pai,line):
        super().__init__(pai, text = 'fit',
                         **lateral_args)
        self.line = line
        
    def funcao1(self,*args):
        self.new_list(True)

        self.label('Salvos',**lateral_args)

        if 'fits_curvas' in self.line.__dict__:
            for i in self.line.fits_curvas:
                self.pai.bl_lateral.lista.append(curvas_menu(self.pai,
                                                         self.line,dic = i))

        self.label('curvas',**lateral_args)
        
        self.pai.bl_lateral.lista.append(curvas_menu(self.pai,
                                                     self.line,'lorentziana'))
        self.pai.bl_lateral.lista.append(curvas_menu(self.pai,
                                                     self.line,'gaussiana'))

        self.pai.bl_lateral.lista.append(fit_funcao_menu(self.pai,self.line))
        
        self.pai.bl_lateral.cria()


class curvas_menu(lateral_menu):
    def __init__(self,pai,line,funcao = 'lorentziana',
                 dic = {}):
        super().__init__(pai, text = funcao,
                         **lateral_args)
        self.line = line
        self.__funcao__ = funcao
        self.dic = dic
        

        
    def funcao1(self,*args):
        self.new_list(True)

        self.carrega()
        self.pai.fix_ax = True
        self.pai.double_click = False
        self.desfazer = True
        self.salvo = False

        #sinal
        self.ti_sinal = self.labelti(lambda x: x,'sinal (1 ou -1)',
        '-1' if 'sinal' not in self.dic else self.dic['sinal'])
        #automatico
        self.labelti(self.automatico,'auto',
        '0.1' if 'auto' not in self.dic else self.dic['auto'])
        
        #tol. nu0 (para mais ou menos do valor central)
        self.ti_tolnu0,self.ti_tolsigma  = self.labelti_cols(lambda x: x,['tol. nu0','tol. sigma'],
        ['1' if 'tol_nu0' not in self.dic else self.dic['tol_nu0'],
         '1' if 'tol_sigma' not in self.dic else self.dic['tol_sigma']])
        
        #off set #tol y0
        
        self.ti_tolintensidade,self.nada = self.labelti_cols(lambda x: x,
                                        ['tol. intensidade',''],
        ['100' if 'tol_intensidade' not in self.dic else self.dic['tol_intensidade'],
         '' if '' not in self.dic else ''])

        #y0
        self.ti_y0,self.ti_toly0 = self.labelti_cols(lambda x: x,
                                        ['y0','tol_y0'],
        ['0' if 'y0' not in self.dic else self.dic['y0'],
         '0' if 'tol_y0' not in self.dic else self.dic['tol_y0']])
        
       
        
        #alfa
        self.ti_alfa_assimetria,self.ti_tol_alfa_assimetria = self.labelti_cols(lambda x: x,
                                        ['alfa ass.','tol alfa'],
        ['0' if 'alfa_assimetria' not in self.dic else self.dic['alfa_assimetria'],
         '0' if 'tol_alfa_assimetria' not in self.dic else self.dic['tol_alfa_assimetria']])
        
        #offset
        self.ti_offset,self.ti_toloffset = self.labelti_cols(lambda x: x,
                                    ['offset','tol_offset'],
        ['0' if 'offset' not in self.dic else self.dic['offset'],
        '0' if 'tol_offset' not in self.dic else self.dic['tol_offset']])
        #regulariza: Se regulariza a line antes de fitar

        self.ti_plotlim1,self.ti_plotlim2 = self.labelti_cols(self.plot,
                                    ['plot lim1','plot lim2'],
        ['%s'%min(self.line.get_xdata()) if 'plot_lim1' not in self.dic else self.dic['plot_lim1'],
         '%s'%max(self.line.get_xdata()) if 'plot_lim2' not in self.dic else self.dic['plot_lim2']])


        self.ti_simbolox,self.ti_unidadex = self.labelti_cols(self.plot,
                                    ['simbolo x','unidade x'],
        ['x' if 'simbolo x' not in self.dic else self.dic['simbolo x'],
         '' if 'unidade x' not in self.dic else self.dic['unidade x']])
                                                              
        self.ti_simboloy,self.ti_unidadey = self.labelti_cols(self.plot,
                                    ['simbolo y','unidade y'],
        ['y' if 'simbolo y' not in self.dic else self.dic['simbolo y'],
         '' if 'unidade y' not in self.dic else self.dic['unidade y']])
        

        self.ti_resolucao = self.labelti(self.plot,'resolucao',
        '10000' if 'resolucao' not in self.dic else self.dic['resolucao'])
    

        #insere manualmente
        self.pai.bl_lateral.lista.append(add_points(self.pai,
                                                    self.line_centro,
                                         text = 'picos',
                                         desfazer_double_click = False))
        #fwhm
        self.pai.bl_lateral.lista.append(add_points(self.pai,
                                                    self.line_fwhm,
                                         text = 'fwhm',
                                         desfazer_double_click = False))
        #limites
        self.pai.bl_lateral.lista.append(add_points(self.pai,
                                                    self.line_limites,
                                         text = 'limites',
                                         max_points = 2,
                                         desfazer_double_click = False))

        #aplica
        self.pai.bl_lateral.lista.append(Button(text = 'FIT',
                                                on_release = self.aplica,
                                                size_hint_y = None,
                                                size = (0,50)))

        self.pai.bl_lateral.lista.append(botao_deleta(self.fit_individuais,
                                                      text = 'FIT individuais',
                                                      size_hint_y = None,
                                                      size = (0,50)))

        self.pai.bl_lateral.lista.append(botao_deleta(self.fit_df,
                                                      text = 'FIT df',
                                                      size_hint_y = None,
                                                      size = (0,50)))

        self.pai.bl_lateral.lista.append(botao_deleta(self.salva,
                                                text = 'SALVA',
                                                size_hint_y = None,
                                                size = (0,50)))

        self.pai.bl_lateral.lista.append(botao_deleta(self.acumula_df,
                                                text = 'Acumula df',
                                                size_hint_y = None,
                                                size = (0,50)))

        self.nome_df = self.labelti(self.salva_dict,'salva dict','df_fit')
        #limites plot e resolucao
        self.pai.bl_lateral.cria()

    def acumula_df(self,*args):
        if 'df_res' not in self.__dict__:
            #return 'não existe o df'
            if 'df_acumulado' not in self.__dict__:
                try:
                    self.df_acumulado = pd.read_pickle(self.nome_df.text + '_acumulado')
                except:
                    return
        else:
            if 'df_acumulado' not in self.__dict__:
                try:
                    self.df_acumulado = pd.read_pickle(self.nome_df.text + '_acumulado')

                    self.df_acumulado = pd.concat([self.df_res,self.df_acumulado],
                                                  ignore_index = True).replace(np.nan,0)
                except:
                    self.df_acumulado = self.df_res.copy()
            else:
                self.df_acumulado = pd.concat([self.df_res,self.df_acumulado],
                                              ignore_index = True).replace(np.nan,0)

        pd.to_pickle(self.df_acumulado,self.nome_df.text + '_acumulado')
        self.salva()
        print(self.df_acumulado)

    def salva_dict(self,*args):
        if 'df_res' not in self.__dict__:
            return 'não existe o dict'
        else:
            self.pai.add_df(self.df_res,args[0].text)

    def fit_individuais(self,*args):
        x,y = self.line.get_data()

        limites = self.line_limites.get_xdata()
        if len(limites) == 2:
            ind1 = busca(x,min(limites))
            ind2 = busca(x,max(limites))
            self.ti_plotlim1.text = str(min(limites))
            self.ti_plotlim2.text = str(max(limites))
        else:
            ind1 = None; ind2 = None

        x = x[ind1:ind2]
        y = y[ind1:ind2]
        
        picos = np.array(self.line_centro.get_xdata())
        funcao = self.__funcao__
        df = None
        y0 = eval(self.ti_offset.text.split('=')[-1])
        #bounds

        tol_nu0 = eval(self.ti_tolnu0.text)
        tol_sigma = eval(self.ti_tolsigma.text)
        tol_y0 = eval(self.ti_toly0.text)
        tol_intensidade = eval(self.ti_tolintensidade.text)
        tol_alfa = eval(self.ti_tol_alfa_assimetria.text)

        self.df_res,X,Y,func = fit_individuais(x,y,picos,y0,funcao,df,
                                      bounds = [tol_nu0,
                                                tol_sigma,
                                                tol_intensidade,
                                                tol_alfa,
                                                tol_y0])


        if 'lines_individuais' in self.__dict__:
            for i in self.lines_individuais:
                i.remove()
        
        self.lines_individuais = plot_fits_individuais(self.df_res,X,Y,func,ax = self.line.axes)
        self.line.axes.figure.canvas.draw()

    def fit_df(self,*args):
        if 'df_acumulado' not in self.__dict__:
            self.pai.ti_baixo.text = 'nao existe df_acumulado'
            return
        try:
            print('fit df')
            x,y = self.line.get_data()
            
            container_name = new_name_func(self.line.get_label() + '_fit_' + self.__funcao__[:5],
                          names_lines_conteiners(self.line.axes,self.pai))
            
            limites = self.line_limites.get_xdata()
            if len(limites) == 2:
                ind1 = busca(x,min(limites))
                ind2 = busca(x,max(limites))
                self.ti_plotlim1.text = str(min(limites))
                self.ti_plotlim2.text = str(max(limites))
            else:
                ind1 = None; ind2 = None

            tol_alfa_assimetria = eval(self.ti_tol_alfa_assimetria.text)
            
            
            if 'y0' not in self.ti_offset.text:
                y0 = None
                if self.ti_offset.text == 'zera':
                    if eval(self.ti_sinal.text) == -1:
                        offset = max(y)
                    else:
                        offset = min(y)
                else:
                    offset = eval(self.ti_offset.text)                
                
            else:
                offset = None
                

            res,err,parametros,func,y0,df = fit_curva_df(x[ind1:ind2],y[ind1:ind2],
                      df = self.df_acumulado,
                      funcao = self.__funcao__,
                      off_set = offset, y0 = y0, regulariza = eval(self.ti_regulariza.text),
                      tol_nu0 = eval(self.ti_tolnu0.text),
                      tol_sigma = eval(self.ti_tolsigma.text),
                      tol_y0 = eval(self.ti_toly0.text),
                      tol_intensidade = eval(self.ti_tolintensidade.text),
                      tol_alfa_assimetria = tol_alfa_assimetria)

            self.df_res = df
            self.res = res; self.err = err
            self.container_name = container_name
            
            self.parametros = parametros
            self.func = func
            if self.ti_alfa_assimetria.text == '0':
                self.ti_alfa_assimetria.text = '1'
            self.plot()

        except Exception as ex:
            print(ex)  

    def aplica(self,*args):
        try:
            print('Aplica')
            x,y = self.line.get_data()
            
            container_name = new_name_func(self.line.get_label() + '_fit_' + self.__funcao__[:5],
                          names_lines_conteiners(self.line.axes,self.pai))
            
            limites = self.line_limites.get_xdata()
            if len(limites) == 2:
                ind1 = busca(x,min(limites))
                ind2 = busca(x,max(limites))
                self.ti_plotlim1.text = str(min(limites))
                self.ti_plotlim2.text = str(max(limites))
            else:
                ind1 = None; ind2 = None


            offset = eval(self.ti_offset.text)
            y0 = eval(self.ti_y0.text)

            M = np.sort(self.line_fwhm.get_xdata())
            M = M.reshape((int(len(M)/2),2)).T
            
            fwhm = abs(M[1]-M[0])
            print(np.sort(self.line_fwhm.get_xdata()),M[0],M[1])
            print(fwhm)
            sinal = eval(self.ti_sinal.text)
            intensidade = np.array(self.line_centro.get_ydata()) + sinal*offset
            
            alfa_assimetria = eval(self.ti_alfa_assimetria.text)
            tol_alfa_assimetria = eval(self.ti_tol_alfa_assimetria.text)
            
            x0 = self.line_centro.get_xdata()

            res,err,df = fit_curva(x[ind1:ind2],y[ind1:ind2],
                      x0 = x0,
                      fwhm = fwhm,
                      intensidade = intensidade,
                      y0 = y0,
                      alfa_assimetria = alfa_assimetria,
                      offset = offset,  
                      tol_x0 = eval(self.ti_tolnu0.text),
                      tol_fwhm = eval(self.ti_tolsigma.text),
                      tol_intensidade = eval(self.ti_tolintensidade.text),
                      tol_y0 = eval(self.ti_toly0.text),
                      tol_alfa_assimetria = tol_alfa_assimetria,
                      tol_offset = eval(self.ti_toloffset.text),
                      funcao = self.__funcao__)

            self.df_res = df
            self.res = res; self.err = err
            self.container_name = container_name

            self.plot()

        except Exception as ex:
            print(ex)

    def plot(self,*args):

        #abrir o container e deletar no container
        if 'container_name' not in self.__dict__:
            return
        dic = group_conteiner(self.line.axes.lines)
        if self.container_name in dic:
            for l in dic[self.container_name]:
                if 'nome_fit' in l.__dict__ and l.nome_fit == self.container_name:
                    l.remove()


        if eval(self.ti_alfa_assimetria.text) == 0:
            alfa_plt = False
        else:
            alfa_plt = True
                
        self.list_lines = plot_fit_curvas(self.df_res,ax = self.line.axes,lim1 = eval(self.ti_plotlim1.text),
                        lim2 = eval(self.ti_plotlim2.text), resolucao = eval(self.ti_resolucao.text),
                            simbolox = self.ti_simbolox.text,simboloy = self.ti_simboloy.text,
                            unidadex = self.ti_unidadex.text,unidadey = self.ti_unidadey.text)
        for l in self.list_lines:
            l.conteiner = self.container_name
            l.nome_fit = self.container_name

        if 'resolucao' in self.dic:
            self.salva(append = True)
        
        self.pai.atualiza()
        
    def salva(self,*args,append = False):
        if 'res' not in self.__dict__:
            return
        dic = {}
        dic['funcao'] = self.__funcao__
        dic['line_centro'] = self.line_centro.get_data()
        dic['line_fwhm'] = self.line_fwhm.get_data()
        dic['line_limites'] = self.line_limites.get_data()
        dic['resolucao'] = self.ti_resolucao.text
        dic['plot_lim1'] = self.ti_plotlim1.text
        dic['plot_lim2'] = self.ti_plotlim2.text
        dic['resultados'] = self.res
        dic['erros'] = self.err
        dic['parametros'] = self.parametros
        dic['sinal'] = self.ti_sinal.text
        dic['tol_sigma'] = self.ti_tolsigma.text
        dic['tol_nu0'] = self.ti_tolnu0.text
        dic['offset'] = self.ti_offset.text
        dic['tol_offset'] = self.ti_offset.text
        dic['tol_y0'] = self.ti_toly0.text
        dic['tol_intensidade'] = self.ti_tolintensidade.text
        dic['conteiner'] = self.container_name
        dic['simbolo x'] = self.ti_simbolox.text
        dic['unidade x'] = self.ti_unidadex.text
        dic['simbolo y'] = self.ti_simboloy.text
        dic['unidade y'] = self.ti_unidadey.text
        dic['df_res'] = self.df_res
        dic['alfa_assimetria'] = self.ti_alfa_assimetria.text
        dic['tol_alfa_assimetria'] = self.ti_tol_alfa_assimetria.text

        if append == True:
            self.line.fits_curvas.remove(self.dic)
            self.dic = dic.copy()
            self.line.fits_curvas.append(self.dic)
            return

        if 'fits_curvas' not in self.line.__dict__:
            self.line.fits_curvas = [dic]
        else:
            self.line.fits_curvas.append(dic)

        self.salvo = True
        self.pai.conteiners.append(self.container_name)

    def automatico(self,*args):

        try:
            from scipy.signal import find_peaks,find_peaks_cwt,peak_prominences,peak_widths
            x,y = self.line.get_data()
       
            
            limites = self.line_limites.get_xdata()
            if len(limites) == 2:
                ind1 = busca(x,min(limites))
                ind2 = busca(x,max(limites))
            else:
                ind1 = None; ind2 = None
            x = x[ind1:ind2]; y = y[ind1:ind2]
    
            sinal = eval(self.ti_sinal.text)
            p1 = find_peaks(sinal*y,prominence = eval(args[0].text))[0]
        
            self.line_centro.set_data(x[p1],y[p1])

            
            prom = peak_prominences(sinal*y,p1)
            fwhm,heighs,left,right = peak_widths(sinal*y,p1,prominence_data = prom)
            M = x[np.array([left.astype('int'),right.astype('int')])]
            self.FWHM = M
            self.line_fwhm.set_data(M.flatten(),sinal*np.array([heighs,heighs]).flatten())
            #tol fwhm 10x
            tol_fwhm = max(abs(M[0]-M[1]))*10
            #tol intensidade 10x
            tol_int = 10*max(self.line_centro.get_ydata())
            #tol x0 (2 x fwhm)
            tol_x0 = tol_fwhm/5

            self.ti_tolsigma.text = str(tol_fwhm)
            self.ti_tolintensidade.text = str(tol_int)
            self.ti_tolnu0.text = str(tol_x0)
            
            self.pai.atualiza()
                
        except Exception as ex:
            print(ex,' automatico - fit')
        
    def carrega(self,*args):
        ax = self.line.axes
        self.line_centro = ax.plot([],[],'o',color = 'black')[0]
        self.line_fwhm = ax.plot([],[],'o',color = 'purple')[0]
        self.line_limites = ax.plot([],[],'o',color = 'blue')[0]

        if 'line_centro' in self.dic:
            self.line_centro.set_data(self.dic['line_centro'])
        if 'line_fwhm' in self.dic:
            self.line_fwhm.set_data(self.dic['line_fwhm'])
        if 'line_limites' in self.dic:
            self.line_limites.set_data(self.dic['line_limites'])

        dic = self.dic
        if 'funcao' in dic:
            self.__funcao__ = dic['funcao']
            x,y = self.line.get_data()

            if 'y0' not in dic['offset']:
                y0 = None
                if dic['offset'] == 'zera':
                    if eval(dic['sinal']) == -1:
                        offset = max(y)
                    else:
                        offset = min(y)
                else:
                    offset = eval(dic['offset'])

            else:
                offset = None
                y0 = eval(dic['offset'].split('=')[-1])
            
            self.func = fit_curva(x,y,dic['line_centro'][0],
                                  dic['line_fwhm'],dic['line_centro'][1],
                                  dic['funcao'],
                                  off_set = offset, y0 = y0,
                  retorna_func = True)

            self.res = dic['resultados']
            self.err = dic['erros'] 
            self.parametros = dic['parametros']

            self.container_name = self.dic['conteiner']

            if 'df_res' in dic:
                self.df_res = dic['df_res']
        self.pai.atualiza()
            
    def funcao_desfazer(self):

        self.pai.fix_ax = False
        self.pai.double_click = True
        try:
            self.line_centro.remove()
            self.line_fwhm.remove()
            self.line_limites.remove()
            if self.salvo == True or self.dic != {}:
                self.pai.atualiza()
                return
            if 'list_lines' in self.__dict__:
                for i in self.list_lines:
                    i.remove()

            if 'container_name' in self.__dict__ and self.container_name in self.pai.conteiners:
                self.pai.conteiners.remove(self.container_name)
            legend(self.line.axes)


            if 'lines_individuais' in self.__dict__:
                for i in self.lines_individuais:
                    i.remove()
        

            self.pai.atualiza()
            
        except Exception as ex:
            print(ex)


class fill_between_menu(lateral_menu):
    def __init__(self,pai,ax):
        super().__init__(pai, text = 'fill between (polly col.)',
                         **lateral_args)

        self.ax = ax

    def funcao1(self,*args):
        self.new_list(True)

        for pc in self.ax.collections:
            self.pai.bl_lateral.lista.append(fill_between_ig(self.pai,pc))

        self.pai.bl_lateral.cria()

class fill_between_ig(lateral_menu):
    def __init__(self,pai,obj):
        super().__init__(pai,text = obj.get_label(),**lateral_args)
        self.obj = obj

    def funcao1(self,*args):
        self.new_list(True)
        self.labelti_attr(self.obj,'obj.')
        self.add_methods(self.obj,polycollection_load_list)
        self.pai.bl_lateral.cria()
        
class imagens_menu(lateral_menu):
    def __init__(self,pai,ax):
        super().__init__(pai, text = 'imagens',
                         **lateral_args)
        self.ax = ax
    def funcao1(self,*args):
        self.new_list(True)

        self.labelti(self.load_img,'load img', '')
        for img in self.ax.images:
            self.pai.bl_lateral.lista.append(image_ig(self.pai,img))
        self.pai.bl_lateral.cria()

    def load_img(self,*args):
        try:
            load_img(args[0].text,self.ax)
            self.funcao1()
            self.funcao2()
            self.pai.atualiza()
        except Exception as ex:
            print(ex)
        
class image_ig(lateral_menu):
    def __init__(self,pai,image,**args):
        super().__init__(pai,**lateral_args)
        self.text = image.get_label()
        self.image = image
        self.__regua = False
        self.desfazer = True
        self.pai.fix_ax = True
        if 'unidade' not in self.image.__dict__:
            self.image.unidade = 1

        self.list_lines = []
        self.list_texts = []
        
    def funcao1(self,*args):
        self.new_list(True)
        self.labelti_attr(self.image,'image.')
        self.pai.bl_lateral.lista.append(methods_ig(self.pai,self.image,img_load_list))

        self.bregua = lateral_menu(self.pai,text = 'regua',**lateral_args)
        self.bregua.funcao1 = self.regua1
        self.bregua.funcao2 = self.regua2
        self.pai.bl_lateral.lista.append(self.bregua)
        self.labelti(self.set_unidade,'unidade',str(self.image.unidade))

        self.bdistancia = lateral_menu(self.pai,text = 'dist',**lateral_args)
        self.bdistancia.funcao1 = self.dist1
        self.bdistancia.funcao2 = self.regua2
        self.pai.bl_lateral.lista.append(self.bdistancia)

        #rotacao da imagem
        self.labelti(self.rotate,'rotate (deg)',
        str(self.image.rotate_angle) if 'rotate_angle' in self.image.__dict__ else '0')

        self.tivline = self.labelti(self.vline,'add vline','')
        self.tihline = self.labelti(self.hline,'add hline','')
        
        
        self.b_plot_perfil_vertical = botao_deleta(self.plot_perfil_vertical,
                                                   text = 'plot perfil vertical',
                                                   **lateral_args)
        self.pai.bl_lateral.lista.append(self.b_plot_perfil_vertical)
        
        self.pai.bl_lateral.cria()

    def plot_perfil_vertical(self,*args):
        try:
            x = eval(self.tivline.text)
            M = self.image.get_array()
            l = M[:,x]
            self.pai.ax.plot(l + x,range(len(l)))

            self.pai.atualiza()
            
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)
            
    def vline(self,*args):

        try:
            
            if args[0].text is None or args[0].text == '':
                self.line_vline.remove()
                self.pai.atualiza()
                self.__dict__.__delitem__('line_vline')
                
                return
            
            x = eval(args[0].text)
     
            if 'line_vline' not in self.__dict__:
                self.line_vline = self.pai.ax.plot([],[],'--',color = 'navy')[0]
                
            shape = self.image.get_array().shape
            self.line_vline.set_data([x,x],[0,shape[1]])
            self.pai.atualiza()
            
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)


    def hline(self,*args):

        try:
            if args[0].text is None or args[0].text == '':
                self.__dict__.__delitem__('line_hline')
                self.line_hline.remove()
                self.pai.atualiza()
                
                
                print('line_hline' in self.__dict__)
                print('asdasd')
                
                return            
            y = eval(args[0].text)
   
            if 'line_hline' not in self.__dict__:
                print('oi')
                self.line_hline = self.pai.ax.plot([],[],'--',color = 'navy')[0]
                
            shape = self.image.get_array().shape
            self.line_hline.set_data([0,shape[0]],[y,y])
            self.pai.atualiza()
        
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)
            
    def rotate(self,*args):
        try:
            if 'array_original' not in self.image.__dict__:
                self.image.array_original = self.image.get_array().copy()
            ang = eval(args[0].text)
            ri = Image.fromarray(self.image.array_original).rotate(ang)
            self.image.set_array(ri)
            self.image.rotate_angle = ang
            self.pai.atualiza()
            
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)

    def set_unidade(self,*args):
        try:
            self.image.unidade = eval(args[0].text)
        except Exception as ex:
            print(ex)
        if 'line_regua_name' in self.image.__dict__:
            self.line_regua = get_line(self.image.line_regua_name,self.image.axes)
            self.texto = get_text(self.image.line_regua_name,self.image.axes)
            if self.line_regua == None:
                return
            x1,x2 = self.line_regua.get_xdata()
            y1,y2 = self.line_regua.get_ydata()
            dpixel = ((x2-x1)**2 + (y2-y1)**2)**0.5
            xr1,yr1 = self.image.regua1
            xr2,yr2 = self.image.regua2
            dregua = ((xr2-xr1)**2 + (yr2-yr1)**2)**0.5
            self.texto.set_text(num2e(dpixel*self.image.unidade/dregua))

            self.pai.atualiza()
        
    def dist1(self,*args):
        self.__regua = False
        self.regua(self,*args)

    def regua1(self,*args):
        self.__regua = True
        self.regua(self,*args)

    def regua(self,*args):

        self.pai.double_click = False
        
        self.pai.bl_figura.on_touch_down = self.desce
        self.pai.bl_figura.on_touch_move = self.move
        self.pai.bl_figura.on_touch_up = self.sobe
        
    def regua2(self,*args):
        self.__regua = False
        self.pai.double_click = True
        
        self.pai.bl_figura.on_touch_down = self.pai.on_touch_down
        self.pai.bl_figura.on_touch_move = self.pai.on_touch_move
        self.pai.bl_figura.on_touch_up = self.pai.on_touch_up
        
    def desce(self,*args):
        self.pai.desce(*args)
        if self.__regua == False:
            if args[0].button == 'left':
                self.line_dist = self.image.axes.plot([],[])[0]
                self.line_dist.conteiner = self.image.get_label()
                self.text_dist = self.image.axes.text(1,1,'')
                self.text_dist.conteiner = self.image.get_label()
            else:
                if len(self.list_lines) > 0:
                    self.list_lines[-1].remove()
                    self.list_texts[-1].remove()
                    self.list_lines = self.list_lines[:-1]
                    self.list_texts = self.list_texts[:-1]
                    
                    self.pai.atualiza()
        else:
            if 'line_regua_name' not in self.image.__dict__ or\
               get_line(self.image.line_regua_name,self.image.axes) == None or\
               get_text(self.image.line_regua_name,self.image.axes) == None:

                self.line_regua = self.image.axes.plot([],[])[0]
                self.line_regua.conteiner = self.image.get_label()
                self.texto = self.image.axes.text(1,1,'')
                self.texto.conteiner = self.image.get_label()
                self.image.line_regua_name = new_name_func('_'+self.image.get_label(),
                                                           self.image.axes.lines + self.image.axes.texts)
                self.line_regua.set_label(self.image.line_regua_name)
                self.texto.set_label(self.image.line_regua_name)
            
            else:
                self.line_regua = get_line(self.image.line_regua_name,self.image.axes)
                self.texto = get_text(self.image.line_regua_name,self.image.axes)

    def move(self,*args):
        if args[0].button != 'left':
            return
        if self.__regua == True:
            text = self.texto
            line = self.line_regua
        else:
            text = self.text_dist
            line = self.line_dist
            
        self.pai.move_(*args)
        x1,x2 = self.pai.ptx, self.pai.ptx2
        y1,y2 = self.pai.pty, self.pai.pty2

        theta = rad2grau(-np.arctan2(y2-y1,x2-x1))
        if abs(theta) > 90:
            theta += 180

        if self.__regua == True:
            self.image.regua1 = (x1,y1)
            self.image.regua2 = (x2,y2)

        line.set_data([x1,x2],[y1,y2])
        text.set_x((x2-x1)/2 + x1)
        text.set_y((y2-y1)/2 + y1)

        if 'regua1' not in self.image.__dict__ or 'regua2' not in self.image.__dict__\
           or 'unidade' not in self.image.__dict__:
            dpixel = ((x2-x1)**2 + (y2-y1)**2)**0.5
            text.set_text(num2e(dpixel))
        else:
            dpixel = ((x2-x1)**2 + (y2-y1)**2)**0.5
            xr1,yr1 = self.image.regua1
            xr2,yr2 = self.image.regua2
            dregua = ((xr2-xr1)**2 + (yr2-yr1)**2)**0.5

            
            text.set_text(num2e(dpixel*self.image.unidade/dregua))
        text.set_rotation(theta)

        self.pai.atualiza()    

    def sobe(self,*args):
        
        if self.__regua == False and args[0].button == 'left':
            self.list_lines.append(self.line_dist)
            self.list_texts.append(self.text_dist)


class pandas_menu(lateral_menu):
    def __init__(self,pai,bl):
        super().__init__(pai,bl = bl,
                         text = 'pandas',
                         size_hint_x = None,
                         size_hint_y = 1, size = (50,1))

    def funcao1(self,*args):
        self.new_list()
        self.pai.bl_lateral.lista.append(open_pandas(self.pai))
        for df in self.pai.df_dict:
            self.pai.df_dict[df][0].name = df
            self.pai.bl_lateral.lista.append(df_ig(self.pai,self.pai.df_dict[df],name = df))
        self.pai.bl_lateral.cria()
        
class open_pandas(lateral_menu):
    def __init__(self,pai,file_name = ''):
        super().__init__(pai,text = 'Open',
                         size_hint_x = 1,
                         size_hint_y = None,
                         size = (0,30))
        self.file_name = file_name
        
    def funcao1(self,*args):
        self.new_list()
        #list all possible pandas read functions
        setattr(pd,'read_atodos',self.read_atodos)
        l = [i for i in dir(pd) if 'read_' in i]
        for i in l:
            self.pai.bl_lateral.lista.append(Button(on_release = self.open_menu,
                                                    text = i,
                                                    size_hint_x = 1,
                                                    size_hint_y = None,
                                                    size = (0,30)))

        self.pai.bl_lateral.cria()

    def read_atodos(name = '',comum = '.csv',inicio_data = 0,columns = None, sep = '\t'):
        l = os.listdir()
        for i in l:
            if comum in i:
                print(i)
                df = read_a(i,inicio_data,columns,sep = sep)
                df.name = i
                ig = df_ig(self.pai,df)
                ig.salva()
        return df
                
    def open_menu(self,*args):
        name = args[0].text
        self.new_list()

        self.pai.bl_lateral.lista.append(Button(text = args[0].text,
                                                on_release = self.funcao2,
                                                background_color = [0,0,1,1],
                                                **lateral_args))
        self.pai.bl_lateral.lista.append(Button(text = 'load',
                                               on_release = self.load,
                                               **lateral_args))
        
        #create labels and ti for all args and dfaults for the method
        method = getattr(pd,args[0].text)
        a = signature(method)
        args = [i for i in a.parameters]

        defaults = [a.parameters[i].default for i in args]

        self.wg_args = []
        
        if len(args) > 0:
            wg = self.labelti(lambda x: None,args[0],self.file_name)
            self.wg_args.append(wg)
    
        if len(args) > 1:            
            if str(defaults[1])[0] == '<':
                defaults[1] = '   '
            
        for n in range(1,len(args[1:])+1):
            wg = self.labelti(lambda x: None, args[n],
                          str(defaults[n]))
            self.wg_args.append(wg)

            
        self.pai.bl_lateral.cria()
        self.method = method
        self.method_name = name
        
    def load(self,*args):
        args = {}
        for wg in self.wg_args:
            try:
                args[wg.label.text] = eval(wg.text)
            except:
                args[wg.label.text] = wg.text
        
        try:
            df = self.method(**args)
            df.name = new_name_func('df',[i for i in self.pai.df_dict])
            print(df.head())
            ig = df_ig(self.pai,df)
            ig.funcao1()
            ig.background_color = [0,0,1,1]
            
            #print(args)
            
        
        except Exception as ex:
            print(ex,'load_pandas')
            return
    
            
#gui to open and manipulate dataframes
class df_ig(lateral_menu):
    def __init__(self,pai,df,name = ''):
        super().__init__(pai,size_hint_x = 1,
                         size_hint_y = None,
                         size = (0,30))

        
        if isinstance(df,tuple) == True:
            self.df = df[0]
            self.selected_columns = df[1]
        else:
            self.df = df
            self.selected_columns = None
           
        self.df_original = self.df.copy()
        self.df_original.name = self.df.name
        self.new_lines = []
        bbox = self.pai.ax.get_position()
        self.old_bbox = bbox
        
        self.text = name

    def funcao1(self,text = None,*args):
        self.new_list(True)
        self.pai.bl_lateral.lista.append(Button(on_release = self.funcao2,
                                                text = self.df.name,
                                               **lateral_args))

        self.labelti(self.change_name,'change name',self.df.name)
        self.labelti(self.manipulate_df,'manipul. df','self.df' if text == None or str(text)[0] == '<' else text)

        self.pai.bl_lateral.lista.append(Button(on_release = self.pivot,
                                                text =  'pivot',
                                               **lateral_args))
        

        
        #add index and columns
        
        df = self.df
        if df.index.name == None:
            df.index.name = 'index'
        self.pai.bl_lateral.lista.append(df_button(self.pai,name = df.index.name,
                                                   menu = self,
                                             index = True))
        
        
        #columns

        self.pai.bl_lateral.lista.append(Label(text = 'Columns',**lateral_args))

        self.pai.bl_lateral.lista.append(Button(on_release = self.sel_all,
                                                text = 'sel. all',
                                                background_color = [0,0,1,1],
                                                **lateral_args))

        if type(self.selected_columns) == type(None):
            self.selected_columns = {i:1 for i in df.columns}

        self.columns_list = []
        for cl in self.df.columns:
            cl_ig = df_button(self.pai,name = cl,selected_columns = self.selected_columns,
                              menu = self)
            self.columns_list.append(cl_ig)
            self.pai.bl_lateral.lista.append(cl_ig)


        ###################

        self.labelti(self.save,'salva df',self.df.name)
        self.pai.bl_lateral.lista.append(Button(text = 'salva plt',on_release = self.save_plt,
                                                **lateral_args))

        self.pai.bl_lateral.lista.append(botao_deleta(self.deleta_plt,text = 'deleta plt',
                                                **lateral_args))


        self.pai.bl_lateral.lista.append(botao_deleta(self.original_df,text = 'original df',
                                                      **lateral_args))
        
        self.pai.bl_lateral.lista.append(botao_deleta(self.deleta,text = 'deleta',
                                                      **lateral_args))

        #plots


        self.pai.bl_lateral.lista.append(Label(text = 'plots',**lateral_args))
        
        self.pai.bl_lateral.lista.append(Button(text = 'plot',
                                                on_release = self.plt,
                                                **lateral_args))

        self.pai.bl_lateral.lista.append(Button(text = 'shadow error plt',
                                                on_release = self.plot_shadow_error,
                                                **lateral_args))

        self.ti_plot_gb = self.labelti(self.plot_gb,'plot gb','index')
        

        #heatmaps
        self.pai.bl_lateral.lista.append(Label(text = 'Eixo x',**lateral_args))
        self.ti_eixox = TextInput(text = '',**lateral_args)
        self.pai.bl_lateral.lista.append(self.ti_eixox)
        
        self.pai.bl_lateral.lista.append(Button(text = 'heatmap',
                                                on_release = self.heatmap,
                                                **lateral_args))

        self.pai.bl_lateral.lista.append(Button(text = 'bar',
                                                on_release = self.bar,
                                                **lateral_args))
        self.pai.bl_lateral.lista.append(Button(text = 'imshow',
                                                on_release = self.imshow,
                                                **lateral_args))

     
        self.pai.bl_lateral.lista.append(Button(text = 'seaborn',
                                                on_release = self.seaborn,
                                                **lateral_args))
            
        self.pai.bl_lateral.cria()

    def pivot(self,*args):
        try:
            columns = self.prepare_plot()
            if len(columns) < 1:
                self.pai.ti_baixo.text = 'Selecionar duas ou maiscolunas: plot gb = values'
                return
            if self.ti_plot_gb.text not in columns:
                self.pai.ti_baixo.text = 'Selecionar duas ou mais colunas: plot gb = values'
                return

            values = self.ti_plot_gb.text
            columns.remove(values)

            name = self.df.name
            self.df = self.df.pivot(columns = columns,values = values)
            self.df.name = name
            self.funcao1()
            #print('ok ok ok')
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)        

    def original_df(self,*args):
        name = self.df.name
        self.df = self.df_original.copy()
        self.df.name = name
        self.funcao1()

    def deleta(self,*args):
        self.pai.df_dict.__delitem__(self.df.name)
        self.lista_original.remove(self)
        self.funcao2()

    def change_name(self,*args):
        
        self.pai.df_dict.__delitem__(self.df.name)
        name = new_name_func(args[0].text,
                                     [df for df in self.pai.df_dict])
        self.df.name = name

        dic_selected = {}
        for i in self.columns_list:
            dic_selected[i.botao_menu.text]  = 1 if i.botao_sel.background_color == [0,0,1,1] else 0
        self.pai.df_dict[self.df.name] = (self.df.copy(),dic_selected)
        self.df_original = self.df

        self.funcao2()
        self.funcao1()

    def sel_all(self,*args):
        if args[0].background_color == [0,0,1,1]:
            for cl in self.columns_list:
                cl.botao_sel.background_color = [0,0,1,1]
                cl.botao_sel.muda_cor()
            args[0].background_color = [1,1,1,1]
        else:
            args[0].background_color = [0,0,1,1]
            for cl in self.columns_list:
                cl.botao_sel.background_color = [1,1,1,1]
                cl.botao_sel.muda_cor()

    def manipulate_df(self,*args):
        df = self.df_original
        try:
            print(args[0].text)
            exec(args[0].text)
            name = df.name
            self.df.name = name
            print(self.df.head(),'asd')
            self.funcao1(text = args[0].text)
            
        except Exception as ex:
            print(ex,'erro')
            print(self.df.head())

    def prepare_plot(self,*args):

        for line in self.new_lines:
            
            line.remove()
        self.new_lines = []

        self.pai.ax.set_position(self.old_bbox)
        
        columns = []
        for i in self.columns_list:
            if i.botao_sel.background_color == [0,0,1,1]:
                columns.append(i.name)

        if self.ti_eixox.text in columns:
            columns.remove(self.ti_eixox.text)
            columns.insert(0,self.ti_eixox.text)
                
        if len(columns) == 0:
            self.pai.atualiza()
        return columns

    def deleta_plt(self,*args):
        for line in self.new_lines:
            
            line.remove()
        self.new_lines = []
        self.pai.atualiza()
        
    def heatmap(self,t = False,*args):

        try:
            columns = self.prepare_plot()
            
            ax,quad,cb = heatmap_df(self.df[columns],self.pai.ax)

            self.new_lines = [quad,cb.ax]
            
            self.pai.atualiza()
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)
        

    def seaborn(self,*args):
        try:
            from seaborn import heatmap

            columns = self.prepare_plot()

            heatmap(self.df[columns],ax = self.pai.ax)
            self.new_lines = [self.pai.ax.collections[-1],
                              self.pai.ax.figure.axes[-1]]
            
            self.pai.atualiza()
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)      

    def imshow(self,*args):
        try:
            columns = self.prepare_plot()

            hm = self.df[columns]
            
            img = self.pai.ax.imshow(hm,**{'origin' : 'Upper',
                                                  'aspect' : 'auto',
                    'cmap': 'RdYlBu_r'})
            
            cb = self.pai.fig.colorbar(img)
            self.new_lines = [img,cb.ax]

            y0 = hm.index.sort_values()[0]
            dy = np.diff(hm.index.sort_values())[0]

            x0 = hm.columns.sort_values()[0]
            dx = np.diff(hm.columns.sort_values())[0]
            
            self.pai.ax.xaxis.set_major_formatter(FuncFormatter("'{}'%({}+{}*x)".format('%.2f',x0,dx)))
            self.pai.ax.yaxis.set_major_formatter(FuncFormatter("'{}'%({}+{}*x)".format('%.2f',y0,dy)))
            
            
            self.pai.atualiza()         
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)
            
    def plot_gb(self,*args):
        try:
            if args[0].text not in self.df.columns:
                return
            columns = self.prepare_plot()
            if len(columns) == 0:
                return
            self.new_lines = []
            
            gb = self.df[columns].groupby(level = 0)
            for a,b in gb:
                old_lines = len(self.pai.ax.lines)
                b.set_index(args[0].text).plot(ax = self.pai.ax)
                self.pai.ax.lines[-1].set_label(str(a))
                self.new_lines += self.pai.ax.lines[old_lines:]
            legend(self.pai.ax)
            self.pai.atualiza()
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)
            
    def plot_shadow_error(self,*args):

        '''plota o shadow error com os dados principais dados pelo ti do plot_gb'''
        try:
            if self.ti_plot_gb.text not in [str(i) for i in self.df.columns]:
                self.pai.ti_baixo.text = 'plot_gb.text not in columns'
                return
            columns = self.prepare_plot()
            if len(columns) == 0:
                self.pai.ti_baixo.text = 'len(columns) = 0'
                return
            self.new_lines = []

            data = self.ti_plot_gb.text
            try:
                columns.remove(data)
            except:
                columns.remove(eval(data))
                data = eval(data)

            error_down,error_up = create_disepertion(self.df[columns].values.T)

            line = self.pai.ax.plot(self.df.index.values,self.df[data].values)[0]
            shadow_error(line,error_down,error_up)

            self.pai.atualiza()
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)
            
    def plt(self,*args):
        try:
            columns = self.prepare_plot()
            if len(columns) == 0:
                return
            old_lines = len(self.pai.ax.lines)

            self.df[columns].plot(ax = self.pai.ax)
            self.new_lines = self.pai.ax.lines[old_lines:]

            self.pai.atualiza()
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)
            
    def bar(self,*args):
        try:
            columns = self.prepare_plot()
            if len(columns) != 1:
                return
            self.df[columns].plot.bar(ax = self.pai.ax)
            self.pai.atualiza()
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)
            
    def save_plt(self,*args):
        self.new_lines = []

    def save(self,*args):
        try:
            self.df.name = args[0].text
            dic_selected = {}
            for i in self.columns_list:
                dic_selected[i.botao_sel.text]  = 1 if i.botao_sel.background_color == [0,0,1,1] else 0
            self.old_bbox = self.pai.ax.get_position()
            self.pai.df_dict[self.df.name] = (self.df.copy(),dic_selected)
            self.df_original = self.df
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)



class df_button(BoxLayout):
    def __init__(self,pai,name,menu,index = False,selected_columns = None):
        super().__init__(orientation = 'horizontal',**lateral_args)
        self.name = name
        self.index = index
        self.menu = menu
        self.selected_columns = selected_columns
        self.pai = pai

        #open menu with options for the column
        self.botao_menu = lateral_menu(pai,text = str(name),
                         size_hint_x = None,
                         size_hint_y = None,
                         size = (0.8*pai.bl_lateral.size[0],30))
        self.botao_menu.funcao1 = self.funcao1_menu
        self.botao_menu.funcao2 = self.funcao2_menu
        self.botao_menu.funcao1d = self.funcao1d_menu
        #select or not the column in the df
        self.botao_sel = lateral_menu(pai,text = 'x',
                         size_hint_x = None,
                         size_hint_y = None,
                         size = (0.2*pai.bl_lateral.size[0],30))
        
        self.botao_sel.funcao1 = self.funcao1_sel
        self.botao_sel.funcao2 = self.funcao2_sel
        self.botao_sel.funcao1d = self.funcao1d_sel
        
        if type(self.selected_columns) != type(None) and self.name not in self.selected_columns:
            self.selected_columns[self.name] = 1
        if index == False and self.selected_columns[self.name] == 1:
            self.botao_sel.background_color = [0,0,1,1]
        if index == True:
            self.botao_sel.background_color = [1,0,0,1]

        self.add_widget(self.botao_menu)
        self.add_widget(self.botao_sel)
            
    def funcao1_sel(self,*args):
        
        if self.index == False:
            self.selected_columns[self.name] = 1
    def funcao2_sel(self,*args):
        if self.index == False:
            self.selected_columns[self.name] = 0

    def funcao1d_sel(self,*args):
        if self.index == True:
            return 
        self.index = True
        name = self.menu.df.name
        self.selected_columns[self.menu.df.index.name] = 1

        #se existe nome duplicado nas colunas:
##        if 'index' in self.menu.df.columns:
##            self.menu.df = self.menu.df.rename({'index':'index_0'},axis = 1)
        self.menu.df = self.menu.df.reset_index()
        self.menu.df = self.menu.df.set_index(self.name)
        self.menu.df.name = name
        self.menu.funcao1()

    def funcao1_menu(self,*args):

        self.botao_menu.position__ = self.children.index(self.botao_menu)
        self.remove_widget(self.botao_menu)
        self.botao_menu.new_list(True)

        if self.index == False:

            self.botao_menu.labelti(self.func_col,'funcao col.',
                                    '')
            self.botao_menu.labelti(self.lim_col,'lim. col.',
                                    '%s : %s'%(self.menu.df[self.name].min(),
                                             self.menu.df[self.name].max()))
            self.botao_menu.labelti(self.name_col,'funcao col.',
                                    str(self.name))


            
        else:
            for i in self.menu.df.index.unique():
                bt = botao_deleta(self.sel_sub_index,text = str(i),
                            **lateral_args)
                bt.valor_index = i
                self.pai.bl_lateral.lista.append(bt)
            
        self.pai.bl_lateral.cria()
                                                 
    def funcao2_menu(self,*args):
##        self.pai.bl_lateral.lista = self.botao_menu.lista_original.copy()
##        self.pai.bl_lateral.cria()
##        self.add_widget(self.botao_menu,self.botao_menu.position__)
        self.menu.funcao1()

    def funcao1d_menu(self,*args):
        self.menu.ti_eixox.text = str(self.name)
        self.menu.ti_plot_gb.text = str(self.name)
        self.botao_menu.background_color = [1,1,1,1]

    def sel_sub_index(self,*args):
        t = self.menu.df.name
        self.menu.df = self.menu.df.loc[args[0].valor_index]
        if isinstance(self.menu.df,pd.Series) == True:
            self.menu.df = self.menu.df.to_frame()
        self.menu.df.name = t
        self.menu.funcao1()

    def func_col(self,*args):
        try:
            nome = new_name_func(self.name,self.menu.df.columns)
            x = self.menu.df[self.name]
            self.menu.df[nome] = eval(args[0].text)
        except Exception as ex:
            print(ex)
            self.pai.ti_baixo.text = str(ex)
        

    def lim_col(self,*args):
        pass
        
    def name_col(self,*args):

        t = self.menu.df.name
        self.menu.df = self.menu.df.rename({self.name:args[0].text},axis = 1)
        self.botao_menu.text = args[0].text
        self.menu.df.name = t
    
class add_points(lateral_menu):
    def __init__(self,pai,line,line_baseline = None,
                 text = 'add_points', max_points = np.inf,
                                         desfazer_double_click = True):
        super().__init__(pai,text = text,
                         **lateral_args)
        self.line = line
        self.desfazer = True
        self.max_points = max_points
        self.desfazer_double_click = desfazer_double_click

    def funcao_rigth(self,*args):
        pass

    def funcao_left(self,*args):
        pass
        
    def funcao1(self,*args):
        self.pai.double_click = False
        self.pai.fix_ax = True
        self.pai.bl_figura.on_touch_down = self.add

    def funcao2(self,*args):
        if self.desfazer_double_click == True:
            self.pai.double_click = True
        self.pai.fix_ax = False
        self.pai.bl_figura.on_touch_down = self.pai.on_touch_down

    def funcao_desfazer(self,*args):
        self.funcao2()

    def add(self,*args):
        self.pai.on_touch_down(*args)
        
        x,y = self.line.get_data()
        if args[0].button == 'left':
            if len(x) >= self.max_points:
                return
            x = np.append(x,self.pai.ptx)
            y = np.append(y,self.pai.pty)
            ind = np.argsort(x)
            x = x[ind]; y = y[ind]
        if args[0].button != 'left' and len(x) != 0:
            if len(x) != 0:
                
                ind = busca(x,self.pai.ptx)
                x = np.delete(x,ind)
                y = np.delete(y,ind)
                
        self.line.set_data(x,y)

        if args[0].button == 'left':
            self.funcao_left(self,*args)
        else:
            self.funcao_rigth(self,*args)
        self.pai.atualiza()       
        
class baseline_ig(lateral_menu):
    def __init__(self,pai,line,line_baseline = None):
        super().__init__(pai,text = 'baseline',
                         **lateral_args)
        self.line = line
        self.line_baseline = line_baseline
        
    def funcao1(self,*args):
        self.new_list(True)

        self.desfazer = True

        if self.line_baseline == None:
            line_baseline = self.pai.ax.plot([],[],'-o',color = 'black')[0]
            line_baseline.set_label(new_name_func('_baseline',
                                    [i.get_label() for i in self.pai.ax.lines]))
        self.line_baseline = line_baseline 

        self.pai.bl_lateral.lista.append(add_points(self.pai,self.line_baseline))
        self.pai.bl_lateral.lista.append(Button(text = 'apply',
                                                on_release = self.apply,
                                                **lateral_args))

        
        self.pai.bl_lateral.cria()

    def funcao_desfazer(self,*args):
        if self.line_baseline != None:
            if len(self.line_baseline.get_data()[0]) == 0:
                self.line_baseline.remove()

    def apply(self,*args):
        from scipy.interpolate import interp1d
        x,y = self.line_baseline.get_data()
        if len(x) < 2:
            return
        func = interp1d(x,y,bounds_error = False,fill_value = 'extrapolate')
        x,y = self.line.get_data()
        bl = func(x)
        l = self.pai.ax.plot(x,y-bl,'--')[0]
        l.set_label(new_name_line(self.line.get_label() + '_baseline',l))
        self.pai.atualiza()

class manipulate_data(lateral_menu):
    def __init__(self,pai,line):
        super().__init__(pai,text = 'man. data',
                         **lateral_args)
        self.line = line
        if 'original_data' not in self.line.__dict__:
            
            x,y = self.line.get_data()
            self.line.original_data = [x.copy(),y.copy()]
        else:
            if isinstance(self.line.original_data,pd.DataFrame) == True:
                x,y = self.line.get_data()
                self.line.original_data = [x.copy(),y.copy()]
        func_line(line)
        self.desfazer = True

        self.deltax = self.line.deltax
        self.deltay = self.line.deltay
        self.ratiox = self.line.ratiox
        self.ratioy = self.line.ratioy

    def funcao1(self,*args):

        self.new_list(True)

        self.list_buttons = []
        self.list_buttons.append(Button(on_release = self.transform,
                                              text = 'move x',
                                              **lateral_args))

        self.list_buttons.append(Button(on_release = self.transform,
                                              text = 'move y',
                                              **lateral_args))

        self.list_buttons.append(Button(on_release = self.transform,
                                              text = 'ratio x',
                                              **lateral_args))

        self.list_buttons.append(Button(on_release = self.transform,
                                              text = 'ratio y',
                                              **lateral_args))

        self.ti_deltax = self.labelti(self.func,
                             'delta x',str(self.deltax))
        self.ti_deltay = self.labelti(self.func,
                             'delta y',str(self.deltay))
        self.ti_ratiox = self.labelti(self.func,
                             'ratio x',str(self.ratiox))
        self.ti_ratioy = self.labelti(self.func,
                             'ratio y',str(self.ratioy))
                

        self.pai.bl_lateral.lista += self.list_buttons

        
        self.funcx = self.labelti(self.func,'func x',self.line.funcao_eixox)
        self.funcy = self.labelti(self.func,'func y',self.line.funcao_eixoy)

        self.labelti(self.savgol,'window_len , polyorder',
                     '5,3' if 'polyorder' not in self.line.__dict__ else '%s,%s'%(self.line.window_lenght,
                                                                                  self.line.polyorder))

        self.labelti(lambda *args: suavisa_line(self.line,eval(args[0].text),
                                           False),'suavisa',
                     '1' if 'suavisa' not in self.line.__dict__ else\
                     str(self.line.suavisa))
        
        self.pai.bl_lateral.lista.append(add_points(self.pai,self.line))
        
        self.funcx_str = self.line.funcao_eixox
        self.funcy_str = self.line.funcao_eixoy
        
        self.pai.bl_lateral.cria()

    def savgol(self,*args):
        try:
            wl = args[0].text.split(',')[0]
            po = args[0].text.split(',')[1]
            savgol(self.line,eval(wl),eval(po))
        except Exception as ex:
            print(ex)
        
    def funcao2(self,*args):
        self.pai.bl_lateral.lista = self.lista_original.copy()
        self.pai.bl_lateral.cria()
        self.funcao_desfazer()

    def move_line_down(self,*args):

        self.pai.on_touch_down(*args)
        if args[0].button != 'left':
            return

        ind = busca(self.line.get_data()[0],self.pai.ptx)
        self.index = ind
        self.__px = self.line.get_data()[0][ind]
        self.__py = self.line.get_data()[1][ind]
        self.__deltax = self.line.deltax
        self.__deltay = self.line.deltay

##        if self.line_sel == 'y':
##            self.l_aux = self.line.get_ydata().copy()
##            self.ratio_aux = self.line.ratioy
##        if self.line_sel == 'x':
##            self.l_aux = self.line.get_xdata().copy()
##            self.ratio_aux = self.line.ratiox
        
        self.move_line(self.__px,self.__py,self.__deltax,self.__deltay)
            
    def move_line_move(self,*args):
        if args[0].button != 'left':
            self.pai.on_touch_move(*args)
            return
        self.pai.on_touch_down(*args)
        self.move_line(self.__px,self.__py,self.__deltax,self.__deltay)
        
    def move_line(self,px,py,dx,dy):
    
        if self.line_sel == 'x':
            #px = self.line.ratiox*self.line.original_data[0][ind]
            self.ti_deltax.text = str(dx + self.pai.ptx - px)
            self.func(*(self.ti_deltax,))
        if self.line_sel == 'y':
            #py = self.line.ratioy*self.line.get_data()[1][ind]
            self.ti_deltay.text = str(dy + self.pai.pty - py)
            self.func(*(self.ti_deltay,))
        
        
    def ratio_line_down(self,*args):
        self.pai.on_touch_down(*args)
        if args[0].button == 'left':
            return
        self.ptx1,self.pty1 = self.pai.ptx,self.pai.pty

        if self.line_sel == 'y':
            self.l_aux = self.line.get_ydata().copy()
            self.ratio_aux = self.line.ratioy
            #buscar ponto proximo ao clique
            self.__idx = busca(self.line.get_xdata(),self.ptx1)
            #posicao antiga do ponto
            self.__y0 = self.line.original_data[1][self.__idx]
            self.__y1 = self.line.get_ydata()[self.__idx]
        if self.line_sel == 'x':
            self.l_aux = self.line.get_xdata().copy()
            self.ratio_aux = self.line.ratiox
            
    def ratio_line_move(self,*args):
        if args[0].button == 'left':
            self.pai.on_touch_move(*args)
            return
        
        self.pai.on_touch_down(*args)
        self.ptx2,self.pty2 = self.pai.ptx,self.pai.pty
            
        if self.line_sel == 'y':
            
            y0 = self.__y0
            y1 = self.__y1
            a,b = self.line.axes.get_ylim()
            delta = (self.pty2-self.pty1)/abs(a-b)
            
            if delta >= 0:
                y2 = y0*self.ratio_aux*(1+delta)
                self.ti_ratioy.text = str(self.ratio_aux*(1+delta))
            else:
                y2 = y0*self.ratio_aux*(1/(1-delta))
                self.ti_ratioy.text = str(self.ratio_aux*(1/(1-delta)))
            
            delta = -(y2 - y1)
            print(y0,y1,y2,delta)
            self.ti_deltay.text = str(delta)
            self.func(*(self.ti_deltay,))
            
        if self.line_sel == 'x':
            a,b = self.line.axes.get_xlim()
            delta = (self.ptx2-self.ptx1)/abs(a-b)
            if delta >= 0:
                self.ti_ratiox.text = str(self.ratio_aux*(1+delta))
            else:
                self.ti_ratiox.text  = str(self.ratio_aux*(1/(1-delta)))
            self.func(*(self.ti_deltax,))

    def transform(self,*args):

        if args[0].background_color == [1,1,1,1]:
            self.pai.double_click = False
            self.pai.fix_ax = True
            args[0].background_color = [0,0,1,1]
            if args[0].text == 'move x':
                self.line_sel = 'x'
                self.pai.bl_figura.on_touch_down = self.move_line_down
                self.pai.bl_figura.on_touch_move = self.move_line_move
            if args[0].text == 'move y':
                self.line_sel = 'y'
                self.pai.bl_figura.on_touch_down = self.move_line_down
                self.pai.bl_figura.on_touch_move = self.move_line_move
            if args[0].text == 'ratio x':
                self.line_sel = 'x'
                self.pai.bl_figura.on_touch_down = self.ratio_line_down
                self.pai.bl_figura.on_touch_move = self.ratio_line_move
            if args[0].text == 'ratio y':
                self.line_sel = 'y'
                self.pai.bl_figura.on_touch_down = self.ratio_line_down
                self.pai.bl_figura.on_touch_move = self.ratio_line_move
        else:
            args[0].background_color = [1,1,1,1]
            self.funcao_desfazer()
            
        for i in self.list_buttons:
            if i != args[0] and i.background_color == [0,0,1,1]:
                i.background_color = [1,1,1,1]

    def func(self,*args):
        try:
##            X,Y = self.line.original_data
            if args[0].label.text[-1] == 'x':
                self.line.funcao_eixox = self.funcx.text
                self.line.deltax = eval(self.ti_deltax.text)
                self.line.ratiox = eval(self.ti_ratiox.text)
##                X = eval(self.line.funcao_eixox+'*%s + %s'%(self.line.ratiox , self.line.deltax))
            else:
                self.line.funcao_eixoy = self.funcy.text
                self.line.deltay = eval(self.ti_deltay.text)
                self.line.ratioy = eval(self.ti_ratioy.text)
##                Y = eval(self.line.funcao_eixoy+'*%s + %s'%(self.line.ratioy , self.line.deltay))

            func_line(self.line)
##            if 'suavisa' in self.line.__dict__ and self.line.suavisa != 0:
##                X,Y = suavisa(X,Y,self.line.suavisa)
##
##            self.line.set_data(X,Y)
            #self.pai.res_zoom()

##            if args[0].label.text[-1] == 'y':
##                if self.line.axes.twinx_ax == None:
##                    ax2 = twin_ax(self.line.axes,'y')
##                else:
##                    ax2 = self.line.axes.twinx_ax
##                string = "'{}'%((x - {})/{})".format('%.4f',self.line.deltay,self.line.ratioy)
##                ax2.yaxis.set_major_formatter(FuncFormatter(string))
            
##            self.pai.atualiza()

        except Exception as ex:
            print(ex)

        
class ax_menu(lateral_menu):
    def __init__(self,pai,bl):
        super().__init__(pai,bl = bl,text = 'ax',
                         size_hint_x = None,
                         size_hint_y = 1,size = (50,1))

    def funcao1(self,*args):
        self.new_list()
        
        #check for twin axes
        
        list_cb,list_axes = find_colorbar_ax(self.pai.fig.axes)
        list_axes = find_twin_ax(list_axes)

        self.labelti(self.add_ax,'add ax','222')

        self.pai.bl_lateral.lista.append(Label(text = 'axes',
                                               **lateral_args))
        
        for ax in list_axes:
            name_ax(ax)
            self.pai.bl_lateral.lista.append(ax_ig(self.pai,
                                             ax = ax,
                                             text = ax.get_label()))


        self.pai.bl_lateral.lista.append(plot_funcao_menu(self.pai))

        self.pai.bl_lateral.lista.append(execute_func(self.pai))
        self.pai.bl_lateral.lista.append(line_operations(self.pai))

        self.pai.bl_lateral.lista.append(obj_operations(self.pai,obj = 'ax'))
        
        self.pai.bl_lateral.cria()

    def add_ax(self,*args):
        try:
            ax = self.pai.fig.add_subplot(eval(args[0].text))
            self.funcao1()
            self.funcao2()
            self.pai.atualiza()
        except Exception as ex:
            print(ex)

class ax_ig(lateral_menu):
    def __init__(self,pai,ax,**args):
        super().__init__(pai,
                         size_hint_x = 1,
                         size_hint_y = None,
                         size = (0,30),**args)
        self.ax = ax
        if 'twiny_ax' not in self.ax.__dict__:
            self.twin = True
        else:
            self.twin = False
        print(self.twin)
        
    def funcao1(self,*args):
        self.new_list()

        #line ig
        self.pai.bl_lateral.lista.append(line_menu(bl = None, pai = self.pai,
                                  **lateral_args))
    
        #ax size ig
        self.pai.bl_lateral.lista.append(ax_size(self.pai,self.ax,**lateral_args))
        
        ti = self.labelti(self.func_axis,'Funcao xaxis',
                     'None' if 'string' not in self.ax.xaxis.get_major_formatter().__dict__\
                     else self.ax.xaxis.get_major_formatter().string)
        ti.axis = self.ax.xaxis

        if self.ax.get_legend() != None:
            self.labelti(self.pos_leg,'pos_leg',str(self.ax.get_legend()._get_loc()))

        if self.twin == False:
            
            if self.ax.twiny_ax != None:
                ti = self.labelti(self.func_axis,'Funcao xaxis2',
                         'None' if 'string' not in self.ax.twiny_ax.xaxis.get_major_formatter().__dict__\
                         else self.ax.twiny_ax.xaxis.get_major_formatter().string)
                ti.axis = self.ax.twiny_ax.xaxis
                     
        ti = self.labelti(self.func_axis,'Funcao yaxis',
                     'None' if 'string' not in self.ax.yaxis.get_major_formatter().__dict__\
                     else self.ax.yaxis.get_major_formatter().string)
        ti.axis = self.ax.yaxis

        if self.twin == False:

            if self.ax.twinx_ax != None:
                ti = self.labelti(self.func_axis,'Funcao yaxis2',
                         'None' if 'string' not in self.ax.twinx_ax.yaxis.get_major_formatter().__dict__\
                         else self.ax.twinx_ax.yaxis.get_major_formatter().string)
                ti.axis = self.ax.twinx_ax.yaxis
        
                     
        self.labelti_attr(self.ax,'ax.')
        self.pai.bl_lateral.lista.append(methods_ig(self.pai,self.ax,ax_load_list))


        #add fill betweeen

        self.pai.bl_lateral.lista.append(add_fill_between(self.pai,**lateral_args))

        
        self.pai.bl_lateral.lista.append(Label(text = 'axis',**lateral_args))
        
        self.pai.bl_lateral.lista.append(axis_ig(self.pai,'xaxis',self.ax.xaxis))
        self.pai.bl_lateral.lista.append(axis_ig(self.pai,'yaxis',self.ax.yaxis))
    
        if self.twin == False:

            if self.ax.twiny_ax == None:
                self.pai.bl_lateral.lista.append(botao_deleta(lambda *args: self._twin_ax(self.ax,'x'),text = 'add x2',
                                                              **lateral_args))
            else:
                self.pai.bl_lateral.lista.append(axis_ig(self.pai,'x2',self.ax.twiny_ax.xaxis))

            if self.ax.twinx_ax == None:
                self.pai.bl_lateral.lista.append(botao_deleta(lambda *args: self._twin_ax(self.ax,'y'),text = 'add y2',
                                                              **lateral_args))
            else:
                self.pai.bl_lateral.lista.append(axis_ig(self.pai,'y2',self.ax.twinx_ax.yaxis))

        self.labelti(lambda *args: load_img(args[0].text,self.ax),'load img','')
        self.pai.bl_lateral.lista.append(imagens_menu(self.pai,self.ax))

        self.pai.bl_lateral.lista.append(text_menu(self.pai))

        #bar plots
        self.pai.bl_lateral.lista.append(bar_menu(self.pai,self.ax))

        #fill between
        self.pai.bl_lateral.lista.append(fill_between_menu(self.pai,self.ax))
        
        
        #ajustar outros ax
        self.pai.bl_lateral.lista.append(botao_deleta(lambda x,*args: centraliza_ax(self.ax),
                                         text = 'alinha axes',**lateral_args))

        #travar eixox (todos os outros ax)
        self.pai.bl_lateral.lista.append(botao_deleta(lambda x,*args: acopla_axis(self.ax,
                                                    [i for i in self.ax.figure.axes if i != self.ax],
                                                                                  eixo = 'x'),
                                         text = 'acopla eixos x',**lateral_args))

        #travar eixoy (todos os outros ax)
        self.pai.bl_lateral.lista.append(botao_deleta(lambda x,*args: acopla_axis(self.ax,
                                                    [i for i in self.ax.figure.axes if i !=  self.ax],
                                                                                  eixo = 'y'),
                                         text = 'acopla eixos y',**lateral_args))

        #desacopla eixos
        self.pai.bl_lateral.lista.append(botao_deleta(lambda x,*args: desacopla_axis(self.ax,
                                                                                     eixo = 'xy'),
                                         text = 'desacopla eixos',**lateral_args))

        
        self.pai.bl_lateral.cria()
    
    def _twin_ax(self,ax,axis):
        twin_ax(ax,axis)
        self.funcao2()
        self.funcao1()


    def pos_leg(self,*args):
        try:
            self.ax.get_legend()._set_loc(eval(args[0].text))
        except Exception as ex:
            print(ex)

    def func_axis(self,*args):
        #implementar fixed formater
        try:
            
            axis = args[0].axis
            if args[0].text.lower() == 'none':
                axis.set_major_formatter(ScalarFormatter())
            else:
                print(args[0].text)
                axis.set_major_formatter(FuncFormatter(args[0].text))
            self.pai.atualiza()
            
        except Exception as ex:
            print('erro func_axis\n%s'%str(ex))

class ax_size(lateral_menu):
    def __init__(self,pai,ax,**args):
        super().__init__(pai,**args)
        self.ax = ax
        self.text = 'adjusts rect'

        selzer = True

    def funcao1(self,*args):

        self.pai.bl_figura.on_touch_down = self.desce
        self.pai.bl_figura.on_touch_move = self.move
        
        self.new_list(True)

        bbox = self.ax.get_position()
            
        self.x0_ti = self.labelti(self.adjust,
                               'x0',str(bbox.x0))
        self.x1_ti = self.labelti(self.adjust,
                               'x1',str(bbox.x1))
        
        self.y0_ti = self.labelti(self.adjust,
                               'y0',str(bbox.y0))
        self.y1_ti = self.labelti(self.adjust,
                               'y1',str(bbox.y1))
        self.pai.bl_lateral.cria()

        

        
    def funcao_desfazer(self,*args):

        self.pai.bl_figura.on_touch_down = self.pai.on_touch_down
        self.pai.bl_figura.on_touch_move = self.pai.on_touch_move

    def funcao2(self,*args):
        self.pai.bl_lateral.lista = self.lista_original.copy()
        self.pai.bl_lateral.cria()
        self.funcao_desfazer()
        
    def adjust(self,*args):
        x0 = eval(self.x0_ti.text)
        x1 = eval(self.x1_ti.text)
        y1 = eval(self.y1_ti.text)
        y0 = eval(self.y0_ti.text)

        self.ax.set_position([x0,y0,x1,y1])
        self.pai.atualiza()



    def clique_dentro(self,x,y):

        a = self.pai.ax.get_window_extent()

        xcima = a.x0 + self.pai.bl_figura.x
        xbaixo = a.x1 +  self.pai.bl_figura.x
        ycima = a.y0 + self.pai.bl_figura.y
        ybaixo = a.y1 + self.pai.bl_figura.y
        #print(x,xbaixo,xcima)
        if x < xbaixo and x > xcima and y < ybaixo and y > ycima:

            if abs(x-xcima)  < abs(xcima-xbaixo)/2:
                return 1
            else:
                if abs(y-ycima) > abs(ycima-ybaixo)/2:
                    return 3
                else:
                    return 2
        else:
            return False
        

    def desce(self,*args):

        x,y = args[0].pos
        ax_sel = self.ax

        self.quadrante = self.clique_dentro(x,y)
        if self.quadrante == False:
            for ax in find_twin_ax(self.pai.fig.axes):
                self.pai.ax = ax
                self.quadrante = self.clique_dentro(x,y)
                if self.quadrante != False:
                    self.funcao2()
                    self.funcao1()
                    ax_sel = ax
                    break

        print(self.quadrante)
        self.pai.ax = ax_sel
        bbox = self.pai.ax.get_position()
        self.px = x; self.py = y
        self.x0 = bbox.x0
        self.y0 = bbox.y0

        self.x1 = bbox.width
        self.y1 = bbox.height
        #print(self.quadrante)
        
    def move(self,*args):
        
        if self.quadrante == False:
            return

        xmin,ymin = 0,0
        xmax,ymax = self.pai.bl_figura.size
        
        dx = (-self.px + args[0].pos[0])/xmax
        dy = (-self.py + args[0].pos[1])/ymax
        if self.quadrante == 1:

            self.x0_ti.text = str(self.x0 + dx)
            self.y0_ti.text = str(self.y0 + dy)
            self.adjust()
        if self.quadrante == 2:
            #parte de baxio
            self.x0_ti.text = str(self.x0 + dx)
            self.y0_ti.text = str(self.y0 + dy)
            
            self.x1_ti.text = str(self.x1 + dx)
            self.y1_ti.text = str(self.y1 + dy)
            self.adjust()
        if self.quadrante == 3:
            #parte de cima
            self.x1_ti.text = str(self.x1 + dx)
            self.y1_ti.text = str(self.y1 + dy)
            self.adjust()
        
        
class axis_ig(lateral_menu):
    def __init__(self,pai,name,axis,**args):
        super().__init__(pai,
                         size_hint_x = 1,
                         size_hint_y = None,
                         size = (0,30),**args,
                         text = name)
        self.axis = axis
        
    def funcao1(self,*args):
        self.new_list(True)

        major_dict = self.axis._major_tick_kw
        
        #labelsize
        self.labelti(self.set_major_param,'labelsize',
                     major_dict['labelsize'] if 'labelsize' in major_dict else '12')
        #labelcolor
        self.labelti(self.set_major_param,'labelcolor',
                     major_dict['labelcolor'] if 'labelcolor' in major_dict else 'black')
        #size
        self.labelti(self.set_major_param,'size',
                     major_dict['size'] if 'size' in major_dict else '12')
        #color
        self.labelti(self.set_major_param,'color',
                     major_dict['color'] if 'color' in major_dict else 'black')
        #rotation
        self.labelti(self.set_major_param,'rotation',
                     major_dict['rotation'] if 'rotation' in major_dict else '0')
        
        self.labelti_attr(self.axis,'axis.')
        self.pai.bl_lateral.lista.append(methods_ig(self.pai,self.axis,axis_load_list))
        self.pai.bl_lateral.lista.append(methods_ig(self.pai,self.axis.get_label(),
                                                    label_load_list, text = 'label'))
        self.pai.bl_lateral.cria()

                
    def set_major_param(self,*args):
        param = args[0].label.text
        valor = args[0].text
        try:
            try:
                self.axis.set_tick_params(which = 'major',**{param:eval(valor)})
            except:
                self.axis.set_tick_params(which = 'major',**{param:eval("'%s'"%valor)})
        except Exception as ex:
            print(ex)

        self.pai.atualiza()

    def set_minor_param(self,*args):
        param = args[0].label.text
        valor = args[0].text
        try:
            self.axis.set_tick_params(which = 'minor',**{param:eval(valor)})
        except:
            self.axis.set_tick_params(which = 'minor',**{param:eval("'%s'"%valor)})

        self.pai.atualiza()


class merge_lines(lateral_menu):
    def __init__(self,pai,menu,**args):
        super().__init__(pai,text = 'merge lines',**lateral_args)
        self.menu = menu

    def funcao1d(self,*args):
        lines = []
        for i in self.pai.bl_lateral.lista.copy():
            if isinstance(i,line_ig) == True:
                if i.button.background_color == [1,0,0,1]:
                    lines.append(i.line)

        if len(lines) == 0:
            return
        if len(lines) == 1:
            'clone'
        else:
            x = np.array([]); y = x.copy()
            for line in lines:
                x2,y2 = line.get_data()
                x = np.append(x,x2)
                y = np.append(y,y2)
            ind = np.argsort(x)
            l2 = line.axes.plot(x[ind],y[ind])[0]
            if 'conteiner' in line.__dict__:
                l2.conteiner = line.conteiner
            self.menu.funcao2()
            self.menu.funcao1()
                

class conteiner_menu(BoxLayout):
    def __init__(self,pai,nome,**args):
        super().__init__(orientation = 'horizontal',**lateral_args)
        self.pai = pai
        self.nome = nome
        self.button = conteiner_menu_button(pai,nome,
                                       size_hint_x = None,
                                       size_hint_y = None,
                                       size = (0.8*pai.bl_lateral.size[0],30)) 
        self.add_widget(self.button)
        b = lateral_menu(pai,bl = self,
                         text = 'x',
                         size_hint_x = None,
                         size_hint_y = None,
                         size = (0.2*pai.bl_lateral.size[0],30))

        b.funcao1 = self.bfuncao1
        b.funcao2 = self.bfuncao2
        
        
        dic = group_conteiner(self.pai.ax.lines)
        if self.nome not in dic:
            dic[self.nome] = []
        self.lista_lines = dic[self.nome]

        dic = group_conteiner(self.pai.ax.texts)
        if self.nome not in dic:
            dic[self.nome] = []
        self.lista_texts = dic[self.nome]


        if len(self.lista_lines + self.lista_texts) == 0:
            b.background_color = [0,0,1,1]
        else:
            b.background_color = [1,1,1,1] if\
                sum([i.get_visible() for i in self.lista_lines + self.lista_texts]) == 0 else [0,0,1,1]

    def bfuncao1(self,*args):
        for i in self.lista_lines + self.lista_texts:
            visible(i,1)
        self.pai.atualiza()

    def bfuncao2(self,*args):
        for i in self.lista_lines + self.lista_texts:
            visible(i,0)
        self.pai.atualiza()

class conteiner_menu_button(lateral_menu):
    def __init__(self,pai,nome,**args):
        super().__init__(pai,text = nome)
        
        self.nome = nome
        
    def funcao1(self,*args):
        self.new_list()
        self.pai.bl_lateral.lista = [self.parent]


        dic = group_conteiner(self.pai.ax.lines)
        if self.nome not in dic:
            dic[self.nome] = []
        self.lista_lines = dic[self.nome]
        self.parent.lista_lines = self.lista_lines

        dic = group_conteiner(self.pai.ax.texts)
        if self.nome not in dic:
            dic[self.nome] = []
        self.lista_texts = dic[self.nome]
        self.parent.lista_texts = self.lista_texts

        self.pai.bl_lateral.lista.append(Button(text = 'remove',
                                                on_release = self.remove,
                                                **lateral_args))
        
        
        self.pai.bl_lateral.lista.append(merge_lines(self.pai,self))
        #ti para aplicar método em todas as lines

        self.labelti(self.deltay,'delta y','0')
        
        self.labelti_attr(self.lista_lines,'lines. - (line = obj)','')
        for line in self.lista_lines:
            self.pai.bl_lateral.lista.append(line_ig(self.pai,line = line))

        self.labelti_attr(self.lista_texts,'texts.','')
        for text in self.lista_texts:
            self.pai.bl_lateral.lista.append(text_ig(self.pai,text = text))

        self.pai.bl_lateral.lista.append(botao_deleta(self.delete,text = 'Delete',
                                                **lateral_args))
        
        self.pai.bl_lateral.cria()

    def deltay(self,*args):
        try:
            n = 0; dy = eval(args[0].text)
            for line in self.lista_lines:
                line.deltay = n*dy
                func_line(line)
                n += 1
        except Exception as ex:
            print(ex)
    
    def funcao1d(self,*args):
        self.background_color = [1,1,1,1]
        for i in self.pai.bl_lateral.lista.copy():
            if isinstance(i,line_ig) == True:
                if i.button.background_color == [1,0,0,1]:
                    i.conteiner(self.nome)
                    self.parent.lista_lines.append(i.line)

    def remove(self,*args):
        
        for i in self.pai.bl_lateral.lista.copy():
            if isinstance(i,line_ig) == True:
                if i.button.background_color == [1,0,0,1]:
                    i.conteiner('__none__')
                    self.lista_lines.remove(i.line)
            if isinstance(i,text_ig) == True:
                if i.button.background_color == [1,0,0,1]:
                    i.conteiner('__none__')
                    self.lista_texts.remove(i.text)
                    
    def delete(self,*args):
        for i in self.pai.bl_lateral.lista.copy():
            if isinstance(i,line_ig) == True:
                i.conteiner('__none__')
        self.pai.conteiners.remove(self.nome)
        self._delete()
            



class line_menu(lateral_menu):
    def __init__(self,pai,bl,**args):
        super().__init__(pai,bl = bl,text = 'Lines',
                         **args)

    def funcao1(self,*args):
        self.new_list()
        self.pai.bl_lateral.lista = []
        dic = group_conteiner(self.pai.ax.lines)
        for line in dic['__none__']:
            self.pai.bl_lateral.lista.append(line_ig(self.pai,line = line))


        #merge lines
        self.pai.bl_lateral.lista.append(merge_lines(self.pai,self))
            
        self.pai.bl_lateral.lista.append(Label(text = 'conteiners',
                                               **lateral_args))
        self.labelti(self.add_conteiner,'add conteiner',new_name_func('conteiner',
                                    [i.text if 'text' in i.__dict__ else '__none__' for i in self.pai.bl_lateral.lista]))
        
        #add conteiners
        for i in dic:
            if i != '__none__':
                self.pai.bl_lateral.lista.append(conteiner_menu(self.pai,i))
            if i not in self.pai.conteiners:
                self.pai.conteiners.append(i)

        for i in self.pai.conteiners:
            if i not in dic:
                self.pai.bl_lateral.lista.append(conteiner_menu(self.pai,i))
                
        self.pai.bl_lateral.cria()

    def add_conteiner(self,*args):
        name = new_name_func(args[0].text,
                                     self.names_lines_conteiners())
        
        self.pai.bl_lateral.lista.append(conteiner_menu(self.pai,
                                                        name))
        self.pai.conteiners.append(name)
        self.pai.bl_lateral.cria()


    def names_lines_conteiners(self,*args):
        return [i.get_label() for i in self.pai.ax.lines] + self.pai.conteiners


##class func_ig(lateral_menu):
##    def __init__(self,pai,**args):
##        super().__init__(pai,
##                         text = 'func',
##                         **lateral_args)
##
##    def funcao1(self,*args):
##        self.new_list(True)
##        self.func_str = self.labelti(lambda *args : *args,
##                                     'func(X)','X')
##
##        bl = BoxLayout(orientation = orizontal
##        

class muda_ax(lateral_menu):
    def __init__(self,pai,line,**args):
        super().__init__(pai,
                         text = 'muda ax',
                         **lateral_args)
        self.line = line

    def funcao1(self,*args):
        self.new_list(True)
        for ax in self.pai.fig.axes:
            b = botao_deleta(self.func,text = ax.get_label(),
                                       **lateral_args)
            b.ax = ax
            self.pai.bl_lateral.lista.append(b)
        self.pai.bl_lateral.cria()

    def func(self,*args):
        ax = args[0].ax
        dic = load_line(self.line)
        line = ax.plot(dic['data'][0],dic['data'][1])[0]
        line = load_line(dic,line)

        self.line.remove()

        self.funcao2(*(self,))
        

class text_menu(lateral_menu):
    def __init__(self,pai,**args):
        super().__init__(pai,text = 'Texts',
                                 **lateral_args)

    def funcao1(self,*args):
        self.new_list(True)
        self.ti_add = self.labelti(self.add_text,'add text','1,1,text')
        self.desfazer = True

        self.pai.bl_figura.on_touch_down = self.down
        for text in self.pai.ax.texts:
            self.pai.bl_lateral.lista.append(text_ig(self.pai,text))

        self.pai.bl_lateral.cria()

    def down(self,*args):
        try:
            self.pai.on_touch_down(*args)
            l = self.ti_add.text.split(',')
            self.ti_add.text = '%.6f, %.6f, %s'%(self.pai.ptx,self.pai.pty,l[2])
        except Exception as ex:
            print(ex)
                    

    def add_text(self,*args):
        l = args[0].text.split(',')
        try:
            self.pai.ax.text(eval(l[0]),eval(l[1]),l[2])
            self.funcao2()
            self.funcao1()
            self.pai.atualiza()
        except Exception as ex:
            print(ex)

class text_ig(BoxLayout):
    def __init__(self,pai,text,**args):
        super().__init__(orientation = 'horizontal',**lateral_args)
        self.pai = pai
        self.text = text
        self.button = text_ig_button(pai,text,
                                       size_hint_x = None,
                                       size_hint_y = None,
                                       size = (0.8*pai.bl_lateral.size[0],30)) 
        self.add_widget(self.button)
        b = lateral_menu(pai,bl = self,
                         text = 'x',
                         size_hint_x = None,
                         size_hint_y = None,
                         size = (0.2*pai.bl_lateral.size[0],30))
        
        b.funcao1 = lambda *x: self.set_visible(1)
        b.funcao2 = lambda *x: self.set_visible(0)
        b.background_color = [1,1,1,1] if text.get_visible() == 0 else [0,0,1,1]
        


    def set_visible(self,v):
        self.text.set_visible(v)
        self.text.axes.figure.canvas.draw()

    def conteiner(self,conteiner,*args):
        self.text.conteiner = conteiner
        self.pai.bl_lateral.lista.remove(self)
        self.pai.bl_lateral.cria()
        #add a line no conteiner


        #self.tipy.text = str(self.pai.pty2)
        


class text_ig_button(lateral_menu):
    def __init__(self,pai,text,**args):
        super().__init__(pai,
                         size_hint_x = 1,
                         size_hint_y = None,
                         size = (0,30))
        
        self.text = text.get_text()
        self.text_obj = text

        self.desfazer = True
        
        
    def funcao1(self,*args):
        self.new_list()
        self.pai.bl_lateral.lista = [self.parent]
        self.labelti_attr(self.text_obj,'text.')
        self.pai.bl_lateral.lista.append(methods_ig(self.pai,self.text_obj,text_load_list))

        
        self.posx = self.labelti(self.set_pos_text,'x',str(self.text_obj.get_position()[0]))
        self.posy = self.labelti(self.set_pos_text,'y',str(self.text_obj.get_position()[1]))

        self.pai.bl_lateral.lista.append(Button(on_release = self.move_textos,
                                                text = 'move texts',
                                                **lateral_args))
        
        self.pai.bl_lateral.cria()

    def set_pos_text(*args):
        try:
            x = eval(self.posx.text)
            y = eval(self.posy.text)
            self.text_obj.set_position((x,y))
            self.pai.atualiza()
        except Exception as ex:
            print(ex)

    def move_textos(self,*args):
        self.pai.double_click = False
        if args[0].background_color == [1,1,1,1]:
            args[0].background_color = [0,0,1,1]

            self.lista_textos = self.pai.ax.texts
            self.pai.bl_figura.on_touch_down = self.desce_textos_
            self.pai.bl_figura.on_touch_move = self.move_textos_
            self.move = self.pai.move
            self.pai.move = self.pai.move_
            
        else:
            args[0].background_color = [1,1,1,1]
            self.pai.bl_figura.on_touch_down = self.pai.on_touch_down
            self.pai.bl_figura.on_touch_move = self.pai.on_touch_move
            self.pai.move = self.move
            
    def desce_textos_(self,*args):
        if len(self.lista_textos) == 0:
            self.texto_selecionado = None
            return
        self.pai.on_touch_down(*args)
        px = self.pai.ptx
        py = self.pai.pty
        texto = self.lista_textos[0]
        
        x1,x2 = self.pai.ax.get_xlim()
        y1,y2 = self.pai.ax.get_ylim()
        DX = abs(x2-x1); DY = abs(y2-y1)
        
        d = (((px-texto._x)/DX)**2 + ((py-texto._y)/DY)**2)**0.5
        for t in self.lista_textos[1:]:
            d2 = (((px-t._x)/DX)**2 + ((py-t._y)/DY)**2)**0.5
            if d2 < d:
                texto = t
                d = d2

        self.texto_selecionado = texto

    def move_textos_(self,*args):
        if self.texto_selecionado == None:
            return
        self.pai.on_touch_move(*args)

        self.texto_selecionado.set_x(self.pai.ptx2)
        self.texto_selecionado.set_y(self.pai.pty2)
        self.pai.atualiza()
        #self.tipx.text = str(self.pai.ptx2)

class bar_menu(lateral_menu):
    def __init__(self,pai,ax,**args):
        super().__init__(pai,text = 'Bar plots',**lateral_args)
        self.ax = ax
    def funcao1(self,*args):
        self.new_list(True)

        for bar in self.ax.containers:
            if isinstance(bar,BarContainer) == True:
                self.pai.bl_lateral.lista.append(bar_ig(self.pai,bar))

        self.pai.bl_lateral.cria()

class bar_ig(lateral_menu):
    def __init__(self,pai,bar,**args):
        super().__init__(pai,text = bar.get_label(),**lateral_args)
        self.bar = bar

    def funcao1(self,*args):
        self.new_list(True)

        self.labelti_attr(self.bar,'set_label',
                              eval('self.bar.get_label()'),
                                                 label_att = True)

        self.pai.bl_lateral.lista.append(patche_menu(self.pai,self.bar))
        
        self.pai.bl_lateral.cria()
        

class patche_menu(lateral_menu):
    def __init__(self,pai,bar,**args):

        super().__init__(pai,text = 'Patches',**lateral_args)
        self.bar = bar

    def funcao1(self,*args):
        self.new_list(True)

        for i in self.bar.patches:
            self.pai.bl_lateral.lista.append(patche_ig(self.pai,i))
        
        self.pai.bl_lateral.cria()


class patche_ig(lateral_menu):
    def __init__(self,pai,patche,**args):

        super().__init__(pai,text = str(patche.get_x()),**lateral_args)
        self.patche = patche

    def funcao1(self,*args):
        self.new_list(True)

        mtd = methods_ig(self.pai,self.patche,patche_load_list)
        self.pai.bl_lateral.lista.append(mtd)
        mtd.muda_cor();mtd.funcao1()
        
        self.pai.bl_lateral.cria()
        
class line_ig(BoxLayout):
    def __init__(self,pai,line,**args):
        super().__init__(orientation = 'horizontal',**lateral_args)
        self.pai = pai
        self.line = line
        self.button =line_ig_button(pai,line,
                                       size_hint_x = None,
                                       size_hint_y = None,
                                       size = (0.8*pai.bl_lateral.size[0],30)) 
        self.add_widget(self.button)
        b = lateral_menu(pai,bl = self,
                         text = 'x',
                         size_hint_x = None,
                         size_hint_y = None,
                         size = (0.2*pai.bl_lateral.size[0],30))
        
        b.funcao1 = lambda *x: self.set_visible(1)
        b.funcao2 = lambda *x: self.set_visible(0)
        b.background_color = [1,1,1,1] if line.get_visible() == 0 else [0,0,1,1]

    def set_visible(self,v):

        visible(self.line,v)
        self.pai.atualiza()
      

    def conteiner(self,conteiner,*args):
        self.line.conteiner = conteiner
        self.pai.bl_lateral.lista.remove(self)
        self.pai.bl_lateral.cria()
        print(self.line.conteiner)
        #add a line no conteiner
        
class line_ig_button(lateral_menu):
    def __init__(self,pai,line,**args):
        super().__init__(pai,
                         size_hint_x = 1,
                         size_hint_y = None,
                         size = (0,30))
        self.text = line.get_label()
        self.line = line
        
        
    def funcao1(self,*args):
        self.new_list()
        self.pai.bl_lateral.lista = [self.parent]
        self.labelti_attr(self.line,'line.')
        self.labelti(lambda *args: legend_line(self.line,args[0].text),
                                               'legend',
                                               self.line.get_label())
        
        self.pai.bl_lateral.lista.append(methods_ig(self.pai,self.line,line_load_list))
        #sort line
        b = lateral_menu(pai = self.pai,text = 'sort line',
                                                **lateral_args)

        self.pai.bl_lateral.lista.append(b)
        b.funcao2 = lambda *args: sort_line(self.line,False)
        b.funcao1 = lambda *args: sort_line(self.line)
        if 'argsort' in self.line.__dict__ and type(self.line.argsort) != type(None):
            b.muda_cor()
        #baseline
        self.pai.bl_lateral.lista.append(baseline_ig(self.pai,self.line))
        #fit
        self.pai.bl_lateral.lista.append(fit_menu(self.pai,self.line))
        #manipulate data
        self.pai.bl_lateral.lista.append(manipulate_data(self.pai,self.line))
        #muda ax
        self.pai.bl_lateral.lista.append(muda_ax(self.pai,self.line))

        #erros
        self.pai.bl_lateral.lista.append(erro_menu(self.pai,self.line,'erro y'))
        
        #separa repetidos
        self.pai.bl_lateral.lista.append(botao_deleta(self.separa_repetidos,
                                                      text = 'separa repetidos',
                                                      **lateral_args))
        #to clipboard
        self.pai.bl_lateral.lista.append(botao_deleta(lambda *args: to_cp(self.line.get_xdata(),
                                                                          self.line.get_ydata()),
                                                text = 'to_clipboard',
                                                **lateral_args))
        #save data
        self.labelti(lambda *args: salva_dados(args[0].text,self.line.get_xdata(),
                                               self.line.get_ydata()),
                     'save data',self.line.get_label())
        self.pai.bl_lateral.cria()



    def separa_repetidos(self,*args):
        x,y = self.line.get_data()
        m = separa_repetidos(x,y)
        if type(m) == type(None):
            return
        else:
            ax = self.line.axes
            for df in m:
                l = ax.plot(df.index,df[0],label = '_' + new_name_func(self.line.get_label(),
                                                [ln.get_label() for ln in ax.lines]),
                            color = self.line.get_color(), ls = self.line.get_ls(),
                            ms = self.line.get_ms())[0]
                if 'conteiner' in self.line.__dict__:
                    l.conteiner = self.line.conteiner
                print(l)
        self.pai.atualiza()

class methods_ig(lateral_menu):
    def __init__(self,pai,obj,load_list,text = 'methods'):
        super().__init__(pai,
                         size_hint_x = 1,
                         size_hint_y = None,
                         size = (0,30),
                         text = text)
        self.obj = obj
        self.list = load_list

    def funcao1(self,*args):
        self.lista_original = self.pai.bl_lateral.lista.copy()
        
        for i in self.list:
            self.labelti_attr(self.obj,get2set(i),
                              eval('self.obj.%s()'%i),
                                                 label_att = True)
        self.pai.bl_lateral.cria()


class erro_menu(lateral_menu):
    def __init__(self,pai,line,text = 'erro y',**args):
        super().__init__(pai,text = text,
                         **lateral_args)

        
        if 'df_err' not in line.__dict__:
            line.df_err = pd.DataFrame()
        if 'list_errx' not in line.__dict__:
            line.list_errx = []
        if 'list_erry' not in line.__dict__:
            line.list_erry = []

        self.line = line

    def funcao1(self,*args):
        line = self.line
        self.new_list(True)

        self.pai.bl_lateral.lista.append(Label(text = 'Down,Up',
                                         **lateral_args))

        self.ti_yerr = self.labelti(self.set_yerr,
                      'yerr',','.join(self.line.list_erry))


        self.pai.bl_lateral.lista.append(Label(text = 'df_err',
                                         **lateral_args))

        for i in self.line.df_err.columns:
            self.pai.bl_lateral.lista.append(button_err(i,line,self.ti_yerr,self.pai))

        self.pai.bl_lateral.cria()

    def set_yerr(self,*args):
        self.line.list_erry = self.ti_yerr.text.split(',')
        


class button_err(lateral_menu):
    def __init__(self,text,line,ti,pai):
        super().__init__(pai = pai,text = text,
                         **lateral_args)
        self.line = line
        self.ti = ti
        
    def funcao1(self,*args):
        '''adiciona a coluna como err down'''
         
        #se existir retira
        l = self.ti.text.strip().split(',')
        if '' in l:
            l.remove('')
        if self.text in l:
            l.remove(self.text)
        else:
            l.insert(0,self.text)
            
        self.ti.text = ','.join(l)

        self.background_color = [1,1,1,1]

    def funcao1d(self,*args):
        '''adiciona a coluna como erro up'''
        #se existir retira
        l = self.ti.text.strip().split(',')
        if '' in l:
            l.remove('')
        if self.text in l:
            l.remove(self.text)
        else:
            l.append(self.text)
        print(l)
        self.ti.text = ','.join(l)

        self.background_color = [1,1,1,1]

class fp_ig(modelo):
    def __init__(self,fig,ax = None):
                
        pd.set_option('display.max_colwidth', 9999999999999)
        pd.set_option('max_rows', 9999999999999)
        pd.set_option('max_columns', 9999999999999)

        print('Abrindo',fig)

        #list of pandas dataframes
        
        pandas_init = False
        if type(fig) == str:
            #open a .plt file
            if '.plt' in fig:
                self.nome_grafico = fig
                dic = pd.read_hdf(fig)['graf'].to_dict()
                
                self.df_dict = dic['df_dict'] if 'df_dict' in dic else {}
                self.conteiners = dic['conteiners'] if 'conteiners' in dic else []
                fig = load_fig(dic)
                super().__init__(fig,fig.axes[0])
                

            else:
                self.df_dict = {}
                self.conteiners = []
                if fig.split('.')[-1] in ['png','jpeg','tif','jpg']:
                    self.nome_grafico = fig.split('.')[0] + '.plt'
                    img = fig
                    fig,ax = plt.subplots()
                    load_img(img,ax)
                    super().__init__(fig,ax)

                else:
                    self.nome_grafico = fig
                    fig,ax = plt.subplots()
                    super().__init__(fig,ax)
                    pandas_init = True            
                
        else:
            super().__init__(fig,ax)
            self.nome_grafico = 'graf1.plt'
            self.df_dict = {}
            self.conteiners = []

        self.double_click = True
    
        #check for twin axes
        list_cb,list_axes = find_colorbar_ax(self.fig.axes)
        find_twin_ax(list_axes)
        
        self.bax = ax_menu(pai = self, bl = self.bl_baixo)

        
        self.blines = line_menu(bl = self.bl_baixo, pai = self,
                                  size_hint_x = None,
                                  size = (50,0))

        self.pandas_menu = pandas_menu(bl = self.bl_baixo,pai = self)

        self.draw = fig.canvas.draw
        fig.canvas.draw = self.atualiza
        
        self.bl_selecao = BoxLayout(size_hint_x = None,
                                    size = (50,0),
                                    orientation = 'vertical')
        
        self.bl_baixo.add_widget(self.bl_selecao)

        tamanho = 125

        bl = BoxLayout(size_hint_x = None,
                             size = (tamanho,0),
                       orientation = 'vertical')

        self.bsalva = Button(size_hint_x = None,
                             size_hint_y = None,
                             size = (tamanho,20),
                             text = 'Salva',
                             on_release = self.salva)

        self.tisalva = TextInput(size_hint_x = None,
                             size = (tamanho,30),
                              size_hint_y = None,
                              text = self.nome_grafico,
                                 multiline = False)

        bl.add_widget(self.bsalva)
        bl.add_widget(self.tisalva)

        self.bl_baixo.add_widget(bl)

        #correct tha name (remove file extention and add the .plt extention
        self.tisalva.text = '.'.join(self.tisalva.text .split('.')[:-1]) + '.plt'

        if pandas_init == True:
            open_pandas(self,self.nome_grafico).funcao1()
            open_pandas(self,self.nome_grafico).funcao1()
        return

##        bl = BoxLayout(size_hint_x = None,
##                       size = (tamanho,0),
##                       orientation = 'vertical')
##        
##        bl.add_widget(Label(text = 'abre arq',
##                            size_hint_x = None,size_hint_y = None,
##                            size = (tamanho,20)))
##        
##        bl.add_widget(TextInput(text = '',multiline = False,
##                                on_text_validate = self.carrega_arquivo,
##                                size_hint_x = None,size_hint_y = None,
##                                size = (tamanho,30)))
##
##
##        self.bl_baixo.add_widget(bl)

        #___________________________________

    def sel_ax(self,nome,*args):
        l = []
        for ax in self.fig.axes:
            name_ax(ax)
            l.append(ax.get_label())
            if ax.get_label() == nome:
                return ax
        self.ti_baixo.text = str(l)
        return None

    def save(self,*args):
        try:
            self.df.name = args[0].text
            dic_selected = {}
            for i in self.columns_list:
                dic_selected[i.botao_sel.text]  = 1 if i.botao_sel.background_color == [0,0,1,1] else 0
            self.old_bbox = self.pai.ax.get_position()
            self.pai.df_dict[self.df.name] = (self.df.copy(),dic_selected)
            self.df_original = self.df
        except Exception as ex:
            self.pai.ti_baixo.text = str(ex)

    def add_df(self,df,nome):
        nome = new_name_func(nome,list(self.df_dict.keys()))
        df.name = nome
        dic_selected = {}
        for i in df.columns:
            dic_selected[i] = 1
        self.df_dict[nome] = (df,dic_selected)

    def atualiza(self,*args):
##        for ax in self.fig.axes:
##            
##            if 'twinx_ax' in ax.__dict__ and ax.twinx_ax != None:
##                ax.twinx_ax.set_ylim(ax.get_ylim())
##            if 'twiny_ax' in ax.__dict__ and ax.twiny_ax != None:
##                ax.twiny_ax.set_xlim(ax.get_xlim())
        self.draw()

    def carrega_arquivo(self,*args):
        pass

    def salva(self,*args):
        
        if '.plt' not in self.tisalva.text:
            file = self.tisalva.text + '.plt'
        else:
            file = self.tisalva.text

        fig = self.fig
        dic = load_fig(fig)
        dic['df_dict'] = self.df_dict
        dic['conteiners'] = self.conteiners
        pd.DataFrame({'graf':dic}).to_hdf(file,mode = 'w',key = 'df')

        fig.savefig('.'+file+'_icone.png')
        pasta = tradus_terminal(os.getcwd())
        
        #arrumar icone
        
        os.system('gio set -t string %s/%s metadata::custom-icon file://%s/%s'%\
                                  (pasta,file,pasta,'.'+file+'_icone.png'))



    def clique_duplo(self,*args):
        if args[0].button == 'left':
            self.clique_duplo_esquerdo(*args)
        if args[0].button == 'right':
            self.clique_duplo_direito(*args)

    def clique_duplo_direito(self,*args):
        if self.double_click == False:
            return
        try:
            ldist = []; lax = []
            #if 'lista_axes' not in self.plot.__dict__:
                #self.plot.lista_axes = []
                #for i in self.plot.fig.get_axes():
                    #self.plot.lista_axes.append(i)

            list_cb,list_axes = find_colorbar_ax(self.fig.axes)
            lista_axes = find_twin_ax(list_axes)
            px = args[0].pos[0]; py = args[0].pos[1]
            for ax in lista_axes:
                b = ax.get_window_extent()
                print(ax)
                dist = ((b.x0 - args[0].pos[0])**2 + (b.y0 - args[0].pos[1])**2)**0.5
                ldist.append(dist)
                lax.append(ax)
                if 'twinx_ax' in ax.__dict__ and ax.twinx_ax != None:
                    ax = ax.twinx_ax
                    b = ax.get_window_extent()
                    dist = ((b.x1 - args[0].pos[0])**2 + (b.y0 - args[0].pos[1])**2)**0.5
                    ldist.append(dist)
                    lax.append(ax)
                        
                if 'twiny_ax' in ax.__dict__ and ax.twiny_ax != None:
                    ax = ax.twiny_ax
                    b = ax.get_window_extent()
                    dist = ((b.x1 - args[0].pos[0])**2 + (b.y1 - args[0].pos[1])**2)**0.5
                    ldist.append(dist)
                    lax.append(ax)
            ##print(ldist,lax)
            self.ax = lax[np.array(ldist).argsort()[0]]
            ig = ax_ig(ax = self.ax,pai = self)
            ig.funcao1(); ig.background_color = [0,0,1,1]

                
        except Exception as ex:
            print(ex,ex.__traceback__.tb_lineno,'clique_duplot_direito')
            
    def clique_duplo_esquerdo(self,*args):
        if self.double_click == False:
            return
        try:
            ld = []
            lista_lines = []
            lista_text = []
            lista_figuras = []
            x1,x2 = self.ax.get_xlim()
            y1,y2 = self.ax.get_ylim()
            DX = abs(x2-x1)
            DY = abs(y2-y1)

            a = self.ax.get_window_extent()

            xcima = a.x0 + self.bl_figura.x; xbaixo = a.x1 +  self.bl_figura.x
            ycima = a.y0 + self.bl_figura.y; ybaixo = a.y1 + self.bl_figura.y

            print(xcima,xbaixo,ycima,ybaixo)
            print(self.px,self.py)
            if abs(self.px - xcima) <= 5:
                t_ig = axis_ig(self,'yaxis',self.ax.yaxis)
                t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return
            if abs(self.px - xbaixo) <= 5:
                if self.ax.twinx_ax != None:
                    t_ig = axis_ig(self,'yaxis2',self.ax.twinx_ax.yaxis)
                    t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return
            if abs(self.py - ycima) <= 5:
                t_ig = axis_ig(self,'xaxis',self.ax.xaxis)
                t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return
            if abs(self.py - ybaixo) <= 5:
                if self.ax.twiny_ax != None:
                    t_ig = axis_ig(self,'xaxis2',self.ax.twiny_ax.xaxis)
                    t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return

            if -xcima + self.px < -5:
                t_ig = label_ig(self,'y1')
                t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return

            if xbaixo - self.px < -5:
                t_ig = label_ig(self,'y2')
                t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return


            if -ycima + self.py < -5:
                t_ig = label_ig(self,'x1')
                t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return


            if ybaixo - self.py < -40:
                #print(ybaixo-self.py)
                t_ig = titulo_ig(self)
                t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return



            if ybaixo - self.py < -5:
                t_ig = label_ig(self,'x2')
                t_ig.funcao1(); t_ig.background_color = [0,0,1,1]
                return

                
            for i in self.ax.lines:
                x,y = i.get_data()
                if len(x) > 0 and i.get_visible() == True:
                    try:
                        ind1 = busca(x,self.ptx)
                        dist = (((x[ind1] - self.ptx)/DX)**2 + ((y[ind1] - self.pty)/DY)**2)**0.5
                        #print(i.nome,ind1,x[ind1],y[ind1],dist)
                        
                        
                        while dist in ld:
                            dist += 0.0000001
                        ld.append(dist)
                        lista_lines.append((dist,i))
                    except Exception as ex:
                        pass

                #texts
                for t in self.ax.texts:
                    if t != None:
                        dist = (((t._x-self.ptx)/DX)**2 + ((t._y-self.pty)/DY)**2)**0.5
                        while  dist in ld:
                            dist += 1.0000001
                        ld.append(dist)
                        lista_text.append((dist,t,i))
                        

                if 'lista_desenhos' in i.__dict__:
                    for cont in i.lista_desenhos:
                        for fig in cont.lista_figuras:
                            dist = (((fig.x0-self.ptx)/DX)**2 + ((fig.y0-self.pty)/DY)**2)**0.5
                            while dist in ld:
                                dist += 1.0000001
                            ld.append(dist)
                            lista_figuras.append((dist,fig))

            l = lista_lines + lista_text + lista_figuras
            
            if 'ultimo_clicado' in self.__dict__:
                if time() - self.t_ultimo_clicado < 1:
                    if self.ultimo_clicado in l:
                        l.remove(self.ultimo_clicado)

            menor = min(l)

            if menor in lista_lines:
                if 'figura' in menor[1].__dict__:
                    menor[1].figura.funcao1()
                    menor[1].figura.background_colorg = [0,0,1,1]
                else:
                    l = line_ig(self,menor[1])
                    l.button.funcao1(); l.background_color = [0,0,1,1]
            if menor in lista_text:
                d,texto,line = menor
                t_ig = text_ig(self,text = texto)
                t_ig.button.funcao1(); t_ig.background_color = [0,0,1,1]

            if menor in lista_figuras:
                menor[1].funcao1()

            self.t_ultimo_clicado = time()
            self.ultimo_clicado = menor
                
        except Exception as ex:
            print(ex,ex.__traceback__.tb_lineno)


    
argv = sys.argv



print(argv)
if len(argv) > 2:
    argv = [argv[0],' '.join(argv[1:])]
if len(argv) == 2:
    nome = argv[1].split('/')[-1].strip('\n')
    if '/' in argv[1]:
        #change to folder (if it is not the same as the program)
        os.chdir('/'+argv[1].strip('\n').strip(nome).strip('/'))
    else:
        pass
    fp_ig(nome).run()

#fp_ig(fig).run()
